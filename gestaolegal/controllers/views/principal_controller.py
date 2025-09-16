import logging

from flask import Blueprint, current_app, flash, redirect, render_template, request

from gestaolegal.services.principal_service import PrincipalService
from gestaolegal.utils.decorators import login_required

logger = logging.getLogger(__name__)

principal_controller = Blueprint(
    "principal", __name__, template_folder="../../static/templates"
)


@principal_controller.route("/")
@login_required()
def index():
    return render_template("principal/home.html")


@principal_controller.errorhandler(404)
def error_404(error):
    logger.warning(f"404 error: {request.url} - {error}")
    return render_template("principal/erros/404.html"), 404


@principal_controller.errorhandler(413)
def error_413(error):
    logger.warning(f"413 error - File too large: {request.url}")
    flash("Arquivo muito grande. O tamanho máximo permitido é de 10MB.")
    return redirect(request.url, code=302)


@principal_controller.errorhandler(403)
def error_403(error):
    logger.warning(f"403 error - Forbidden: {request.url}")
    return render_template("principal/erros/403.html"), 403


@principal_controller.errorhandler(500)
def error_500(error):
    logger.error(
        f"500 error - Internal server error: {request.url} - {error}", exc_info=True
    )
    return render_template("principal/erros/500.html"), 500


@principal_controller.route("/termos_de_uso")
@login_required()
def termos():
    return render_template("principal/termos_uso.html")


@principal_controller.route("/busca_geral", methods=["GET", "POST"])
@login_required()
def busca_geral():
    principal_service = PrincipalService()

    page_assistido_pfisica = request.args.get("page_assistido_pfisica", 1, type=int)
    page_assistido_pjuridica = request.args.get("page_assistido_pjuridica", 1, type=int)
    page_usuario = request.args.get("page_usuario", 1, type=int)
    page_caso = request.args.get("page_caso", 1, type=int)

    if request.method == "POST":
        busca = request.form["busca_geral"]
    else:
        busca = request.args.get("busca_atual", "", type=str)

    search_results = principal_service.busca_geral(
        busca=busca,
        page_assistido_pfisica=page_assistido_pfisica,
        page_assistido_pjuridica=page_assistido_pjuridica,
        page_usuario=page_usuario,
        page_caso=page_caso,
        per_page_assistido=current_app.config["ATENDIDOS_POR_PAGINA"],
        per_page_usuario=current_app.config["USUARIOS_POR_PAGINA"],
        per_page_caso=current_app.config["CASOS_POR_PAGINA"],
    )

    return render_template(
        "principal/busca_geral.html",
        assistidos=search_results["assistidos"],
        assistidos_pjuridica=search_results["assistidos_pjuridica"],
        usuarios=search_results["usuarios"],
        casos=search_results["casos"],
        orientacoes_juridicas=search_results["orientacoes_juridicas"],
        busca_atual=busca,
    )
