"""Importa o banco de uma unidade (Nova Lima) para o banco final da 3.0.

Fase B de `docs/unidades.md`. Pressupõe que o banco de origem já foi restaurado
do dump e migrado até a mesma revisão Alembic do destino (§5.2 do documento):
origem e destino têm o mesmo schema, e a importação é só remapeamento de ids.

Uso:

    uv run python scripts/importar_unidade.py \
        --origem mysql+pymysql://user:senha@host/gestaolegal_nl \
        --destino mysql+pymysql://user:senha@host/gestaolegal \
        --sigla NL

Sem `--executar` o script roda a importação inteira dentro de uma transação e
dá **rollback** no fim: as contagens e os conflitos do relatório são reais, o
banco não muda. Com `--executar`, a mesma transação é confirmada — tudo ou
nada.

O que o script faz, na ordem de `PLANO`:

* copia cada tabela da origem para o destino, gerando ids novos e remapeando
  todas as FKs pela tabela de mapeamento `{tabela: {id_antigo: id_novo}}`;
* grava `unidade_id` da unidade importada nas tabelas raiz (§4.3);
* deduplica usuários por e-mail e atendidos por CPF (decisão 3), reaproveitando
  o registro que já existe no destino em vez de inserir outro;
* vincula em `usuarios_unidades` todo usuário importado ou reaproveitado à
  unidade nova;
* prefixa os nomes de arquivo físico (`--prefixo-arquivo`, padrão a sigla),
  acompanhando a cópia dos arquivos feita fora daqui.

O que ele **não** faz: copiar os arquivos físicos (passo 3 da Fase B), mexer em
`alembic_version`, importar `documentos_roteiro` (conteúdo institucional
compartilhado) nem `unidades`/`usuarios_unidades` da origem.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import MetaData, Table, create_engine, select
from sqlalchemy.engine import Connection

# Tabelas que nunca são importadas, e o motivo.
IGNORADAS = {
    "alembic_version": "controle do Alembic; origem e destino já estão na mesma revisão",
    "unidades": "criadas pela migration da Fase A no destino",
    "usuarios_unidades": "reconstruída a partir dos usuários importados",
    "documentos_roteiro": "conteúdo institucional compartilhado (§4.5)",
}


@dataclass(frozen=True)
class Tabela:
    """Uma tabela do plano de importação.

    `fks` mapeia coluna -> tabela referenciada, e é o que faz o remapeamento de
    id. `unidade=True` marca as raízes do §4.3, que recebem `unidade_id`.
    `dedup` é a coluna que decide se o registro já existe no destino; quando
    existe, o id antigo passa a apontar para o registro de lá e nada é inserido.
    """

    nome: str
    fks: dict[str, str] = field(default_factory=dict)
    unidade: bool = False
    dedup: str | None = None
    # FK cuja unicidade no destino decide o reaproveitamento: a filha um-para-um
    # de um pai deduplicado já existe lá e não pode ser inserida de novo.
    dedup_fk: str | None = None
    # Colunas com nome de arquivo físico, que ganham o prefixo da unidade.
    arquivos: tuple[str, ...] = ()
    # Colunas UNIQUE cuja colisão entre as duas bases só aparece na importação.
    unicas: tuple[str, ...] = ()
    # Tabela sem id próprio (ligação) ou que pode não existir no schema.
    sem_id: bool = False
    opcional: bool = False


PLANO: tuple[Tabela, ...] = (
    Tabela("enderecos"),
    Tabela("usuarios", fks={"endereco_id": "enderecos"}, dedup="email"),
    Tabela(
        "atendidos",
        fks={"endereco_id": "enderecos"},
        unidade=True,
        dedup="cpf",
    ),
    Tabela("assistidos", fks={"id_atendido": "atendidos"}, dedup_fk="id_atendido"),
    Tabela(
        "assistidos_pessoa_juridica",
        fks={"id_assistido": "assistidos"},
        dedup_fk="id_assistido",
        opcional=True,
    ),
    Tabela("orientacao_juridica", fks={"id_usuario": "usuarios"}, unidade=True),
    Tabela(
        "atendido_xOrientacaoJuridica",
        fks={
            "id_orientacaoJuridica": "orientacao_juridica",
            "id_atendido": "atendidos",
        },
    ),
    Tabela(
        "assistencias_judiciarias",
        fks={"endereco_id": "enderecos"},
        unidade=True,
        unicas=("email",),
    ),
    Tabela(
        "assistenciasJudiciarias_xOrientacao_juridica",
        fks={
            "id_orientacaoJuridica": "orientacao_juridica",
            "id_assistenciaJudiciaria": "assistencias_judiciarias",
        },
    ),
    Tabela(
        "casos",
        fks={
            "id_usuario_responsavel": "usuarios",
            "id_orientador": "usuarios",
            "id_estagiario": "usuarios",
            "id_colaborador": "usuarios",
            "id_criado_por": "usuarios",
            "id_modificado_por": "usuarios",
        },
        unidade=True,
    ),
    Tabela(
        "casos_atendidos",
        fks={"id_caso": "casos", "id_atendido": "atendidos"},
        sem_id=True,
    ),
    Tabela(
        "processos",
        fks={"id_caso": "casos", "id_criado_por": "usuarios"},
        unicas=("numero",),
    ),
    Tabela(
        "eventos",
        fks={
            "id_caso": "casos",
            "id_criado_por": "usuarios",
            "id_usuario_responsavel": "usuarios",
        },
        unidade=True,
        arquivos=("arquivo",),
    ),
    Tabela("arquivosCaso", fks={"id_caso": "casos"}, arquivos=("link_arquivo",)),
    Tabela(
        "arquivosEvento",
        fks={"id_evento": "eventos", "id_caso": "casos"},
        arquivos=("link_arquivo",),
        opcional=True,
    ),
    Tabela("historicos", fks={"id_usuario": "usuarios", "id_caso": "casos"}),
    Tabela(
        "lembretes",
        fks={
            "id_do_criador": "usuarios",
            "id_caso": "casos",
            "id_usuario": "usuarios",
        },
        unidade=True,
    ),
    Tabela("arquivos", fks={"id_criado_por": "usuarios"}, arquivos=("nome", "caminho")),
    Tabela("fila_atendimentos", fks={"id_atendido": "atendidos"}, unidade=True),
    Tabela("registro_entrada", fks={"id_usuario": "usuarios"}, unidade=True),
    Tabela("plantao", unidade=True),
    Tabela("dias_plantao", unidade=True),
    Tabela("dias_marcados_plantao", fks={"id_usuario": "usuarios"}, unidade=True),
    # `id_caso` e `id_referencia` não têm FK declarada; ver `_ajustar_notificacao`.
    Tabela(
        "notificacao",
        fks={"id_executor_acao": "usuarios", "id_usu_notificar": "usuarios"},
    ),
    Tabela(
        "password_reset_tokens",
        fks={"usuario_id": "usuarios"},
        unicas=("token_hash",),
    ),
)


@dataclass
class Relatorio:
    inseridos: Counter = field(default_factory=Counter)
    reaproveitados: Counter = field(default_factory=Counter)
    descartados: Counter = field(default_factory=Counter)
    ausentes: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    erros: list[str] = field(default_factory=list)
    vinculos_unidade: int = 0

    def aviso(self, texto: str) -> None:
        if texto not in self.avisos:
            self.avisos.append(texto)

    def erro(self, texto: str) -> None:
        if texto not in self.erros:
            self.erros.append(texto)


class ImportacaoAbortada(RuntimeError):
    """Erro que impede a importação de continuar."""


def _refletir(conn: Connection) -> dict[str, Table]:
    metadata = MetaData()
    metadata.reflect(bind=conn)
    return dict(metadata.tables)


def conferir_schema(
    origem: dict[str, Table], destino: dict[str, Table], rel: Relatorio
) -> None:
    """Recusa a importação se a origem tiver tabela que o plano não conhece.

    Uma tabela nova na origem, importada pela metade ou esquecida, é justamente
    o erro que ninguém percebe até o dado sumir. Antes de escrever qualquer
    linha, o conjunto de tabelas tem de estar inteiramente coberto.
    """

    conhecidas = {t.nome for t in PLANO} | set(IGNORADAS)
    sobrando = sorted(set(origem) - conhecidas)
    if sobrando:
        rel.erro(
            "tabelas na origem que o plano de importação não cobre: "
            + ", ".join(sobrando)
        )

    for spec in PLANO:
        if spec.nome not in origem or spec.nome not in destino:
            if spec.opcional:
                rel.ausentes.append(spec.nome)
            else:
                onde = "origem" if spec.nome not in origem else "destino"
                rel.erro(f"tabela {spec.nome} não existe no banco de {onde}")
            continue

        colunas_origem = set(origem[spec.nome].columns.keys())
        colunas_destino = set(destino[spec.nome].columns.keys())
        for coluna in sorted(colunas_origem - colunas_destino):
            rel.aviso(
                f"{spec.nome}.{coluna} existe na origem e não no destino; será ignorada"
            )
        for coluna in sorted(colunas_destino - colunas_origem):
            col = destino[spec.nome].columns[coluna]
            if coluna == "unidade_id" and spec.unidade:
                continue
            if not col.nullable and col.default is None and not col.autoincrement:
                rel.erro(
                    f"{spec.nome}.{coluna} é NOT NULL no destino e não existe na origem"
                )
            else:
                rel.aviso(
                    f"{spec.nome}.{coluna} existe no destino e não na origem; ficará no default"
                )


def resolver_unidade(conn: Connection, destino: dict[str, Table], sigla: str) -> int:
    unidades = destino.get("unidades")
    if unidades is None:
        raise ImportacaoAbortada(
            "o banco de destino não tem a tabela `unidades`: rode a migration da Fase A antes"
        )
    linha = conn.execute(
        select(unidades.c.id).where(unidades.c.sigla == sigla)
    ).first()
    if linha is None:
        raise ImportacaoAbortada(
            f"nenhuma unidade com sigla {sigla!r} no destino"
        )
    return int(linha[0])


def _valores_unicos(conn: Connection, tabela: Table, coluna: str) -> set[Any]:
    col = tabela.columns[coluna]
    return {
        linha[0]
        for linha in conn.execute(select(col).where(col.isnot(None)))
    }


def conferir_colisoes(
    conn_origem: Connection,
    conn_destino: Connection,
    origem: dict[str, Table],
    destino: dict[str, Table],
    rel: Relatorio,
    *,
    reusar_assistencia_por_email: bool,
    zerar_numero_processo_colidido: bool,
) -> None:
    """Procura colisão de coluna UNIQUE entre as duas bases antes de inserir.

    Colisão em UNIQUE não deduplicada quebra a importação no meio; melhor
    listar todas de uma vez do que descobrir uma por execução.
    """

    for spec in PLANO:
        if spec.nome not in origem or spec.nome not in destino:
            continue
        for coluna in spec.unicas:
            if coluna not in origem[spec.nome].columns:
                continue
            colididos = _valores_unicos(
                conn_origem, origem[spec.nome], coluna
            ) & _valores_unicos(conn_destino, destino[spec.nome], coluna)
            if not colididos:
                continue
            amostra = ", ".join(str(v) for v in sorted(colididos, key=str)[:5])
            texto = (
                f"{len(colididos)} valor(es) de {spec.nome}.{coluna} existem nas duas "
                f"bases (ex.: {amostra})"
            )
            tratado = (
                spec.nome == "assistencias_judiciarias" and reusar_assistencia_por_email
            ) or (spec.nome == "processos" and zerar_numero_processo_colidido)
            if tratado:
                rel.aviso(texto + " — tratados pela opção escolhida")
            else:
                rel.erro(
                    texto
                    + "; escolha o tratamento (--reusar-assistencia-por-email, "
                    "--zerar-numero-processo-colidido) ou limpe a origem"
                )


def _prefixar(valor: Any, prefixo: str) -> Any:
    """Prefixa o nome do arquivo preservando o diretório, se houver."""

    if not isinstance(valor, str) or not valor.strip():
        return valor
    caminho, sep, nome = valor.rpartition("/")
    if nome.startswith(prefixo):
        return valor
    return f"{caminho}{sep}{prefixo}{nome}"


def _ajustar_notificacao(
    valores: dict[str, Any], mapa: dict[str, dict[Any, Any]], rel: Relatorio
) -> None:
    """Remapeia `id_caso` e `id_referencia`, que não têm FK declarada.

    `id_referencia` só é remapeável quando `tipo` diz de que entidade ele é.
    Registros herdados da 2.0 têm `tipo` nulo: aí o id aponta para coisa
    nenhuma no banco novo e é zerado, em vez de virar referência a outro
    registro pelo id coincidente.
    """

    if valores.get("id_caso") is not None:
        valores["id_caso"] = mapa["casos"].get(valores["id_caso"])

    referencia = valores.get("id_referencia")
    if referencia is None:
        return
    tabela = {"evento": "eventos", "lembrete": "lembretes"}.get(valores.get("tipo") or "")
    if tabela is None:
        valores["id_referencia"] = None
        rel.aviso(
            "notificacao.id_referencia zerada em registros sem `tipo` (herdados da 2.0)"
        )
    else:
        valores["id_referencia"] = mapa[tabela].get(referencia)


def importar_tabela(
    spec: Tabela,
    conn_origem: Connection,
    conn_destino: Connection,
    origem: dict[str, Table],
    destino: dict[str, Table],
    mapa: dict[str, dict[Any, Any]],
    novos: dict[str, set[Any]],
    rel: Relatorio,
    *,
    unidade_id: int,
    prefixo: str,
    dedup: dict[str, str],
    numeros_colididos: set[Any],
) -> None:
    tab_origem = origem[spec.nome]
    tab_destino = destino[spec.nome]
    colunas_destino = tab_destino.columns
    mapa.setdefault(spec.nome, {})
    novos.setdefault(spec.nome, set())

    pk = None if spec.sem_id else "id"
    coluna_dedup = dedup.get(spec.nome)
    indice_dedup: dict[Any, Any] = {}
    if coluna_dedup:
        indice_dedup = {
            linha[0]: linha[1]
            for linha in conn_destino.execute(
                select(colunas_destino[coluna_dedup], colunas_destino[pk or "id"])
            )
        }

    # Filha cuja existência no destino é decidida pelo pai já deduplicado:
    # o atendido reaproveitado já tem o seu assistido, e um segundo violaria
    # a relação um-para-um.
    indice_por_fk: dict[Any, Any] = {}
    if spec.dedup_fk:
        indice_por_fk = {
            linha[0]: linha[1]
            for linha in conn_destino.execute(
                select(colunas_destino[spec.dedup_fk], colunas_destino["id"])
            )
            if linha[0] is not None
        }

    ordem = [tab_origem.columns[pk]] if pk and pk in tab_origem.columns else []
    linhas = conn_origem.execute(select(tab_origem).order_by(*ordem))

    for linha in linhas:
        dados = dict(linha._mapping)
        id_antigo = dados.get(pk) if pk else None

        if coluna_dedup and dados.get(coluna_dedup) in indice_dedup:
            mapa[spec.nome][id_antigo] = indice_dedup[dados[coluna_dedup]]
            rel.reaproveitados[spec.nome] += 1
            continue

        valores: dict[str, Any] = {}
        descartar = False
        for coluna, valor in dados.items():
            if coluna == pk or coluna not in colunas_destino:
                continue
            if coluna in spec.fks and valor is not None:
                alvo = spec.fks[coluna]
                novo = mapa.get(alvo, {}).get(valor)
                if novo is None:
                    if colunas_destino[coluna].nullable:
                        rel.aviso(
                            f"{spec.nome}.{coluna} apontava para {alvo} #{valor}, "
                            "que não veio na importação; gravado como nulo"
                        )
                        valor = None
                    else:
                        rel.aviso(
                            f"{spec.nome} #{id_antigo} descartado: {coluna} exige "
                            f"{alvo} #{valor}, que não veio na importação"
                        )
                        descartar = True
                        break
                else:
                    valor = novo
            if coluna in spec.arquivos:
                valor = _prefixar(valor, prefixo)
            if spec.nome == "processos" and coluna == "numero" and valor in numeros_colididos:
                rel.aviso(f"processos.numero {valor} zerado por colidir com o destino")
                valor = None
            valores[coluna] = valor

        if descartar:
            rel.descartados[spec.nome] += 1
            continue

        if spec.dedup_fk:
            existente = indice_por_fk.get(valores.get(spec.dedup_fk))
            if existente is not None:
                mapa[spec.nome][id_antigo] = existente
                rel.reaproveitados[spec.nome] += 1
                continue

        if spec.unidade:
            valores["unidade_id"] = unidade_id
        if spec.nome == "notificacao":
            _ajustar_notificacao(valores, mapa, rel)

        resultado = conn_destino.execute(tab_destino.insert().values(**valores))
        rel.inseridos[spec.nome] += 1
        if pk and id_antigo is not None:
            mapa[spec.nome][id_antigo] = resultado.inserted_primary_key[0]
            novos[spec.nome].add(id_antigo)


def ajustar_autoria_usuarios(
    conn_origem: Connection,
    conn_destino: Connection,
    origem: dict[str, Table],
    destino: dict[str, Table],
    mapa: dict[str, dict[Any, Any]],
    novos: dict[str, set[Any]],
    rel: Relatorio,
) -> None:
    """Remapeia `usuarios.criadopor` e `modificadopor`, que são id de usuário.

    As duas colunas não têm FK declarada, então não entram no remapeamento
    normal — e são autorreferência: o mapa de `usuarios` só fica completo
    depois que a tabela inteira foi inserida. Daí a passada de UPDATE no fim.
    Quem criou o usuário pode não ter vindo na importação (conta apagada na
    origem); nesse caso o valor antigo fica como está, porque a coluna é NOT
    NULL e apontar para um usuário de Belo Horizonte seria pior que um id
    velho sem dono.
    """

    tab_origem = origem["usuarios"]
    tab_destino = destino["usuarios"]
    orfaos = 0
    for id_antigo in sorted(novos.get("usuarios", set())):
        linha = conn_origem.execute(
            select(tab_origem.c.criadopor, tab_origem.c.modificadopor).where(
                tab_origem.c.id == id_antigo
            )
        ).first()
        if linha is None:
            continue
        valores: dict[str, Any] = {}
        for coluna, antigo in zip(("criadopor", "modificadopor"), linha):
            if antigo is None:
                continue
            novo = mapa["usuarios"].get(antigo)
            if novo is None:
                orfaos += 1
            elif novo != antigo:
                valores[coluna] = novo
        if valores:
            conn_destino.execute(
                tab_destino.update()
                .where(tab_destino.c.id == mapa["usuarios"][id_antigo])
                .values(**valores)
            )
    if orfaos:
        rel.aviso(
            f"{orfaos} referência(s) de autoria em `usuarios` apontam para usuário "
            "que não veio na importação; o id antigo foi mantido"
        )


def vincular_usuarios(
    conn_destino: Connection,
    destino: dict[str, Table],
    mapa: dict[str, dict[Any, Any]],
    unidade_id: int,
    rel: Relatorio,
) -> None:
    """Dá acesso à unidade nova a todo usuário importado ou reaproveitado.

    Os 16 que já existiam em Belo Horizonte passam a ter as duas linhas em
    `usuarios_unidades`; é o que faz o seletor do cabeçalho aparecer para eles.
    """

    tabela = destino["usuarios_unidades"]
    ja_vinculados = {
        linha[0]
        for linha in conn_destino.execute(
            select(tabela.c.usuario_id).where(tabela.c.unidade_id == unidade_id)
        )
    }
    for usuario_id in sorted(set(mapa.get("usuarios", {}).values())):
        if usuario_id in ja_vinculados:
            continue
        conn_destino.execute(
            tabela.insert().values(usuario_id=usuario_id, unidade_id=unidade_id)
        )
        rel.vinculos_unidade += 1


def importar(
    url_origem: str,
    url_destino: str,
    sigla: str,
    *,
    executar: bool = False,
    prefixo: str | None = None,
    importar_arquivos_gerais: bool = True,
    reusar_assistencia_por_email: bool = False,
    zerar_numero_processo_colidido: bool = False,
) -> Relatorio:
    """Roda a importação inteira numa transação; só confirma com `executar`."""

    rel = Relatorio()
    prefixo = prefixo if prefixo is not None else f"{sigla}_"

    motor_origem = create_engine(url_origem)
    motor_destino = create_engine(url_destino)
    with motor_origem.connect() as conn_origem, motor_destino.connect() as conn_destino:
        transacao = conn_destino.begin()
        origem = _refletir(conn_origem)
        destino = _refletir(conn_destino)

        conferir_schema(origem, destino, rel)
        unidade_id = resolver_unidade(conn_destino, destino, sigla)
        conferir_colisoes(
            conn_origem,
            conn_destino,
            origem,
            destino,
            rel,
            reusar_assistencia_por_email=reusar_assistencia_por_email,
            zerar_numero_processo_colidido=zerar_numero_processo_colidido,
        )
        if rel.erros:
            raise ImportacaoAbortada("; ".join(rel.erros))

        dedup = {spec.nome: spec.dedup for spec in PLANO if spec.dedup}
        if reusar_assistencia_por_email:
            dedup["assistencias_judiciarias"] = "email"

        numeros_colididos: set[Any] = set()
        if zerar_numero_processo_colidido and "processos" in origem:
            numeros_colididos = _valores_unicos(
                conn_origem, origem["processos"], "numero"
            ) & _valores_unicos(conn_destino, destino["processos"], "numero")

        mapa: dict[str, dict[Any, Any]] = {}
        novos: dict[str, set[Any]] = {}
        for spec in PLANO:
            if spec.nome in rel.ausentes:
                continue
            if spec.nome == "arquivos" and not importar_arquivos_gerais:
                rel.aviso("biblioteca de arquivos gerais da origem não foi importada")
                continue
            importar_tabela(
                spec,
                conn_origem,
                conn_destino,
                origem,
                destino,
                mapa,
                novos,
                rel,
                unidade_id=unidade_id,
                prefixo=prefixo,
                dedup=dedup,
                numeros_colididos=numeros_colididos,
            )

        ajustar_autoria_usuarios(
            conn_origem, conn_destino, origem, destino, mapa, novos, rel
        )
        vincular_usuarios(conn_destino, destino, mapa, unidade_id, rel)

        if executar:
            transacao.commit()
        else:
            # Ensaio: a transação inteira roda e é desfeita, então as contagens
            # do relatório são as da importação de verdade.
            transacao.rollback()

    return rel


def formatar(rel: Relatorio, *, executar: bool) -> str:
    linhas = [
        "IMPORTAÇÃO CONFIRMADA" if executar else "ENSAIO (nada foi gravado; use --executar)",
        "",
        f"{'tabela':<45} {'inseridos':>10} {'reaproveit.':>12} {'descartados':>12}",
    ]
    for spec in PLANO:
        if spec.nome in rel.ausentes:
            continue
        linhas.append(
            f"{spec.nome:<45} {rel.inseridos[spec.nome]:>10} "
            f"{rel.reaproveitados[spec.nome]:>12} {rel.descartados[spec.nome]:>12}"
        )
    linhas += [
        "",
        f"vínculos criados em usuarios_unidades: {rel.vinculos_unidade}",
        f"total inserido: {sum(rel.inseridos.values())}",
    ]
    if rel.ausentes:
        linhas.append("tabelas opcionais ausentes do schema: " + ", ".join(rel.ausentes))
    if rel.avisos:
        linhas += ["", "AVISOS:"] + [f"  - {a}" for a in rel.avisos]
    return "\n".join(linhas)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Importa o banco de uma unidade para o banco final da 3.0 (Fase B)."
    )
    parser.add_argument("--origem", required=True, help="URL SQLAlchemy do banco de origem")
    parser.add_argument("--destino", required=True, help="URL SQLAlchemy do banco final")
    parser.add_argument("--sigla", required=True, help="sigla da unidade no destino, ex.: NL")
    parser.add_argument(
        "--executar",
        action="store_true",
        help="confirma a transação; sem isso o script só ensaia e dá rollback",
    )
    parser.add_argument(
        "--prefixo-arquivo",
        default=None,
        help="prefixo dos nomes de arquivo físico (padrão: a sigla e um sublinhado)",
    )
    parser.add_argument(
        "--sem-arquivos-gerais",
        action="store_true",
        help="não importa a tabela `arquivos` (biblioteca compartilhada)",
    )
    parser.add_argument(
        "--reusar-assistencia-por-email",
        action="store_true",
        help="assistência judiciária com e-mail já existente no destino é reaproveitada",
    )
    parser.add_argument(
        "--zerar-numero-processo-colidido",
        action="store_true",
        help="grava NULL em processos.numero quando o número já existe no destino",
    )
    args = parser.parse_args(argv)

    try:
        rel = importar(
            args.origem,
            args.destino,
            args.sigla,
            executar=args.executar,
            prefixo=args.prefixo_arquivo,
            importar_arquivos_gerais=not args.sem_arquivos_gerais,
            reusar_assistencia_por_email=args.reusar_assistencia_por_email,
            zerar_numero_processo_colidido=args.zerar_numero_processo_colidido,
        )
    except ImportacaoAbortada as erro:
        print("importação abortada:", erro, file=sys.stderr)
        return 1

    print(formatar(rel, executar=args.executar))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
