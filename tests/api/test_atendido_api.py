from typing import Any

from flask.testing import FlaskClient

from tests.api.conftest import clean_tables


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
    clean_tables("atendidos")

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
    clean_tables("atendidos")

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
    clean_tables("atendidos")

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


def test_atendido_update_with_individual_address_fields(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
) -> None:
    """Test that atendido update works with individual address fields"""
    create_response = client.post(
        "/api/atendido/", json=sample_atendido_data, headers=auth_headers
    )
    assert create_response.json is not None
    atendido_id = create_response.json["id"]

    # Update with individual address fields
    update_data = {
        **sample_atendido_data,
        "logradouro": "Rua Atualizada",
        "numero": "999",
        "complemento": "Sala 5",
        "bairro": "Bairro Novo",
        "cep": "99999-999",
        "cidade": "Nova Cidade",
        "estado": "SP",
    }
    response = client.put(
        f"/api/atendido/{atendido_id}", json=update_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["endereco"]["logradouro"] == "Rua Atualizada"
    assert data["endereco"]["numero"] == "999"
    assert data["endereco"]["complemento"] == "Sala 5"
    assert data["endereco"]["bairro"] == "Bairro Novo"
    assert data["endereco"]["cep"] == "99999-999"
    assert data["endereco"]["cidade"] == "Nova Cidade"
    assert data["endereco"]["estado"] == "SP"


def test_atendido_date_parsing_from_string(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
) -> None:
    """Test that data_nascimento is parsed correctly from ISO string"""
    sample_atendido_data["data_nascimento"] = "1985-06-15"

    response = client.post(
        "/api/atendido/", json=sample_atendido_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    # Backend returns dates in HTTP date format (RFC 2822), not ISO
    assert "data_nascimento" in data
    assert "1985" in data["data_nascimento"]
    assert "Jun" in data["data_nascimento"] or "06" in data["data_nascimento"]


def test_atendido_conditional_orgaos_pub_requires_indicacao(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
) -> None:
    """Test that when como_conheceu is 'orgaos_pub', indicacao_orgao is stored"""
    sample_atendido_data["como_conheceu"] = "orgaos_pub"
    sample_atendido_data["indicacao_orgao"] = "Defensoria Pública"

    response = client.post(
        "/api/atendido/", json=sample_atendido_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["como_conheceu"] == "orgaos_pub"
    assert data["indicacao_orgao"] == "Defensoria Pública"


def test_atendido_conditional_procurou_outro_local(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
) -> None:
    """Test that when procurou_outro_local is 'sim', procurou_qual_local is stored"""
    sample_atendido_data["procurou_outro_local"] = "sim"
    sample_atendido_data["procurou_qual_local"] = "OAB"

    response = client.post(
        "/api/atendido/", json=sample_atendido_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["procurou_outro_local"] == "sim"
    assert data["procurou_qual_local"] == "OAB"


def test_atendido_conditional_pj_constituida_requires_cnpj(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
) -> None:
    """Test that when pj_constituida is 'sim', CNPJ is stored"""
    sample_atendido_data["pj_constituida"] = "sim"
    sample_atendido_data["cnpj"] = "12.345.678/0001-90"

    response = client.post(
        "/api/atendido/", json=sample_atendido_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["pj_constituida"] == "sim"
    assert data["cnpj"] == "12.345.678/0001-90"


def test_atendido_pj_with_representante_legal(
    client: FlaskClient,
    auth_headers: dict[str, Any],
    sample_atendido_data: dict[str, Any],
) -> None:
    """Test atendido with PJ and representante legal data"""
    sample_atendido_data["pj_constituida"] = "sim"
    sample_atendido_data["cnpj"] = "12.345.678/0001-90"
    sample_atendido_data["repres_legal"] = False
    sample_atendido_data["nome_repres_legal"] = "Maria Silva"
    sample_atendido_data["cpf_repres_legal"] = "987.654.321-00"
    sample_atendido_data["contato_repres_legal"] = "(11) 99999-9999"
    sample_atendido_data["rg_repres_legal"] = "12.345.678-9"
    sample_atendido_data["nascimento_repres_legal"] = "1980-01-01"

    response = client.post(
        "/api/atendido/", json=sample_atendido_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["repres_legal"] is False
    assert data["nome_repres_legal"] == "Maria Silva"
    assert data["cpf_repres_legal"] == "987.654.321-00"
