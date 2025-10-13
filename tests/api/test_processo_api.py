from typing import Any

from flask.testing import FlaskClient


def test_create_processo_with_date_strings(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    """Test processo creation with date fields as ISO strings"""
    # First create a caso
    caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert caso_response.status_code == 200
    assert caso_response.json is not None
    caso_id = caso_response.json["id"]

    processo_data = {
        "especie": "Ação Civil Pública",
        "numero": 1234567890,
        "data_distribuicao": "2024-01-15",
        "data_transito_em_julgado": "2024-12-31",
        "status": True,
    }

    response = client.post(
        f"/api/caso/{caso_id}/processos", json=processo_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["especie"] == "Ação Civil Pública"
    assert data["numero"] == 1234567890
    # Backend returns dates in HTTP date format (RFC 2822), not ISO
    assert "data_distribuicao" in data
    assert "2024" in data["data_distribuicao"]
    assert "Jan" in data["data_distribuicao"] or "01" in data["data_distribuicao"]
    assert "data_transito_em_julgado" in data
    assert "2024" in data["data_transito_em_julgado"]
    assert (
        "Dec" in data["data_transito_em_julgado"]
        or "12" in data["data_transito_em_julgado"]
    )


def test_create_processo_with_link_url(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    """Test processo creation with valid URL link"""
    caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert caso_response.status_code == 200
    assert caso_response.json is not None
    caso_id = caso_response.json["id"]

    processo_data = {
        "especie": "Ação Ordinária",
        "link": "https://esaj.tjmg.jus.br/processo/123456",
        "status": True,
    }

    response = client.post(
        f"/api/caso/{caso_id}/processos", json=processo_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["link"] == "https://esaj.tjmg.jus.br/processo/123456"


def test_create_processo_with_empty_link(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    """Test processo creation with empty string link (should be accepted)"""
    caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert caso_response.status_code == 200
    assert caso_response.json is not None
    caso_id = caso_response.json["id"]

    processo_data = {"especie": "Ação Monitória", "link": "", "status": True}

    response = client.post(
        f"/api/caso/{caso_id}/processos", json=processo_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None


def test_create_processo_with_numeric_fields(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    """Test processo creation with valor_causa fields"""
    caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert caso_response.status_code == 200
    assert caso_response.json is not None
    caso_id = caso_response.json["id"]

    processo_data = {
        "especie": "Ação de Indenização",
        "valor_causa_inicial": 50000,
        "valor_causa_atual": 75000,
        "status": True,
    }

    response = client.post(
        f"/api/caso/{caso_id}/processos", json=processo_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["valor_causa_inicial"] == 50000
    assert data["valor_causa_atual"] == 75000


def test_update_processo_partial_data(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    """Test processo update with partial data"""
    caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert caso_response.status_code == 200
    assert caso_response.json is not None
    caso_id = caso_response.json["id"]

    processo_data = {"especie": "Ação Trabalhista", "numero": 999999, "status": True}

    create_response = client.post(
        f"/api/caso/{caso_id}/processos", json=processo_data, headers=auth_headers
    )
    assert create_response.status_code == 200
    assert create_response.json is not None
    processo_id = create_response.json["id"]

    # Update only specific fields
    update_data = {"probabilidade": "Alta", "posicao_assistido": "Autor"}

    response = client.put(
        f"/api/caso/{caso_id}/processos/{processo_id}",
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["probabilidade"] == "Alta"
    assert data["posicao_assistido"] == "Autor"
    assert data["especie"] == "Ação Trabalhista"  # Original value preserved


def test_processo_with_all_optional_fields(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    """Test processo creation with all optional fields populated"""
    caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert caso_response.status_code == 200
    assert caso_response.json is not None
    caso_id = caso_response.json["id"]

    processo_data = {
        "especie": "Ação Completa",
        "numero": 1112223344,
        "identificacao": "ID-2024-001",
        "vara": "1ª Vara Cível",
        "link": "https://processo.exemplo.com/111222",
        "probabilidade": "Média",
        "posicao_assistido": "Réu",
        "valor_causa_inicial": 10000,
        "valor_causa_atual": 15000,
        "data_distribuicao": "2024-01-01",
        "data_transito_em_julgado": None,
        "obs": "Processo aguardando julgamento",
        "status": True,
    }

    response = client.post(
        f"/api/caso/{caso_id}/processos", json=processo_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["especie"] == "Ação Completa"
    assert data["identificacao"] == "ID-2024-001"
    assert data["vara"] == "1ª Vara Cível"
    assert data["obs"] == "Processo aguardando julgamento"


def test_delete_processo(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    """Test processo deletion (soft delete)"""
    caso_response = client.post(
        "/api/caso/", json=sample_caso_data, headers=auth_headers
    )
    assert caso_response.status_code == 200
    assert caso_response.json is not None
    caso_id = caso_response.json["id"]

    processo_data = {"especie": "Ação a Deletar", "status": True}

    create_response = client.post(
        f"/api/caso/{caso_id}/processos", json=processo_data, headers=auth_headers
    )
    assert create_response.status_code == 200
    assert create_response.json is not None
    processo_id = create_response.json["id"]

    # Delete processo
    delete_response = client.delete(
        f"/api/caso/{caso_id}/processos/{processo_id}", headers=auth_headers
    )

    assert delete_response.status_code == 200
