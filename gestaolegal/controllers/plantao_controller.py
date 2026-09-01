from typing import Any, cast

from flask import Blueprint, request

from gestaolegal.models.plantao_input import ConfiguracaoPlantaoInput, MarcarDiaInput
from gestaolegal.services.plantao_service import PlantaoService
from gestaolegal.utils.api_decorators import authenticated, authorized
from gestaolegal.utils.api_response import success_response
from gestaolegal.utils.request_context import RequestContext

plantao_controller = Blueprint("plantao_api", __name__)


@plantao_controller.route("/", methods=["GET"])
@authenticated
def get_pagina():
    service = PlantaoService()
    return success_response(data=service.get_pagina(RequestContext.get_current_user()))


@plantao_controller.route("/marcacoes", methods=["POST"])
@authenticated
def marcar_dia():
    json_data = cast(dict[str, Any], request.get_json(force=True))
    dados = MarcarDiaInput.model_validate(json_data)

    service = PlantaoService()
    pagina = service.marcar_dia(dados, RequestContext.get_current_user())

    return success_response(
        data=pagina,
        message="Data de plantão cadastrada!",
        status_code=201,
    )


@plantao_controller.route("/marcacoes", methods=["DELETE"])
@authenticated
def limpar_marcacoes():
    service = PlantaoService()
    pagina = service.limpar_marcacoes(RequestContext.get_current_user())
    return success_response(
        data=pagina,
        message="Registro apagado. Selecione novamente os dias do seu plantão.",
    )


@plantao_controller.route("/configuracao", methods=["GET"])
@authorized("admin", "colab_proj")
def get_configuracao():
    service = PlantaoService()
    return success_response(data=service.get_configuracao())


@plantao_controller.route("/configuracao", methods=["PUT"])
@authorized("admin", "colab_proj")
def salvar_configuracao():
    json_data = cast(dict[str, Any], request.get_json(force=True))
    dados = ConfiguracaoPlantaoInput.model_validate(json_data)

    service = PlantaoService()
    configuracao = service.salvar_configuracao(dados)

    return success_response(
        data=configuracao, message="Configuração do plantão salva com sucesso"
    )
