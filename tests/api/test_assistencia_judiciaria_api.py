from typing import Any

import pytest
from flask.testing import FlaskClient

from tests.api.conftest import clean_tables, get_success_data


@pytest.fixture
def sample_assistencia_data() -> dict[str, Any]:
    return {
        "nome": "Defensoria Pública de Teste",
        "regiao": "centro",
        "areas_atendidas": ["civel"],
        "telefone": "(31) 3333-3333",
        "email": "defensoria.teste@example.com",
        "logradouro": "Rua dos Testes",
        "numero": "100",
        "bairro": "Centro",
        "cep": "30000-000",
        "cidade": "Belo Horizonte",
        "estado": "MG",
    }


@pytest.fixture
def sample_orientacao_data() -> dict[str, Any]:
    return {
        "area_direito": "civel",
        "descricao": "Orientação jurídica usada para testar o encaminhamento",
        "atendidos_ids": [],
    }


def criar_assistencia(
    client: FlaskClient,
    headers: dict[str, str],
    data: dict[str, Any],
    **overrides: Any,
) -> int:
    response = client.post(
        "/api/assistencia_judiciaria/", json={**data, **overrides}, headers=headers
    )
    assert response.status_code == 201, response.get_json()
    return get_success_data(response)["id"]


def test_assistencia_listagem_isolada_por_unidade(
    client: FlaskClient,
    auth_headers: dict[str, str],
    auth_headers_nl: dict[str, str],
    sample_assistencia_data: dict[str, Any],
) -> None:
    """Cada unidade só enxerga as assistências judiciárias que cadastrou."""
    clean_tables(
        "assistenciasJudiciarias_xOrientacao_juridica", "assistencias_judiciarias"
    )

    id_bh = criar_assistencia(client, auth_headers, sample_assistencia_data)
    id_nl = criar_assistencia(
        client,
        auth_headers_nl,
        sample_assistencia_data,
        nome="Núcleo de Nova Lima",
        email="nucleo.nl@example.com",
    )

    data_bh = get_success_data(
        client.get("/api/assistencia_judiciaria", headers=auth_headers)
    )
    assert [item["id"] for item in data_bh["items"]] == [id_bh]
    assert data_bh["total"] == 1

    data_nl = get_success_data(
        client.get("/api/assistencia_judiciaria", headers=auth_headers_nl)
    )
    assert [item["id"] for item in data_nl["items"]] == [id_nl]
    assert data_nl["total"] == 1


def test_assistencia_de_outra_unidade_responde_404(
    client: FlaskClient,
    auth_headers: dict[str, str],
    auth_headers_nl: dict[str, str],
    sample_assistencia_data: dict[str, Any],
) -> None:
    """Assistência de outra unidade não é lida, alterada nem inativada."""
    clean_tables(
        "assistenciasJudiciarias_xOrientacao_juridica", "assistencias_judiciarias"
    )

    id_bh = criar_assistencia(client, auth_headers, sample_assistencia_data)

    assert (
        client.get(
            f"/api/assistencia_judiciaria/{id_bh}", headers=auth_headers
        ).status_code
        == 200
    )
    assert (
        client.get(
            f"/api/assistencia_judiciaria/{id_bh}", headers=auth_headers_nl
        ).status_code
        == 404
    )
    assert (
        client.put(
            f"/api/assistencia_judiciaria/{id_bh}",
            json={"regiao": "sul"},
            headers=auth_headers_nl,
        ).status_code
        == 404
    )
    assert (
        client.delete(
            f"/api/assistencia_judiciaria/{id_bh}", headers=auth_headers_nl
        ).status_code
        == 404
    )


def test_assistencia_create_grava_unidade_ativa(
    client: FlaskClient,
    auth_headers: dict[str, str],
    auth_headers_nl: dict[str, str],
    sample_assistencia_data: dict[str, Any],
) -> None:
    """Criada com a unidade ativa: aparece na listagem de NL e não na de BH."""
    clean_tables(
        "assistenciasJudiciarias_xOrientacao_juridica", "assistencias_judiciarias"
    )

    id_nl = criar_assistencia(client, auth_headers_nl, sample_assistencia_data)

    data_nl = get_success_data(
        client.get("/api/assistencia_judiciaria", headers=auth_headers_nl)
    )
    assert [item["id"] for item in data_nl["items"]] == [id_nl]

    data_bh = get_success_data(
        client.get("/api/assistencia_judiciaria", headers=auth_headers)
    )
    assert data_bh["items"] == []


def test_encaminhar_orientacao_de_outra_unidade_responde_404(
    client: FlaskClient,
    auth_headers: dict[str, str],
    auth_headers_nl: dict[str, str],
    sample_assistencia_data: dict[str, Any],
    sample_orientacao_data: dict[str, Any],
) -> None:
    """O encaminhamento exige que assistência e orientação sejam da unidade ativa."""
    clean_tables(
        "assistenciasJudiciarias_xOrientacao_juridica", "assistencias_judiciarias"
    )

    id_assistencia_nl = criar_assistencia(
        client, auth_headers_nl, sample_assistencia_data
    )
    id_orientacao_bh = get_success_data(
        client.post(
            "/api/orientacao_juridica/",
            json=sample_orientacao_data,
            headers=auth_headers,
        )
    )["id"]

    response = client.post(
        f"/api/assistencia_judiciaria/{id_assistencia_nl}/encaminhar",
        json={"id_orientacao": id_orientacao_bh},
        headers=auth_headers_nl,
    )
    assert response.status_code == 404


def test_assistencias_por_orientacao_respeitam_a_unidade(
    client: FlaskClient,
    auth_headers: dict[str, str],
    auth_headers_nl: dict[str, str],
    sample_assistencia_data: dict[str, Any],
    sample_orientacao_data: dict[str, Any],
) -> None:
    """A tabela de ligação não tem unidade: o filtro vem da assistência."""
    clean_tables(
        "assistenciasJudiciarias_xOrientacao_juridica", "assistencias_judiciarias"
    )

    id_orientacao_bh = get_success_data(
        client.post(
            "/api/orientacao_juridica/",
            json=sample_orientacao_data,
            headers=auth_headers,
        )
    )["id"]
    id_assistencia_bh = criar_assistencia(
        client, auth_headers, sample_assistencia_data
    )
    encaminhar = client.post(
        f"/api/assistencia_judiciaria/{id_assistencia_bh}/encaminhar",
        json={"id_orientacao": id_orientacao_bh},
        headers=auth_headers,
    )
    assert encaminhar.status_code == 200

    vistas_bh = get_success_data(
        client.get(
            f"/api/assistencia_judiciaria?orientacao_id={id_orientacao_bh}",
            headers=auth_headers,
        )
    )
    assert [item["id"] for item in vistas_bh] == [id_assistencia_bh]

    vistas_nl = get_success_data(
        client.get(
            f"/api/assistencia_judiciaria?orientacao_id={id_orientacao_bh}",
            headers=auth_headers_nl,
        )
    )
    assert vistas_nl == []
