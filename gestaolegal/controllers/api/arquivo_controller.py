import logging

from flask import Blueprint
from gestaolegal.utils.api_decorators import api_auth_required

logger = logging.getLogger(__name__)

arquivo_controller = Blueprint("arquivo_api", __name__)

@arquivo_controller.route("/", methods=["GET"])
@api_auth_required
def get():
    return {"message": "Not implemented"}

@arquivo_controller.route("/<int:id>", methods=["GET"])
@api_auth_required
def get_by_id(id: int):
    return {"message": "Not implemented"}

@arquivo_controller.route("/", methods=["POST"])
@api_auth_required
def create():
    return {"message": "Not implemented"}

@arquivo_controller.route("/<int:id>", methods=["PUT"])
@api_auth_required
def update(id: int):
    return {"message": "Not implemented"}

@arquivo_controller.route("/<int:id>", methods=["DELETE"])
@api_auth_required
def delete(id: int):
    return {"message": "Not implemented"}

@arquivo_controller.route("/ver-arquivos", methods=["GET"])
@api_auth_required
def view_files():
    return {"message": "Not implemented"}

@arquivo_controller.route("/cadastrar-arquivo", methods=["POST"])
@api_auth_required
def register_file():
    return {"message": "Not implemented"}
