import logging
from typing import Any, cast

from flask import Blueprint, make_response, request

from gestaolegal.common import PageParams
from gestaolegal.services.atendido_service import AtendidoService
from gestaolegal.utils import StringBool
from gestaolegal.utils.api_decorators import api_auth_required

logger = logging.getLogger(__name__)

atendido_controller = Blueprint("atendido_api", __name__)


@atendido_controller.route("/", methods=["GET"])
@api_auth_required
def get():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    search = request.args.get("search", default="", type=str)
    tipo_busca = request.args.get("tipo_busca", default="todos", type=str)
    show_inactive = request.args.get(
        "show_inactive", default=StringBool("false"), type=StringBool
    )

    atendido_service = AtendidoService()
    logger.info(
        f"Getting atendidos with search: {search}, tipo_busca: {tipo_busca}, show_inactive: {show_inactive.value}"
    )
    return atendido_service.search(
        page_params=PageParams(page=page, per_page=per_page),
        search=search,
        tipo_busca=tipo_busca,
        show_inactive=show_inactive.value,
    ).to_dict()


@atendido_controller.route("/<int:id>", methods=["GET"])
@api_auth_required
def find_by_id(id: int):
    atendido_service = AtendidoService()
    logger.info(f"Getting atendido by id: {id}")
    atendido = atendido_service.find_by_id(id)
    if not atendido:
        return make_response("Atendido not found", 404)

    logger.info(f"Atendido found: {atendido}")
    return atendido.to_dict()


@atendido_controller.route("/", methods=["POST"])
@api_auth_required
def create():
    logger.info("Creating atendido")
    atendido_service = AtendidoService()

    try:
        atendido_data = cast(dict[str, Any], request.get_json(force=True))
        atendido = atendido_service.create(atendido_data)
    except Exception as e:
        logger.error(f"Error creating atendido: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    logger.info(f"Atendido created: {atendido}")

    return atendido.to_dict()


@atendido_controller.route("/<int:id>", methods=["PUT"])
@api_auth_required
def update(id: int):
    logger.info(f"Updating atendido: {id}")
    atendido_service = AtendidoService()
    atendido_data: Any = request.get_json(force=True)

    atendido = atendido_service.update(id, atendido_data)
    if not atendido:
        logger.error(f"Atendido not found: {id}")
        return make_response("Atendido not found", 404)

    logger.info(f"Atendido updated: {atendido}")
    return atendido.to_dict()


@atendido_controller.route("/<int:id>", methods=["DELETE"])
@api_auth_required
def delete(id: int):
    logger.info(f"Deactivating atendido: {id}")

    atendido_service = AtendidoService()
    atendido = atendido_service.soft_delete(id)

    logger.info(f"Atendido deactivated: {atendido}")

    return make_response("Atendido deactivated", 200)


@atendido_controller.route("/<int:id>/tornar-assistido", methods=["POST"])
@api_auth_required
def tornar_assistido(id: int):
    logger.info(f"Converting atendido {id} to assistido")
    atendido_service = AtendidoService()

    try:
        assistido_data = cast(dict[str, Any], request.get_json(force=True))
        assistido = atendido_service.create_assistido(id, assistido_data)
    except Exception as e:
        logger.error(f"Error creating assistido: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    logger.info(f"Assistido created: {assistido}")
    return assistido.to_dict()


@atendido_controller.route("/<int:id>/assistido", methods=["PUT"])
@api_auth_required
def update_assistido(id: int):
    logger.info(f"Updating assistido for atendido {id}")
    atendido_service = AtendidoService()
    data: Any = request.get_json(force=True)

    assistido_fields = [
        "sexo",
        "profissao",
        "raca",
        "rg",
        "grau_instrucao",
        "salario",
        "beneficio",
        "qual_beneficio",
        "contribui_inss",
        "qtd_pessoas_moradia",
        "renda_familiar",
        "participacao_renda",
        "tipo_moradia",
        "possui_outros_imoveis",
        "quantos_imoveis",
        "possui_veiculos",
        "possui_veiculos_obs",
        "quantos_veiculos",
        "ano_veiculo",
        "doenca_grave_familia",
        "pessoa_doente",
        "pessoa_doente_obs",
        "gastos_medicacao",
        "obs",
    ]

    atendido_data = {k: v for k, v in data.items() if k not in assistido_fields}
    assistido_data = {k: v for k, v in data.items() if k in assistido_fields}

    try:
        updated_assistido = atendido_service.update_assistido(
            id, atendido_data, assistido_data
        )
    except Exception as e:
        logger.error(f"Error updating assistido: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    logger.info(f"Assistido updated: {updated_assistido}")
    return updated_assistido.to_dict()
