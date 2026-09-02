from flask import Blueprint, request

from gestaolegal.exceptions import ValidationException
from gestaolegal.services.relatorio_service import RelatorioService
from gestaolegal.utils.api_decorators import authorized
from gestaolegal.utils.api_response import success_response

relatorio_controller = Blueprint("relatorio_api", __name__)

ALLOWED_ROLES = ("admin", "orient", "colab_ext")


def _params() -> tuple[str, str, str | None]:
    data_inicio = request.args.get("data_inicio", type=str)
    data_final = request.args.get("data_final", type=str)
    areas = request.args.get("areas", default=None, type=str)
    if not data_inicio or not data_final:
        raise ValidationException(
            "Informe data_inicio e data_final.", field="data_inicio"
        )
    return data_inicio, data_final, areas


@relatorio_controller.route("/casos-cadastrados", methods=["GET"])
@authorized(*ALLOWED_ROLES)
def casos_cadastrados():
    data_inicio, data_final, areas = _params()
    result = RelatorioService().casos_cadastrados(data_inicio, data_final, areas)
    return success_response(data=result)


@relatorio_controller.route("/casos-por-status", methods=["GET"])
@authorized(*ALLOWED_ROLES)
def casos_por_status():
    data_inicio, data_final, areas = _params()
    result = RelatorioService().casos_por_status(data_inicio, data_final, areas)
    return success_response(data=result)


@relatorio_controller.route("/casos-por-orientacao", methods=["GET"])
@authorized(*ALLOWED_ROLES)
def casos_por_orientacao():
    data_inicio, data_final, areas = _params()
    result = RelatorioService().casos_por_orientacao(data_inicio, data_final, areas)
    return success_response(data=result)


@relatorio_controller.route("/usuarios", methods=["GET"])
@authorized(*ALLOWED_ROLES)
def usuarios_disponiveis():
    """Usuários ativos para filtrar o relatório de horários.

    Existe porque a listagem geral de usuários é restrita ao admin, e o
    relatório também pode ser gerado por orientadores e colaboradores externos.
    """
    return success_response(data={"items": RelatorioService().usuarios_disponiveis()})


@relatorio_controller.route("/horarios", methods=["GET"])
@authorized(*ALLOWED_ROLES)
def horarios():
    data_inicio = request.args.get("data_inicio", type=str)
    data_final = request.args.get("data_final", type=str)
    usuarios = request.args.get("usuarios", default=None, type=str)
    if not data_inicio or not data_final:
        raise ValidationException(
            "Informe data_inicio e data_final.", field="data_inicio"
        )
    result = RelatorioService().horarios(data_inicio, data_final, usuarios)
    return success_response(data=result)
