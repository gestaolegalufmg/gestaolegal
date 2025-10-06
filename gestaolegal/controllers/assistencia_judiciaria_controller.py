import logging
from typing import Any, cast

from flask import Blueprint, make_response, request

from gestaolegal.common import PageParams
from gestaolegal.models.assistencia_judiciaria_input import (
    AssistenciaJudiciariaCreateInput,
    AssistenciaJudiciariaUpdateInput,
)
from gestaolegal.services.assistencia_judiciaria_service import (
    AssistenciaJudiciariaService,
)
from gestaolegal.utils.api_decorators import api_auth_required

logger = logging.getLogger(__name__)

assistencia_judiciaria_controller = Blueprint("assistencia_judiciaria_api", __name__)


@assistencia_judiciaria_controller.route("/", methods=["GET"])
@api_auth_required
def get():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    search = request.args.get("search", default="", type=str)
    show_inactive = (
        request.args.get("show_inactive", default="false", type=str).lower() == "true"
    )

    assistencia_judiciaria_service = AssistenciaJudiciariaService()

    return assistencia_judiciaria_service.search(
        page_params=PageParams(page=page, per_page=per_page),
        search=search,
        show_inactive=show_inactive,
    ).to_dict()


@assistencia_judiciaria_controller.route("/<int:id>", methods=["GET"])
@api_auth_required
def find_by_id(id: int):
    assistencia_judiciaria_service = AssistenciaJudiciariaService()

    assistencia = assistencia_judiciaria_service.find_by_id(id)
    if not assistencia:
        return make_response("Assistência judiciária não encontrada", 404)

    return assistencia.model_dump()


@assistencia_judiciaria_controller.route("/", methods=["POST"])
@api_auth_required
def create():
    assistencia_judiciaria_service = AssistenciaJudiciariaService()

    try:
        json_data = cast(dict[str, Any], request.get_json(force=True))
        assistencia_input = AssistenciaJudiciariaCreateInput(**json_data)
        assistencia = assistencia_judiciaria_service.create(assistencia_input)
    except Exception as e:
        logger.error(f"Error creating assistência judiciária: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    return assistencia.model_dump()


@assistencia_judiciaria_controller.route("/<int:id>", methods=["PUT"])
@api_auth_required
def update(id: int):
    assistencia_judiciaria_service = AssistenciaJudiciariaService()

    try:
        json_data = cast(dict[str, Any], request.get_json(force=True))
        assistencia_input = AssistenciaJudiciariaUpdateInput(**json_data)
        assistencia = assistencia_judiciaria_service.update(id, assistencia_input)
    except ValueError as e:
        return make_response(str(e), 404)
    except Exception as e:
        logger.error(
            f"Error updating assistência judiciária {id}: {str(e)}", exc_info=True
        )
        return make_response(str(e), 500)

    if not assistencia:
        return make_response("Erro ao atualizar assistência judiciária", 404)

    return assistencia.model_dump()


@assistencia_judiciaria_controller.route("/<int:id>", methods=["DELETE"])
@api_auth_required
def delete(id: int):
    assistencia_judiciaria_service = AssistenciaJudiciariaService()
    result = assistencia_judiciaria_service.soft_delete(id)

    if not result:
        return make_response("Assistência judiciária não encontrada", 404)

    return make_response("Assistência judiciária inativada com sucesso", 200)
