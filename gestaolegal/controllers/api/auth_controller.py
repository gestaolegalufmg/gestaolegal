import logging
from typing import cast
from flask import Blueprint, make_response, request
from gestaolegal.services.usuario_service import UsuarioService
from gestaolegal.utils.jwt_auth import JWTAuth

logger = logging.getLogger(__name__)

auth_controller = Blueprint("auth_api", __name__)

@auth_controller.route("/login", methods=["POST"])
def login():
    try:
        logger.info("Login request received")
        data = cast(dict[str, str], request.get_json())

        if not data or 'email' not in data or 'password' not in data:
            return make_response("Email and password are required", 400)
        
        email = data['email']
        password = data['password']
        
        user_service = UsuarioService()
        user = user_service.authenticate(email, password)
        
        if not user:
            return make_response("Invalid email or password", 401)
        
        if not user.status:
            return make_response("Account is disabled", 401)
        
        token = JWTAuth.generate_token(user)
        
        logger.info(f"token in login -> {token}");

        return make_response({
            'token': token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return make_response("Internal server error", 500)

