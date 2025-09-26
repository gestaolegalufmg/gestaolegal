import logging

from flask import Blueprint

from gestaolegal.services.usuario_service import UsuarioService


logger = logging.getLogger(__name__)

user_controller = Blueprint("user", __name__)

@user_controller.route("/api/user", methods=["GET"])
def get_user():
    user_service = UsuarioService()
    return user_service.get_all().to_dict()