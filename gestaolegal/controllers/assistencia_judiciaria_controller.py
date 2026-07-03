from dataclasses import asdict
from typing import Any, cast

from flask import Blueprint, request

from gestaolegal.common import PageParams
from gestaolegal.exceptions import NotFoundException
from gestaolegal.models.assistencia_judiciaria_input import (
    AssistenciaJudiciariaCreateInput,
    AssistenciaJudiciariaUpdateInput,
    EncaminharInput,
)
from gestaolegal.services.assistencia_judiciaria_service import (
    AssistenciaJudiciariaService,
)
from gestaolegal.utils.api_decorators import authenticated, authorized
from gestaolegal.utils.api_response import success_response
from gestaolegal.utils.StringBool import StringBool

assistencia_judiciaria_controller = Blueprint("assistencia_judiciaria_api", __name__)


@assistencia_judiciaria_controller.route("", methods=["GET"])
@authenticated
def get():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    search = request.args.get("search", default="", type=str)
    show_inactive = request.args.get(
        "show_inactive", default=StringBool("false"), type=StringBool
    )
    area = request.args.get("area", default="", type=str)
    regiao = request.args.get("regiao", default="", type=str)
    orientacao_id = request.args.get("orientacao_id", default=None, type=int)

    service = AssistenciaJudiciariaService()

    if orientacao_id is not None:
        items = service.get_by_orientacao(orientacao_id)
        return success_response(data=[asdict(item) for item in items])

    result = service.search(
        page_params=PageParams(page=page, per_page=per_page),
        search=search,
        show_inactive=show_inactive.value,
        area=area,
        regiao=regiao,
    )
    return success_response(data=result.to_dict())


@assistencia_judiciaria_controller.route("/<int:id>", methods=["GET"])
@authenticated
def find_by_id(id: int):
    service = AssistenciaJudiciariaService()
    assistencia = service.find_by_id(id)
    if not assistencia:
        raise NotFoundException(resource="Assistencia Judiciaria", resource_id=id)
    return success_response(data=asdict(assistencia))


@assistencia_judiciaria_controller.route("/", methods=["POST"])
@authenticated
def create():
    service = AssistenciaJudiciariaService()
    json_data = cast(dict[str, Any], request.get_json(force=True))
    assistencia_input = AssistenciaJudiciariaCreateInput(**json_data)
    assistencia = service.create(assistencia_input)
    return success_response(
        data=asdict(assistencia),
        message="Assistência judiciária criada com sucesso",
        status_code=201,
    )


@assistencia_judiciaria_controller.route("/<int:id>", methods=["PUT"])
@authenticated
def update(id: int):
    service = AssistenciaJudiciariaService()
    json_data = cast(dict[str, Any], request.get_json(force=True))
    assistencia_input = AssistenciaJudiciariaUpdateInput(**json_data)
    assistencia = service.update(id, assistencia_input)
    return success_response(
        data=asdict(assistencia),
        message="Assistência judiciária atualizada com sucesso",
    )


@assistencia_judiciaria_controller.route("/<int:id>", methods=["DELETE"])
@authorized("admin")
def delete(id: int):
    service = AssistenciaJudiciariaService()
    service.delete(id)
    return success_response(message="Assistência judiciária inativada com sucesso")


@assistencia_judiciaria_controller.route("/<int:id>/encaminhar", methods=["POST"])
@authenticated
def encaminhar(id: int):
    service = AssistenciaJudiciariaService()
    json_data = cast(dict[str, Any], request.get_json(force=True))
    encaminhar_input = EncaminharInput(**json_data)
    assistencia = service.encaminhar(id, encaminhar_input.id_orientacao)
    return success_response(
        data=asdict(assistencia),
        message="Assistência judiciária associada à orientação com sucesso",
    )


@assistencia_judiciaria_controller.route(
    "/<int:id>/orientacoes/<int:id_orientacao>", methods=["DELETE"]
)
@authenticated
def desvincular(id: int, id_orientacao: int):
    service = AssistenciaJudiciariaService()
    service.desvincular(id, id_orientacao)
    return success_response(message="Associação removida com sucesso")
