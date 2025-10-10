import logging
from dataclasses import asdict
from typing import Any, cast

from flask import Blueprint, make_response, request

from gestaolegal.common import PageParams
from gestaolegal.models.assistido_input import (
    AssistidoCreateInput,
    AssistidoUpdateInput,
)
from gestaolegal.models.atendido_input import AtendidoCreateInput, AtendidoUpdateInput
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
    result = atendido_service.search(
        page_params=PageParams(page=page, per_page=per_page),
        search=search,
        tipo_busca=tipo_busca,
        show_inactive=show_inactive.value,
    )
    return result.to_dict()


@atendido_controller.route("/<int:id>", methods=["GET"])
@api_auth_required
def find_by_id(id: int):
    atendido_service = AtendidoService()
    atendido = atendido_service.find_by_id(id)
    if not atendido:
        return make_response("Atendido not found", 404)

    return asdict(atendido)


@atendido_controller.route("/", methods=["POST"])
@api_auth_required
def create():
    atendido_service = AtendidoService()

    try:
        json_data = cast(dict[str, Any], request.get_json(force=True))
        atendido_input = AtendidoCreateInput.model_validate(json_data)
        atendido = atendido_service.create(atendido_input)
    except Exception as e:
        logger.error(f"Error creating atendido: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    return asdict(atendido)


@atendido_controller.route("/<int:id>", methods=["PUT"])
@api_auth_required
def update(id: int):
    atendido_service = AtendidoService()

    try:
        json_data = cast(dict[str, Any], request.get_json(force=True))
        atendido_input = AtendidoUpdateInput.model_validate(json_data)
        atendido = atendido_service.update(id, atendido_input)
    except Exception as e:
        logger.error(f"Error updating atendido {id}: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    return asdict(atendido)


@atendido_controller.route("/<int:id>", methods=["DELETE"])
@api_auth_required
def delete(id: int):
    atendido_service = AtendidoService()
    atendido_service.soft_delete(id)

    return make_response("Atendido deactivated", 200)


@atendido_controller.route("/<int:id>/tornar-assistido", methods=["POST"])
@api_auth_required
def tornar_assistido(id: int):
    atendido_service = AtendidoService()

    try:
        json_data = cast(dict[str, Any], request.get_json(force=True))
        assistido_input = AssistidoCreateInput.model_validate(json_data)
        atendido_service.create_assistido(id, assistido_input)
    except Exception as e:
        logger.error(f"Error creating assistido: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    atendido = atendido_service.find_by_id(id)
    return asdict(atendido)


@atendido_controller.route("/<int:id>/assistido", methods=["PUT"])
@api_auth_required
def update_assistido(id: int):
    atendido_service = AtendidoService()

    try:
        json_data = cast(dict[str, Any], request.get_json(force=True))

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

        atendido_data = {
            k: v for k, v in json_data.items() if k not in assistido_fields
        }
        assistido_data = {k: v for k, v in json_data.items() if k in assistido_fields}

        atendido_input = (
            AtendidoUpdateInput.model_validate(atendido_data) if atendido_data else None
        )
        assistido_input = AssistidoUpdateInput.model_validate(assistido_data)

        atendido_service.update_assistido(id, atendido_input, assistido_input)
    except Exception as e:
        logger.error(f"Error updating assistido: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    atendido = atendido_service.find_by_id(id)
    return asdict(atendido)
