"""Fase de inventário do migrador de anexos legados (#190).

O script vive em `scripts/`, que não é pacote instalado: ele é carregado por
caminho, como faria quem o executa pela linha de comando.
"""

import importlib.util
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

import pytest
from sqlalchemy import create_engine, insert, select

from gestaolegal.database.tables import arquivos, arquivos_caso, casos, eventos, metadata

_CAMINHO_SCRIPT = (
    Path(__file__).resolve().parents[2] / "scripts" / "migrar_arquivos_privados.py"
)
_spec = importlib.util.spec_from_file_location("migrar_arquivos_privados", _CAMINHO_SCRIPT)
assert _spec and _spec.loader
migrador = importlib.util.module_from_spec(_spec)
sys.modules["migrar_arquivos_privados"] = migrador
_spec.loader.exec_module(migrador)


# --------------------------------------------------------------------------
# Cenário: um banco SQLite em arquivo e os mounts de leitura das três origens.
# --------------------------------------------------------------------------


@pytest.fixture
def origens(tmp_path: Path) -> dict[str, Path]:
    """Mounts de leitura das três categorias, vazios."""
    mounts = {}
    for categoria in ("casos", "eventos", "arquivos"):
        destino = tmp_path / "mount" / categoria
        destino.mkdir(parents=True)
        mounts[categoria] = destino
    return mounts


PREFIXOS = {
    "casos": "/code/gestaolegal/static/casos",
    "eventos": "/code/gestaolegal/static/eventos",
    "arquivos": "/code/gestaolegal/static/arquivos",
}


@pytest.fixture
def mapa(origens: dict[str, Path]) -> dict[str, str]:
    return migrador.carregar_mapa_origens(
        [f"{PREFIXOS[categoria]}={origens[categoria]}" for categoria in PREFIXOS]
    )


@pytest.fixture
def banco(tmp_path: Path):
    """Engine SQLite em arquivo, com o esquema do projeto e um caso."""
    url = f"sqlite:///{tmp_path / 'inventario.db'}"
    engine = create_engine(url)
    metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(
            insert(casos).values(
                id=1,
                id_usuario_responsavel=1,
                area_direito="civel",
                data_criacao=datetime(2026, 1, 1),
                id_criado_por=1,
                situacao_deferimento="ativo",
                status=True,
                unidade_id=1,
            )
        )
    yield engine, url
    engine.dispose()


def _plantar(diretorio: Path, nome: str, conteudo: bytes = b"conteudo") -> str:
    caminho = diretorio / nome
    caminho.write_bytes(conteudo)
    return str(caminho)


def _anexo_caso(conn, registro_id: int, referencia: str | None, id_caso: int | None = 1) -> None:
    conn.execute(
        insert(arquivos_caso).values(id=registro_id, link_arquivo=referencia, id_caso=id_caso)
    )


def _anexo_evento(
    conn, registro_id: int, referencia: str | None, status: bool = True, id_caso: int = 1
) -> None:
    conn.execute(
        insert(eventos).values(
            id=registro_id,
            id_caso=id_caso,
            tipo="reuniao",
            arquivo=referencia,
            data_evento=date(2026, 1, 1),
            data_criacao=datetime(2026, 1, 1),
            id_criado_por=1,
            status=status,
            unidade_id=1,
        )
    )


def _arquivo_geral(conn, registro_id: int, caminho: str | None, nome: str) -> None:
    conn.execute(
        insert(arquivos).values(
            id=registro_id, titulo=f"t{registro_id}", nome=nome, caminho=caminho
        )
    )


def _por_registro(itens, tabela: str, registro_id: int):
    return next(i for i in itens if i.tabela == tabela and i.registro_id == registro_id)


# --------------------------------------------------------------------------
# Inventário
# --------------------------------------------------------------------------


def test_caminho_absoluto_legado_vira_item_migravel(banco, origens, mapa):
    engine, _ = banco
    _plantar(origens["casos"], "procuracao.pdf", b"pdf de teste")
    with engine.begin() as conn:
        _anexo_caso(conn, 1, f"{PREFIXOS['casos']}/procuracao.pdf")

    with engine.connect() as conn:
        itens = migrador.inventariar(conn, mapa)

    item = _por_registro(itens, "arquivosCaso", 1)
    assert item.classificacao == migrador.MIGRAVEL
    assert item.origem == str(origens["casos"] / "procuracao.pdf")
    assert item.referencia_anterior == f"{PREFIXOS['casos']}/procuracao.pdf"
    assert item.tamanho == len(b"pdf de teste")
    assert item.sha256 == migrador.sha256_de(item.origem)
    assert item.destino and item.destino.endswith("_procuracao.pdf")
    assert not os.path.isabs(item.destino)
    assert item.categoria == "casos"


def test_evento_inativo_tambem_entra_no_inventario(banco, origens, mapa):
    engine, _ = banco
    _plantar(origens["eventos"], "ata.docx")
    with engine.begin() as conn:
        _anexo_evento(conn, 1, f"{PREFIXOS['eventos']}/ata.docx", status=False)

    with engine.connect() as conn:
        itens = migrador.inventariar(conn, mapa)

    assert _por_registro(itens, "eventos", 1).classificacao == migrador.MIGRAVEL


def test_arquivo_geral_sem_caminho_e_procurado_no_diretorio_legado(banco, origens, mapa):
    engine, _ = banco
    _plantar(origens["arquivos"], "estatuto.pdf", b"herdado da v2")
    with engine.begin() as conn:
        _arquivo_geral(conn, 1, None, "estatuto.pdf")

    with engine.connect() as conn:
        itens = migrador.inventariar(conn, mapa, arquivos_legado=str(origens["arquivos"]))

    item = _por_registro(itens, "arquivos", 1)
    assert item.classificacao == migrador.MIGRAVEL
    assert item.referencia_anterior is None
    assert item.origem == str(origens["arquivos"] / "estatuto.pdf")
    assert item.tamanho == len(b"herdado da v2")
    assert item.destino and item.destino.endswith("_estatuto.pdf")


def test_arquivo_geral_sem_caminho_e_sem_diretorio_legado_fica_externo(banco, mapa):
    engine, _ = banco
    with engine.begin() as conn:
        _arquivo_geral(conn, 1, None, "estatuto.pdf")

    with engine.connect() as conn:
        itens = migrador.inventariar(conn, mapa)

    item = _por_registro(itens, "arquivos", 1)
    assert item.classificacao == migrador.EXTERNO
    assert item.motivos


def test_nome_do_registro_nao_pode_escapar_do_diretorio_legado(banco, origens, mapa):
    engine, _ = banco
    with engine.begin() as conn:
        _arquivo_geral(conn, 1, None, "../fora.pdf")

    with engine.connect() as conn:
        itens = migrador.inventariar(conn, mapa, arquivos_legado=str(origens["arquivos"]))

    item = _por_registro(itens, "arquivos", 1)
    assert item.classificacao == migrador.EXTERNO
    assert item.origem is None


def test_nomes_iguais_em_origens_diferentes_sao_marcados(banco, origens, mapa):
    engine, _ = banco
    _plantar(origens["casos"], "contrato.pdf", b"a")
    _plantar(origens["eventos"], "contrato.pdf", b"b")
    with engine.begin() as conn:
        _anexo_caso(conn, 1, f"{PREFIXOS['casos']}/contrato.pdf")
        _anexo_evento(conn, 1, f"{PREFIXOS['eventos']}/contrato.pdf")

    with engine.connect() as conn:
        itens = migrador.inventariar(conn, mapa)

    do_caso = _por_registro(itens, "arquivosCaso", 1)
    do_evento = _por_registro(itens, "eventos", 1)
    assert do_caso.nome_repetido and do_evento.nome_repetido
    assert not do_caso.compartilhado and not do_evento.compartilhado
    # Nomes iguais, arquivos diferentes: destinos e checksums não se confundem.
    assert do_caso.destino != do_evento.destino
    assert do_caso.sha256 != do_evento.sha256


def test_referencia_compartilhada_ganha_destino_por_registro(banco, origens, mapa):
    engine, _ = banco
    compartilhado = f"{PREFIXOS['casos']}/laudo.pdf"
    _plantar(origens["casos"], "laudo.pdf", b"mesmo arquivo")
    with engine.begin() as conn:
        _anexo_caso(conn, 1, compartilhado)
        _anexo_caso(conn, 2, compartilhado)

    with engine.connect() as conn:
        itens = migrador.inventariar(conn, mapa)

    primeiro = _por_registro(itens, "arquivosCaso", 1)
    segundo = _por_registro(itens, "arquivosCaso", 2)
    assert primeiro.compartilhado and segundo.compartilhado
    assert primeiro.origem == segundo.origem
    # Destinos distintos: excluir um registro não pode apagar o anexo do outro.
    assert primeiro.destino != segundo.destino
    assert primeiro.sha256 == segundo.sha256


def test_arquivo_ausente_no_mount_e_classificado_como_ausente(banco, origens, mapa):
    engine, _ = banco
    with engine.begin() as conn:
        _anexo_caso(conn, 1, f"{PREFIXOS['casos']}/sumiu.pdf")

    with engine.connect() as conn:
        itens = migrador.inventariar(conn, mapa)

    item = _por_registro(itens, "arquivosCaso", 1)
    assert item.classificacao == migrador.AUSENTE
    assert item.origem == str(origens["casos"] / "sumiu.pdf")
    assert item.destino  # o destino já é conhecido; falta o arquivo
    assert item.sha256 is None and item.tamanho is None


def test_caminho_fora_do_mapa_e_externo(banco, mapa):
    engine, _ = banco
    with engine.begin() as conn:
        _anexo_caso(conn, 1, "/etc/passwd")
        _anexo_caso(conn, 2, f"{PREFIXOS['casos']}/../../../etc/passwd")

    with engine.connect() as conn:
        itens = migrador.inventariar(conn, mapa)

    for registro_id in (1, 2):
        item = _por_registro(itens, "arquivosCaso", registro_id)
        assert item.classificacao == migrador.EXTERNO
        assert item.origem is None


def test_referencia_ja_relativa_e_marcada_como_migrada(banco, mapa):
    engine, _ = banco
    with engine.begin() as conn:
        _anexo_caso(conn, 1, "a" * 32 + "_ja_migrado.pdf")

    with engine.connect() as conn:
        itens = migrador.inventariar(conn, mapa)

    item = _por_registro(itens, "arquivosCaso", 1)
    assert item.classificacao == migrador.JA_MIGRADO
    assert item.origem is None and item.destino is None


def test_registro_sem_anexo_e_registro_orfao(banco, origens, mapa):
    engine, _ = banco
    _plantar(origens["casos"], "orfao.pdf")
    with engine.begin() as conn:
        _anexo_caso(conn, 1, None)
        _anexo_caso(conn, 2, f"{PREFIXOS['casos']}/orfao.pdf", id_caso=None)

    with engine.connect() as conn:
        itens = migrador.inventariar(conn, mapa)

    assert _por_registro(itens, "arquivosCaso", 1).classificacao == migrador.SEM_REFERENCIA
    orfao = _por_registro(itens, "arquivosCaso", 2)
    assert orfao.orfao is True
    assert orfao.classificacao == migrador.MIGRAVEL
    assert migrador.resumir(itens)["orfaos"] == 1


def test_inventario_nao_escreve_nada(banco, origens, mapa):
    engine, _ = banco
    caminho = _plantar(origens["casos"], "intacto.pdf", b"conteudo original")
    with engine.begin() as conn:
        _anexo_caso(conn, 1, f"{PREFIXOS['casos']}/intacto.pdf")

    antes = {p: p.stat().st_mtime_ns for p in origens["casos"].iterdir()}
    with engine.connect() as conn:
        migrador.inventariar(conn, mapa)

    assert {p: p.stat().st_mtime_ns for p in origens["casos"].iterdir()} == antes
    assert Path(caminho).read_bytes() == b"conteudo original"
    with engine.connect() as conn:
        assert conn.execute(select(arquivos_caso.c.link_arquivo)).scalar() == (
            f"{PREFIXOS['casos']}/intacto.pdf"
        )


# --------------------------------------------------------------------------
# Manifesto e linha de comando
# --------------------------------------------------------------------------


def test_manifesto_dentro_do_repositorio_e_recusado():
    dentro = str(Path(__file__).resolve().parents[2] / "manifesto.json")
    with pytest.raises(migrador.ErroDeUso):
        migrador.validar_manifesto_fora_do_git(dentro)
    assert not os.path.exists(dentro)


def test_origem_mal_formada_ou_sem_mount_e_recusada(tmp_path: Path):
    with pytest.raises(migrador.ErroDeUso):
        migrador.carregar_mapa_origens(["/code/static/casos"])
    with pytest.raises(migrador.ErroDeUso):
        migrador.carregar_mapa_origens([f"relativo={tmp_path}"])
    with pytest.raises(migrador.ErroDeUso):
        migrador.carregar_mapa_origens([f"/code/static/casos={tmp_path / 'nao-existe'}"])


def test_cli_gera_manifesto_com_todos_os_campos(banco, origens, tmp_path, capsys):
    engine, url = banco
    _plantar(origens["casos"], "peticao.pdf", b"peticao inicial")
    _plantar(origens["arquivos"], "regimento.pdf", b"regimento")
    with engine.begin() as conn:
        _anexo_caso(conn, 1, f"{PREFIXOS['casos']}/peticao.pdf")
        _anexo_caso(conn, 2, f"{PREFIXOS['casos']}/sumiu.pdf")
        _arquivo_geral(conn, 1, None, "regimento.pdf")

    manifesto = tmp_path / "privado" / "manifesto.json"
    codigo = migrador.main(
        [
            "inventario",
            "--origem",
            f"{PREFIXOS['casos']}={origens['casos']}",
            "--origem",
            f"{PREFIXOS['arquivos']}={origens['arquivos']}",
            "--arquivos-legado",
            str(origens["arquivos"]),
            "--manifesto",
            str(manifesto),
            "--database-url",
            url,
        ]
    )

    assert codigo == 0
    assert manifesto.exists()
    # Manifesto é privado: nomes de arquivos de pessoas não são legíveis por outros.
    assert manifesto.stat().st_mode & 0o077 == 0
    conteudo = json.loads(manifesto.read_text(encoding="utf-8"))
    assert conteudo["resumo"]["total"] == 3
    assert conteudo["resumo"][migrador.MIGRAVEL] == 2
    assert conteudo["resumo"][migrador.AUSENTE] == 1
    for item in conteudo["itens"]:
        assert set(item) >= {
            "tabela",
            "registro_id",
            "referencia_anterior",
            "origem",
            "destino",
            "tamanho",
            "sha256",
            "classificacao",
        }
    migravel = next(
        i for i in conteudo["itens"] if i["origem"] == str(origens["casos"] / "peticao.pdf")
    )
    assert migravel["tamanho"] == len(b"peticao inicial")
    assert migravel["sha256"] == migrador.sha256_de(migravel["origem"])
    assert "manifesto em" in capsys.readouterr().out


def test_cli_recusa_manifesto_no_repositorio(banco, origens, capsys):
    _engine, url = banco
    codigo = migrador.main(
        [
            "inventario",
            "--origem",
            f"{PREFIXOS['casos']}={origens['casos']}",
            "--manifesto",
            str(Path(__file__).resolve().parents[2] / "manifesto.json"),
            "--database-url",
            url,
        ]
    )
    assert codigo == 2
    assert "repositório" in capsys.readouterr().err


def test_destino_e_deterministico_e_respeita_o_limite_do_filesystem():
    assert migrador.destino_para("eventos", 7, "ata.pdf") == migrador.destino_para(
        "eventos", 7, "ata.pdf"
    )
    assert migrador.destino_para("eventos", 7, "ata.pdf") != migrador.destino_para(
        "eventos", 8, "ata.pdf"
    )
    longo = migrador.destino_para("arquivos", 1, "n" * 400 + ".pdf")
    assert len(longo) <= migrador.NAME_MAX
    assert longo.endswith(".pdf")
    prefixo = longo.split("_", 1)[0]
    assert len(prefixo) == 32 and all(c in "0123456789abcdef" for c in prefixo)
