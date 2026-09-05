from typing import Any

from flask.testing import FlaskClient

from tests.api.conftest import assert_success_response, get_success_data


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
    assert caso_response.status_code == 201
    caso_data = get_success_data(caso_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

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

    assert response.status_code == 201
    data = get_success_data(response)
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
    assert caso_response.status_code == 201
    caso_data = get_success_data(caso_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

    processo_data = {
        "especie": "Ação Ordinária",
        "link": "https://esaj.tjmg.jus.br/processo/123456",
        "status": True,
    }

    response = client.post(
        f"/api/caso/{caso_id}/processos", json=processo_data, headers=auth_headers
    )

    assert response.status_code == 201
    data = get_success_data(response)
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
    assert caso_response.status_code == 201
    caso_data = get_success_data(caso_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

    processo_data = {"especie": "Ação Monitória", "link": "", "status": True}

    response = client.post(
        f"/api/caso/{caso_id}/processos", json=processo_data, headers=auth_headers
    )

    assert response.status_code == 201
    data = get_success_data(response)
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
    assert caso_response.status_code == 201
    caso_data = get_success_data(caso_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

    processo_data = {
        "especie": "Ação de Indenização",
        "valor_causa_inicial": 50000,
        "valor_causa_atual": 75000,
        "status": True,
    }

    response = client.post(
        f"/api/caso/{caso_id}/processos", json=processo_data, headers=auth_headers
    )

    assert response.status_code == 201
    data = get_success_data(response)
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
    assert caso_response.status_code == 201
    caso_data = get_success_data(caso_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

    processo_data = {"especie": "Ação Trabalhista", "numero": 999999, "status": True}

    create_response = client.post(
        f"/api/caso/{caso_id}/processos", json=processo_data, headers=auth_headers
    )
    assert create_response.status_code == 201
    processo_data_response = get_success_data(create_response)
    assert processo_data_response is not None
    processo_id = processo_data_response["id"]

    # Update only specific fields
    update_data = {"probabilidade": "Alta", "posicao_assistido": "Autor"}

    response = client.put(
        f"/api/caso/{caso_id}/processos/{processo_id}",
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = get_success_data(response)
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
    assert caso_response.status_code == 201
    caso_data = get_success_data(caso_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

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

    assert response.status_code == 201
    data = get_success_data(response)
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
    assert caso_response.status_code == 201
    caso_data = get_success_data(caso_response)
    assert caso_data is not None
    caso_id = caso_data["id"]

    processo_data = {"especie": "Ação a Deletar", "status": True}

    create_response = client.post(
        f"/api/caso/{caso_id}/processos", json=processo_data, headers=auth_headers
    )
    assert create_response.status_code == 201
    processo_data_response = get_success_data(create_response)
    assert processo_data_response is not None
    processo_id = processo_data_response["id"]

    # Delete processo
    delete_response = client.delete(
        f"/api/caso/{caso_id}/processos/{processo_id}", headers=auth_headers
    )

    assert delete_response.status_code == 200
    assert_success_response(delete_response)


def _criar_caso_com_processo(
    client: FlaskClient,
    headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> tuple[int, int]:
    caso_response = client.post("/api/caso/", json=sample_caso_data, headers=headers)
    assert caso_response.status_code == 201
    caso_id = get_success_data(caso_response)["id"]

    processo_response = client.post(
        f"/api/caso/{caso_id}/processos",
        json={"especie": "Ação de Nova Lima", "status": True},
        headers=headers,
    )
    assert processo_response.status_code == 201
    return caso_id, get_success_data(processo_response)["id"]


def test_processos_de_caso_de_outra_unidade_respondem_404(
    client: FlaskClient,
    auth_headers: dict[str, str],
    auth_headers_nl: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    """As seis rotas de processo recusam caso que não é da unidade ativa.

    O DELETE é @authorized("admin") e o admin tem as duas unidades: ele navega
    com uma por vez, então a guarda vale para ele igual.
    """
    caso_nl, processo_id = _criar_caso_com_processo(
        client, auth_headers_nl, sample_caso_data
    )

    colecao = f"/api/caso/{caso_nl}/processos"
    item = f"{colecao}/{processo_id}"

    assert client.get(colecao, headers=auth_headers).status_code == 404
    assert (
        client.post(
            colecao,
            json={"especie": "Tentativa de outra unidade", "status": True},
            headers=auth_headers,
        ).status_code
        == 404
    )
    assert client.get(item, headers=auth_headers).status_code == 404
    assert (
        client.put(
            item, json={"especie": "Tentativa de outra unidade"}, headers=auth_headers
        ).status_code
        == 404
    )
    assert client.delete(item, headers=auth_headers).status_code == 404


def test_processos_da_unidade_ativa_seguem_funcionando(
    client: FlaskClient,
    auth_headers_nl: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    """O mesmo caso, pela unidade em que foi aberto, responde normalmente."""
    caso_nl, processo_id = _criar_caso_com_processo(
        client, auth_headers_nl, sample_caso_data
    )

    colecao = f"/api/caso/{caso_nl}/processos"
    item = f"{colecao}/{processo_id}"

    listagem = client.get(colecao, headers=auth_headers_nl)
    assert listagem.status_code == 200
    assert get_success_data(listagem)["total"] == 1

    criacao = client.post(
        colecao,
        json={"especie": "Segunda ação", "status": True},
        headers=auth_headers_nl,
    )
    assert criacao.status_code == 201

    assert client.get(item, headers=auth_headers_nl).status_code == 200

    edicao = client.put(
        item, json={"especie": "Ação renomeada"}, headers=auth_headers_nl
    )
    assert edicao.status_code == 200
    assert get_success_data(edicao)["especie"] == "Ação renomeada"

    assert client.delete(item, headers=auth_headers_nl).status_code == 200
