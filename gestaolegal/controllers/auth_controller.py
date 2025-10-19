import logging
from dataclasses import asdict
from typing import cast

from flask import Blueprint, request

from gestaolegal.config import Config
from gestaolegal.exceptions import (
    SetupException,
    UnauthorizedException,
    ValidationException,
)
from gestaolegal.services.usuario_service import UsuarioService
from gestaolegal.utils.api_response import success_response
from gestaolegal.utils.jwt_auth import JWTAuth

logger = logging.getLogger(__name__)

auth_controller = Blueprint("auth_api", __name__)


@auth_controller.route("/login", methods=["POST"])
def login():
    logger.info("Login request received")
    data = cast(dict[str, str], request.get_json())

    if not data or "email" not in data or "password" not in data:
        raise ValidationException("Email e senha são obrigatórios")

    email = data["email"]
    password = data["password"]

    user_service = UsuarioService()
    user = user_service.authenticate(email, password)

    if not user:
        raise UnauthorizedException("Email ou senha inválidos")

    if not user.status:
        raise UnauthorizedException("Conta desativada")

    token = JWTAuth.generate_token(user)

    logger.info(f"User logged in successfully: {email}")
    return success_response(data={"token": token, "user": asdict(user)})


@auth_controller.route("/needs-setup", methods=["GET"])
def needs_setup():
    user_service = UsuarioService()
    has_users = user_service.has_any_users()
    return success_response(data={"needs_setup": not has_users})


@auth_controller.route("/setup-admin", methods=["POST"])
def setup_admin():
    logger.info("Setup admin request received")
    data = cast(dict[str, str], request.get_json())

    required_fields = ["email", "password", "setup_token"]
    if not data or not all(field in data for field in required_fields):
        logger.warning("Setup admin failed: missing required fields")
        raise ValidationException("Campos obrigatórios: email, password, setup_token")

    if not Config.ADMIN_SETUP_TOKEN:
        logger.error("Setup admin failed: ADMIN_SETUP_TOKEN not configured")
        raise SetupException(
            "Configuração de administrador não disponível neste servidor"
        )

    if data["setup_token"] != Config.ADMIN_SETUP_TOKEN:
        logger.warning("Setup admin failed: invalid setup token")
        raise UnauthorizedException("Token de configuração inválido")

    user_service = UsuarioService()
    if user_service.has_any_users():
        logger.warning("Setup admin failed: users already exist")
        raise SetupException(
            "Usuário administrador já existe. Este endpoint está desabilitado."
        )

    email = data["email"]
    password = data["password"]

    user = user_service.create_admin(email, password)
    token = JWTAuth.generate_token(user)

    logger.info(f"Admin user created successfully with email: {email}")
    return success_response(
        data={"token": token, "user": asdict(user)},
        message="Administrador criado com sucesso",
        status_code=201,
    )
