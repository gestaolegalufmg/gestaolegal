from flask import Blueprint, flash, redirect, render_template, request
from sqlalchemy import and_, or_

from gestaolegal import app, login_required
from gestaolegal.casos.models import Caso
from gestaolegal.plantao.models import Assistido, AssistidoPessoaJuridica, Atendido
from gestaolegal.usuario.models import Usuario

principal = Blueprint("principal", __name__, template_folder="templates")


@principal.route("/")
@login_required()
def index():
    return render_template("home.html")


@app.errorhandler(404)
def error_404(error):
    return render_template("erros/404.html"), 404


@app.errorhandler(413)
def error_413(error):
    flash("Arquivo muito grande. O tamanho máximo permitido é de 10MB.")
    return redirect(request.url, code=302)


@app.errorhandler(403)
def error_403(error):
    return render_template("erros/403.html"), 403


@app.errorhandler(500)
def error_500(error):
    return render_template("erros/500.html"), 403


@principal.route("/termos_de_uso")
@login_required()
def termos():
    return render_template("termos_de_uso.html")


@principal.route("/busca_geral", methods=["GET", "POST"])
@login_required()
def busca_geral():
    page_assistido_pfisica = request.args.get("page_assistido_pfisica", 1, type=int)
    page_assistido_pjuridica = request.args.get("page_assistido_pjuridica", 1, type=int)
    page_usuario = request.args.get("page_usuario", 1, type=int)
    page_caso = request.args.get("page_caso", 1, type=int)

    if request.method == "POST":
        busca = request.form["busca_geral"]
    else:
        busca = request.args.get("busca_atual", "", type=str)

    assistidos = (
        Atendido.query.join(Assistido)
        .filter(or_(Atendido.nome.contains(busca), Atendido.cpf.contains(busca)))
        .order_by("nome")
        .paginate(
            page=page_assistido_pfisica,
            per_page=app.config["ATENDIDOS_POR_PAGINA"],
            error_out=False,
        )
    )

    assistidos_pjuridica = (
        Atendido.query.join(Assistido)
        .join(AssistidoPessoaJuridica)
        .filter(or_(Atendido.nome.contains(busca), Atendido.cpf.contains(busca)))
        .order_by("nome")
        .paginate(
            page=page_assistido_pjuridica,
            per_page=app.config["ATENDIDOS_POR_PAGINA"],
            error_out=False,
        )
    )

    usuarios = (
        db.session.query(Usuario)
        .filter(
            or_(
                and_(Usuario.nome.contains(busca), Usuario.status != False),
                and_(Usuario.cpf.contains(busca), Usuario.status != False),
            )
        )
        .order_by("nome")
        .paginate(
            page=page_usuario,
            per_page=app.config["USUARIOS_POR_PAGINA"],
            error_out=False,
        )
    )

    casos = None
    if busca.isdigit():
        casos = (
            db.session.query(Caso)
            .filter_by(status=True, id=int(busca))
            .paginate(
                page=page_caso, per_page=app.config["CASOS_POR_PAGINA"], error_out=False
            )
        )

    return render_template(
        "busca_geral.html",
        assistidos=assistidos,
        assistidos_pjuridica=assistidos_pjuridica,
        usuarios=usuarios,
        casos=casos,
        busca_atual=busca,
    )
