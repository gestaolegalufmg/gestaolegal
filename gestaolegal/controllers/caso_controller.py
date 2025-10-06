import logging
from typing import Any, cast

from flask import Blueprint, make_response, request

from gestaolegal.common import PageParams
from gestaolegal.models.caso_input import CasoCreateInput, CasoUpdateInput
from gestaolegal.models.user import User
from gestaolegal.services.caso_service import CasoService
from gestaolegal.utils.api_decorators import api_auth_required

logger = logging.getLogger(__name__)

caso_controller = Blueprint("caso_api", __name__)


@caso_controller.route("/", methods=["GET"])
@api_auth_required
def get(current_user: User):
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    search = request.args.get("search", default="", type=str)
    show_inactive = (
        request.args.get("show_inactive", default="false", type=str).lower() == "true"
    )
    situacao_deferimento = request.args.get(
        "situacao_deferimento", default=None, type=str
    )

    caso_service = CasoService()

    return caso_service.search(
        page_params=PageParams(page=page, per_page=per_page),
        search=search,
        show_inactive=show_inactive,
        situacao_deferimento=situacao_deferimento,
    ).to_dict()


@caso_controller.route("/<int:id>", methods=["GET"])
@api_auth_required
def find_by_id(current_user: User, id: int):
    caso_service = CasoService()

    caso = caso_service.find_by_id(id)
    if not caso:
        return make_response("Caso não encontrado", 404)

    return caso.model_dump()


@caso_controller.route("/", methods=["POST"])
@api_auth_required
def create(current_user: User):
    caso_service = CasoService()

    try:
        json_data = cast(dict[str, Any], request.get_json(force=True))
        caso_input = CasoCreateInput(**json_data)
        caso = caso_service.create(caso_input, criado_por_id=current_user.id)
    except Exception as e:
        logger.error(f"Error creating caso: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    return caso.model_dump()


@caso_controller.route("/<int:id>", methods=["PUT"])
@api_auth_required
def update(current_user: User, id: int):
    caso_service = CasoService()

    try:
        json_data = cast(dict[str, Any], request.get_json(force=True))
        caso_input = CasoUpdateInput(**json_data)
        caso = caso_service.update(id, caso_input, modificado_por_id=current_user.id)
    except ValueError as e:
        return make_response(str(e), 404)
    except Exception as e:
        logger.error(f"Error updating caso {id}: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    if not caso:
        return make_response("Erro ao atualizar caso", 404)

    return caso.model_dump()


@caso_controller.route("/<int:id>", methods=["DELETE"])
@api_auth_required
def delete(current_user: User, id: int):
    caso_service = CasoService()
    result = caso_service.soft_delete(id)

    if not result:
        return make_response("Caso não encontrado", 404)

    return make_response("Caso inativado com sucesso", 200)
