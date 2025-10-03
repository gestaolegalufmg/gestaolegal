import logging

from flask import Blueprint

from gestaolegal.utils.api_decorators import api_auth_required

logger = logging.getLogger(__name__)

plantao_controller = Blueprint("plantao_api", __name__)


@plantao_controller.route("/", methods=["GET"])
@api_auth_required
def get():
    return {"message": "Not implemented"}


@plantao_controller.route("/registro-presenca", methods=["POST"])
@api_auth_required
def register_presence():
    return {"message": "Not implemented"}


@plantao_controller.route("/confirmar-presenca", methods=["POST"])
@api_auth_required
def confirm_presence():
    return {"message": "Not implemented"}


@plantao_controller.route("/fila-atendimento", methods=["GET"])
@api_auth_required
def get_queue():
    return {"message": "Not implemented"}


@plantao_controller.route("/fila-atendimento", methods=["POST"])
@api_auth_required
def add_to_queue():
    return {"message": "Not implemented"}


@plantao_controller.route("/orientacoes-juridicas", methods=["GET"])
@api_auth_required
def get_legal_guidance():
    return {"message": "Not implemented"}


@plantao_controller.route("/orientacoes-juridicas", methods=["POST"])
@api_auth_required
def create_legal_guidance():
    return {"message": "Not implemented"}


@plantao_controller.route("/assistencias-judiciarias", methods=["GET"])
@api_auth_required
def get_legal_assistance():
    return {"message": "Not implemented"}


@plantao_controller.route("/assistencias-judiciarias", methods=["POST"])
@api_auth_required
def create_legal_assistance():
    return {"message": "Not implemented"}
