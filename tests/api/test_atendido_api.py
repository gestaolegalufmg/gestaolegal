from typing import Any

from flask.testing import FlaskClient


def test_create_atendido_success(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
) -> None:
    response = client.post(
        "/api/atendido/", json=sample_atendido_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["nome"] == "João Silva Teste"
    assert data["cpf"] == "123.456.789-00"
    assert data["email"] == "joao.teste@exemplo.com"
    assert "id" in data
    assert isinstance(data["id"], int)


def test_create_atendido_requires_auth(
    client: FlaskClient, sample_atendido_data: dict[str, Any]
) -> None:
    response = client.post("/api/atendido/", json=sample_atendido_data)

    assert response.status_code == 401


def test_get_atendido_by_id(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
) -> None:
    create_response = client.post(
        "/api/atendido/", json=sample_atendido_data, headers=auth_headers
    )
    assert create_response.json is not None
    atendido_id = create_response.json["id"]

    response = client.get(f"/api/atendido/{atendido_id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["nome"] == "João Silva Teste"
    assert data["cpf"] == "123.456.789-00"
    assert data["id"] == atendido_id


def test_get_atendido_not_found(
    client: FlaskClient, auth_headers: dict[str, str]
) -> None:
    response = client.get("/api/atendido/99999", headers=auth_headers)

    assert response.status_code == 404


def test_update_atendido(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
) -> None:
    create_response = client.post(
        "/api/atendido/", json=sample_atendido_data, headers=auth_headers
    )
    assert create_response.json is not None
    atendido_id = create_response.json["id"]

    update_data = {**sample_atendido_data, "nome": "João Silva Atualizado"}
    response = client.put(
        f"/api/atendido/{atendido_id}", json=update_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["nome"] == "João Silva Atualizado"
    assert data["id"] == atendido_id


def test_delete_atendido(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
) -> None:
    create_response = client.post(
        "/api/atendido/", json=sample_atendido_data, headers=auth_headers
    )
    assert create_response.json is not None
    atendido_id = create_response.json["id"]

    response = client.delete(f"/api/atendido/{atendido_id}", headers=auth_headers)

    assert response.status_code == 200

    get_response = client.get(f"/api/atendido/{atendido_id}", headers=auth_headers)
    assert get_response.status_code == 200
    data = get_response.json
    assert data is not None
    assert data["status"] == 0


def test_search_atendidos(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
) -> None:
    client.post("/api/atendido/", json=sample_atendido_data, headers=auth_headers)

    response = client.get("/api/atendido/?search=João", headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0


def test_tornar_assistido(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
    sample_assistido_data: dict[str, Any],
) -> None:
    create_response = client.post(
        "/api/atendido/", json=sample_atendido_data, headers=auth_headers
    )
    assert create_response.json is not None
    atendido_id = create_response.json["id"]

    response = client.post(
        f"/api/atendido/{atendido_id}/tornar-assistido",
        json=sample_assistido_data,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert "assistido" in data
    assistido = data["assistido"]
    assert assistido["profissao"] == "Engenheiro"
    assert assistido["raca"] == "parda"


def test_update_assistido(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
    sample_assistido_data: dict[str, Any],
) -> None:
    create_response = client.post(
        "/api/atendido/", json=sample_atendido_data, headers=auth_headers
    )
    assert create_response.json is not None
    atendido_id = create_response.json["id"]

    client.post(
        f"/api/atendido/{atendido_id}/tornar-assistido",
        json=sample_assistido_data,
        headers=auth_headers,
    )

    update_data = {**sample_assistido_data, "profissao": "Arquiteto"}
    response = client.put(
        f"/api/atendido/{atendido_id}/assistido",
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert "assistido" in data
    assert data["assistido"]["profissao"] == "Arquiteto"


def test_get_atendidos_pagination(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
) -> None:
    for i in range(5):
        data = {**sample_atendido_data, "cpf": f"123.456.789-{i:02d}"}
        client.post("/api/atendido/", json=data, headers=auth_headers)

    response = client.get("/api/atendido/?page=1&per_page=2", headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) <= 2
    assert "total" in data
    assert isinstance(data["total"], int)
    assert data["total"] >= 5


def test_atendido_show_inactive_false_excludes_inactive(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
) -> None:
    active_atendido_response = client.post(
        "/api/atendido/", json=sample_atendido_data, headers=auth_headers
    )
    assert active_atendido_response.status_code == 200
    assert active_atendido_response.json is not None
    active_atendido_id = active_atendido_response.json["id"]

    inactive_atendido_data = {**sample_atendido_data, "cpf": "987.654.321-00"}
    inactive_atendido_response = client.post(
        "/api/atendido/", json=inactive_atendido_data, headers=auth_headers
    )
    assert inactive_atendido_response.status_code == 200
    assert inactive_atendido_response.json is not None
    inactive_atendido_id = inactive_atendido_response.json["id"]

    delete_response = client.delete(
        f"/api/atendido/{inactive_atendido_id}", headers=auth_headers
    )
    assert delete_response.status_code == 200

    search_response = client.get(
        "/api/atendido/?show_inactive=false", headers=auth_headers
    )
    assert search_response.status_code == 200
    data = search_response.json
    assert data is not None

    atendido_ids = [atendido["id"] for atendido in data["items"]]
    assert active_atendido_id in atendido_ids
    assert inactive_atendido_id not in atendido_ids


def test_atendido_show_inactive_true_includes_inactive(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
) -> None:
    active_atendido_response = client.post(
        "/api/atendido/", json=sample_atendido_data, headers=auth_headers
    )
    assert active_atendido_response.status_code == 200
    assert active_atendido_response.json is not None
    active_atendido_id = active_atendido_response.json["id"]

    inactive_atendido_data = {**sample_atendido_data, "cpf": "111.222.333-44"}
    inactive_atendido_response = client.post(
        "/api/atendido/", json=inactive_atendido_data, headers=auth_headers
    )
    assert inactive_atendido_response.status_code == 200
    assert inactive_atendido_response.json is not None
    inactive_atendido_id = inactive_atendido_response.json["id"]

    delete_response = client.delete(
        f"/api/atendido/{inactive_atendido_id}", headers=auth_headers
    )
    assert delete_response.status_code == 200

    search_response = client.get(
        "/api/atendido/?show_inactive=true", headers=auth_headers
    )
    assert search_response.status_code == 200
    data = search_response.json
    assert data is not None

    atendido_ids = [atendido["id"] for atendido in data["items"]]
    assert active_atendido_id in atendido_ids
    assert inactive_atendido_id in atendido_ids


def test_atendido_show_inactive_default_excludes_inactive(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
) -> None:
    active_atendido_response = client.post(
        "/api/atendido/", json=sample_atendido_data, headers=auth_headers
    )
    assert active_atendido_response.status_code == 200
    assert active_atendido_response.json is not None
    active_atendido_id = active_atendido_response.json["id"]

    inactive_atendido_data = {**sample_atendido_data, "cpf": "555.444.333-22"}
    inactive_atendido_response = client.post(
        "/api/atendido/", json=inactive_atendido_data, headers=auth_headers
    )
    assert inactive_atendido_response.status_code == 200
    assert inactive_atendido_response.json is not None
    inactive_atendido_id = inactive_atendido_response.json["id"]

    delete_response = client.delete(
        f"/api/atendido/{inactive_atendido_id}", headers=auth_headers
    )
    assert delete_response.status_code == 200

    search_response = client.get("/api/atendido/", headers=auth_headers)
    assert search_response.status_code == 200
    data = search_response.json
    assert data is not None

    atendido_ids = [atendido["id"] for atendido in data["items"]]
    assert active_atendido_id in atendido_ids
    assert inactive_atendido_id not in atendido_ids
