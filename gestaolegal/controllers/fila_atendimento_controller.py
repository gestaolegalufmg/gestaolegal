from dataclasses import asdict
from typing import Any, cast

from flask import Blueprint, request

from gestaolegal.models.fila_atendimento_input import FilaAtendimentoCreateInput
from gestaolegal.services.fila_atendimento_service import FilaAtendimentoService
from gestaolegal.utils.api_decorators import authenticated
from gestaolegal.utils.api_response import success_response

fila_atendimento_controller = Blueprint("fila_atendimento_api", __name__)


@fila_atendimento_controller.route("/", methods=["GET"])
@authenticated
def get_fila():
    service = FilaAtendimentoService()
    return success_response(data=service.get_fila_hoje())


@fila_atendimento_controller.route("/preview", methods=["GET"])
@authenticated
def preview_senha():
    prioridade = request.args.get("prioridade", default=0, type=int)
    service = FilaAtendimentoService()
    senha = service.preview_senha(prioridade)
    return success_response(data={"senha": senha})


@fila_atendimento_controller.route("/", methods=["POST"])
@authenticated
def criar():
    json_data = cast(dict[str, Any], request.get_json(force=True))
    fila_input = FilaAtendimentoCreateInput.model_validate(json_data)

    service = FilaAtendimentoService()
    item = service.criar(fila_input)

    return success_response(
        data=asdict(item),
        message="Atendido incluído na fila com sucesso",
        status_code=201,
    )


@fila_atendimento_controller.route("/<int:id>/chamar", methods=["POST"])
@authenticated
def chamar(id: int):
    service = FilaAtendimentoService()
    item = service.chamar(id)
    return success_response(data=asdict(item), message="Atendido chamado com sucesso")


@fila_atendimento_controller.route("/<int:id>/cancelar", methods=["POST"])
@authenticated
def cancelar(id: int):
    service = FilaAtendimentoService()
    item = service.cancelar(id)
    return success_response(data=asdict(item), message="Atendido removido da fila")
