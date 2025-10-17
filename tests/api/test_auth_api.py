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


def test_setup_admin_success(client: FlaskClient, clean_db: None) -> None:
    """Test successful admin creation when no users exist."""
    response = client.post(
        "/api/auth/setup-admin",
        json={
            "email": "newadmin@example.com",
            "password": "secure-password-123",
            "setup_token": "test-setup-token-12345",
        },
    )

    assert response.status_code == 201
    assert response.json is not None
    assert "token" in response.json
    assert "user" in response.json
    assert response.json["user"]["email"] == "newadmin@example.com"
    assert response.json["user"]["urole"] == "admin"


def test_setup_admin_missing_email(client: FlaskClient, clean_db: None) -> None:
    """Test setup-admin with missing email field."""
    response = client.post(
        "/api/auth/setup-admin",
        json={
            "password": "secure-password-123",
            "setup_token": "test-setup-token-12345",
        },
    )

    assert response.status_code == 400
    assert response.json is not None
    assert "error" in response.json


def test_setup_admin_missing_password(client: FlaskClient, clean_db: None) -> None:
    """Test setup-admin with missing password field."""
    response = client.post(
        "/api/auth/setup-admin",
        json={
            "email": "newadmin@example.com",
            "setup_token": "test-setup-token-12345",
        },
    )

    assert response.status_code == 400
    assert response.json is not None
    assert "error" in response.json


def test_setup_admin_missing_token(client: FlaskClient, clean_db: None) -> None:
    """Test setup-admin with missing setup_token field."""
    response = client.post(
        "/api/auth/setup-admin",
        json={
            "email": "newadmin@example.com",
            "password": "secure-password-123",
        },
    )

    assert response.status_code == 400
    assert response.json is not None
    assert "error" in response.json


def test_setup_admin_invalid_token(client: FlaskClient, clean_db: None) -> None:
    """Test setup-admin with incorrect setup token."""
    response = client.post(
        "/api/auth/setup-admin",
        json={
            "email": "newadmin@example.com",
            "password": "secure-password-123",
            "setup_token": "wrong-token",
        },
    )

    assert response.status_code == 403
    assert response.json is not None
    assert "error" in response.json
    assert "Invalid setup token" in response.json["error"]


def test_setup_admin_users_already_exist(client: FlaskClient, clean_db: None) -> None:
    """Test that setup-admin fails when users already exist."""
    # Create the first admin via setup endpoint
    first_response = client.post(
        "/api/auth/setup-admin",
        json={
            "email": "firstadmin@example.com",
            "password": "password123",
            "setup_token": "test-setup-token-12345",
        },
    )
    assert first_response.status_code == 201

    # Try to create another admin - should fail
    response = client.post(
        "/api/auth/setup-admin",
        json={
            "email": "newadmin@example.com",
            "password": "secure-password-123",
            "setup_token": "test-setup-token-12345",
        },
    )

    assert response.status_code == 403
    assert response.json is not None
    assert "error" in response.json
    assert "already exists" in response.json["error"]


def test_setup_admin_can_login_after_creation(client: FlaskClient, clean_db: None) -> None:
    """Test that the created admin can successfully login."""
    # Create admin via setup endpoint
    setup_response = client.post(
        "/api/auth/setup-admin",
        json={
            "email": "logintest@example.com",
            "password": "mypassword123",
            "setup_token": "test-setup-token-12345",
        },
    )

    assert setup_response.status_code == 201

    # Try to login with the created admin
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "logintest@example.com",
            "password": "mypassword123",
        },
    )

    assert login_response.status_code == 200
    assert login_response.json is not None
    assert "token" in login_response.json
