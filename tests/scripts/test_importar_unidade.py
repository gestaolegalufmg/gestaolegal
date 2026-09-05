"""Testes do script de importação de unidade (Fase B de `docs/unidades.md`).

Os dois bancos são SQLite em arquivo, criados a partir do próprio
`tables.py`, e o script fala com eles por reflection — o mesmo caminho que
usará contra o MySQL de produção.
"""

from datetime import date, datetime

import pytest
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, select

from gestaolegal.database.tables import metadata
from scripts.importar_unidade import ImportacaoAbortada, importar

HOJE = date(2026, 9, 5)
AGORA = datetime(2026, 9, 5, 10, 0, 0)


def usuario(email: str, nome: str = "Fulano") -> dict:
    return {
        "email": email,
        "senha": "x" * 60,
        "urole": "estag_direito",
        "nome": nome,
        "sexo": "M",
        "rg": "MG1",
        "cpf": "111.111.111-11",
        "profissao": "estudante",
        "estado_civil": "solteiro",
        "nascimento": HOJE,
        "celular": "31999999999",
        "data_entrada": HOJE,
        "criado": AGORA,
        "criadopor": 1,
        "bolsista": False,
        "status": True,
        "cert_atuacao_DAJ": "nao",
    }


def atendido(cpf: str, nome: str = "Beltrano") -> dict:
    return {
        "nome": nome,
        "data_nascimento": HOJE,
        "cpf": cpf,
        "celular": "31988888888",
        "email": f"{cpf}@exemplo.com",
        "estado_civil": "solteiro",
        "como_conheceu": "amigos",
        "procurou_outro_local": "nao",
        "pj_constituida": "nao",
        "status": 1,
    }


def assistido(id_atendido: int) -> dict:
    return {
        "id_atendido": id_atendido,
        "sexo": "M",
        "profissao": "pedreiro",
        "raca": "parda",
        "rg": "MG2",
        "grau_instrucao": "medio",
        "salario": 1500,
        "beneficio": "nao",
        "contribui_inss": "nao",
        "qtd_pessoas_moradia": 3,
        "renda_familiar": 3000,
        "participacao_renda": "principal",
        "tipo_moradia": "alugada",
        "possui_outros_imoveis": False,
        "possui_veiculos": False,
        "doenca_grave_familia": "nao",
    }


def caso(id_usuario: int) -> dict:
    return {
        "id_usuario_responsavel": id_usuario,
        "area_direito": "civel",
        "data_criacao": AGORA,
        "id_criado_por": id_usuario,
        "situacao_deferimento": "deferido",
        "status": True,
    }


def evento(id_caso: int, id_usuario: int, arquivo: str | None = None) -> dict:
    return {
        "id_caso": id_caso,
        "tipo": "audiencia",
        "data_evento": HOJE,
        "data_criacao": AGORA,
        "id_criado_por": id_usuario,
        "status": True,
        "arquivo": arquivo,
    }


def _criar_banco(caminho, unidades: list[tuple[str, str]]):
    motor = create_engine(f"sqlite:///{caminho}")
    metadata.create_all(motor)
    with motor.begin() as conn:
        for indice, (nome, sigla) in enumerate(unidades, start=1):
            conn.execute(
                metadata.tables["unidades"].insert().values(
                    id=indice, nome=nome, sigla=sigla, ativa=True, criado=AGORA
                )
            )
    return motor


@pytest.fixture
def bancos(tmp_path):
    """Origem com uma unidade só; destino já com Belo Horizonte e Nova Lima."""

    origem = _criar_banco(tmp_path / "nl.db", [("Nova Lima", "NL")])
    destino = _criar_banco(
        tmp_path / "final.db", [("Belo Horizonte", "BH"), ("Nova Lima", "NL")]
    )
    return origem, destino


def urls(bancos):
    origem, destino = bancos
    return str(origem.url), str(destino.url)


def inserir(motor, tabela: str, valores: dict) -> int:
    with motor.begin() as conn:
        resultado = conn.execute(metadata.tables[tabela].insert().values(**valores))
        return resultado.inserted_primary_key[0]


def linhas(motor, tabela: str) -> list:
    with motor.connect() as conn:
        return conn.execute(select(metadata.tables[tabela])).mappings().all()


class TestEnsaio:
    def test_ensaio_conta_sem_gravar(self, bancos):
        origem, destino = bancos
        inserir(origem, "usuarios", usuario("novo@nl.br"))

        rel = importar(*urls(bancos), "NL")

        assert rel.inseridos["usuarios"] == 1
        assert linhas(destino, "usuarios") == []

    def test_executar_grava(self, bancos):
        origem, destino = bancos
        inserir(origem, "usuarios", usuario("novo@nl.br"))

        importar(*urls(bancos), "NL", executar=True)

        assert [linha["email"] for linha in linhas(destino, "usuarios")] == ["novo@nl.br"]


class TestRemapeamento:
    def test_ids_colididos_viram_ids_novos_e_fks_seguem(self, bancos):
        origem, destino = bancos
        # O destino já tem um usuário e um caso com id 1: a origem não pode
        # sobrescrever nem apontar para eles.
        u_bh = inserir(destino, "usuarios", usuario("bh@bh.br", "De BH"))
        inserir(destino, "casos", caso(u_bh) | {"unidade_id": 1})

        u_nl = inserir(origem, "usuarios", usuario("nl@nl.br", "De NL"))
        c_nl = inserir(origem, "casos", caso(u_nl) | {"unidade_id": 1})
        inserir(origem, "eventos", evento(c_nl, u_nl) | {"unidade_id": 1})

        importar(*urls(bancos), "NL", executar=True)

        casos = {linha["id"]: linha for linha in linhas(destino, "casos")}
        assert len(casos) == 2
        importado = next(c for c in casos.values() if c["unidade_id"] == 2)
        usuarios = {linha["id"]: linha["nome"] for linha in linhas(destino, "usuarios")}
        assert usuarios[importado["id_usuario_responsavel"]] == "De NL"

        eventos = linhas(destino, "eventos")
        assert len(eventos) == 1
        assert eventos[0]["id_caso"] == importado["id"]
        assert eventos[0]["unidade_id"] == 2

    def test_raizes_recebem_a_unidade_importada(self, bancos):
        origem, destino = bancos
        u = inserir(origem, "usuarios", usuario("nl@nl.br"))
        a = inserir(origem, "atendidos", atendido("222.222.222-22") | {"unidade_id": 1})
        inserir(origem, "casos", caso(u) | {"unidade_id": 1})
        inserir(
            origem,
            "fila_atendimentos",
            {
                "psicologia": 0,
                "prioridade": 0,
                "senha": "N01",
                "status": 1,
                "id_atendido": a,
                "unidade_id": 1,
            },
        )

        importar(*urls(bancos), "NL", executar=True)

        for tabela in ("atendidos", "casos", "fila_atendimentos"):
            assert {linha["unidade_id"] for linha in linhas(destino, tabela)} == {2}


class TestDeduplicacao:
    def test_usuario_com_email_repetido_e_reaproveitado(self, bancos):
        origem, destino = bancos
        u_bh = inserir(destino, "usuarios", usuario("comum@daj.br", "De BH"))
        u_nl = inserir(origem, "usuarios", usuario("comum@daj.br", "De NL"))
        inserir(origem, "casos", caso(u_nl) | {"unidade_id": 1})

        rel = importar(*urls(bancos), "NL", executar=True)

        assert rel.reaproveitados["usuarios"] == 1
        assert len(linhas(destino, "usuarios")) == 1
        # O caso de Nova Lima aponta para o usuário que já existia em BH.
        assert linhas(destino, "casos")[0]["id_usuario_responsavel"] == u_bh

    def test_usuario_das_duas_unidades_fica_vinculado_as_duas(self, bancos):
        origem, destino = bancos
        u_bh = inserir(destino, "usuarios", usuario("comum@daj.br"))
        with destino.begin() as conn:
            conn.execute(
                metadata.tables["usuarios_unidades"].insert().values(
                    usuario_id=u_bh, unidade_id=1
                )
            )
        inserir(origem, "usuarios", usuario("comum@daj.br"))

        importar(*urls(bancos), "NL", executar=True)

        vinculos = {
            (linha["usuario_id"], linha["unidade_id"])
            for linha in linhas(destino, "usuarios_unidades")
        }
        assert vinculos == {(u_bh, 1), (u_bh, 2)}

    def test_atendido_com_cpf_repetido_nao_duplica_o_assistido(self, bancos):
        origem, destino = bancos
        a_bh = inserir(destino, "atendidos", atendido("333.333.333-33") | {"unidade_id": 1})
        inserir(destino, "assistidos", assistido(a_bh))
        a_nl = inserir(origem, "atendidos", atendido("333.333.333-33") | {"unidade_id": 1})
        inserir(origem, "assistidos", assistido(a_nl))

        rel = importar(*urls(bancos), "NL", executar=True)

        assert rel.reaproveitados["atendidos"] == 1
        assert rel.reaproveitados["assistidos"] == 1
        assert len(linhas(destino, "atendidos")) == 1
        assert len(linhas(destino, "assistidos")) == 1
        # O cadastro único fica na unidade onde foi criado primeiro (decisão 3).
        assert linhas(destino, "atendidos")[0]["unidade_id"] == 1


class TestAutoriaDeUsuarios:
    def test_criadopor_aponta_para_o_usuario_importado(self, bancos):
        origem, destino = bancos
        inserir(destino, "usuarios", usuario("bh@bh.br", "De BH"))
        chefe = inserir(origem, "usuarios", usuario("chefe@nl.br", "Chefe"))
        inserir(
            origem, "usuarios", usuario("novato@nl.br", "Novato") | {"criadopor": chefe}
        )

        importar(*urls(bancos), "NL", executar=True)

        usuarios = {linha["nome"]: linha for linha in linhas(destino, "usuarios")}
        assert usuarios["Novato"]["criadopor"] == usuarios["Chefe"]["id"]

    def test_criador_ausente_mantem_o_id_antigo_e_avisa(self, bancos):
        origem, _ = bancos
        inserir(origem, "usuarios", usuario("novato@nl.br") | {"criadopor": 777})

        rel = importar(*urls(bancos), "NL", executar=True)

        assert any("autoria" in aviso for aviso in rel.avisos)


class TestArquivosENotificacoes:
    def test_nome_de_arquivo_ganha_prefixo_da_unidade(self, bancos):
        origem, destino = bancos
        u = inserir(origem, "usuarios", usuario("nl@nl.br"))
        c = inserir(origem, "casos", caso(u) | {"unidade_id": 1})
        inserir(origem, "eventos", evento(c, u, arquivo="ata.pdf") | {"unidade_id": 1})
        inserir(origem, "arquivosCaso", {"id_caso": c, "link_arquivo": "casos/peca.pdf"})

        importar(*urls(bancos), "NL", executar=True)

        assert linhas(destino, "eventos")[0]["arquivo"] == "NL_ata.pdf"
        assert linhas(destino, "arquivosCaso")[0]["link_arquivo"] == "casos/NL_peca.pdf"

    def test_notificacao_remapeia_caso_e_zera_referencia_sem_tipo(self, bancos):
        origem, destino = bancos
        u = inserir(origem, "usuarios", usuario("nl@nl.br"))
        c = inserir(origem, "casos", caso(u) | {"unidade_id": 1})
        e = inserir(origem, "eventos", evento(c, u) | {"unidade_id": 1})
        inserir(
            origem,
            "notificacao",
            {
                "acao": "evento criado",
                "data": HOJE,
                "id_usu_notificar": u,
                "tipo": "evento",
                "id_caso": c,
                "id_referencia": e,
                "lida": False,
            },
        )
        inserir(
            origem,
            "notificacao",
            {"acao": "herdada da 2.0", "data": HOJE, "id_referencia": 99, "lida": False},
        )

        importar(*urls(bancos), "NL", executar=True)

        novo_caso = linhas(destino, "casos")[0]["id"]
        novo_evento = linhas(destino, "eventos")[0]["id"]
        avisos = {linha["acao"]: linha for linha in linhas(destino, "notificacao")}
        assert avisos["evento criado"]["id_caso"] == novo_caso
        assert avisos["evento criado"]["id_referencia"] == novo_evento
        assert avisos["herdada da 2.0"]["id_referencia"] is None


class TestSalvaguardas:
    def test_numero_de_processo_colidido_aborta_sem_a_opcao(self, bancos):
        origem, destino = bancos
        u_bh = inserir(destino, "usuarios", usuario("bh@bh.br"))
        c_bh = inserir(destino, "casos", caso(u_bh) | {"unidade_id": 1})
        inserir(
            destino,
            "processos",
            {"especie": "civel", "numero": 42, "id_caso": c_bh, "status": True, "id_criado_por": u_bh},
        )
        u_nl = inserir(origem, "usuarios", usuario("nl@nl.br"))
        c_nl = inserir(origem, "casos", caso(u_nl) | {"unidade_id": 1})
        inserir(
            origem,
            "processos",
            {"especie": "civel", "numero": 42, "id_caso": c_nl, "status": True, "id_criado_por": u_nl},
        )

        with pytest.raises(ImportacaoAbortada, match="processos.numero"):
            importar(*urls(bancos), "NL")

        rel = importar(*urls(bancos), "NL", executar=True, zerar_numero_processo_colidido=True)
        assert rel.inseridos["processos"] == 1
        numeros = {linha["numero"] for linha in linhas(destino, "processos")}
        assert numeros == {42, None}

    def test_tabela_fora_do_plano_aborta_a_importacao(self, bancos):
        origem, _ = bancos
        avulsa = Table(
            "tabela_nova",
            MetaData(),
            Column("id", Integer, primary_key=True),
            Column("valor", String(10)),
        )
        avulsa.create(origem)

        with pytest.raises(ImportacaoAbortada, match="tabela_nova"):
            importar(*urls(bancos), "NL")

    def test_sigla_inexistente_aborta(self, bancos):
        with pytest.raises(ImportacaoAbortada, match="XX"):
            importar(*urls(bancos), "XX")
