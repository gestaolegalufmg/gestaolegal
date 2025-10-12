from flask.testing import FlaskClient


def test_create_user_success(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    user_data = {
        "email": "test.user@gl.com",
        "nome": "Test User",
        "urole": "estag_direito",
        "sexo": "F",
        "rg": "98.765.432-1",
        "cpf": "987.654.321-00",
        "profissao": "Estagiário",
        "estado_civil": "solteiro",
        "nascimento": "1995-05-15",
        "telefone": "(11) 3333-4444",
        "celular": "(11) 99876-5432",
        "oab": None,
        "obs": None,
        "data_entrada": "2024-01-15",
        "data_saida": None,
        "matricula": "EST001",
        "bolsista": True,
        "tipo_bolsa": "integral",
        "horario_atendimento": "08:00-12:00",
        "suplente": None,
        "ferias": None,
        "cert_atuacao_DAJ": "sim",
        "inicio_bolsa": "2024-01-15T00:00:00",
        "fim_bolsa": None,
        "logradouro": "Rua Teste User",
        "numero": "456",
        "bairro": "Centro",
        "cep": "30000-111",
        "cidade": "Belo Horizonte",
        "estado": "MG",
        "complemento": None,
    }

    response = client.post("/api/user/", json=user_data, headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["nome"] == "Test User"
    assert data["email"] == "test.user@gl.com"
    assert data["urole"] == "estag_direito"
    assert "id" in data
    assert isinstance(data["id"], int)
    assert data["status"] is True


def test_create_user_requires_auth(client: FlaskClient) -> None:
    user_data = {
        "email": "unauthorized@gl.com",
        "nome": "Unauthorized User",
        "urole": "estag_direito",
    }

    response = client.post("/api/user/", json=user_data)

    assert response.status_code == 401


def test_get_user_by_id(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    user_data = {
        "email": "getbyid@gl.com",
        "nome": "Get By ID User",
        "urole": "estag_direito",
        "sexo": "M",
        "rg": "11.111.111-1",
        "cpf": "111.111.111-11",
        "profissao": "Estudante",
        "estado_civil": "solteiro",
        "nascimento": "1996-06-20",
        "celular": "(11) 91111-1111",
        "data_entrada": "2024-02-01",
        "bolsista": False,
        "cert_atuacao_DAJ": "nao",
        "logradouro": "Rua Get",
        "numero": "789",
        "bairro": "Test",
        "cep": "30000-222",
        "cidade": "Belo Horizonte",
        "estado": "MG",
    }

    create_response = client.post("/api/user/", json=user_data, headers=auth_headers)
    assert create_response.status_code == 200
    assert create_response.json is not None
    user_id = create_response.json["id"]

    response = client.get(f"/api/user/{user_id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["nome"] == "Get By ID User"
    assert data["email"] == "getbyid@gl.com"
    assert data["id"] == user_id


def test_get_user_not_found(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    response = client.get("/api/user/99999", headers=auth_headers)

    assert response.status_code == 404


def test_update_user(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    user_data = {
        "email": "update.test@gl.com",
        "nome": "Update Test User",
        "urole": "estag_direito",
        "sexo": "F",
        "rg": "22.222.222-2",
        "cpf": "222.222.222-22",
        "profissao": "Estagiário",
        "estado_civil": "solteiro",
        "nascimento": "1997-07-25",
        "celular": "(11) 92222-2222",
        "data_entrada": "2024-03-01",
        "bolsista": True,
        "cert_atuacao_DAJ": "sim",
        "logradouro": "Rua Update",
        "numero": "321",
        "bairro": "Test",
        "cep": "30000-333",
        "cidade": "Belo Horizonte",
        "estado": "MG",
    }

    create_response = client.post("/api/user/", json=user_data, headers=auth_headers)
    assert create_response.status_code == 200
    assert create_response.json is not None
    user_id = create_response.json["id"]

    update_data = {"nome": "Updated Name", "profissao": "Advogado"}
    response = client.put(
        f"/api/user/{user_id}", json=update_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["nome"] == "Updated Name"
    assert data["profissao"] == "Advogado"
    assert data["id"] == user_id
    assert data["email"] == "update.test@gl.com"


def test_delete_user(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    user_data = {
        "email": "delete.test@gl.com",
        "nome": "Delete Test User",
        "urole": "estag_direito",
        "sexo": "M",
        "rg": "33.333.333-3",
        "cpf": "333.333.333-33",
        "profissao": "Estagiário",
        "estado_civil": "solteiro",
        "nascimento": "1998-08-30",
        "celular": "(11) 93333-3333",
        "data_entrada": "2024-04-01",
        "bolsista": False,
        "cert_atuacao_DAJ": "nao",
        "logradouro": "Rua Delete",
        "numero": "654",
        "bairro": "Test",
        "cep": "30000-444",
        "cidade": "Belo Horizonte",
        "estado": "MG",
    }

    create_response = client.post("/api/user/", json=user_data, headers=auth_headers)
    assert create_response.status_code == 200
    assert create_response.json is not None
    user_id = create_response.json["id"]

    response = client.delete(f"/api/user/{user_id}", headers=auth_headers)

    assert response.status_code == 200

    get_response = client.get(f"/api/user/{user_id}", headers=auth_headers)
    assert get_response.status_code == 200
    data = get_response.json
    assert data is not None
    assert data["status"] is False


def test_search_users(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    user_data = {
        "email": "search.test@gl.com",
        "nome": "Searchable User Test",
        "urole": "estag_direito",
        "sexo": "F",
        "rg": "44.444.444-4",
        "cpf": "444.444.444-44",
        "profissao": "Estagiário",
        "estado_civil": "solteiro",
        "nascimento": "1999-09-15",
        "celular": "(11) 94444-4444",
        "data_entrada": "2024-05-01",
        "bolsista": True,
        "cert_atuacao_DAJ": "sim",
        "logradouro": "Rua Search",
        "numero": "987",
        "bairro": "Test",
        "cep": "30000-555",
        "cidade": "Belo Horizonte",
        "estado": "MG",
    }

    client.post("/api/user/", json=user_data, headers=auth_headers)

    response = client.get("/api/user/?search=Searchable", headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0
    found_user = next(
        (u for u in data["items"] if u["nome"] == "Searchable User Test"), None
    )
    assert found_user is not None


def test_user_creation_with_all_roles(
    client: FlaskClient, auth_headers: dict[str, str]
) -> None:
    roles = ["admin", "colab_proj", "orient", "estag_direito", "colab_ext"]

    for idx, role in enumerate(roles):
        user_data = {
            "email": f"{role}.test@gl.com",
            "nome": f"{role.title()} User",
            "urole": role,
            "sexo": "M",
            "rg": f"{idx}{idx}.{idx}{idx}{idx}.{idx}{idx}{idx}-{idx}",
            "cpf": f"{idx}{idx}{idx}.{idx}{idx}{idx}.{idx}{idx}{idx}-{idx}{idx}",
            "profissao": "Test",
            "estado_civil": "solteiro",
            "nascimento": "1990-01-01",
            "celular": f"(11) 9{idx}{idx}{idx}{idx}-{idx}{idx}{idx}{idx}",
            "data_entrada": "2024-01-01",
            "bolsista": False,
            "cert_atuacao_DAJ": "nao",
            "logradouro": "Rua Test",
            "numero": "1",
            "bairro": "Test",
            "cep": "30000-000",
            "cidade": "Belo Horizonte",
            "estado": "MG",
        }

        response = client.post("/api/user/", json=user_data, headers=auth_headers)

        assert response.status_code == 200, f"Failed to create user with role {role}"
        data = response.json
        assert data is not None
        assert data["urole"] == role
        assert "id" in data
        assert isinstance(data["id"], int)


def test_get_me_endpoint(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    response = client.get("/api/user/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert "id" in data
    assert "email" in data
    assert "nome" in data


def test_change_password(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    user_data = {
        "email": "password.test@gl.com",
        "nome": "Password Test User",
        "urole": "estag_direito",
        "sexo": "M",
        "rg": "55.555.555-5",
        "cpf": "555.555.555-55",
        "profissao": "Test",
        "estado_civil": "solteiro",
        "nascimento": "1990-01-01",
        "celular": "(11) 95555-5555",
        "data_entrada": "2024-01-01",
        "bolsista": False,
        "cert_atuacao_DAJ": "nao",
        "logradouro": "Rua Test",
        "numero": "1",
        "bairro": "Test",
        "cep": "30000-000",
        "cidade": "Belo Horizonte",
        "estado": "MG",
    }

    create_response = client.post("/api/user/", json=user_data, headers=auth_headers)
    assert create_response.status_code == 200
    assert create_response.json is not None
    user_id = create_response.json["id"]

    password_data = {"newPassword": "newPassword123", "fromAdmin": True}

    response = client.put(
        f"/api/user/{user_id}/password", json=password_data, headers=auth_headers
    )

    assert response.status_code == 200


def test_update_user_without_changes(
    client: FlaskClient, auth_headers: dict[str, str]
) -> None:
    user_data = {
        "email": "nochanges.test@gl.com",
        "nome": "No Changes User",
        "urole": "estag_direito",
        "sexo": "F",
        "rg": "88.888.888-8",
        "cpf": "888.888.888-88",
        "profissao": "Estagiário",
        "estado_civil": "solteiro",
        "nascimento": "1995-05-15",
        "celular": "(11) 98888-8888",
        "data_entrada": "2024-01-15",
        "bolsista": True,
        "cert_atuacao_DAJ": "sim",
        "logradouro": "Rua No Changes",
        "numero": "111",
        "bairro": "Centro",
        "cep": "30000-666",
        "cidade": "Belo Horizonte",
        "estado": "MG",
    }

    create_response = client.post("/api/user/", json=user_data, headers=auth_headers)
    assert create_response.status_code == 200
    assert create_response.json is not None
    user_id = create_response.json["id"]

    update_data = {}
    response = client.put(
        f"/api/user/{user_id}", json=update_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["nome"] == "No Changes User"
    assert data["email"] == "nochanges.test@gl.com"
    assert data["id"] == user_id


def test_update_user_partial_data(
    client: FlaskClient, auth_headers: dict[str, str]
) -> None:
    user_data = {
        "email": "partial.update@gl.com",
        "nome": "Partial Update User",
        "urole": "estag_direito",
        "sexo": "M",
        "rg": "99.999.999-9",
        "cpf": "999.999.999-99",
        "profissao": "Estudante",
        "estado_civil": "solteiro",
        "nascimento": "1996-06-20",
        "celular": "(11) 99999-9999",
        "data_entrada": "2024-02-01",
        "bolsista": False,
        "cert_atuacao_DAJ": "nao",
        "logradouro": "Rua Partial",
        "numero": "222",
        "bairro": "Test",
        "cep": "30000-777",
        "cidade": "Belo Horizonte",
        "estado": "MG",
    }

    create_response = client.post("/api/user/", json=user_data, headers=auth_headers)
    assert create_response.status_code == 200
    assert create_response.json is not None
    user_id = create_response.json["id"]

    update_data = {"celular": "(11) 91111-2222"}
    response = client.put(
        f"/api/user/{user_id}", json=update_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["celular"] == "(11) 91111-2222"
    assert data["nome"] == "Partial Update User"
    assert data["email"] == "partial.update@gl.com"
    assert data["id"] == user_id


def test_update_user_address(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    user_data = {
        "email": "address.update@gl.com",
        "nome": "Address Update User",
        "urole": "estag_direito",
        "sexo": "F",
        "rg": "10.101.010-1",
        "cpf": "101.010.101-01",
        "profissao": "Estudante",
        "estado_civil": "solteiro",
        "nascimento": "1997-07-07",
        "celular": "(11) 91010-1010",
        "data_entrada": "2024-03-01",
        "bolsista": False,
        "cert_atuacao_DAJ": "nao",
        "logradouro": "Rua Original",
        "numero": "100",
        "bairro": "Centro",
        "cep": "30000-888",
        "cidade": "Belo Horizonte",
        "estado": "MG",
    }

    create_response = client.post("/api/user/", json=user_data, headers=auth_headers)
    assert create_response.status_code == 200
    assert create_response.json is not None
    user_id = create_response.json["id"]

    update_data = {
        "logradouro": "Rua Atualizada",
        "numero": "200",
        "bairro": "Savassi",
    }
    response = client.put(
        f"/api/user/{user_id}", json=update_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["nome"] == "Address Update User"
    assert data["endereco"]["logradouro"] == "Rua Atualizada"
    assert data["endereco"]["numero"] == "200"
    assert data["endereco"]["bairro"] == "Savassi"
    assert data["endereco"]["cidade"] == "Belo Horizonte"


def test_user_show_inactive_filter(
    client: FlaskClient, auth_headers: dict[str, str]
) -> None:
    active_user_data = {
        "email": "active.filter@gl.com",
        "nome": "Active Filter User",
        "urole": "estag_direito",
        "sexo": "F",
        "rg": "66.666.666-6",
        "cpf": "666.666.666-66",
        "profissao": "Test",
        "estado_civil": "solteiro",
        "nascimento": "1990-01-01",
        "celular": "(11) 96666-6666",
        "data_entrada": "2024-01-01",
        "bolsista": False,
        "cert_atuacao_DAJ": "nao",
        "logradouro": "Rua Test",
        "numero": "1",
        "bairro": "Test",
        "cep": "30000-000",
        "cidade": "Belo Horizonte",
        "estado": "MG",
    }

    active_response = client.post(
        "/api/user/", json=active_user_data, headers=auth_headers
    )
    assert active_response.status_code == 200
    assert active_response.json is not None
    active_user_id = active_response.json["id"]

    inactive_user_data = {
        "email": "inactive.filter@gl.com",
        "nome": "Inactive Filter User",
        "urole": "estag_direito",
        "sexo": "M",
        "rg": "77.777.777-7",
        "cpf": "777.777.777-77",
        "profissao": "Test",
        "estado_civil": "solteiro",
        "nascimento": "1990-01-01",
        "celular": "(11) 97777-7777",
        "data_entrada": "2024-01-01",
        "bolsista": False,
        "cert_atuacao_DAJ": "nao",
        "logradouro": "Rua Test",
        "numero": "2",
        "bairro": "Test",
        "cep": "30000-000",
        "cidade": "Belo Horizonte",
        "estado": "MG",
    }

    inactive_response = client.post(
        "/api/user/", json=inactive_user_data, headers=auth_headers
    )
    assert inactive_response.status_code == 200
    assert inactive_response.json is not None
    inactive_user_id = inactive_response.json["id"]

    delete_response = client.delete(
        f"/api/user/{inactive_user_id}", headers=auth_headers
    )
    assert delete_response.status_code == 200

    search_response = client.get("/api/user/?show_inactive=false", headers=auth_headers)
    assert search_response.status_code == 200
    data = search_response.json
    assert data is not None

    user_ids = [user["id"] for user in data["items"]]
    assert active_user_id in user_ids
    assert inactive_user_id not in user_ids
