import logging
from typing import Any, cast

from flask import Blueprint, make_response, request

from gestaolegal.common import PageParams
from gestaolegal.models.orientacao_juridica_input import (
    OrientacaoJuridicaCreateInput,
    OrientacaoJuridicaUpdateInput,
)
from gestaolegal.models.user import User
from gestaolegal.services.orientacao_juridica_service import OrientacaoJuridicaService
from gestaolegal.utils.api_decorators import api_auth_required

logger = logging.getLogger(__name__)

orientacao_juridica_controller = Blueprint("orientacao_juridica_api", __name__)


@orientacao_juridica_controller.route("/", methods=["GET"])
@api_auth_required
def get():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    search = request.args.get("search", default="", type=str)
    show_inactive = (
        request.args.get("show_inactive", default="false", type=str).lower() == "true"
    )
    area = request.args.get("area", default="", type=str)

    orientacao_juridica_service = OrientacaoJuridicaService()

    orientacoes_result = orientacao_juridica_service.search(
        page_params=PageParams(page=page, per_page=per_page),
        search=search,
        show_inactive=show_inactive,
        area=area,
    )
    return orientacoes_result.to_dict()


@orientacao_juridica_controller.route("/<int:id>", methods=["GET"])
@api_auth_required
def find_by_id(id: int):
    orientacao_juridica_service = OrientacaoJuridicaService()

    orientacao_data = orientacao_juridica_service.find_by_id(id)
    if not orientacao_data:
        return make_response("Orientação jurídica não encontrada", 404)

    return orientacao_data.model_dump()


@orientacao_juridica_controller.route("/<int:id>", methods=["DELETE"])
@api_auth_required
def delete(id: int):
    orientacao_juridica_service = OrientacaoJuridicaService()
    orientacao_juridica_service.delete(id)

    return make_response("Orientação jurídica inativada com sucesso", 200)


@orientacao_juridica_controller.route("/", methods=["POST"])
@api_auth_required
def create(current_user: User):
    orientacao_juridica_service = OrientacaoJuridicaService()

    try:
        json_data = cast(dict[str, Any], request.get_json(force=True))

        orientacao_input = OrientacaoJuridicaCreateInput(**json_data)
        orientacao = orientacao_juridica_service.create(
            orientacao_input, cast(int, current_user.id)
        )
    except Exception as e:
        logger.error(f"Error creating orientacao juridica: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    return orientacao.model_dump()


@orientacao_juridica_controller.route("/<int:id>", methods=["PUT"])
@api_auth_required
def update(id: int):
    orientacao_juridica_service = OrientacaoJuridicaService()

    try:
        json_data = cast(dict[str, Any], request.get_json(force=True))
        orientacao_input = OrientacaoJuridicaUpdateInput(**json_data)
        orientacao = orientacao_juridica_service.update(id, orientacao_input)
    except Exception as e:
        logger.error(
            f"Error updating orientacao juridica {id}: {str(e)}", exc_info=True
        )
        return make_response(str(e), 500)

    return orientacao.model_dump()
