"""Dados fictícios de desenvolvimento, sem depender da API.

Uso: uv run python scripts/seed_database.py [--dry-run] [--unidade SIGLA]
Requer migrations aplicadas. Toda a carga usa uma única transação.
"""

from __future__ import annotations

import argparse
import os
import runpy
import sys
from collections import Counter
from datetime import date, datetime, time, timedelta
from pathlib import Path

import bcrypt
from dotenv import load_dotenv
from sqlalchemy import Table, create_engine, select
from sqlalchemy.engine import Connection, Engine, URL
from sqlalchemy.exc import SQLAlchemyError

# Importar gestaolegal.database inicializa a sessão e exige configuração da
# API. Carregamos somente a declaração do schema, sem esses efeitos colaterais.
metadata = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "gestaolegal/database/tables.py")
)["metadata"]

MARCA_ANTIGA = "seed_database:v1"
MARCA = "Demonstração"
CONTAS = (
    ("admin", "Administrador"),
    ("orient", "Olívia Orientadora"),
    ("estag_direito", "Eduardo Estagiário"),
    ("colab_ext", "Carla Colaboradora"),
)
NOMES_ATENDIDOS = (
    "Maria Exemplo", "José Exemplo", "Ana Martins", "Bruno Ferreira",
    "Camila Costa", "Diego Almeida", "Elisa Santos", "Fábio Oliveira",
    "Gabriela Souza", "Henrique Lima", "Isabela Rocha", "João Pereira",
    "Larissa Gomes", "Marcos Ribeiro", "Natália Barros", "Otávio Teixeira",
    "Patrícia Araújo", "Rafael Mendes", "Sílvia Carvalho", "Tiago Nunes",
)


def cpf_demonstracao(base: int) -> str:
    """Identificador sintético determinístico, com verificadores válidos.

    Não identifica uma pessoa real nem comprova inscrição na Receita Federal.
    """
    if not 100_000_000 <= base <= 999_999_999:
        raise ValueError("Base do CPF de demonstração deve ter nove dígitos.")
    digits = [int(digit) for digit in str(base)]
    for length in (9, 10):
        remainder = sum(digit * weight for digit, weight in
                        zip(digits, range(length + 1, 1, -1))) % 11
        digits.append(0 if remainder < 2 else 11 - remainder)
    value = "".join(map(str, digits))
    return f"{value[:3]}.{value[3:6]}.{value[6:9]}-{value[9:]}"


class Seed:
    def __init__(self, conn: Connection):
        self.conn = conn
        self.criados: Counter[str] = Counter()

    def buscar(self, tabela: Table, chave: dict):
        return self.conn.execute(select(tabela).filter_by(**chave)).mappings().one_or_none()

    def inserir(self, tabela: Table, dados: dict):
        result = self.conn.execute(tabela.insert().values(**dados))
        self.criados[tabela.name] += 1
        return result.inserted_primary_key[0] if "id" in tabela.c else None

    def garantir(self, nome_tabela: str, chave: dict, **dados):
        tabela = metadata.tables[nome_tabela]
        existente = self.buscar(tabela, chave)
        # Reconhece os identificadores antigos sem duplicar casos, eventos e escalas.
        antiga = {k: v.replace(f"[{MARCA}]", f"[{MARCA_ANTIGA}]")
                  if isinstance(v, str) else v for k, v in chave.items()}
        if existente is None and antiga != chave:
            existente = self.buscar(tabela, antiga)
            if existente is not None:
                self.conn.execute(tabela.update().where(tabela.c.id == existente["id"]).values(**chave))
        if existente is not None:
            return existente.get("id")
        return self.inserir(tabela, {**dados, **chave})

    def endereco(self):
        return self.inserir(metadata.tables["enderecos"], {
            "logradouro": "Rua de Demonstração", "numero": "100",
            "bairro": "Centro", "cep": "30000-000",
            "cidade": "Belo Horizonte", "estado": "MG",
        })

    def carregar(self, senha: str, sigla: str | None, hoje: date):
        unidades = metadata.tables["unidades"]
        query = select(unidades).where(unidades.c.ativa.is_(True)).order_by(unidades.c.id)
        if sigla:
            query = query.where(unidades.c.sigla == sigla)
        selecionadas = self.conn.execute(query).mappings().all()
        if not selecionadas:
            raise ValueError("Nenhuma unidade ativa selecionada. Aplique as migrations e confira --unidade.")

        agora = datetime.combine(hoje, time(9))
        usuarios = {}
        for numero_usuario, (papel, nome) in enumerate(CONTAS, start=1):
            email = f"{papel}@ufmg.br"
            existente = self.buscar(metadata.tables["usuarios"], {"email": email})
            if existente is not None:
                if existente["obs"] not in (MARCA, MARCA_ANTIGA):
                    raise ValueError(f"E-mail reservado ao seed já está em uso: {email}")
                ajustes = {"obs": MARCA}
                if existente["nome"] == f"{nome} Seed":
                    ajustes["nome"] = nome
                if existente["cpf"] == "000.000.000-00":
                    ajustes["cpf"] = cpf_demonstracao(900_000_000 + numero_usuario)
                if existente["rg"] == "SEED":
                    ajustes["rg"] = f"MG-{100_000 + numero_usuario}"
                tabela = metadata.tables["usuarios"]
                self.conn.execute(tabela.update().where(tabela.c.id == existente["id"]).values(**ajustes))
                usuarios[papel] = existente["id"]
                continue
            uid = self.garantir("usuarios", {"email": email},
                nome=nome, senha=bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode(),
                urole=papel, sexo="F", rg=f"MG-{100_000 + numero_usuario}",
                cpf=cpf_demonstracao(900_000_000 + numero_usuario),
                profissao="Demonstração", estado_civil="solteiro",
                nascimento=date(1990, 1, 15), celular="(31) 90000-0000",
                data_entrada=hoje, criado=agora, criadopor=usuarios.get("admin", 0),
                bolsista=False, status=True, cert_atuacao_DAJ="nao", obs=MARCA,
                endereco_id=self.endereco())
            usuarios[papel] = uid
            if papel == "admin":
                tabela = metadata.tables["usuarios"]
                self.conn.execute(tabela.update().where(tabela.c.id == uid).values(criadopor=uid))

        for unidade in selecionadas:
            unidade_id = unidade["id"]
            for uid in usuarios.values():
                self.garantir("usuarios_unidades", {"usuario_id": uid, "unidade_id": unidade_id})
            admin, orient, estag = (usuarios[p] for p in ("admin", "orient", "estag_direito"))
            for indice, nome in enumerate(NOMES_ATENDIDOS, start=1):
                chave = {"unidade_id": unidade_id, "email": f"atendido{indice}.u{unidade_id}@example.test"}
                tabela = metadata.tables["atendidos"]
                existente = self.buscar(tabela, chave)
                if existente is None:
                    existente = self.buscar(tabela, {**chave, "email": f"atendido{indice}.u{unidade_id}@seed.example.test"})
                cpf = cpf_demonstracao(800_000_000 + unidade_id * 100 + indice)
                if existente is not None:
                    if existente["obs"] not in (MARCA, MARCA_ANTIGA):
                        raise ValueError(f"E-mail de demonstração já está em uso: {chave['email']}")
                    ajustes = {"obs": MARCA, "email": chave["email"]}
                    if existente["nome"] == f"{nome} Seed":
                        ajustes["nome"] = nome
                    if existente["cpf"] == "000.000.000-00":
                        ajustes["cpf"] = cpf
                    self.conn.execute(tabela.update().where(tabela.c.id == existente["id"]).values(**ajustes))
                atendido = existente["id"] if existente else self.garantir("atendidos", chave,
                    nome=nome, data_nascimento=date(1985, (indice - 1) % 12 + 1, 10), cpf=cpf,
                    celular="(31) 90000-0000", estado_civil="solteiro", como_conheceu="assist",
                    procurou_outro_local="nao", pj_constituida="nao", status=1,
                    obs=MARCA, endereco_id=self.endereco())
                if indice <= 10:
                    self.garantir("assistidos", {"id_atendido": atendido},
                        sexo="F" if indice % 2 else "M", profissao="Autônomo",
                        raca="nao_declarado", rg=f"MG-{unidade_id:03d}{indice:04d}",
                        grau_instrucao="medio_comp", salario=1200, beneficio="nao",
                        contribui_inss="nao", qtd_pessoas_moradia=3, renda_familiar=1800,
                        participacao_renda="contribuinte", tipo_moradia="alugada",
                        possui_outros_imoveis=False, possui_veiculos=False,
                        doenca_grave_familia="nao", obs=MARCA)
                # Preserva os dois casos e demais registros originais por unidade.
                if indice > 2:
                    continue
                area, assunto = (("civel", "Pedido de alimentos"),
                                 ("trabalhista", "Verbas rescisórias"))[indice - 1]
                caso = self.garantir("casos", {
                    "unidade_id": unidade_id, "descricao": f"[{MARCA}] {assunto}"},
                    area_direito=area, sub_area="familia" if area == "civel" else None,
                    id_usuario_responsavel=estag, id_orientador=orient, id_estagiario=estag,
                    id_colaborador=usuarios["colab_ext"], data_criacao=agora,
                    id_criado_por=admin, situacao_deferimento="ativo", status=True)
                self.garantir("casos_atendidos", {"id_caso": caso, "id_atendido": atendido})
                self.garantir("processos", {"id_caso": caso, "identificacao": f"[{MARCA}] {assunto}"},
                    especie="Ação", status=True, id_criado_por=admin,
                    vara="Vara de demonstração", data_distribuicao=hoje,
                    obs="Processo fictício, sem número judicial real.")
                for numero, (tipo, dias, descricao) in enumerate((
                    ("reuniao", -7, "Entrevista inicial"),
                    ("audencia", 7, "Audiência de conciliação"),
                ), start=1):
                    self.garantir("eventos", {"id_caso": caso, "descricao": f"[{MARCA}] {descricao}"},
                        unidade_id=unidade_id, num_evento=numero, tipo=tipo,
                        data_evento=hoje + timedelta(days=dias), data_criacao=agora,
                        id_criado_por=admin, id_usuario_responsavel=estag, status=True)
                self.garantir("lembretes", {"id_caso": caso, "descricao": f"[{MARCA}] Conferir documentos"},
                    unidade_id=unidade_id, num_lembrete=1, id_do_criador=orient,
                    id_usuario=estag, data_criacao=agora, data_lembrete=agora + timedelta(days=3), status=True)
                orientacao = self.garantir("orientacao_juridica", {
                    "unidade_id": unidade_id, "descricao": f"[{MARCA}] Orientação: {assunto}"},
                    area_direito=area, sub_area="familia" if area == "civel" else None,
                    data_criacao=agora, status=1, id_usuario=orient)
                self.garantir("atendido_xOrientacaoJuridica", {
                    "id_orientacaoJuridica": orientacao, "id_atendido": atendido})

            escala = self.garantir("plantao", {"unidade_id": unidade_id, "nome": f"[{MARCA}] Escala demonstrativa"},
                data_abertura=agora - timedelta(days=7), data_fechamento=agora + timedelta(days=7),
                legado=False, cancelado=False)
            # Datas ancoradas na primeira execução mantêm a reexecução idempotente.
            abertura = self.buscar(metadata.tables["plantao"], {"id": escala})["data_abertura"]
            dia = abertura.date() + timedelta(days=14)
            self.garantir("dias_plantao", {"plantao_id": escala, "data": dia}, unidade_id=unidade_id, status=True)
            for uid in (orient, estag):
                self.garantir("dias_marcados_plantao", {"plantao_id": escala, "id_usuario": uid, "data_marcada": dia},
                    unidade_id=unidade_id, confirmacao="aberto", status=True)


def seed_database(engine: Engine, *, senha: str, sigla: str | None = None,
                  dry_run: bool = False, hoje: date | None = None) -> Counter:
    if not 6 <= len(senha.encode("utf-8")) <= 72:
        raise ValueError("SEED_PASSWORD deve ter entre 6 e 72 bytes em UTF-8.")
    with engine.connect() as conn:
        with conn.begin() as transaction:
            seed = Seed(conn)
            seed.carregar(senha, sigla, hoje or date.today())
            if dry_run:
                transaction.rollback()
        return seed.criados


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Executa e desfaz a transação ao final.")
    parser.add_argument("--unidade", metavar="SIGLA", help="Semeia apenas esta unidade ativa.")
    args = parser.parse_args(argv)
    load_dotenv(Path.cwd() / ".env")
    if os.environ.get("FLASK_ENV") == "production":
        parser.error("Seed de demonstração disponível apenas fora de production.")
    engine = None
    try:
        missing = [key for key in ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME") if not os.environ.get(key)]
        if missing:
            raise ValueError("Configure no .env: " + ", ".join(missing))
        url = URL.create("mysql+pymysql", username=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"],
            port=int(os.environ.get("DB_PORT", "3306")), database=os.environ["DB_NAME"])
        engine = create_engine(url)
        criados = seed_database(engine, senha=os.environ.get("SEED_PASSWORD", "123456"),
            sigla=args.unidade, dry_run=args.dry_run)
    except (ValueError, SQLAlchemyError) as exc:
        # Erros SQL podem carregar parâmetros, inclusive hashes de senha.
        mensagem = str(exc) if isinstance(exc, ValueError) else "Falha no banco. Confira a conexão e aplique as migrations. A transação foi desfeita."
        print(f"seed: {mensagem}", file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()
    print("Simulação concluída (rollback)." if args.dry_run else "Seed concluído.")
    for tabela, quantidade in sorted(criados.items()):
        print(f"  {tabela}: {quantidade}")
    if not criados:
        print("Nenhum registro novo; os dados de seed já existem.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
