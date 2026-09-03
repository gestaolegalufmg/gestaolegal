"""Recuperação de senha por e-mail ("esqueci minha senha" da v2)."""

import re
from datetime import datetime, timedelta

import pytest
from flask.testing import FlaskClient

from gestaolegal import mail
from gestaolegal.config import Config
from tests.api.conftest import (
    assert_error_response,
    clean_tables,
    criar_usuario,
    get_success_data,
)

EMAIL = "recuperacao@gl.com"
SENHA_ANTIGA = "senhaantiga123"
SENHA_NOVA = "senhanova456"


@pytest.fixture(autouse=True)
def _limpar(app):
    with app.app_context():
        clean_tables("password_reset_tokens")
    yield


@pytest.fixture
def usuario(app) -> int:
    with app.app_context():
        return criar_usuario(EMAIL, SENHA_ANTIGA, "estag_direito", "Alvo da Recuperação")


def _pedir(client: FlaskClient, email: str):
    return client.post("/api/auth/forgot-password", json={"email": email})


def _token_do_email(corpo: str) -> str:
    achado = re.search(r"/redefinir-senha/([\w\-]+)", corpo)
    assert achado, f"Link de redefinição não encontrado no corpo:\n{corpo}"
    return achado.group(1)


def _pedir_e_capturar_token(client: FlaskClient, email: str = EMAIL) -> str:
    with mail.record_messages() as enviados:
        response = _pedir(client, email)
        assert response.status_code == 200, response.get_json()
        assert len(enviados) == 1
        return _token_do_email(enviados[0].body)


class TestPedido:
    def test_envia_email_com_link(self, client, usuario):
        with mail.record_messages() as enviados:
            response = _pedir(client, EMAIL)
            assert response.status_code == 200
            assert len(enviados) == 1
            mensagem = enviados[0]
            assert mensagem.recipients == [EMAIL]
            assert "Recuperação de senha" in mensagem.subject
            assert f"{Config.FRONTEND_URL}/redefinir-senha/" in mensagem.body

    def test_email_sem_conta_responde_igual_e_nao_envia(self, client, usuario):
        with mail.record_messages() as enviados:
            response = _pedir(client, "ninguem@gl.com")
            assert response.status_code == 200
            assert enviados == []

    def test_conta_desativada_responde_igual_e_nao_envia(self, client, app):
        with app.app_context():
            criar_usuario(
                "inativo@gl.com", SENHA_ANTIGA, "estag_direito", "Inativo", status=False
            )
        with mail.record_messages() as enviados:
            response = _pedir(client, "inativo@gl.com")
            assert response.status_code == 200
            assert enviados == []

    def test_mensagem_nao_revela_existencia(self, client, usuario):
        com_conta = _pedir(client, EMAIL).get_json()["message"]
        sem_conta = _pedir(client, "ninguem@gl.com").get_json()["message"]
        assert com_conta == sem_conta

    def test_email_ausente(self, client):
        response = client.post("/api/auth/forgot-password", json={})
        assert response.status_code == 400
        assert_error_response(response)

    def test_excesso_de_pedidos_para_de_enviar(self, client, usuario):
        for _ in range(Config.PASSWORD_RESET_MAX_PEDIDOS):
            _pedir(client, EMAIL)
        with mail.record_messages() as enviados:
            response = _pedir(client, EMAIL)
            assert response.status_code == 200
            assert enviados == []

    def test_pedido_novo_invalida_o_anterior(self, client, usuario):
        primeiro = _pedir_e_capturar_token(client)
        segundo = _pedir_e_capturar_token(client)
        assert primeiro != segundo
        assert (
            client.get(f"/api/auth/reset-password/{primeiro}/validate").status_code
            == 400
        )
        assert (
            client.get(f"/api/auth/reset-password/{segundo}/validate").status_code == 200
        )


class TestValidacao:
    def test_token_valido(self, client, usuario):
        token = _pedir_e_capturar_token(client)
        response = client.get(f"/api/auth/reset-password/{token}/validate")
        assert get_success_data(response) == {"valid": True}

    def test_token_inexistente(self, client, usuario):
        response = client.get("/api/auth/reset-password/token-que-nao-existe/validate")
        assert response.status_code == 400

    def test_token_expirado(self, client, app, usuario):
        import hashlib

        from gestaolegal.repositories.password_reset_repository import (
            PasswordResetRepository,
        )

        token = "token-vencido"
        with app.app_context():
            repo = PasswordResetRepository()
            repo.create(
                usuario,
                hashlib.sha256(token.encode()).hexdigest(),
                datetime.now() - timedelta(minutes=1),
            )
            repo.session.commit()
        response = client.get(f"/api/auth/reset-password/{token}/validate")
        assert response.status_code == 400


class TestRedefinicao:
    def test_troca_a_senha_e_permite_login(self, client, usuario):
        token = _pedir_e_capturar_token(client)
        response = client.post(
            "/api/auth/reset-password", json={"token": token, "password": SENHA_NOVA}
        )
        assert response.status_code == 200, response.get_json()

        assert (
            client.post(
                "/api/auth/login", json={"email": EMAIL, "password": SENHA_NOVA}
            ).status_code
            == 200
        )
        assert (
            client.post(
                "/api/auth/login", json={"email": EMAIL, "password": SENHA_ANTIGA}
            ).status_code
            == 401
        )

    def test_token_de_uso_unico(self, client, usuario):
        token = _pedir_e_capturar_token(client)
        client.post(
            "/api/auth/reset-password", json={"token": token, "password": SENHA_NOVA}
        )
        segunda = client.post(
            "/api/auth/reset-password", json={"token": token, "password": "outrasenha1"}
        )
        assert segunda.status_code == 400

    def test_senha_curta(self, client, usuario):
        token = _pedir_e_capturar_token(client)
        response = client.post(
            "/api/auth/reset-password", json={"token": token, "password": "1234"}
        )
        assert response.status_code == 400
        # Recusada a senha, o link continua valendo.
        assert (
            client.get(f"/api/auth/reset-password/{token}/validate").status_code == 200
        )

    def test_token_ausente(self, client):
        response = client.post("/api/auth/reset-password", json={"password": SENHA_NOVA})
        assert response.status_code == 400
