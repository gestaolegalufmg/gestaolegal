from flask.testing import FlaskClient


def test_login_success(client: FlaskClient, create_admin_user: None) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@gl.com", "password": "123456"},
    )

    assert response.status_code == 200
    assert response.json is not None


def test_login_wrong_password(client: FlaskClient, create_admin_user: None) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@gl.com", "password": "wrong_password"},
    )

    assert response.status_code == 401


def test_login_wrong_email(client: FlaskClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.com", "password": "123456"},
    )

    assert response.status_code == 401


def test_login_missing_email(client: FlaskClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"password": "123456"},
    )

    assert response.status_code == 400


def test_login_missing_password(client: FlaskClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@gl.com"},
    )

    assert response.status_code == 400


def test_login_empty_payload(client: FlaskClient) -> None:
    response = client.post("/api/auth/login", json={})

    assert response.status_code == 400


def test_api_requires_authentication(client: FlaskClient) -> None:
    response = client.get("/api/atendido/")

    assert response.status_code == 401


def test_api_accepts_authenticated_request(
    client: FlaskClient, auth_headers: dict[str, str]
) -> None:
    response = client.get("/api/atendido/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json
    assert data is not None
    assert isinstance(data, (dict, list))
