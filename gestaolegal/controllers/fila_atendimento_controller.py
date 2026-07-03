from dataclasses import asdict
from typing import Any, cast

from flask import Blueprint, request

from gestaolegal.models.fila_atendimento_input import AdicionarFilaInput
from gestaolegal.services.fila_atendimento_service import FilaAtendimentoService
from gestaolegal.utils.api_decorators import authenticated
from gestaolegal.utils.api_response import success_response

fila_atendimento_controller = Blueprint("fila_atendimento_api", __name__)


@fila_atendimento_controller.route("", methods=["GET"])
@authenticated
def get_fila():
    service = FilaAtendimentoService()
    items = service.get_fila()
    return success_response(data=[asdict(item) for item in items])


@fila_atendimento_controller.route("", methods=["POST"])
@authenticated
def adicionar():
    service = FilaAtendimentoService()
    json_data = cast(dict[str, Any], request.get_json(force=True))
    fila_input = AdicionarFilaInput(**json_data)
    items = service.adicionar(fila_input)
    return success_response(
        data=[asdict(item) for item in items],
        message="Adicionado à fila com sucesso",
        status_code=201,
    )


@fila_atendimento_controller.route("/chamar-proximo", methods=["POST"])
@authenticated
def chamar_proximo():
    service = FilaAtendimentoService()
    items = service.chamar_proximo()
    return success_response(
        data=[asdict(item) for item in items],
        message="Próximo atendimento iniciado",
    )


@fila_atendimento_controller.route("/<int:id>/concluir", methods=["PATCH"])
@authenticated
def concluir(id: int):
    service = FilaAtendimentoService()
    items = service.concluir(id)
    return success_response(
        data=[asdict(item) for item in items],
        message="Atendimento concluído",
    )


@fila_atendimento_controller.route("/<int:id>", methods=["DELETE"])
@authenticated
def remover(id: int):
    service = FilaAtendimentoService()
    items = service.remover(id)
    return success_response(
        data=[asdict(item) for item in items],
        message="Removido da fila",
    )
