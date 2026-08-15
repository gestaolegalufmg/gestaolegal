from datetime import date
from typing import Any, cast

from flask import Blueprint, request

from gestaolegal.exceptions import ValidationException
from gestaolegal.models.presenca_input import (
    ConfirmacaoBatchInput,
    RegistrarPresencaInput,
)
from gestaolegal.services.presenca_service import PresencaService
from gestaolegal.utils.api_decorators import authenticated, authorized
from gestaolegal.utils.api_response import success_response
from gestaolegal.utils.request_context import RequestContext

presenca_controller = Blueprint("presenca_api", __name__)


@presenca_controller.route("/registro", methods=["GET"])
@authenticated
def get_registro():
    service = PresencaService()
    return success_response(data=service.get_estado(RequestContext.get_current_user()))


@presenca_controller.route("/registro", methods=["POST"])
@authenticated
def registrar():
    json_data = cast(dict[str, Any], request.get_json(force=True))
    dados = RegistrarPresencaInput.model_validate(json_data)

    service = PresencaService()
    estado = service.registrar(dados, RequestContext.get_current_user())

    mensagem = (
        "Hora de saída registrada com sucesso!"
        if estado["acao"] == "saida"
        else "Hora de entrada registrada com sucesso!"
    )
    return success_response(data=estado, message=mensagem)


@presenca_controller.route("/confirmacao", methods=["GET"])
@authorized("admin", "colab_proj", "prof")
def get_confirmacao():
    parametro = request.args.get("data")
    dia = None
    if parametro:
        try:
            dia = date.fromisoformat(parametro)
        except ValueError:
            raise ValidationException(
                "Data inválida, use o formato AAAA-MM-DD", field="data"
            )

    service = PresencaService()
    return success_response(data=service.listar_para_confirmacao(dia))


@presenca_controller.route("/confirmacao", methods=["POST"])
@authorized("admin", "colab_proj", "prof")
def salvar_confirmacao():
    json_data = cast(dict[str, Any], request.get_json(force=True))
    dados = ConfirmacaoBatchInput.model_validate(json_data)

    service = PresencaService()
    resultado = service.confirmar_em_lote(dados)

    return success_response(data=resultado, message="Conferência salva com sucesso")
