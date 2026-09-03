from dataclasses import asdict

from flask import Blueprint, request

from gestaolegal.common import PageParams
from gestaolegal.services.notificacao_service import NotificacaoService
from gestaolegal.utils.api_decorators import authenticated
from gestaolegal.utils.api_response import success_response
from gestaolegal.utils.request_context import RequestContext

notificacao_controller = Blueprint("notificacao", __name__)


@notificacao_controller.route("/", methods=["GET"])
@authenticated
def listar():
    user = RequestContext.get_current_user()
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    result = NotificacaoService().listar(user, PageParams(page=page, per_page=per_page))
    return success_response(data=result.to_dict())


@notificacao_controller.route("/nao-lidas", methods=["GET"])
@authenticated
def nao_lidas():
    user = RequestContext.get_current_user()
    return success_response(data={"total": NotificacaoService().contar_nao_lidas(user)})


@notificacao_controller.route("/<int:id>/lida", methods=["PATCH"])
@authenticated
def marcar_lida(id: int):
    user = RequestContext.get_current_user()
    NotificacaoService().marcar_lida(id, user)
    return success_response(message="Notificação marcada como lida")


@notificacao_controller.route("/lidas", methods=["PATCH"])
@authenticated
def marcar_todas_lidas():
    user = RequestContext.get_current_user()
    total = NotificacaoService().marcar_todas_lidas(user)
    return success_response(data={"total": total}, message="Notificações marcadas como lidas")
