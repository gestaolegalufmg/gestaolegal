"""Busca global: o filtro por unidade vem dos services já ajustados na F3.

Este arquivo existe para provar isso — `global_search` não tem cláusula própria,
então uma regressão em qualquer um dos services vazaria aqui sem que os testes
específicos de atendido, caso ou orientação percebessem.
"""

from typing import Any

import pytest
from flask.testing import FlaskClient

from tests.api.conftest import clean_tables, get_success_data

TABELAS = (
    "casos_atendidos",
    "casos",
    "atendido_xOrientacaoJuridica",
    "orientacao_juridica",
    "atendidos",
)


@pytest.fixture(autouse=True)
def _reset(app):
    with app.app_context():
        clean_tables(*TABELAS)
    yield


def _buscar(client: FlaskClient, headers: dict[str, str], termo: str) -> dict[str, Any]:
    response = client.get(f"/api/search/?q={termo}", headers=headers)
    assert response.status_code == 200, response.get_json()
    return get_success_data(response)["results"]


def _criar_atendido(
    client: FlaskClient, headers: dict[str, str], base: dict[str, Any], nome: str, email: str
) -> int:
    dados = {**base, "nome": nome, "email": email}
    response = client.post("/api/atendido/", json=dados, headers=headers)
    assert response.status_code == 201, response.get_json()
    return get_success_data(response)["id"]


def test_busca_global_nao_retorna_atendido_de_outra_unidade(
    client: FlaskClient,
    auth_headers: dict[str, str],
    auth_headers_nl: dict[str, str],
    sample_atendido_data: dict[str, Any],
) -> None:
    _criar_atendido(client, auth_headers, sample_atendido_data, "Zenaide Buscavel", "zen.bh@gl.com")
    _criar_atendido(
        client, auth_headers_nl, sample_atendido_data, "Zenaide Buscanova", "zen.nl@gl.com"
    )

    bh = _buscar(client, auth_headers, "Zenaide")
    assert [item["nome"] for item in bh["atendidos"]["items"]] == ["Zenaide Buscavel"]
    assert bh["atendidos"]["total"] == 1

    nl = _buscar(client, auth_headers_nl, "Zenaide")
    assert [item["nome"] for item in nl["atendidos"]["items"]] == ["Zenaide Buscanova"]
    assert nl["atendidos"]["total"] == 1


def test_busca_global_nao_retorna_caso_de_outra_unidade(
    client: FlaskClient,
    auth_headers: dict[str, str],
    auth_headers_nl: dict[str, str],
    sample_atendido_data: dict[str, Any],
    sample_caso_data: dict[str, Any],
) -> None:
    atendido_bh = _criar_atendido(
        client, auth_headers, sample_atendido_data, "Quirino Casobusca", "qui.bh@gl.com"
    )
    response = client.post(
        "/api/caso/",
        json={**sample_caso_data, "ids_clientes": [atendido_bh]},
        headers=auth_headers,
    )
    assert response.status_code == 201, response.get_json()

    nl = _buscar(client, auth_headers_nl, "Quirino")
    assert nl["casos"]["total"] == 0
    assert nl["atendidos"]["total"] == 0

    bh = _buscar(client, auth_headers, "Quirino")
    assert bh["atendidos"]["total"] == 1
    assert bh["casos"]["total"] == 1


def test_busca_global_nao_retorna_orientacao_de_outra_unidade(
    client: FlaskClient,
    auth_headers: dict[str, str],
    auth_headers_nl: dict[str, str],
    sample_orientacao_data: dict[str, Any],
) -> None:
    response = client.post(
        "/api/orientacao_juridica/",
        json={**sample_orientacao_data, "descricao": "Orientacao sobre despejo em Xanxere"},
        headers=auth_headers,
    )
    assert response.status_code == 201, response.get_json()

    nl = _buscar(client, auth_headers_nl, "Xanxere")
    assert nl["orientacoes_juridicas"]["total"] == 0

    bh = _buscar(client, auth_headers, "Xanxere")
    assert bh["orientacoes_juridicas"]["total"] == 1


def test_busca_curta_devolve_estrutura_vazia(
    client: FlaskClient, auth_headers: dict[str, str]
) -> None:
    resultados = _buscar(client, auth_headers, "a")
    assert resultados == {
        "atendidos": [],
        "casos": [],
        "orientacoes_juridicas": [],
        "usuarios": [],
    }
