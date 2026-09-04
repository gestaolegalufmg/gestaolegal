import random
from typing import Any

from flask.testing import FlaskClient

from tests.api.conftest import assert_success_response, get_success_data

from .conftest import TEST_NON_ADMIN_EMAIL


def _create_user(
    client: FlaskClient,
    auth_headers: dict[str, str],
    user_payload: dict[str, Any],
):
    response = client.post("/api/user/", json=user_payload, headers=auth_headers)
    assert response.status_code == 201
    data = get_success_data(response)
    assert data is not None
    return data


def test_create_user_success(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    data = _create_user(client, auth_headers, sample_user_data)
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
    created_user = _create_user(client, auth_headers, sample_user_data)
    user_id = created_user["id"]

    response = client.get(f"/api/user/{user_id}", headers=auth_headers)

    assert response.status_code == 200
    data = get_success_data(response)
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
    created_user = _create_user(client, auth_headers, sample_user_data)
    user_id = created_user["id"]

    update_data = {"nome": "Updated Name", "profissao": "Advogado"}
    response = client.put(
        f"/api/user/{user_id}", json=update_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = get_success_data(response)
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

    created_user = _create_user(client, auth_headers, sample_user_data)
    user_id = created_user["id"]

    response = client.delete(f"/api/user/{user_id}", headers=auth_headers)

    assert response.status_code == 200
    assert_success_response(response)

    get_response = client.get(f"/api/user/{user_id}", headers=auth_headers)
    assert get_response.status_code == 200
    data = get_success_data(get_response)
    assert data is not None
    assert data["status"] is False


def test_search_users(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    sample_user_data["id"] = random.randint(1, 1000000)
    sample_user_data["email"] = f"searchuser{sample_user_data['id']}@gl.com"
    sample_user_data["nome"] = f"Searchable User {sample_user_data['id']}"

    _create_user(client, auth_headers, sample_user_data)

    response = client.get("/api/user/?search=Searchable", headers=auth_headers)

    assert response.status_code == 200
    data = get_success_data(response)
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

        data = _create_user(client, auth_headers, user_data)
        assert data is not None, f"Failed to create user with role {role}"
        assert data["urole"] == role
        assert "id" in data
        assert isinstance(data["id"], int)


def test_get_me_endpoint(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    response = client.get("/api/user/me", headers=auth_headers)

    assert response.status_code == 200
    data = get_success_data(response)
    assert data is not None
    assert "id" in data
    assert "email" in data
    assert "nome" in data


def test_get_me_devolve_unidades(
    client: FlaskClient, auth_headers: dict[str, str]
) -> None:
    response = client.get("/api/user/me", headers=auth_headers)

    assert response.status_code == 200
    data = get_success_data(response)
    assert [u["sigla"] for u in data["unidades"]] == ["BH", "NL"]


def test_get_me_unidades_apenas_das_vinculadas(
    client: FlaskClient, non_admin_auth_headers: dict[str, str]
) -> None:
    """Usuário comum só enxerga a unidade a que está vinculado."""
    response = client.get("/api/user/me", headers=non_admin_auth_headers)

    assert response.status_code == 200
    data = get_success_data(response)
    assert [u["sigla"] for u in data["unidades"]] == ["BH"]


def test_get_me_endpoint_non_admin(
    client: FlaskClient, non_admin_auth_headers: dict[str, str]
) -> None:
    response = client.get("/api/user/me", headers=non_admin_auth_headers)

    assert response.status_code == 200
    data = get_success_data(response)
    assert data is not None
    assert data["email"] == TEST_NON_ADMIN_EMAIL


def test_change_password(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    sample_user_data["id"] = random.randint(1, 1000000)
    sample_user_data["email"] = f"changepassworduser{sample_user_data['id']}@gl.com"

    created_user = _create_user(client, auth_headers, sample_user_data)
    user_id = created_user["id"]

    password_data = {"newPassword": "newPassword123", "fromAdmin": True}

    response = client.put(
        f"/api/user/{user_id}/password", json=password_data, headers=auth_headers
    )

    assert response.status_code == 200
    assert_success_response(response)


def test_update_user_without_changes(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    sample_user_data["id"] = random.randint(1, 1000000)
    sample_user_data["email"] = f"nochangesuser{sample_user_data['id']}@gl.com"
    sample_user_data["nome"] = f"No Changes User {sample_user_data['id']}"

    created_user = _create_user(client, auth_headers, sample_user_data)
    user_id = created_user["id"]

    update_data = {}
    response = client.put(
        f"/api/user/{user_id}", json=update_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = get_success_data(response)
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

    created_user = _create_user(client, auth_headers, sample_user_data)
    user_id = created_user["id"]

    update_data = {"celular": "(11) 91111-2222"}
    response = client.put(
        f"/api/user/{user_id}", json=update_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = get_success_data(response)
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

    created_user = _create_user(client, auth_headers, sample_user_data)
    user_id = created_user["id"]

    update_data = {
        "logradouro": "Rua Atualizada",
        "numero": "200",
        "bairro": "Savassi",
    }
    response = client.put(
        f"/api/user/{user_id}", json=update_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = get_success_data(response)
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

    active_user = _create_user(client, auth_headers, sample_user_data)
    active_user_id = active_user["id"]

    inactive_user_data = {**sample_user_data, "status": False}
    inactive_user_data["email"] = f"inactiveuser{inactive_user_data['id']}@gl.com"
    inactive_user_data["nome"] = f"Inactive User {inactive_user_data['id']}"

    inactive_user = _create_user(client, auth_headers, inactive_user_data)
    inactive_user_id = inactive_user["id"]

    delete_response = client.delete(
        f"/api/user/{inactive_user_id}", headers=auth_headers
    )
    assert delete_response.status_code == 200
    assert_success_response(delete_response)

    search_response = client.get("/api/user/?show_inactive=false", headers=auth_headers)
    assert search_response.status_code == 200
    data = get_success_data(search_response)
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

    data = _create_user(client, auth_headers, sample_user_data)
    assert "id" in data


def test_user_creation_with_complemento_as_null(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    """Test that complemento can be null"""
    sample_user_data["id"] = random.randint(1, 1000000)
    sample_user_data["email"] = f"nullcomplemento{sample_user_data['id']}@gl.com"
    sample_user_data["complemento"] = None

    data = _create_user(client, auth_headers, sample_user_data)
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

    data = _create_user(client, auth_headers, sample_user_data)
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

    data = _create_user(client, auth_headers, sample_user_data)
    assert data["bolsista"] is False


def test_user_update_with_individual_address_fields(
    client: FlaskClient, auth_headers: dict[str, str], sample_user_data: dict[str, Any]
) -> None:
    """Test that address update works with individual fields, not Endereco object"""
    sample_user_data["id"] = random.randint(1, 1000000)
    sample_user_data["email"] = f"addressfields{sample_user_data['id']}@gl.com"

    created_user = _create_user(client, auth_headers, sample_user_data)
    user_id = created_user["id"]

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
    data = get_success_data(response)
    assert data is not None
    assert data["endereco"]["logradouro"] == "Nova Rua"
    assert data["endereco"]["numero"] == "999"
    assert data["endereco"]["complemento"] == "Apto 101"
    assert data["endereco"]["bairro"] == "Novo Bairro"
    assert data["endereco"]["cep"] == "99999-999"
    assert data["endereco"]["cidade"] == "Nova Cidade"
    assert data["endereco"]["estado"] == "SP"


class TestUserOpcoes:
    def test_lista_usuarios_ativos_para_qualquer_autenticado(self, client, estagiario_auth_headers):
        data = get_success_data(client.get("/api/user/opcoes", headers=estagiario_auth_headers))
        nomes = [u["nome"] for u in data["items"]]
        assert len(nomes) >= 2
        assert nomes == sorted(nomes)
        assert {"id", "nome", "urole"} <= set(data["items"][0].keys())

    def test_exige_autenticacao(self, client):
        assert client.get("/api/user/opcoes").status_code == 401


class TestUsuarioUnidades:
    """Vínculo usuário↔unidade no cadastro (story f4-usuario-vinculo)."""

    def _payload(self, sample_user_data: dict[str, Any]) -> dict[str, Any]:
        sample_user_data["id"] = random.randint(1, 1000000)
        sample_user_data["email"] = f"unidade{sample_user_data['id']}@gl.com"
        return sample_user_data

    def test_create_sem_unidades_e_recusado(
        self,
        client: FlaskClient,
        auth_headers: dict[str, str],
        sample_user_data: dict[str, Any],
    ) -> None:
        payload = self._payload(sample_user_data)
        payload.pop("unidade_ids")

        response = client.post("/api/user/", json=payload, headers=auth_headers)

        assert response.status_code == 400

    def test_create_com_lista_vazia_e_recusado(
        self,
        client: FlaskClient,
        auth_headers: dict[str, str],
        sample_user_data: dict[str, Any],
    ) -> None:
        payload = self._payload(sample_user_data)
        payload["unidade_ids"] = []

        response = client.post("/api/user/", json=payload, headers=auth_headers)

        assert response.status_code == 400

    def test_create_com_unidade_inexistente_e_recusado(
        self,
        client: FlaskClient,
        auth_headers: dict[str, str],
        sample_user_data: dict[str, Any],
    ) -> None:
        payload = self._payload(sample_user_data)
        payload["unidade_ids"] = [9999]

        response = client.post("/api/user/", json=payload, headers=auth_headers)

        assert response.status_code == 400

    def test_create_vincula_e_get_devolve_unidades(
        self,
        client: FlaskClient,
        auth_headers: dict[str, str],
        sample_user_data: dict[str, Any],
    ) -> None:
        payload = self._payload(sample_user_data)
        payload["unidade_ids"] = [1, 2]

        created = _create_user(client, auth_headers, payload)
        assert [u["sigla"] for u in created["unidades"]] == ["BH", "NL"]

        response = client.get(f"/api/user/{created['id']}", headers=auth_headers)

        assert response.status_code == 200
        data = get_success_data(response)
        assert [u["sigla"] for u in data["unidades"]] == ["BH", "NL"]

    def test_update_troca_o_vinculo(
        self,
        client: FlaskClient,
        auth_headers: dict[str, str],
        sample_user_data: dict[str, Any],
    ) -> None:
        payload = self._payload(sample_user_data)
        payload["unidade_ids"] = [1]
        created = _create_user(client, auth_headers, payload)

        response = client.put(
            f"/api/user/{created['id']}",
            json={"unidade_ids": [2]},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = get_success_data(response)
        assert [u["sigla"] for u in data["unidades"]] == ["NL"]

    def test_update_sem_unidade_ids_preserva_o_vinculo(
        self,
        client: FlaskClient,
        auth_headers: dict[str, str],
        sample_user_data: dict[str, Any],
    ) -> None:
        """Update parcial (só o nome) não pode zerar as unidades."""
        payload = self._payload(sample_user_data)
        payload["unidade_ids"] = [1, 2]
        created = _create_user(client, auth_headers, payload)

        response = client.put(
            f"/api/user/{created['id']}",
            json={"nome": "Nome Trocado"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = get_success_data(response)
        assert data["nome"] == "Nome Trocado"
        assert [u["sigla"] for u in data["unidades"]] == ["BH", "NL"]

    def test_update_com_lista_vazia_e_recusado(
        self,
        client: FlaskClient,
        auth_headers: dict[str, str],
        sample_user_data: dict[str, Any],
    ) -> None:
        payload = self._payload(sample_user_data)
        created = _create_user(client, auth_headers, payload)

        response = client.put(
            f"/api/user/{created['id']}",
            json={"unidade_ids": []},
            headers=auth_headers,
        )

        assert response.status_code == 400
        depois = get_success_data(
            client.get(f"/api/user/{created['id']}", headers=auth_headers)
        )
        assert [u["sigla"] for u in depois["unidades"]] == ["BH"]

    def test_admin_nao_remove_a_propria_ultima_unidade(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        eu = get_success_data(client.get("/api/user/me", headers=auth_headers))

        response = client.put(
            f"/api/user/{eu['id']}",
            json={"unidade_ids": []},
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "última unidade" in response.get_json()["error"]["message"]

        depois = get_success_data(client.get("/api/user/me", headers=auth_headers))
        assert [u["sigla"] for u in depois["unidades"]] == ["BH", "NL"]

    def test_update_me_ignora_unidade_ids(
        self, client: FlaskClient, non_admin_auth_headers: dict[str, str]
    ) -> None:
        """Usuário comum não se auto-vincula a outra unidade pelo próprio perfil."""
        response = client.put(
            "/api/user/me",
            json={"unidade_ids": [1, 2]},
            headers=non_admin_auth_headers,
        )

        assert response.status_code == 200
        data = get_success_data(response)
        assert [u["sigla"] for u in data["unidades"]] == ["BH"]
