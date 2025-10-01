import logging

from flask import Blueprint
from gestaolegal.utils.api_decorators import api_auth_required

logger = logging.getLogger(__name__)

notificacao_controller = Blueprint("notificacao_api", __name__)

@notificacao_controller.route("/", methods=["GET"])
@api_auth_required
def get():
    return {"message": "Not implemented"}

@notificacao_controller.route("/<int:id>", methods=["GET"])
@api_auth_required
def get_by_id(id: int):
    return {"message": "Not implemented"}

@notificacao_controller.route("/", methods=["POST"])
@api_auth_required
def create():
    return {"message": "Not implemented"}

@notificacao_controller.route("/<int:id>", methods=["PUT"])
@api_auth_required
def update(id: int):
    return {"message": "Not implemented"}

@notificacao_controller.route("/<int:id>", methods=["DELETE"])
@api_auth_required
def delete(id: int):
    return {"message": "Not implemented"}

@notificacao_controller.route("/mark-read/<int:id>", methods=["PUT"])
@api_auth_required
def mark_as_read(id: int):
    return {"message": "Not implemented"}

@notificacao_controller.route("/mark-all-read", methods=["PUT"])
@api_auth_required
def mark_all_as_read():
    return {"message": "Not implemented"}
