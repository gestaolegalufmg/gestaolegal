from dataclasses import asdict
from typing import Any, cast

from flask import Blueprint, request

from gestaolegal.models.unidade_input import UnidadeCreateInput, UnidadeUpdateInput
from gestaolegal.services.unidade_service import UnidadeService
from gestaolegal.utils.api_decorators import authenticated, authorized
from gestaolegal.utils.api_response import success_response
from gestaolegal.utils.StringBool import StringBool
from gestaolegal.utils.request_context import RequestContext

unidade_controller = Blueprint("unidade_api", __name__)


@unidade_controller.route("/", methods=["GET"])
@authenticated(unidade=False)
def listar():
    """Unidades ativas — e as inativas também, se admin pedir.

    Dispensa o `X-Unidade-Id` de propósito: é esta rota que alimenta o seletor
    do front, que roda antes de haver unidade ativa. Por isso `incluir_inativas`
    só vale para admin: o seletor de quem não é admin não pode passar a oferecer
    unidade desativada. Pedido de não-admin é ignorado em silêncio (lista de
    ativas, 200), não é 403 — a tela /unidades é que é restrita, não esta rota.
    """
    # `StringBool` só reconhece "true"; a tela /unidades manda "1", e é o valor
    # anunciado no contrato desta rota. Normaliza antes de converter.
    bruto = request.args.get("incluir_inativas", default="false", type=str)
    incluir_inativas = StringBool("true" if bruto == "1" else bruto)
    is_admin = RequestContext.get_current_user().urole == "admin"

    service = UnidadeService()
    unidades = service.listar(incluir_inativas=incluir_inativas.value and is_admin)
    return success_response(data=[asdict(u) for u in unidades])


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
