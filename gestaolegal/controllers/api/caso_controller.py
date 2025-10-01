import logging

from flask import Blueprint
from gestaolegal.utils.api_decorators import api_auth_required

logger = logging.getLogger(__name__)

caso_controller = Blueprint("caso_api", __name__)

@caso_controller.route("/", methods=["GET"])
@api_auth_required
def get():
    return {"message": "Not implemented"}

@caso_controller.route("/<int:id>", methods=["GET"])
@api_auth_required
def get_by_id(id: int):
    return {"message": "Not implemented"}

@caso_controller.route("/", methods=["POST"])
@api_auth_required
def create():
    return {"message": "Not implemented"}

@caso_controller.route("/<int:id>", methods=["PUT"])
@api_auth_required
def update(id: int):
    return {"message": "Not implemented"}

@caso_controller.route("/<int:id>", methods=["DELETE"])
@api_auth_required
def delete(id: int):
    return {"message": "Not implemented"}

@caso_controller.route("/meus-casos", methods=["GET"])
def get_my_cases():
    return {"message": "Not implemented"}

@caso_controller.route("/gerenciar-roteiros", methods=["GET"])
def manage_scripts():
    return {"message": "Not implemented"}
