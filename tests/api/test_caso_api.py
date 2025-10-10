from typing import Any

from flask.testing import FlaskClient


def test_create_caso_success(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    response = client.post("/api/caso/", json=sample_caso_data, headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["area_direito"] == "penal"
    assert data["situacao_deferimento"] == "deferido"
    assert "id" in data
    assert isinstance(data["id"], int)


def test_create_caso_requires_auth(
    client: FlaskClient, sample_caso_data: dict[str, Any]
) -> None:
    response = client.post("/api/caso/", json=sample_caso_data)

    assert response.status_code == 401


def test_get_caso_by_id(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_response.json is not None
    caso_id = create_response.json["id"]

    response = client.get(f"/api/caso/{caso_id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["area_direito"] == "penal"
    assert data["id"] == caso_id


def test_get_caso_not_found(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    response = client.get("/api/caso/99999", headers=auth_headers)

    assert response.status_code == 404


def test_update_caso(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_response.json is not None
    caso_id = create_response.json["id"]

    update_data = {**sample_caso_data, "descricao": "Descrição atualizada"}
    response = client.put(
        f"/api/caso/{caso_id}", json=update_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["descricao"] == "Descrição atualizada"
    assert data["id"] == caso_id


def test_delete_caso(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_response.json is not None
    caso_id = create_response.json["id"]

    response = client.delete(f"/api/caso/{caso_id}", headers=auth_headers)

    assert response.status_code == 200


def test_deferir_caso(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_response.json is not None
    caso_id = create_response.json["id"]

    response = client.patch(f"/api/caso/{caso_id}/deferir", headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["situacao_deferimento"] == "deferido"


def test_indeferir_caso(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_response.json is not None
    caso_id = create_response.json["id"]

    response = client.patch(
        f"/api/caso/{caso_id}/indeferir",
        json={"justif_indeferimento": "Fora do escopo do projeto"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["situacao_deferimento"] == "indeferido"
    assert data["justif_indeferimento"] == "Fora do escopo do projeto"


def test_search_casos(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    client.post("/api/caso/", json=sample_caso_data, headers=auth_headers)

    response = client.get("/api/caso/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert isinstance(data, (dict, list))


def test_create_processo_for_caso(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_response.json is not None
    caso_id = create_response.json["id"]

    processo_data = {"especie": "Ação Civil Pública", "numero": 123456, "status": True}

    response = client.post(
        f"/api/caso/{caso_id}/processo",
        json=processo_data,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["especie"] == "Ação Civil Pública"
    assert "id" in data


def test_get_processos_by_caso(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_response.json is not None
    caso_id = create_response.json["id"]

    processo_data = {"especie": "Ação Civil Pública", "status": True}
    client.post(
        f"/api/caso/{caso_id}/processo", json=processo_data, headers=auth_headers
    )

    response = client.get(f"/api/caso/{caso_id}/processo", headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert isinstance(data, (dict, list))


def test_create_evento_for_caso(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_response.json is not None
    caso_id = create_response.json["id"]

    evento_data = {
        "tipo_evento": "audiencia",
        "descricao": "Audiência de conciliação",
        "data_evento": "2024-12-01",
    }

    response = client.post(
        f"/api/caso/{caso_id}/evento",
        json=evento_data,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None


def test_get_eventos_by_caso(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_response.json is not None
    caso_id = create_response.json["id"]

    response = client.get(f"/api/caso/{caso_id}/evento", headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert isinstance(data, (dict, list))


def test_filter_casos_by_situacao(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    client.post("/api/caso/", json=sample_caso_data, headers=auth_headers)

    response = client.get(
        "/api/caso/?situacao_deferimento=deferido", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    items = data["items"] if isinstance(data, dict) and "items" in data else data
    assert isinstance(items, list)
    for item in items:
        assert item["situacao_deferimento"] == "deferido"


def test_caso_show_inactive_false_excludes_inactive(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    active_caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert active_caso_response.json is not None
    active_caso_id = active_caso_response.json["id"]

    inactive_caso_data = {**sample_caso_data, "area_direito": "civil"}
    inactive_caso_response = client.post(
        "/api/caso/", json=inactive_caso_data, headers=auth_headers
    )
    assert inactive_caso_response.json is not None
    inactive_caso_id = inactive_caso_response.json["id"]

    delete_response = client.delete(
        f"/api/caso/{inactive_caso_id}", headers=auth_headers
    )
    assert delete_response.status_code == 200

    search_response = client.get("/api/caso/?show_inactive=false", headers=auth_headers)
    assert search_response.status_code == 200
    data = search_response.json
    assert data is not None

    caso_ids = [caso["id"] for caso in data["items"]]
    assert active_caso_id in caso_ids
    assert inactive_caso_id not in caso_ids


def test_caso_show_inactive_true_includes_inactive(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    active_caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert active_caso_response.json is not None
    active_caso_id = active_caso_response.json["id"]

    inactive_caso_data = {**sample_caso_data, "area_direito": "trabalhista"}
    inactive_caso_response = client.post(
        "/api/caso/", json=inactive_caso_data, headers=auth_headers
    )
    assert inactive_caso_response.json is not None
    inactive_caso_id = inactive_caso_response.json["id"]

    delete_response = client.delete(
        f"/api/caso/{inactive_caso_id}", headers=auth_headers
    )
    assert delete_response.status_code == 200

    search_response = client.get("/api/caso/?show_inactive=true", headers=auth_headers)
    assert search_response.status_code == 200
    data = search_response.json
    assert data is not None

    caso_ids = [caso["id"] for caso in data["items"]]
    assert active_caso_id in caso_ids
    assert inactive_caso_id in caso_ids


def test_caso_show_inactive_default_excludes_inactive(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    active_caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert active_caso_response.json is not None
    active_caso_id = active_caso_response.json["id"]

    inactive_caso_data = {**sample_caso_data, "area_direito": "consumidor"}
    inactive_caso_response = client.post(
        "/api/caso/", json=inactive_caso_data, headers=auth_headers
    )
    assert inactive_caso_response.json is not None
    inactive_caso_id = inactive_caso_response.json["id"]

    delete_response = client.delete(
        f"/api/caso/{inactive_caso_id}", headers=auth_headers
    )
    assert delete_response.status_code == 200

    search_response = client.get("/api/caso/", headers=auth_headers)
    assert search_response.status_code == 200
    data = search_response.json
    assert data is not None

    caso_ids = [caso["id"] for caso in data["items"]]
    assert active_caso_id in caso_ids
    assert inactive_caso_id not in caso_ids
