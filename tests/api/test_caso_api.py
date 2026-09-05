import os
from io import BytesIO
from typing import Any

import pytest
from flask import Flask
from flask.testing import FlaskClient

from gestaolegal.services import private_file_storage
from tests.api.conftest import (
    assert_success_response,
    clean_tables,
    get_success_data,
)


def caminho_do_anexo(app: Flask, ref: str) -> str:
    """Caminho real do anexo de caso a partir da referência guardada no banco.

    O banco guarda só a referência relativa à categoria; quem sabe traduzir
    para disco é o `private_file_storage`, e ele precisa do contexto do app.
    """
    with app.app_context():
        return private_file_storage.resolve("casos", ref)


def anexo_existe(app: Flask, ref: str) -> bool:
    with app.app_context():
        return private_file_storage.exists("casos", ref)


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
    # Um caso deferido passa a ser "ativo" (valor que filtros e badges esperam).
    assert data["situacao_deferimento"] == "ativo"


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
    app: Flask,
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
    ref = data_response["link_arquivo"]

    # A resposta traz a referência relativa, nunca a raiz privada.
    assert not os.path.isabs(ref)
    assert "/" not in ref
    raiz = app.config["PRIVATE_FILES_ROOT"]
    assert raiz not in response.get_data(as_text=True)
    assert ref.endswith("test_documento.pdf")
    assert anexo_existe(app, ref)


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


def test_replace_arquivo_caso(
    app: Flask,
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    caso_id = get_success_data(
        client.post("/api/caso/", json=sample_caso_data, headers=auth_headers)
    )["id"]

    upload = client.post(
        f"/api/caso/{caso_id}/arquivos",
        data={"arquivo": (BytesIO(b"versao 1"), "original.pdf")},
        headers=auth_headers,
        content_type="multipart/form-data",
    )
    arquivo = get_success_data(upload)
    ref_antiga = arquivo["link_arquivo"]
    assert anexo_existe(app, ref_antiga)

    response = client.put(
        f"/api/caso/{caso_id}/arquivos/{arquivo['id']}",
        data={"arquivo": (BytesIO(b"versao 2"), "corrigido.pdf")},
        headers=auth_headers,
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    atualizado = get_success_data(response)
    assert atualizado["id"] == arquivo["id"]
    assert atualizado["link_arquivo"] != ref_antiga
    assert atualizado["link_arquivo"].endswith("corrigido.pdf")
    assert anexo_existe(app, atualizado["link_arquivo"])
    assert not anexo_existe(app, ref_antiga)

    # O caso continua com um único anexo.
    lista = get_success_data(client.get(f"/api/caso/{caso_id}/arquivos", headers=auth_headers))
    assert len(lista["arquivos"]) == 1

    os.remove(caminho_do_anexo(app, atualizado["link_arquivo"]))


def test_replace_arquivo_caso_rejects_non_pdf(
    app: Flask,
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    caso_id = get_success_data(
        client.post("/api/caso/", json=sample_caso_data, headers=auth_headers)
    )["id"]
    arquivo = get_success_data(
        client.post(
            f"/api/caso/{caso_id}/arquivos",
            data={"arquivo": (BytesIO(b"pdf"), "doc.pdf")},
            headers=auth_headers,
            content_type="multipart/form-data",
        )
    )

    response = client.put(
        f"/api/caso/{caso_id}/arquivos/{arquivo['id']}",
        data={"arquivo": (BytesIO(b"texto"), "doc.txt")},
        headers=auth_headers,
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert anexo_existe(app, arquivo["link_arquivo"])
    os.remove(caminho_do_anexo(app, arquivo["link_arquivo"]))


def test_replace_arquivo_caso_rollback_mantem_o_anterior(
    app: Flask,
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Transação que não confirma: o anexo antigo fica, o novo não sobra.

    O novo arquivo chega a ser gravado antes do update; se o banco recusar, ele
    não pode continuar no volume — ninguém o referencia — e o antigo tem que
    seguir baixável.
    """
    from gestaolegal.repositories.arquivo_caso_repository import ArquivoCasoRepository
    from gestaolegal.services import private_file_storage as pfs

    caso_id = get_success_data(
        client.post("/api/caso/", json=sample_caso_data, headers=auth_headers)
    )["id"]
    arquivo = get_success_data(
        client.post(
            f"/api/caso/{caso_id}/arquivos",
            data={"arquivo": (BytesIO(b"versao 1"), "original.pdf")},
            headers=auth_headers,
            content_type="multipart/form-data",
        )
    )
    ref_antiga = arquivo["link_arquivo"]

    gravadas: list[str] = []
    save_real = pfs.save

    def save_espiao(categoria: str, file: Any) -> str:
        ref = save_real(categoria, file)
        gravadas.append(ref)
        return ref

    monkeypatch.setattr(pfs, "save", save_espiao)

    def update_explode(self: Any, *args: Any, **kwargs: Any) -> None:
        raise RuntimeError("banco fora do ar")

    monkeypatch.setattr(ArquivoCasoRepository, "update", update_explode)

    response = client.put(
        f"/api/caso/{caso_id}/arquivos/{arquivo['id']}",
        data={"arquivo": (BytesIO(b"versao 2"), "corrigido.pdf")},
        headers=auth_headers,
        content_type="multipart/form-data",
    )
    assert response.status_code >= 400

    assert len(gravadas) == 1
    assert not anexo_existe(app, gravadas[0])

    monkeypatch.undo()
    atual = get_success_data(
        client.get(f"/api/caso/{caso_id}/arquivos", headers=auth_headers)
    )["arquivos"]
    assert [a["link_arquivo"] for a in atual] == [ref_antiga]
    assert anexo_existe(app, ref_antiga)

    download = client.get(
        f"/api/caso/{caso_id}/arquivos/{arquivo['id']}/download", headers=auth_headers
    )
    assert download.status_code == 200
    assert download.data == b"versao 1"

    os.remove(caminho_do_anexo(app, ref_antiga))


def test_download_arquivo_caso(
    app: Flask,
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    caso_id = get_success_data(
        client.post("/api/caso/", json=sample_caso_data, headers=auth_headers)
    )["id"]
    arquivo = get_success_data(
        client.post(
            f"/api/caso/{caso_id}/arquivos",
            data={"arquivo": (BytesIO(b"conteudo do pdf"), "peticao inicial.pdf")},
            headers=auth_headers,
            content_type="multipart/form-data",
        )
    )

    response = client.get(
        f"/api/caso/{caso_id}/arquivos/{arquivo['id']}/download", headers=auth_headers
    )

    assert response.status_code == 200
    assert response.data == b"conteudo do pdf"
    assert "attachment" in response.headers["Content-Disposition"]
    # O nome oferecido é o original, sem o prefixo de unicidade.
    assert "peticao_inicial.pdf" in response.headers["Content-Disposition"]
    assert app.config["PRIVATE_FILES_ROOT"] not in response.headers[
        "Content-Disposition"
    ]
    assert response.headers["Cache-Control"] == "private, no-store"

    os.remove(caminho_do_anexo(app, arquivo["link_arquivo"]))


def test_download_arquivo_caso_requires_auth(
    app: Flask,
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    caso_id = get_success_data(
        client.post("/api/caso/", json=sample_caso_data, headers=auth_headers)
    )["id"]
    arquivo = get_success_data(
        client.post(
            f"/api/caso/{caso_id}/arquivos",
            data={"arquivo": (BytesIO(b"sigiloso"), "sigiloso.pdf")},
            headers=auth_headers,
            content_type="multipart/form-data",
        )
    )

    response = client.get(f"/api/caso/{caso_id}/arquivos/{arquivo['id']}/download")

    assert response.status_code == 401

    os.remove(caminho_do_anexo(app, arquivo["link_arquivo"]))


def test_download_arquivo_caso_de_outra_unidade_recusado(
    app: Flask,
    client: FlaskClient,
    auth_headers: dict[str, str],
    auth_headers_nl: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    """O caso é de Belo Horizonte; quem está em Nova Lima não alcança o anexo."""
    caso_id = get_success_data(
        client.post("/api/caso/", json=sample_caso_data, headers=auth_headers)
    )["id"]
    arquivo = get_success_data(
        client.post(
            f"/api/caso/{caso_id}/arquivos",
            data={"arquivo": (BytesIO(b"de bh"), "bh.pdf")},
            headers=auth_headers,
            content_type="multipart/form-data",
        )
    )

    download = client.get(
        f"/api/caso/{caso_id}/arquivos/{arquivo['id']}/download",
        headers=auth_headers_nl,
    )
    assert download.status_code == 404

    exclusao = client.delete(
        f"/api/caso/{caso_id}/arquivos/{arquivo['id']}", headers=auth_headers_nl
    )
    assert exclusao.status_code == 404

    # O anexo continua intacto para quem é da unidade certa.
    assert anexo_existe(app, arquivo["link_arquivo"])
    os.remove(caminho_do_anexo(app, arquivo["link_arquivo"]))


def test_download_arquivo_caso_ausente_no_volume(
    app: Flask,
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    """Registro no banco sem arquivo no volume: recusa clara, não stack trace."""
    caso_id = get_success_data(
        client.post("/api/caso/", json=sample_caso_data, headers=auth_headers)
    )["id"]
    arquivo = get_success_data(
        client.post(
            f"/api/caso/{caso_id}/arquivos",
            data={"arquivo": (BytesIO(b"some depois"), "sumido.pdf")},
            headers=auth_headers,
            content_type="multipart/form-data",
        )
    )

    os.remove(caminho_do_anexo(app, arquivo["link_arquivo"]))

    response = client.get(
        f"/api/caso/{caso_id}/arquivos/{arquivo['id']}/download", headers=auth_headers
    )
    assert response.status_code >= 400


def test_delete_arquivo_caso_remove_do_volume(
    app: Flask,
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    caso_id = get_success_data(
        client.post("/api/caso/", json=sample_caso_data, headers=auth_headers)
    )["id"]
    arquivo = get_success_data(
        client.post(
            f"/api/caso/{caso_id}/arquivos",
            data={"arquivo": (BytesIO(b"para apagar"), "apagar.pdf")},
            headers=auth_headers,
            content_type="multipart/form-data",
        )
    )
    assert anexo_existe(app, arquivo["link_arquivo"])

    response = client.delete(
        f"/api/caso/{caso_id}/arquivos/{arquivo['id']}", headers=auth_headers
    )

    assert response.status_code == 200
    assert not anexo_existe(app, arquivo["link_arquivo"])


def test_replace_arquivo_caso_not_found(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    caso_id = get_success_data(
        client.post("/api/caso/", json=sample_caso_data, headers=auth_headers)
    )["id"]
    response = client.put(
        f"/api/caso/{caso_id}/arquivos/99999",
        data={"arquivo": (BytesIO(b"pdf"), "doc.pdf")},
        headers=auth_headers,
        content_type="multipart/form-data",
    )
    assert response.status_code == 404


def test_filter_casos_by_criado_por_me(
    client: FlaskClient,
    auth_headers: dict[str, str],
    non_admin_auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    # Admin cria um caso cujo responsável é o usuário 2; o outro usuário cria um
    # caso cujo responsável é o admin. "Cadastrado por mim" olha só o criador.
    criado_pelo_admin = get_success_data(
        client.post(
            "/api/caso/",
            json={**sample_caso_data, "id_usuario_responsavel": 2},
            headers=auth_headers,
        )
    )["id"]
    criado_pelo_outro = get_success_data(
        client.post(
            "/api/caso/",
            json={**sample_caso_data, "id_usuario_responsavel": 1},
            headers=non_admin_auth_headers,
        )
    )["id"]

    ids = [
        c["id"]
        for c in get_success_data(client.get("/api/caso/?criado_por=me", headers=auth_headers))[
            "items"
        ]
    ]
    assert criado_pelo_admin in ids
    assert criado_pelo_outro not in ids

    # Pode combinar com o filtro de responsável (user=me): aqui nenhum caso
    # satisfaz os dois ao mesmo tempo.
    ids = [
        c["id"]
        for c in get_success_data(
            client.get("/api/caso/?criado_por=me&user=me", headers=auth_headers)
        )["items"]
    ]
    assert criado_pelo_admin not in ids
    assert criado_pelo_outro not in ids


def test_upload_arquivo_too_large_returns_portuguese_message(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    caso_id = get_success_data(
        client.post("/api/caso/", json=sample_caso_data, headers=auth_headers)
    )["id"]
    grande = BytesIO(b"0" * (10 * 1024 * 1024 + 1024))
    response = client.post(
        f"/api/caso/{caso_id}/arquivos",
        data={"arquivo": (grande, "grande.pdf")},
        headers=auth_headers,
        content_type="multipart/form-data",
    )
    assert response.status_code == 413
    assert response.json["error"]["message"] == "O arquivo excede o tamanho máximo de 10 MB"


def test_caso_listagem_isolada_por_unidade(
    client: FlaskClient,
    auth_headers: dict[str, str],
    auth_headers_nl: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    """Cada unidade só enxerga os casos que criou."""
    clean_tables("casos_atendidos", "casos")

    id_bh = get_success_data(
        client.post("/api/caso/", json=sample_caso_data, headers=auth_headers)
    )["id"]
    id_nl = get_success_data(
        client.post("/api/caso/", json=sample_caso_data, headers=auth_headers_nl)
    )["id"]

    data_bh = get_success_data(client.get("/api/caso/", headers=auth_headers))
    assert [item["id"] for item in data_bh["items"]] == [id_bh]
    assert data_bh["total"] == 1

    data_nl = get_success_data(client.get("/api/caso/", headers=auth_headers_nl))
    assert [item["id"] for item in data_nl["items"]] == [id_nl]
    assert data_nl["total"] == 1


def test_caso_de_outra_unidade_responde_404(
    client: FlaskClient,
    auth_headers: dict[str, str],
    auth_headers_nl: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    """Caso de outra unidade não é acessível por id, nem para editar."""
    clean_tables("casos_atendidos", "casos")

    id_bh = get_success_data(
        client.post("/api/caso/", json=sample_caso_data, headers=auth_headers)
    )["id"]

    assert client.get(f"/api/caso/{id_bh}", headers=auth_headers).status_code == 200
    assert client.get(f"/api/caso/{id_bh}", headers=auth_headers_nl).status_code == 404

    update = client.put(
        f"/api/caso/{id_bh}",
        json={**sample_caso_data, "descricao": "Tentativa de outra unidade"},
        headers=auth_headers_nl,
    )
    assert update.status_code == 404

    assert (
        client.delete(f"/api/caso/{id_bh}", headers=auth_headers_nl).status_code == 404
    )


def test_caso_create_grava_unidade_ativa(
    client: FlaskClient,
    auth_headers_nl: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    """A criação grava a unidade ativa da requisição, não a unidade padrão."""
    clean_tables("casos_atendidos", "casos")

    data = get_success_data(
        client.post("/api/caso/", json=sample_caso_data, headers=auth_headers_nl)
    )
    assert data["unidade_id"] == 2


def test_caso_vincula_atendido_de_outra_unidade(
    client: FlaskClient,
    auth_headers: dict[str, str],
    auth_headers_nl: dict[str, str],
    sample_atendido_data: dict[str, Any],
    sample_caso_data: dict[str, Any],
) -> None:
    """Atendido de BH pode ser cliente de um caso de NL (decisão 3 do plano):
    o caso mostra o atendido, mas a listagem de atendidos de NL não."""
    clean_tables("casos_atendidos", "casos", "atendidos")

    id_atendido_bh = get_success_data(
        client.post("/api/atendido/", json=sample_atendido_data, headers=auth_headers)
    )["id"]

    caso_nl = get_success_data(
        client.post(
            "/api/caso/",
            json={**sample_caso_data, "ids_clientes": [id_atendido_bh]},
            headers=auth_headers_nl,
        )
    )
    assert caso_nl["unidade_id"] == 2
    assert [cliente["id"] for cliente in caso_nl["clientes"]] == [id_atendido_bh]

    detalhe = get_success_data(
        client.get(f"/api/caso/{caso_nl['id']}", headers=auth_headers_nl)
    )
    assert [cliente["id"] for cliente in detalhe["clientes"]] == [id_atendido_bh]

    atendidos_nl = get_success_data(client.get("/api/atendido/", headers=auth_headers_nl))
    assert [item["id"] for item in atendidos_nl["items"]] == []


def test_arquivos_de_caso_de_outra_unidade_responde_404(
    client: FlaskClient,
    auth_headers: dict[str, str],
    auth_headers_nl: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    """Anexos herdam o isolamento do caso a que pertencem."""
    clean_tables("casos_atendidos", "casos")

    id_bh = get_success_data(
        client.post("/api/caso/", json=sample_caso_data, headers=auth_headers)
    )["id"]

    assert (
        client.get(f"/api/caso/{id_bh}/arquivos", headers=auth_headers).status_code
        == 200
    )
    assert (
        client.get(f"/api/caso/{id_bh}/arquivos", headers=auth_headers_nl).status_code
        == 404
    )

    upload = client.post(
        f"/api/caso/{id_bh}/arquivos",
        data={"arquivo": (BytesIO(b"%PDF-1.4 teste"), "doc.pdf")},
        headers=auth_headers_nl,
        content_type="multipart/form-data",
    )
    assert upload.status_code == 404
