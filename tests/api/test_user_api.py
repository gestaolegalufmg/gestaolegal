import random
from typing import Any

from flask.testing import FlaskClient

from .conftest import TEST_NON_ADMIN_EMAIL


def test_create_user_success(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    response = client.post("/api/user/", json=sample_user_data, headers=auth_headers)

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


def test_admin_routes_forbid_non_admin_user(
    client: FlaskClient, non_admin_auth_headers: dict[str, str]
) -> None:
    response = client.get("/api/user/", headers=non_admin_auth_headers)

    assert response.status_code == 403


def test_get_user_by_id(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    sample_user_data["id"] = random.randint(1, 1000000)
    sample_user_data["email"] = f"getbyid{sample_user_data['id']}@gl.com"
    create_response = client.post(
        "/api/user/", json=sample_user_data, headers=auth_headers
    )

    assert create_response.status_code == 200
    assert create_response.json is not None
    user_id = create_response.json["id"]

    response = client.get(f"/api/user/{user_id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["nome"] == sample_user_data["nome"]
    assert data["email"] == sample_user_data["email"]
    assert data["id"] == user_id


def test_get_user_not_found(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    response = client.get("/api/user/99999", headers=auth_headers)

    assert response.status_code == 404


def test_update_user(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    sample_user_data["id"] = random.randint(1, 1000000)
    sample_user_data["email"] = f"updateuser{sample_user_data['id']}@gl.com"
    create_response = client.post(
        "/api/user/", json=sample_user_data, headers=auth_headers
    )
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
    assert data["email"] == sample_user_data["email"]


def test_delete_user(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    sample_user_data["id"] = random.randint(1, 1000000)
    sample_user_data["email"] = f"deleteuser{sample_user_data['id']}@gl.com"

    create_response = client.post(
        "/api/user/", json=sample_user_data, headers=auth_headers
    )
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


def test_search_users(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    sample_user_data["id"] = random.randint(1, 1000000)
    sample_user_data["email"] = f"searchuser{sample_user_data['id']}@gl.com"
    sample_user_data["nome"] = f"Searchable User {sample_user_data['id']}"

    client.post("/api/user/", json=sample_user_data, headers=auth_headers)

    response = client.get("/api/user/?search=Searchable", headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0
    found_user = next(
        (
            u
            for u in data["items"]
            if u["nome"] == f"Searchable User {sample_user_data['id']}"
        ),
        None,
    )
    assert found_user is not None


def test_user_creation_with_all_roles(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    roles = ["admin", "colab_proj", "orient", "estag_direito", "colab_ext"]

    for idx, role in enumerate(roles):
        sample_user_data["id"] = random.randint(1, 1000000)
        sample_user_data["email"] = f"allrolesuser{sample_user_data['id']}@gl.com"
        sample_user_data["nome"] = f"All Roles User {sample_user_data['id']}"
        user_data = {**sample_user_data, "urole": role}

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


def test_get_me_endpoint_non_admin(
    client: FlaskClient, non_admin_auth_headers: dict[str, str]
) -> None:
    response = client.get("/api/user/me", headers=non_admin_auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["email"] == TEST_NON_ADMIN_EMAIL


def test_change_password(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    sample_user_data["id"] = random.randint(1, 1000000)
    sample_user_data["email"] = f"changepassworduser{sample_user_data['id']}@gl.com"

    create_response = client.post(
        "/api/user/", json=sample_user_data, headers=auth_headers
    )
    assert create_response.status_code == 200
    assert create_response.json is not None
    user_id = create_response.json["id"]

    password_data = {"newPassword": "newPassword123", "fromAdmin": True}

    response = client.put(
        f"/api/user/{user_id}/password", json=password_data, headers=auth_headers
    )

    assert response.status_code == 200


def test_update_user_without_changes(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    sample_user_data["id"] = random.randint(1, 1000000)
    sample_user_data["email"] = f"nochangesuser{sample_user_data['id']}@gl.com"
    sample_user_data["nome"] = f"No Changes User {sample_user_data['id']}"

    create_response = client.post(
        "/api/user/", json=sample_user_data, headers=auth_headers
    )
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
    assert data["nome"] == f"No Changes User {sample_user_data['id']}"
    assert data["email"] == sample_user_data["email"]
    assert data["id"] == user_id


def test_update_user_partial_data(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    sample_user_data["id"] = random.randint(1, 1000000)
    sample_user_data["email"] = f"partialupdateuser{sample_user_data['id']}@gl.com"
    sample_user_data["nome"] = f"Partial Update User {sample_user_data['id']}"

    create_response = client.post(
        "/api/user/", json=sample_user_data, headers=auth_headers
    )
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
    assert data["nome"] == f"Partial Update User {sample_user_data['id']}"
    assert data["email"] == sample_user_data["email"]
    assert data["id"] == user_id


def test_update_user_address(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    sample_user_data["id"] = random.randint(1, 1000000)
    sample_user_data["email"] = f"addressupdateuser{sample_user_data['id']}@gl.com"
    sample_user_data["nome"] = f"Address Update User {sample_user_data['id']}"

    create_response = client.post(
        "/api/user/", json=sample_user_data, headers=auth_headers
    )
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
    assert data["nome"] == f"Address Update User {sample_user_data['id']}"
    assert data["endereco"]["logradouro"] == "Rua Atualizada"
    assert data["endereco"]["numero"] == "200"
    assert data["endereco"]["bairro"] == "Savassi"
    assert data["endereco"]["cidade"] == "Belo Horizonte"


def test_user_show_inactive_filter(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    sample_user_data["id"] = random.randint(1, 1000000)
    sample_user_data["email"] = f"activeuser{sample_user_data['id']}@gl.com"
    sample_user_data["nome"] = f"Active User {sample_user_data['id']}"

    active_response = client.post(
        "/api/user/", json=sample_user_data, headers=auth_headers
    )
    assert active_response.status_code == 200
    assert active_response.json is not None
    active_user_id = active_response.json["id"]

    inactive_user_data = {**sample_user_data, "status": False}
    inactive_user_data["email"] = f"inactiveuser{inactive_user_data['id']}@gl.com"
    inactive_user_data["nome"] = f"Inactive User {inactive_user_data['id']}"

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


def test_user_creation_with_complemento_as_empty_string(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    """Test that complemento can be empty string (backend should handle it)"""
    sample_user_data["id"] = random.randint(1, 1000000)
    sample_user_data["email"] = f"emptycomplemento{sample_user_data['id']}@gl.com"
    sample_user_data["complemento"] = ""

    response = client.post("/api/user/", json=sample_user_data, headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert "id" in data


def test_user_creation_with_complemento_as_null(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    """Test that complemento can be null"""
    sample_user_data["id"] = random.randint(1, 1000000)
    sample_user_data["email"] = f"nullcomplemento{sample_user_data['id']}@gl.com"
    sample_user_data["complemento"] = None

    response = client.post("/api/user/", json=sample_user_data, headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert "id" in data


def test_bolsista_requires_bolsa_fields(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    """Test that when bolsista=true, tipo_bolsa, inicio_bolsa, fim_bolsa are required"""
    sample_user_data["id"] = random.randint(1, 1000000)
    sample_user_data["email"] = f"bolsistatest{sample_user_data['id']}@gl.com"
    sample_user_data["bolsista"] = True
    sample_user_data["tipo_bolsa"] = "integral"
    sample_user_data["inicio_bolsa"] = "2024-01-01"
    sample_user_data["fim_bolsa"] = "2024-12-31"

    response = client.post("/api/user/", json=sample_user_data, headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["bolsista"] is True
    assert data["tipo_bolsa"] == "integral"


def test_non_bolsista_without_bolsa_fields(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    """Test that when bolsista=false, bolsa fields can be null"""
    sample_user_data["id"] = random.randint(1, 1000000)
    sample_user_data["email"] = f"nonbolsista{sample_user_data['id']}@gl.com"
    sample_user_data["bolsista"] = False
    sample_user_data["tipo_bolsa"] = None
    sample_user_data["inicio_bolsa"] = None
    sample_user_data["fim_bolsa"] = None

    response = client.post("/api/user/", json=sample_user_data, headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["bolsista"] is False


def test_user_update_with_individual_address_fields(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    """Test that address update works with individual fields, not Endereco object"""
    sample_user_data["id"] = random.randint(1, 1000000)
    sample_user_data["email"] = f"addressfields{sample_user_data['id']}@gl.com"

    create_response = client.post(
        "/api/user/", json=sample_user_data, headers=auth_headers
    )
    assert create_response.status_code == 200
    assert create_response.json is not None
    user_id = create_response.json["id"]

    # Update with individual address fields
    update_data = {
        "logradouro": "Nova Rua",
        "numero": "999",
        "complemento": "Apto 101",
        "bairro": "Novo Bairro",
        "cep": "99999-999",
        "cidade": "Nova Cidade",
        "estado": "SP",
    }
    response = client.put(
        f"/api/user/{user_id}", json=update_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert data["endereco"]["logradouro"] == "Nova Rua"
    assert data["endereco"]["numero"] == "999"
    assert data["endereco"]["complemento"] == "Apto 101"
    assert data["endereco"]["bairro"] == "Novo Bairro"
    assert data["endereco"]["cep"] == "99999-999"
    assert data["endereco"]["cidade"] == "Nova Cidade"
    assert data["endereco"]["estado"] == "SP"
