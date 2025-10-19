from dataclasses import asdict
from typing import Any, cast

from flask import Blueprint, request

from gestaolegal.common import PageParams
from gestaolegal.exceptions import NotFoundException
from gestaolegal.models.orientacao_juridica_input import (
    OrientacaoJuridicaCreate,
    OrientacaoJuridicaUpdate,
)
from gestaolegal.models.user import UserInfo
from gestaolegal.services.orientacao_juridica_service import OrientacaoJuridicaService
from gestaolegal.utils.api_decorators import authenticated, authorized
from gestaolegal.utils.api_response import success_response
from gestaolegal.utils.request_context import RequestContext
from gestaolegal.utils.StringBool import StringBool

orientacao_juridica_controller = Blueprint("orientacao_juridica_api", __name__)


@orientacao_juridica_controller.route("", methods=["GET"])
@authenticated
def get():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    search = request.args.get("search", default="", type=str)
    show_inactive = request.args.get(
        "show_inactive", default=StringBool("false"), type=StringBool
    )
    area = request.args.get("area", default="", type=str)

    orientacao_juridica_service = OrientacaoJuridicaService()

    orientacoes_result = orientacao_juridica_service.search(
        page_params=PageParams(page=page, per_page=per_page),
        search=search,
        show_inactive=show_inactive.value,
        area=area,
    )
    return success_response(data=orientacoes_result.to_dict())


@orientacao_juridica_controller.route("/<int:id>", methods=["GET"])
@authenticated
def find_by_id(id: int):
    orientacao_juridica_service = OrientacaoJuridicaService()

    orientacao = orientacao_juridica_service.find_by_id(id)
    if not orientacao:
        raise NotFoundException(resource="Orientacao Juridica", resource_id=id)

    return success_response(data=asdict(orientacao))


@orientacao_juridica_controller.route("/<int:id>", methods=["DELETE"])
@authorized("admin")
def delete(id: int):
    orientacao_juridica_service = OrientacaoJuridicaService()
    orientacao_juridica_service.delete(id)
    return success_response(message="Orientação jurídica inativada com sucesso")


@orientacao_juridica_controller.route("/", methods=["POST"])
@authenticated
def create():
    current_user: UserInfo = RequestContext.get_current_user()
    orientacao_juridica_service = OrientacaoJuridicaService()

    json_data = cast(dict[str, Any], request.get_json(force=True))

    orientacao_input = OrientacaoJuridicaCreate(**json_data)
    orientacao = orientacao_juridica_service.create(
        orientacao_input, cast(int, current_user.id)
    )

    return success_response(
        data=asdict(orientacao),
        message="Orientação jurídica criada com sucesso",
        status_code=201,
    )


@orientacao_juridica_controller.route("/<int:id>", methods=["PUT"])
@authenticated
def update(id: int):
    orientacao_juridica_service = OrientacaoJuridicaService()

    json_data = cast(dict[str, Any], request.get_json(force=True))
    orientacao_input = OrientacaoJuridicaUpdate(**json_data)
    orientacao = orientacao_juridica_service.update(id, orientacao_input)

    return success_response(
        data=asdict(orientacao), message="Orientação jurídica atualizada com sucesso"
    )
