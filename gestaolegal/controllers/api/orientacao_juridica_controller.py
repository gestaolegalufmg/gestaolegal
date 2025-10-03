import logging
from typing import Any, cast

from flask import Blueprint, make_response, request

from gestaolegal.common import PageParams
from gestaolegal.models.orientacao_juridica import OrientacaoJuridica
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

    orientacao_juridica_service = OrientacaoJuridicaService()
    logger.info(f"Getting orientacoes juridicas with search: {search}")

    orientacoes_result = orientacao_juridica_service.search(
        page_params=PageParams(page=page, per_page=per_page), search=search
    )

    return orientacoes_result.to_dict()


@orientacao_juridica_controller.route("/<int:id>", methods=["GET"])
@api_auth_required
def find_by_id(id: int):
    orientacao_juridica_service = OrientacaoJuridicaService()
    logger.info(f"Getting orientacao juridica by id: {id}")

    orientacao_data = orientacao_juridica_service.find_by_id(id)
    if not orientacao_data:
        return make_response("Orientação jurídica não encontrada", 404)

    logger.info(f"Orientacao juridica found: {id}")
    return orientacao_data.to_dict()


@orientacao_juridica_controller.route("/<int:id>", methods=["DELETE"])
@api_auth_required
def delete(id: int):
    logger.info(f"Deactivating orientacao juridica: {id}")

    orientacao_juridica_service = OrientacaoJuridicaService()
    orientacao = orientacao_juridica_service.delete(id)

    logger.info(f"Orientacao juridica deactivated: {orientacao}")

    return make_response("Orientação jurídica inativada com sucesso", 200)


@orientacao_juridica_controller.route("/", methods=["POST"])
@api_auth_required
def create(current_user: User):
    logger.info("Creating orientacao juridica")
    orientacao_juridica_service = OrientacaoJuridicaService()

    try:
        orientacao_data = cast(dict[str, Any], request.get_json(force=True))
        orientacao_data["id_usuario"] = current_user.id

        orientacao = OrientacaoJuridica(**orientacao_data)
        orientacao = orientacao_juridica_service.create(orientacao)
    except Exception as e:
        logger.error(f"Error creating orientacao juridica: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    logger.info(f"Orientacao juridica created: {orientacao}")
    return orientacao.to_dict()


@orientacao_juridica_controller.route("/<int:id>", methods=["PUT"])
@api_auth_required
def update(id: int):
    logger.info(f"Updating orientacao juridica: {id}")
    orientacao_juridica_service = OrientacaoJuridicaService()
    orientacao_data: Any = request.get_json(force=True)

    orientacao = orientacao_juridica_service.update(id, orientacao_data)
    if not orientacao:
        logger.error(f"Orientacao juridica not found: {id}")
        return make_response("Orientação jurídica não encontrada", 404)

    logger.info(f"Orientacao juridica updated: {orientacao}")
    return orientacao.to_dict()
