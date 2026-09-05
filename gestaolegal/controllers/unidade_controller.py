from dataclasses import asdict
from typing import Any, cast

from flask import Blueprint, request

from gestaolegal.models.unidade_input import UnidadeCreateInput, UnidadeUpdateInput
from gestaolegal.services.unidade_service import UnidadeService
from gestaolegal.utils.api_decorators import authenticated, authorized
from gestaolegal.utils.api_response import success_response

unidade_controller = Blueprint("unidade_api", __name__)


@unidade_controller.route("/", methods=["GET"])
@authenticated(unidade=False)
def listar():
    """Unidades ativas.

    Dispensa o `X-Unidade-Id` de propósito: é esta rota que alimenta o seletor
    do front, que roda antes de haver unidade ativa.
    """
    service = UnidadeService()
    return success_response(data=[asdict(u) for u in service.list_ativas()])


@unidade_controller.route("/", methods=["POST"])
@authorized("admin")
def criar():
    json_data = cast(dict[str, Any], request.get_json(force=True))
    unidade_input = UnidadeCreateInput.model_validate(json_data)

    service = UnidadeService()
    unidade = service.criar(unidade_input)

    return success_response(
        data=asdict(unidade),
        message="Unidade criada com sucesso",
        status_code=201,
    )


@unidade_controller.route("/<int:id>", methods=["PUT"])
@authorized("admin")
def atualizar(id: int):
    json_data = cast(dict[str, Any], request.get_json(force=True))
    unidade_input = UnidadeUpdateInput.model_validate(json_data)

    service = UnidadeService()
    unidade = service.atualizar(id, unidade_input)

    return success_response(
        data=asdict(unidade), message="Unidade atualizada com sucesso"
    )
