from typing import Any, cast

from flask import Blueprint, request

from gestaolegal.exceptions import ValidationException
from gestaolegal.models.plantao_input import ConfiguracaoPlantaoInput, MarcarDiaInput
from gestaolegal.services.plantao_service import PlantaoService
from gestaolegal.utils.api_decorators import authenticated, authorized
from gestaolegal.utils.api_response import success_response
from gestaolegal.utils.request_context import RequestContext

plantao_controller = Blueprint("plantao_api", __name__)


def _service():
    valor = request.args.get("escala_id")
    if valor is not None and (
        len(valor) > 10
        or not valor.isascii()
        or not valor.isdigit()
        or not 0 < int(valor) <= 2147483647
    ):
        raise ValidationException("Escala inválida.", field="escala_id")
    return PlantaoService(int(valor) if valor is not None else None)


@plantao_controller.route("/escalas", methods=["GET"])
@authenticated
def listar_escalas():
    return success_response(data=PlantaoService().listar_escalas())


@plantao_controller.route("/escalas", methods=["POST"])
@authorized("admin", "colab_proj")
def criar_escala():
    dados = ConfiguracaoPlantaoInput.model_validate(request.get_json(force=True))
    result = PlantaoService().salvar_configuracao(
        dados, RequestContext.get_current_user().id, criar=True
    )
    return success_response(data=result, status_code=201, message="Escala criada")


@plantao_controller.route("/escalas/<int:escala_id>/cancelar", methods=["POST"])
@authorized("admin", "colab_proj")
def cancelar_escala(escala_id):
    return success_response(
        data=PlantaoService(escala_id).cancelar(RequestContext.get_current_user().id)
    )


@plantao_controller.route("/", methods=["GET"])
@authenticated
def get_pagina():
    service = _service()
    return success_response(data=service.get_pagina(RequestContext.get_current_user()))


@plantao_controller.route("/marcacoes", methods=["POST"])
@authenticated
def marcar_dia():
    json_data = cast(dict[str, Any], request.get_json(force=True))
    dados = MarcarDiaInput.model_validate(json_data)

    service = _service()
    pagina = service.marcar_dia(dados, RequestContext.get_current_user())

    return success_response(
        data=pagina,
        message="Data de plantão cadastrada!",
        status_code=201,
    )


@plantao_controller.route("/marcacoes", methods=["DELETE"])
@authenticated
def limpar_marcacoes():
    service = _service()
    pagina = service.limpar_marcacoes(RequestContext.get_current_user())
    return success_response(
        data=pagina,
        message="Registro apagado. Selecione novamente os dias do seu plantão.",
    )


@plantao_controller.route("/configuracao", methods=["GET"])
@authorized("admin", "colab_proj")
def get_configuracao():
    service = _service()
    return success_response(data=service.get_configuracao())


@plantao_controller.route("/configuracao", methods=["PUT"])
@authorized("admin", "colab_proj")
def salvar_configuracao():
    json_data = cast(dict[str, Any], request.get_json(force=True))
    dados = ConfiguracaoPlantaoInput.model_validate(json_data)

    service = _service()
    configuracao = service.salvar_configuracao(
        dados, executor_id=RequestContext.get_current_user().id
    )

    return success_response(
        data=configuracao, message="Configuração do plantão salva com sucesso"
    )
