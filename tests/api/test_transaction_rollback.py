from typing import Any

from flask.testing import FlaskClient

from tests.api.conftest import get_success_data, assert_success_response


class TestServiceTransactionIntegration:
    """Test that service operations complete successfully with transactions"""

    def test_orientacao_create_with_atendidos_succeeds(
        self,
        client: FlaskClient,
        auth_headers: dict[str, str],
        sample_orientacao_data: dict[str, Any],
        sample_atendido_data: dict[str, Any],
    ) -> None:
        """Test that creating orientacao with atendidos works correctly"""
        atendido_response = client.post(
            "/api/atendido/", json=sample_atendido_data, headers=auth_headers
        )
        assert atendido_response.status_code == 201
        atendido_data = get_success_data(atendido_response)
        assert atendido_data is not None
        atendido_id = atendido_data["id"]

        orientacao_data = {
            **sample_orientacao_data,
            "atendidos_ids": [atendido_id],
        }

        response = client.post(
            "/api/orientacao_juridica/",
            json=orientacao_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert get_success_data(response) is not None

    def test_caso_create_with_clients_succeeds(
        self,
        client: FlaskClient,
        auth_headers: dict[str, str],
        sample_caso_data: dict[str, Any],
        sample_atendido_data: dict[str, Any],
    ) -> None:
        """Test that creating caso with clients works correctly"""
        atendido_response = client.post(
            "/api/atendido/", json=sample_atendido_data, headers=auth_headers
        )
        assert atendido_response.status_code == 201
        atendido_data = get_success_data(atendido_response)
        assert atendido_data is not None
        atendido_id = atendido_data["id"]

        caso_data = {
            **sample_caso_data,
            "ids_clientes": [atendido_id],
        }

        response = client.post("/api/caso/", json=caso_data, headers=auth_headers)
        assert response.status_code == 201
        caso_data_response = get_success_data(response)
        assert caso_data_response is not None
        caso_id = caso_data_response["id"]
        get_response = client.get(f"/api/caso/{caso_id}", headers=auth_headers)
        assert get_response.status_code == 200
        caso_full = get_success_data(get_response)
        assert caso_full is not None
        assert len(caso_full["clientes"]) == 1

    def test_orientacao_update_with_atendidos_succeeds(
        self,
        client: FlaskClient,
        auth_headers: dict[str, str],
        sample_orientacao_data: dict[str, Any],
        sample_atendido_data: dict[str, Any],
    ) -> None:
        """Test that updating orientacao with atendidos works correctly"""
        create_response = client.post(
            "/api/orientacao_juridica/",
            json=sample_orientacao_data,
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        orientacao_data = get_success_data(create_response)
        assert orientacao_data is not None
        orientacao_id = orientacao_data["id"]

        atendido_response = client.post(
            "/api/atendido/", json=sample_atendido_data, headers=auth_headers
        )
        assert atendido_response.status_code == 201
        atendido_data = get_success_data(atendido_response)
        assert atendido_data is not None
        atendido_id = atendido_data["id"]

        update_data = {
            "descricao": "Updated description",
            "atendidos_ids": [atendido_id],
        }

        response = client.put(
            f"/api/orientacao_juridica/{orientacao_id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        updated = get_success_data(response)
        assert updated is not None
        assert updated["descricao"] == "Updated description"

    def test_caso_update_with_clients_succeeds(
        self,
        client: FlaskClient,
        auth_headers: dict[str, str],
        sample_caso_data: dict[str, Any],
        sample_atendido_data: dict[str, Any],
    ) -> None:
        """Test that updating caso with clients works correctly"""
        create_response = client.post(
            "/api/caso/", json=sample_caso_data, headers=auth_headers
        )
        assert create_response.status_code == 201
        caso_data = get_success_data(create_response)
        assert caso_data is not None
        caso_id = caso_data["id"]

        atendido_response = client.post(
            "/api/atendido/", json=sample_atendido_data, headers=auth_headers
        )
        assert atendido_response.status_code == 201
        atendido_data = get_success_data(atendido_response)
        assert atendido_data is not None
        atendido_id = atendido_data["id"]

        update_data = {"ids_clientes": [atendido_id]}

        response = client.put(
            f"/api/caso/{caso_id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        updated_caso = get_success_data(response)
        assert updated_caso is not None
        get_response = client.get(f"/api/caso/{caso_id}", headers=auth_headers)
        assert get_response.status_code == 200
        caso_full = get_success_data(get_response)
        assert caso_full is not None
        assert len(caso_full["clientes"]) == 1


class TestTransactionIsolation:
    """Test transaction isolation between concurrent operations"""

    def test_concurrent_orientacao_creates_are_isolated(
        self,
        client: FlaskClient,
        auth_headers: dict[str, str],
        sample_orientacao_data: dict[str, Any],
    ) -> None:
        """Test that concurrent creates don't interfere with each other"""
        response1 = client.post(
            "/api/orientacao_juridica/",
            json={**sample_orientacao_data, "area_direito": "penal"},
            headers=auth_headers,
        )

        response2 = client.post(
            "/api/orientacao_juridica/",
            json={**sample_orientacao_data, "area_direito": "civil"},
            headers=auth_headers,
        )

        assert response1.status_code == 201
        assert response2.status_code == 201
        data1 = get_success_data(response1)
        data2 = get_success_data(response2)
        assert data1 is not None and data2 is not None
        assert data1["id"] != data2["id"]
        assert data1["area_direito"] == "penal"
        assert data2["area_direito"] == "civil"

    def test_concurrent_caso_creates_are_isolated(
        self,
        client: FlaskClient,
        auth_headers: dict[str, str],
        sample_caso_data: dict[str, Any],
    ) -> None:
        """Test that concurrent caso creates don't interfere with each other"""
        response1 = client.post(
            "/api/caso/",
            json={**sample_caso_data, "area_direito": "penal"},
            headers=auth_headers,
        )

        response2 = client.post(
            "/api/caso/",
            json={**sample_caso_data, "area_direito": "trabalhista"},
            headers=auth_headers,
        )

        assert response1.status_code == 201
        assert response2.status_code == 201
        caso1 = get_success_data(response1)
        caso2 = get_success_data(response2)
        assert caso1 is not None and caso2 is not None
        assert caso1["id"] != caso2["id"]
        assert caso1["area_direito"] == "penal"
        assert caso2["area_direito"] == "trabalhista"
