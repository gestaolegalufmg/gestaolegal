import logging

from flask import Blueprint
from gestaolegal.utils.api_decorators import api_auth_required

logger = logging.getLogger(__name__)

relatorio_controller = Blueprint("relatorio_api", __name__)

@relatorio_controller.route("/", methods=["GET"])
@api_auth_required
def get():
    return {"message": "Not implemented"}

@relatorio_controller.route("/<int:id>", methods=["GET"])
@api_auth_required
def get_by_id(id: int):
    return {"message": "Not implemented"}

@relatorio_controller.route("/", methods=["POST"])
@api_auth_required
def create():
    return {"message": "Not implemented"}

@relatorio_controller.route("/<int:id>", methods=["PUT"])
@api_auth_required
def update(id: int):
    return {"message": "Not implemented"}

@relatorio_controller.route("/<int:id>", methods=["DELETE"])
@api_auth_required
def delete(id: int):
    return {"message": "Not implemented"}

@relatorio_controller.route("/generate", methods=["POST"])
@api_auth_required
def generate():
    return {"message": "Not implemented"}

@relatorio_controller.route("/export/<int:id>", methods=["GET"])
@api_auth_required
def export(id: int):
    return {"message": "Not implemented"}
