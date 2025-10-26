from io import BytesIO
from typing import Any

from flask.testing import FlaskClient

from tests.api.conftest import assert_success_response, get_success_data


def test_create_caso_success(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    response = client.post("/api/caso/", json=sample_caso_data, headers=auth_headers)

    assert response.status_code == 201
    data = get_success_data(response)
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
    assert create_response.status_code == 201
    create_data = get_success_data(create_response)
    assert create_data is not None
    caso_id = create_data["id"]

    response = client.get(f"/api/caso/{caso_id}", headers=auth_headers)

    assert response.status_code == 200
    data = get_success_data(response)
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
    assert create_response.status_code == 201
    create_data = get_success_data(create_response)
    assert create_data is not None
    caso_id = create_data["id"]

    update_data = {**sample_caso_data, "descricao": "Descrição atualizada"}
    response = client.put(
        f"/api/caso/{caso_id}", json=update_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = get_success_data(response)
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
    assert create_response.status_code == 201
    create_data = get_success_data(create_response)
    assert create_data is not None
    caso_id = create_data["id"]

    response = client.delete(f"/api/caso/{caso_id}", headers=auth_headers)

    assert response.status_code == 200
    assert_success_response(response)


def test_deferir_caso(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_response.status_code == 201
    create_data = get_success_data(create_response)
    assert create_data is not None
    caso_id = create_data["id"]

    response = client.patch(f"/api/caso/{caso_id}/deferir", headers=auth_headers)

    assert response.status_code == 200
    data = get_success_data(response)
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
    assert create_response.status_code == 201
    create_data = get_success_data(create_response)
    assert create_data is not None
    caso_id = create_data["id"]

    response = client.patch(
        f"/api/caso/{caso_id}/indeferir",
        json={"justif_indeferimento": "Fora do escopo do projeto"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = get_success_data(response)
    assert data is not None
    assert data["situacao_deferimento"] == "indeferido"
    assert data["justif_indeferimento"] == "Fora do escopo do projeto"


def test_search_casos(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    creation_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert creation_response.status_code == 201

    response = client.get("/api/caso/", headers=auth_headers)

    assert response.status_code == 200
    data = get_success_data(response)
    assert data is not None
    assert isinstance(data, dict)


def test_create_processo_for_caso(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_response.status_code == 201
    caso_data = get_success_data(create_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

    processo_data = {"especie": "Ação Civil Pública", "numero": 123456, "status": True}

    response = client.post(
        f"/api/caso/{caso_id}/processos",
        json=processo_data,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = get_success_data(response)
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
    assert create_response.status_code == 201
    caso_data = get_success_data(create_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

    processo_data = {"especie": "Ação Civil Pública", "status": True}
    processo_response = client.post(
        f"/api/caso/{caso_id}/processos", json=processo_data, headers=auth_headers
    )
    assert processo_response.status_code == 201
    assert get_success_data(processo_response) is not None

    response = client.get(f"/api/caso/{caso_id}/processos", headers=auth_headers)

    assert response.status_code == 200
    data = get_success_data(response)
    assert data is not None
    assert isinstance(data, dict)


def test_create_evento_for_caso(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_response.status_code == 201
    caso_data = get_success_data(create_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

    evento_data = {
        "tipo": "audiencia",
        "descricao": "Audiência de conciliação",
        "data_evento": "2024-12-01",
        "status": "true",
    }

    response = client.post(
        f"/api/caso/{caso_id}/eventos",
        data=evento_data,
        headers=auth_headers,
        content_type="multipart/form-data",
    )

    assert response.status_code == 201
    data = get_success_data(response)
    assert data is not None


def test_get_eventos_by_caso(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_response.status_code == 201
    caso_data = get_success_data(create_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

    response = client.get(f"/api/caso/{caso_id}/eventos", headers=auth_headers)

    assert response.status_code == 200
    data = get_success_data(response)
    assert data is not None
    assert isinstance(data, dict)
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data
    assert "total_pages" in data
    assert "has_next_page" in data
    assert "has_previous_page" in data
    assert isinstance(data["items"], list)


def test_filter_casos_by_situacao(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    creation_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert creation_response.status_code == 201

    response = client.get(
        "/api/caso/?situacao_deferimento=deferido", headers=auth_headers
    )

    assert response.status_code == 200
    data = get_success_data(response)
    assert data is not None
    items = data["items"]
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
    assert active_caso_response.status_code == 201
    active_data = get_success_data(active_caso_response)
    assert active_data is not None
    active_caso_id = active_data["id"]

    inactive_caso_data = {**sample_caso_data, "area_direito": "civil"}
    inactive_caso_response = client.post(
        "/api/caso/", json=inactive_caso_data, headers=auth_headers
    )
    assert inactive_caso_response.status_code == 201
    inactive_data = get_success_data(inactive_caso_response)
    assert inactive_data is not None
    inactive_caso_id = inactive_data["id"]

    delete_response = client.delete(
        f"/api/caso/{inactive_caso_id}", headers=auth_headers
    )
    assert delete_response.status_code == 200
    assert_success_response(delete_response)

    search_response = client.get("/api/caso/?show_inactive=false", headers=auth_headers)
    assert search_response.status_code == 200
    data = get_success_data(search_response)
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
    assert active_caso_response.status_code == 201
    active_data = get_success_data(active_caso_response)
    assert active_data is not None
    active_caso_id = active_data["id"]

    inactive_caso_data = {**sample_caso_data, "area_direito": "trabalhista"}
    inactive_caso_response = client.post(
        "/api/caso/", json=inactive_caso_data, headers=auth_headers
    )
    assert inactive_caso_response.status_code == 201
    inactive_data = get_success_data(inactive_caso_response)
    assert inactive_data is not None
    inactive_caso_id = inactive_data["id"]

    delete_response = client.delete(
        f"/api/caso/{inactive_caso_id}", headers=auth_headers
    )
    assert delete_response.status_code == 200
    assert_success_response(delete_response)

    search_response = client.get("/api/caso/?show_inactive=true", headers=auth_headers)
    assert search_response.status_code == 200
    data = get_success_data(search_response)
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
    assert active_caso_response.status_code == 201
    active_data = get_success_data(active_caso_response)
    assert active_data is not None
    active_caso_id = active_data["id"]

    inactive_caso_data = {**sample_caso_data, "area_direito": "consumidor"}
    inactive_caso_response = client.post(
        "/api/caso/", json=inactive_caso_data, headers=auth_headers
    )
    assert inactive_caso_response.status_code == 201
    inactive_data = get_success_data(inactive_caso_response)
    assert inactive_data is not None
    inactive_caso_id = inactive_data["id"]

    delete_response = client.delete(
        f"/api/caso/{inactive_caso_id}", headers=auth_headers
    )
    assert delete_response.status_code == 200
    assert_success_response(delete_response)

    search_response = client.get("/api/caso/", headers=auth_headers)
    assert search_response.status_code == 200
    data = get_success_data(search_response)
    assert data is not None

    caso_ids = [caso["id"] for caso in data["items"]]
    assert active_caso_id in caso_ids
    assert inactive_caso_id not in caso_ids


def test_update_processo_for_caso(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_caso_response.status_code == 201
    caso_data = get_success_data(create_caso_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

    processo_data = {"especie": "Ação Civil Pública", "numero": 999888, "status": True}
    create_processo_response = client.post(
        f"/api/caso/{caso_id}/processos",
        json=processo_data,
        headers=auth_headers,
    )
    assert create_processo_response.status_code == 201
    processo_data_response = get_success_data(create_processo_response)
    assert processo_data_response is not None
    processo_id = processo_data_response["id"]

    update_data = {"especie": "Ação Penal Privada", "numero": 654321}
    response = client.put(
        f"/api/caso/{caso_id}/processos/{processo_id}",
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = get_success_data(response)
    assert data is not None
    assert data["especie"] == "Ação Penal Privada"
    assert data["numero"] == 654321
    assert data["id"] == processo_id


def test_delete_processo_for_caso(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_caso_response.status_code == 201
    caso_data = get_success_data(create_caso_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

    processo_data = {"especie": "Ação Trabalhista", "numero": 789012, "status": True}
    create_processo_response = client.post(
        f"/api/caso/{caso_id}/processos",
        json=processo_data,
        headers=auth_headers,
    )
    assert create_processo_response.status_code == 201
    processo_data_response = get_success_data(create_processo_response)
    assert processo_data_response is not None
    processo_id = processo_data_response["id"]

    response = client.delete(
        f"/api/caso/{caso_id}/processos/{processo_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert_success_response(response)


def test_get_single_processo_for_caso(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_caso_response.status_code == 201
    caso_data = get_success_data(create_caso_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

    processo_data = {"especie": "Habeas Corpus", "numero": 111222, "status": True}
    create_processo_response = client.post(
        f"/api/caso/{caso_id}/processos",
        json=processo_data,
        headers=auth_headers,
    )
    assert create_processo_response.status_code == 201
    processo_data_response = get_success_data(create_processo_response)
    assert processo_data_response is not None
    processo_id = processo_data_response["id"]

    response = client.get(
        f"/api/caso/{caso_id}/processos/{processo_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = get_success_data(response)
    assert data is not None
    assert data["especie"] == "Habeas Corpus"
    assert data["id"] == processo_id


def test_update_processo_wrong_caso_returns_error(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    caso_response_1 = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert caso_response_1.status_code == 201
    caso_data_1 = get_success_data(caso_response_1)
    assert caso_data_1 is not None
    caso_id_1 = caso_data_1["id"]

    caso_data_2 = {**sample_caso_data, "area_direito": "civil"}
    caso_response_2 = client.post("/api/caso/", json=caso_data_2, headers=auth_headers)
    assert caso_response_2.status_code == 201
    caso_data_2_response = get_success_data(caso_response_2)
    assert caso_data_2_response is not None
    caso_id_2 = caso_data_2_response["id"]

    processo_data = {"especie": "Ação de Despejo", "status": True}
    processo_response = client.post(
        f"/api/caso/{caso_id_1}/processos",
        json=processo_data,
        headers=auth_headers,
    )
    assert processo_response.status_code == 201
    processo_data_response = get_success_data(processo_response)
    assert processo_data_response is not None
    processo_id = processo_data_response["id"]

    response = client.put(
        f"/api/caso/{caso_id_2}/processos/{processo_id}",
        json={"especie": "Updated"},
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_update_evento_for_caso(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_caso_response.status_code == 201
    caso_data = get_success_data(create_caso_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

    evento_data = {
        "tipo": "audiencia",
        "descricao": "Audiência inicial",
        "data_evento": "2024-12-01",
        "status": "true",
    }
    create_evento_response = client.post(
        f"/api/caso/{caso_id}/eventos",
        data=evento_data,
        headers=auth_headers,
        content_type="multipart/form-data",
    )
    assert create_evento_response.status_code == 201
    evento_data_response = get_success_data(create_evento_response)
    assert evento_data_response is not None
    evento_id = evento_data_response["id"]

    update_data = {
        "tipo": "reuniao",
        "descricao": "Reunião com cliente",
        "data_evento": "2024-12-15",
    }
    response = client.put(
        f"/api/caso/{caso_id}/eventos/{evento_id}",
        data=update_data,
        headers=auth_headers,
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    data = get_success_data(response)
    assert data is not None
    assert data["tipo"] == "reuniao"
    assert data["descricao"] == "Reunião com cliente"


def test_get_single_evento_for_caso(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_caso_response.status_code == 201
    caso_data = get_success_data(create_caso_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

    evento_data = {
        "tipo": "prazo",
        "descricao": "Prazo para recurso",
        "data_evento": "2024-11-30",
        "status": "true",
    }
    create_evento_response = client.post(
        f"/api/caso/{caso_id}/eventos",
        data=evento_data,
        headers=auth_headers,
        content_type="multipart/form-data",
    )
    assert create_evento_response.status_code == 201
    evento_data_response = get_success_data(create_evento_response)
    assert evento_data_response is not None
    evento_id = evento_data_response["id"]

    response = client.get(
        f"/api/caso/{caso_id}/eventos/{evento_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = get_success_data(response)
    assert data is not None
    assert data["tipo"] == "prazo"
    assert data["id"] == evento_id


def test_update_evento_wrong_caso_returns_error(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    caso_response_1 = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert caso_response_1.status_code == 201
    caso_data_1 = get_success_data(caso_response_1)
    assert caso_data_1 is not None
    caso_id_1 = caso_data_1["id"]

    caso_data_2 = {**sample_caso_data, "area_direito": "trabalhista"}
    caso_response_2 = client.post("/api/caso/", json=caso_data_2, headers=auth_headers)
    assert caso_response_2.status_code == 201
    caso_data_2_response = get_success_data(caso_response_2)
    assert caso_data_2_response is not None
    caso_id_2 = caso_data_2_response["id"]

    evento_data = {
        "tipo": "audiencia",
        "descricao": "Audiência trabalhista",
        "data_evento": "2024-12-20",
        "status": "true",
    }
    evento_response = client.post(
        f"/api/caso/{caso_id_1}/eventos",
        data=evento_data,
        headers=auth_headers,
        content_type="multipart/form-data",
    )
    assert evento_response.status_code == 201
    evento_data_response = get_success_data(evento_response)
    assert evento_data_response is not None
    evento_id = evento_data_response["id"]

    response = client.put(
        f"/api/caso/{caso_id_2}/eventos/{evento_id}",
        data={"tipo": "reuniao"},
        headers=auth_headers,
        content_type="multipart/form-data",
    )

    assert response.status_code == 404


def test_upload_arquivo_to_caso(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_caso_response.status_code == 201
    caso_data = get_success_data(create_caso_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

    file_content = b"Test file content for caso"
    data = {
        "arquivo": (BytesIO(file_content), "test_documento.pdf"),
    }

    response = client.post(
        f"/api/caso/{caso_id}/arquivos",
        data=data,
        headers=auth_headers,
        content_type="multipart/form-data",
    )

    assert response.status_code == 201
    data_response = get_success_data(response)
    assert data_response is not None
    assert "id" in data_response
    assert "link_arquivo" in data_response


def test_get_arquivos_by_caso(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_caso_response.status_code == 201
    caso_data = get_success_data(create_caso_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

    file_content = b"Test file for listing"
    data = {
        "arquivo": (BytesIO(file_content), "documento_lista.pdf"),
    }
    upload_response = client.post(
        f"/api/caso/{caso_id}/arquivos",
        data=data,
        headers=auth_headers,
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 201
    assert get_success_data(upload_response) is not None

    response = client.get(f"/api/caso/{caso_id}/arquivos", headers=auth_headers)

    assert response.status_code == 200
    data_response = get_success_data(response)
    assert data_response is not None
    assert "arquivos" in data_response
    assert isinstance(data_response["arquivos"], list)


def test_delete_arquivo_from_caso(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_caso_response.status_code == 201
    caso_data = get_success_data(create_caso_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

    file_content = b"Test file to delete"
    data = {
        "arquivo": (BytesIO(file_content), "to_delete.pdf"),
    }
    upload_response = client.post(
        f"/api/caso/{caso_id}/arquivos",
        data=data,
        headers=auth_headers,
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 201
    upload_data = get_success_data(upload_response)
    assert upload_data is not None
    arquivo_id = upload_data["id"]

    response = client.delete(
        f"/api/caso/{caso_id}/arquivos/{arquivo_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert_success_response(response)


def test_upload_arquivo_to_nonexistent_caso(
    client: FlaskClient, auth_headers: dict[str, str]
) -> None:
    file_content = b"Test file content"
    data = {
        "arquivo": (BytesIO(file_content), "test_doc.pdf"),
    }

    response = client.post(
        "/api/caso/99999/arquivos",
        data=data,
        headers=auth_headers,
        content_type="multipart/form-data",
    )

    assert response.status_code == 404


def test_upload_arquivo_without_file(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_caso_response.status_code == 201
    caso_data = get_success_data(create_caso_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

    response = client.post(
        f"/api/caso/{caso_id}/arquivos",
        data={},
        headers=auth_headers,
        content_type="multipart/form-data",
    )

    assert response.status_code == 400


def test_filter_casos_by_user_me(
    client: FlaskClient,
    auth_headers: dict[str, str],
    non_admin_auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    caso_admin_data = {
        **sample_caso_data,
        "area_direito": "penal",
        "id_usuario_responsavel": 1,
    }
    admin_caso_response = client.post(
        "/api/caso/", json=caso_admin_data, headers=auth_headers
    )
    assert admin_caso_response.status_code == 201
    admin_caso = get_success_data(admin_caso_response)
    assert admin_caso is not None
    admin_caso_id = admin_caso["id"]

    caso_non_admin_data = {
        **sample_caso_data,
        "area_direito": "civil",
        "id_usuario_responsavel": 2,
    }
    non_admin_caso_response = client.post(
        "/api/caso/", json=caso_non_admin_data, headers=non_admin_auth_headers
    )
    assert non_admin_caso_response.status_code == 201
    non_admin_caso = get_success_data(non_admin_caso_response)
    assert non_admin_caso is not None
    non_admin_caso_id = non_admin_caso["id"]

    response = client.get("/api/caso/?user=me", headers=auth_headers)

    assert response.status_code == 200
    data = get_success_data(response)
    assert data is not None
    items = data["items"]
    assert isinstance(items, list)

    caso_ids = [caso["id"] for caso in items]
    assert admin_caso_id in caso_ids
    assert non_admin_caso_id not in caso_ids


def test_filter_casos_by_user_id(
    client: FlaskClient,
    auth_headers: dict[str, str],
    non_admin_auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    caso_admin_data = {
        **sample_caso_data,
        "area_direito": "trabalhista",
        "id_usuario_responsavel": 1,
    }
    admin_caso_response = client.post(
        "/api/caso/", json=caso_admin_data, headers=auth_headers
    )
    assert admin_caso_response.status_code == 201
    admin_caso = get_success_data(admin_caso_response)
    assert admin_caso is not None
    admin_caso_id = admin_caso["id"]
    admin_user_id = admin_caso["id_usuario_responsavel"]

    caso_non_admin_data = {
        **sample_caso_data,
        "area_direito": "consumidor",
        "id_usuario_responsavel": 2,
    }
    non_admin_caso_response = client.post(
        "/api/caso/", json=caso_non_admin_data, headers=non_admin_auth_headers
    )
    assert non_admin_caso_response.status_code == 201
    non_admin_caso = get_success_data(non_admin_caso_response)
    assert non_admin_caso is not None
    non_admin_caso_id = non_admin_caso["id"]
    non_admin_caso["id_usuario_responsavel"]

    response = client.get(f"/api/caso/?user={admin_user_id}", headers=auth_headers)

    assert response.status_code == 200
    data = get_success_data(response)
    assert data is not None
    items = data["items"]
    assert isinstance(items, list)

    caso_ids = [caso["id"] for caso in items]
    assert admin_caso_id in caso_ids
    assert non_admin_caso_id not in caso_ids

    for caso in items:
        assert caso["id_usuario_responsavel"] == admin_user_id


def test_filter_casos_by_user_id_as_non_admin(
    client: FlaskClient,
    auth_headers: dict[str, str],
    non_admin_auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    caso_admin_data = {
        **sample_caso_data,
        "area_direito": "penal",
        "id_usuario_responsavel": 1,
    }
    admin_caso_response = client.post(
        "/api/caso/", json=caso_admin_data, headers=auth_headers
    )
    assert admin_caso_response.status_code == 201
    admin_caso = get_success_data(admin_caso_response)
    assert admin_caso is not None
    admin_caso_id = admin_caso["id"]

    caso_non_admin_data = {
        **sample_caso_data,
        "area_direito": "civil",
        "id_usuario_responsavel": 2,
    }
    non_admin_caso_response = client.post(
        "/api/caso/", json=caso_non_admin_data, headers=non_admin_auth_headers
    )
    assert non_admin_caso_response.status_code == 201
    non_admin_caso = get_success_data(non_admin_caso_response)
    assert non_admin_caso is not None
    non_admin_caso_id = non_admin_caso["id"]
    non_admin_user_id = non_admin_caso["id_usuario_responsavel"]

    response = client.get(
        f"/api/caso/?user={non_admin_user_id}", headers=non_admin_auth_headers
    )

    assert response.status_code == 200
    data = get_success_data(response)
    assert data is not None
    items = data["items"]
    assert isinstance(items, list)

    caso_ids = [caso["id"] for caso in items]
    assert non_admin_caso_id in caso_ids
    assert admin_caso_id not in caso_ids

    for caso in items:
        assert caso["id_usuario_responsavel"] == non_admin_user_id


def test_filter_casos_without_user_param_returns_all(
    client: FlaskClient,
    auth_headers: dict[str, str],
    non_admin_auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    caso_admin_data = {
        **sample_caso_data,
        "area_direito": "ambiental",
        "id_usuario_responsavel": 1,
    }
    admin_caso_response = client.post(
        "/api/caso/", json=caso_admin_data, headers=auth_headers
    )
    assert admin_caso_response.status_code == 201
    admin_caso = get_success_data(admin_caso_response)
    assert admin_caso is not None
    admin_caso_id = admin_caso["id"]

    caso_non_admin_data = {
        **sample_caso_data,
        "area_direito": "tributario",
        "id_usuario_responsavel": 2,
    }
    non_admin_caso_response = client.post(
        "/api/caso/", json=caso_non_admin_data, headers=non_admin_auth_headers
    )
    assert non_admin_caso_response.status_code == 201
    non_admin_caso = get_success_data(non_admin_caso_response)
    assert non_admin_caso is not None
    non_admin_caso_id = non_admin_caso["id"]

    response = client.get("/api/caso/", headers=auth_headers)

    assert response.status_code == 200
    data = get_success_data(response)
    assert data is not None
    items = data["items"]
    assert isinstance(items, list)

    caso_ids = [caso["id"] for caso in items]
    assert admin_caso_id in caso_ids
    assert non_admin_caso_id in caso_ids


def test_filter_casos_by_invalid_user_param_returns_all(
    client: FlaskClient,
    auth_headers: dict[str, str],
    non_admin_auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    caso_admin_data = {
        **sample_caso_data,
        "area_direito": "familia",
        "id_usuario_responsavel": 1,
    }
    admin_caso_response = client.post(
        "/api/caso/", json=caso_admin_data, headers=auth_headers
    )
    assert admin_caso_response.status_code == 201
    admin_caso = get_success_data(admin_caso_response)
    assert admin_caso is not None
    admin_caso_id = admin_caso["id"]

    caso_non_admin_data = {
        **sample_caso_data,
        "area_direito": "previdenciario",
        "id_usuario_responsavel": 2,
    }
    non_admin_caso_response = client.post(
        "/api/caso/", json=caso_non_admin_data, headers=non_admin_auth_headers
    )
    assert non_admin_caso_response.status_code == 201
    non_admin_caso = get_success_data(non_admin_caso_response)
    assert non_admin_caso is not None
    non_admin_caso_id = non_admin_caso["id"]

    response = client.get("/api/caso/?user=invalid_value", headers=auth_headers)

    assert response.status_code == 200
    data = get_success_data(response)
    assert data is not None
    items = data["items"]
    assert isinstance(items, list)

    caso_ids = [caso["id"] for caso in items]
    assert admin_caso_id in caso_ids
    assert non_admin_caso_id in caso_ids


def test_update_caso_not_found(
    client: FlaskClient, auth_headers: dict[str, str]
) -> None:
    update_data = {"descricao": "Updated description"}
    response = client.put("/api/caso/99999", json=update_data, headers=auth_headers)

    assert response.status_code == 404


def test_deferir_caso_not_found(
    client: FlaskClient, auth_headers: dict[str, str]
) -> None:
    response = client.patch("/api/caso/99999/deferir", headers=auth_headers)

    assert response.status_code == 404


def test_indeferir_caso_not_found(
    client: FlaskClient, auth_headers: dict[str, str]
) -> None:
    response = client.patch(
        "/api/caso/99999/indeferir",
        json={"justif_indeferimento": "Justificativa"},
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_delete_caso_not_found(
    client: FlaskClient, auth_headers: dict[str, str]
) -> None:
    response = client.delete("/api/caso/99999", headers=auth_headers)

    assert response.status_code == 404


def test_get_processo_not_found(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_caso_response.status_code == 201
    caso_data = get_success_data(create_caso_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

    response = client.get(f"/api/caso/{caso_id}/processos/99999", headers=auth_headers)

    assert response.status_code == 404


def test_get_evento_not_found(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    create_caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert create_caso_response.status_code == 201
    caso_data = get_success_data(create_caso_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

    response = client.get(f"/api/caso/{caso_id}/eventos/99999", headers=auth_headers)

    assert response.status_code == 404
