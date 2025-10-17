import logging
from dataclasses import asdict
from typing import cast

from flask import Blueprint, make_response, request

from gestaolegal.config import Config
from gestaolegal.services.usuario_service import UsuarioService
from gestaolegal.utils.jwt_auth import JWTAuth

logger = logging.getLogger(__name__)

auth_controller = Blueprint("auth_api", __name__)


@auth_controller.route("/login", methods=["POST"])
def login():
    try:
        logger.info("Login request received")
        data = cast(dict[str, str], request.get_json())

        if not data or "email" not in data or "password" not in data:
            return make_response("Email and password are required", 400)

        email = data["email"]
        password = data["password"]

        user_service = UsuarioService()
        user = user_service.authenticate(email, password)

        if not user:
            return make_response("Invalid email or password", 401)

        if not user.status:
            return make_response("Account is disabled", 401)

        token = JWTAuth.generate_token(user)

        logger.info(f"token in login -> {token}")
        return make_response({"token": token, "user": asdict(user)})

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return make_response("Internal server error", 500)


@auth_controller.route("/setup-admin", methods=["POST"])
def setup_admin():
    try:
        logger.info("Setup admin request received")
        data = cast(dict[str, str], request.get_json())

        required_fields = ["email", "password", "setup_token"]
        if not data or not all(field in data for field in required_fields):
            logger.warning("Setup admin failed: missing required fields")
            return make_response(
                {"error": "Missing required fields: email, password, setup_token"}, 400
            )

        if not Config.ADMIN_SETUP_TOKEN:
            logger.error("Setup admin failed: ADMIN_SETUP_TOKEN not configured")
            return make_response(
                {"error": "Admin setup is not configured on this server"}, 403
            )

        if data["setup_token"] != Config.ADMIN_SETUP_TOKEN:
            logger.warning("Setup admin failed: invalid setup token")
            return make_response({"error": "Invalid setup token"}, 403)

        user_service = UsuarioService()
        if user_service.has_any_users():
            logger.warning("Setup admin failed: users already exist")
            return make_response(
                {"error": "Admin user already exists. This endpoint is disabled."}, 403
            )

        email = data["email"]
        password = data["password"]

        user = user_service.create_admin(email, password)
        token = JWTAuth.generate_token(user)

        logger.info(f"Admin user created successfully with email: {email}")
        return make_response({"token": token, "user": asdict(user)}, 201)

    except ValueError as e:
        logger.error(f"Setup admin validation error: {str(e)}")
        return make_response({"error": str(e)}, 400)
    except Exception as e:
        logger.error(f"Setup admin error: {str(e)}")
        return make_response({"error": "Internal server error"}, 500)
