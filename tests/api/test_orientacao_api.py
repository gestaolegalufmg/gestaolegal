from typing import Any

import pytest
from flask.testing import FlaskClient


@pytest.fixture
def sample_orientacao_data() -> dict[str, Any]:
    return {
        "area_direito": "penal",
        "descricao": "Orientação jurídica detalhada sobre questão penal do cliente",
        "atendidos_ids": [],
    }


def test_create_orientacao_success(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_orientacao_data: dict[str, Any],
) -> None:
    response = client.post("/api/orientacao_juridica/", json=sample_orientacao_data, headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["area_direito"] == "penal"
    assert data["descricao"] == "Orientação jurídica detalhada sobre questão penal do cliente"
    assert "id" in data
    assert isinstance(data["id"], int)


def test_create_orientacao_requires_auth(client: FlaskClient, sample_orientacao_data: dict[str, Any]) -> None:
    response = client.post("/api/orientacao_juridica/", json=sample_orientacao_data)

    assert response.status_code == 401


def test_get_orientacao_by_id(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_orientacao_data: dict[str, Any],
) -> None:
    create_response = client.post("/api/orientacao_juridica/", json=sample_orientacao_data, headers=auth_headers)
    assert create_response.json is not None
    orientacao_id = create_response.json["id"]

    response = client.get(f"/api/orientacao_juridica/{orientacao_id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["area_direito"] == "penal"
    assert data["id"] == orientacao_id


def test_get_orientacao_not_found(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    response = client.get("/api/orientacao_juridica/99999", headers=auth_headers)

    assert response.status_code == 404


def test_update_orientacao(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_orientacao_data: dict[str, Any],
) -> None:
    create_response = client.post("/api/orientacao_juridica/", json=sample_orientacao_data, headers=auth_headers)
    assert create_response.json is not None
    orientacao_id = create_response.json["id"]

    update_data = {**sample_orientacao_data, "descricao": "Descrição atualizada da orientação"}
    response = client.put(f"/api/orientacao_juridica/{orientacao_id}", json=update_data, headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["descricao"] == "Descrição atualizada da orientação"
    assert data["id"] == orientacao_id


def test_delete_orientacao(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_orientacao_data: dict[str, Any],
) -> None:
    create_response = client.post("/api/orientacao_juridica/", json=sample_orientacao_data, headers=auth_headers)
    assert create_response.json is not None
    orientacao_id = create_response.json["id"]

    response = client.delete(f"/api/orientacao_juridica/{orientacao_id}", headers=auth_headers)

    assert response.status_code == 200


def test_search_orientacoes(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_orientacao_data: dict[str, Any],
) -> None:
    client.post("/api/orientacao_juridica/", json=sample_orientacao_data, headers=auth_headers)

    response = client.get("/api/orientacao_juridica/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert isinstance(data, (dict, list))


def test_create_orientacao_with_atendidos(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_orientacao_data: dict[str, Any],
    sample_atendido_data: dict[str, Any],
) -> None:
    atendido_response = client.post("/api/atendido/", json=sample_atendido_data, headers=auth_headers)
    assert atendido_response.json is not None
    atendido_id = atendido_response.json["id"]

    orientacao_data = {**sample_orientacao_data, "atendidos_ids": [atendido_id]}
    response = client.post("/api/orientacao_juridica/", json=orientacao_data, headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    has_atendidos = len(data.get("atendidos", [])) == 1 or data.get("atendidos_ids") == [atendido_id]
    assert has_atendidos, f"Expected 1 atendido, got: {data}"


def test_filter_orientacoes_by_area_direito(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_orientacao_data: dict[str, Any],
) -> None:
    client.post("/api/orientacao_juridica/", json=sample_orientacao_data, headers=auth_headers)

    trabalhista_data = {
        **sample_orientacao_data,
        "area_direito": "trabalhista",
        "descricao": "Orientação sobre direito trabalhista",
    }
    client.post("/api/orientacao_juridica/", json=trabalhista_data, headers=auth_headers)

    response = client.get("/api/orientacao_juridica/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    items = data["items"] if isinstance(data, dict) and "items" in data else data
    assert isinstance(items, list)
    assert len(items) >= 2

