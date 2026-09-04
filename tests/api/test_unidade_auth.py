"""Exigência do header X-Unidade-Id no decorator @authenticated (F2.4/F2.5).

Usa o usuário não admin, que pertence só a Belo Horizonte: é ele quem exercita
o 403 ao pedir Nova Lima.
"""

from flask import Flask
from flask.testing import FlaskClient

from gestaolegal.services.usuario_service import UsuarioService
from gestaolegal.utils.api_decorators import _resolver_unidade_ativa
from gestaolegal.utils.request_context import RequestContext
from tests.api.conftest import (
    TEST_ADMIN_EMAIL,
    UNIDADE_BH,
    UNIDADE_NL,
    get_success_data,
)

ROTA = "/api/atendido/"


def _sem_unidade(headers: dict[str, str]) -> dict[str, str]:
    return {k: v for k, v in headers.items() if k != "X-Unidade-Id"}


def test_sem_header_de_unidade_responde_400(
    client: FlaskClient, auth_headers: dict[str, str]
):
    response = client.get(ROTA, headers=_sem_unidade(auth_headers))

    assert response.status_code == 400
    assert "Unidade ativa não informada" in response.get_json()["error"]["message"]


def test_header_de_unidade_nao_numerico_responde_400(
    client: FlaskClient, auth_headers: dict[str, str]
):
    headers = {**auth_headers, "X-Unidade-Id": "belo-horizonte"}

    response = client.get(ROTA, headers=headers)

    assert response.status_code == 400


def test_unidade_a_que_o_usuario_nao_pertence_responde_403(
    client: FlaskClient, non_admin_auth_headers: dict[str, str], unidades: None
):
    headers = {**non_admin_auth_headers, "X-Unidade-Id": str(UNIDADE_NL)}

    response = client.get(ROTA, headers=headers)

    assert response.status_code == 403


def test_unidade_valida_responde_200(
    client: FlaskClient, auth_headers: dict[str, str], unidades: None
):
    response = client.get(ROTA, headers=auth_headers)

    assert response.status_code == 200


def test_unidade_valida_fica_no_request_context(app: Flask, auth_headers: dict[str, str]):
    """O header não só é aceito: ele é o que o resto da requisição enxerga."""
    user = UsuarioService().find_by_email(TEST_ADMIN_EMAIL)
    assert user is not None

    with app.test_request_context(headers={"X-Unidade-Id": str(UNIDADE_NL)}):
        _resolver_unidade_ativa(user)
        assert RequestContext.get_unidade_ativa() == UNIDADE_NL


def test_user_me_dispensa_o_header_e_traz_unidades(
    client: FlaskClient, auth_headers: dict[str, str], unidades: None
):
    response = client.get("/api/user/me", headers=_sem_unidade(auth_headers))

    assert response.status_code == 200
    data = get_success_data(response)
    assert sorted(u["id"] for u in data["unidades"]) == [UNIDADE_BH, UNIDADE_NL]


def test_user_opcoes_dispensa_o_header(
    client: FlaskClient, auth_headers: dict[str, str]
):
    response = client.get("/api/user/opcoes", headers=_sem_unidade(auth_headers))

    assert response.status_code == 200


def test_login_dispensa_o_header(client: FlaskClient, create_admin_user: None):
    from tests.api.conftest import TEST_ADMIN_PASSWORD

    response = client.post(
        "/api/auth/login",
        json={"email": TEST_ADMIN_EMAIL, "password": TEST_ADMIN_PASSWORD},
    )

    assert response.status_code == 200
