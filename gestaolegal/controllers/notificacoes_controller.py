from flask import Blueprint, current_app, redirect, render_template, request, url_for
from flask_login import current_user

from gestaolegal.database import get_db
from gestaolegal.services.notificacao_service import NotificacaoService
from gestaolegal.utils.decorators import login_required

notificacoes_controller = Blueprint(
    "notificacoes", __name__, template_folder="../templates/notificacoes"
)


@notificacoes_controller.route("/")
@login_required()
def index():
    db = get_db()
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["ATENDIDOS_POR_PAGINA"]

    def paginator(query):
        return db.paginate(
            query,
            page=page,
            per_page=per_page,
            error_out=False,
        )

    notificacao_service = NotificacaoService()
    notificacoes = notificacao_service.get_notificacoes_for_user(
        current_user.id, current_user.urole, paginator
    )

    return render_template("notificacoes.html", notificacoes=notificacoes)


@notificacoes_controller.route("/pagina/<notificacao_acao>")
@login_required()
def pagina(notificacao_acao):
    splitted = notificacao_acao.split(" ")

    if splitted[2] == "plantão":
        return redirect(url_for("plantao.pg_plantao"))

    elif splitted[2] == "caso":
        return redirect(url_for("casos.visualizar_caso", id=int(splitted[3])))

    elif splitted[2] == "evento":
        return redirect(
            url_for(
                "casos.visualizar_evento",
                num_evento=int(splitted[3]),
                id_caso=int(splitted[6]),
            )
        )
    return redirect(
        url_for(
            "casos.lembretes", id_caso=int(splitted[6]), num_lembrete=int(splitted[3])
        )
    )
