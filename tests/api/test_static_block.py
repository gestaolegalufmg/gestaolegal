"""Bloqueio do caminho estático dos anexos (#190).

Os anexos passaram para o volume privado, mas `app.static_folder` continua
servido em `/static/<path>` sem autenticação. Estes testes plantam arquivos DE
FATO dentro das três pastas e conferem que a API responde 404 — e que o
restante de `static/` segue público.
"""

from collections.abc import Generator
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient

CATEGORIAS = ("casos", "eventos", "arquivos")


@pytest.fixture
def anexos_plantados(app: Flask) -> Generator[dict[str, Path], None, None]:
    """Cria um arquivo real em cada pasta bloqueada e limpa depois."""
    static = Path(app.static_folder or "")
    criados: dict[str, Path] = {}
    diretorios_criados: list[Path] = []

    for categoria in CATEGORIAS:
        pasta = static / categoria
        if not pasta.exists():
            pasta.mkdir(parents=True)
            diretorios_criados.append(pasta)
        alvo = pasta / "vazado.txt"
        alvo.write_text("segredo do atendido")
        criados[categoria] = alvo

    yield criados

    for alvo in criados.values():
        alvo.unlink(missing_ok=True)
    for pasta in diretorios_criados:
        if not any(pasta.iterdir()):
            pasta.rmdir()


@pytest.fixture
def asset_publico(app: Flask) -> Generator[str, None, None]:
    """Asset sintético em imgs_daj, para provar que o bloqueio não é excessivo."""
    pasta = Path(app.static_folder or "") / "imgs_daj"
    criada = not pasta.exists()
    if criada:
        pasta.mkdir(parents=True)
    alvo = pasta / "asset-sintetico-teste.txt"
    alvo.write_text("logo publica")

    yield "/static/imgs_daj/asset-sintetico-teste.txt"

    alvo.unlink(missing_ok=True)
    if criada and not any(pasta.iterdir()):
        pasta.rmdir()


@pytest.mark.parametrize("categoria", CATEGORIAS)
def test_arquivo_plantado_nao_e_servido(
    client: FlaskClient, anexos_plantados: dict[str, Path], categoria: str
):
    assert anexos_plantados[categoria].is_file()

    resposta = client.get(f"/static/{categoria}/vazado.txt")

    assert resposta.status_code == 404
    assert b"segredo do atendido" not in resposta.data


@pytest.mark.parametrize("categoria", CATEGORIAS)
def test_head_tambem_bloqueado(
    client: FlaskClient, anexos_plantados: dict[str, Path], categoria: str
):
    assert client.head(f"/static/{categoria}/vazado.txt").status_code == 404


@pytest.mark.parametrize("categoria", CATEGORIAS)
def test_diretorio_da_categoria_bloqueado(client: FlaskClient, categoria: str):
    assert client.get(f"/static/{categoria}").status_code == 404
    assert client.get(f"/static/{categoria}/").status_code == 404


@pytest.mark.parametrize(
    "caminho",
    [
        "//static//casos//vazado.txt",
        "/static//eventos/vazado.txt",
        "/static/./arquivos/vazado.txt",
        "/static/imgs_daj/../casos/vazado.txt",
        "/static/imgs_daj/%2e%2e/casos/vazado.txt",
        "/static/%2e%2e/static/casos/vazado.txt",
        "/static/casos/../casos/vazado.txt",
        "/static/casos/subpasta/vazado.txt",
    ],
)
def test_formas_normalizadas_bloqueadas(
    client: FlaskClient, anexos_plantados: dict[str, Path], caminho: str
):
    resposta = client.get(caminho)

    assert resposta.status_code == 404, caminho
    assert b"segredo do atendido" not in resposta.data


def test_asset_publico_continua_acessivel(client: FlaskClient, asset_publico: str):
    resposta = client.get(asset_publico)

    assert resposta.status_code == 200
    assert resposta.data == b"logo publica"
