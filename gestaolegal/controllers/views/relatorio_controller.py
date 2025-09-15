import logging

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
)
from flask_login import current_user

from gestaolegal.common.constants import (
    UserRole,
)
from gestaolegal.forms.relatorio import RelatorioForm
from gestaolegal.services.relatorio_service import RelatorioService
from gestaolegal.utils.decorators import login_required

logger = logging.getLogger(__name__)

relatorios_controller = Blueprint(
    "relatorios", __name__, template_folder="../../static/templates"
)


@relatorios_controller.route("/", methods=["POST", "GET"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_EXTERNO,
    ]
)
def index():  # vai listar os dados como o select2 entende
    form = RelatorioForm()
    if request.method == "POST":
        relatorio_service = RelatorioService()
        redirect_url = relatorio_service.process_relatorio_form(form)

        if redirect_url:
            return redirect(redirect_url)

    return render_template("relatorios/pagina_relatorios.html", form=form)


@relatorios_controller.route("/casos_orientacao_juridica/<inicio>/<final>/<areas>")
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_EXTERNO,
    ]
)
def casos_orientacao_juridica(inicio, final, areas):
    relatorio_service = RelatorioService()

    report_data = relatorio_service.get_casos_orientacao_report_data(
        inicio=inicio, final=final, areas=areas, current_user=current_user
    )

    return render_template(
        "relatorios/relatorio_casos_orientacao.html",
        orientacoes_juridicas=report_data["orientacoes_juridicas"],
        data_emissao=report_data["data_emissao"],
        usuario=report_data["usuario"],
        datas=report_data["datas"],
    )


@relatorios_controller.route(
    "/casos_cadastrados/<inicio>/<final>/<areas>", methods=["POST", "GET"]
)
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_EXTERNO,
    ]
)
def casos_cadastrados(inicio, final, areas):
    relatorio_service = RelatorioService()

    report_data = relatorio_service.get_casos_cadastrados_report_data(
        inicio=inicio, final=final, areas=areas, current_user=current_user
    )

    return render_template(
        "relatorios/relatorio_casos_cadastrados.html",
        casos=report_data["casos"],
        data_emissao=report_data["data_emissao"],
        usuario=report_data["usuario"],
        datas=report_data["datas"],
    )


@relatorios_controller.route("/relatorio_horarios/<inicio>/<final>/<usuarios>")
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_EXTERNO,
    ]
)
def relatorio_horarios(inicio, final, usuarios):
    relatorio_service = RelatorioService()

    report_data = relatorio_service.get_relatorio_horarios_data(
        inicio=inicio, final=final, usuarios=usuarios, current_user=current_user
    )

    return render_template(
        "relatorios/relatorio_horarios.html",
        data_emissao=report_data["data_emissao"],
        usuario=report_data["usuario"],
        horarios=report_data["horarios"],
        datas=report_data["datas"],
        horarios_plantao=report_data["horarios_plantao"],
    )


@relatorios_controller.route("/casos_arq_sol_ativ/<inicio>/<final>/<areas>")
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_EXTERNO,
    ]
)
def casos_arq_sol_ativ(inicio, final, areas):
    relatorio_service = RelatorioService()

    report_data = relatorio_service.get_casos_arq_sol_ativ_report_data(
        inicio=inicio, final=final, areas=areas, current_user=current_user
    )

    return render_template(
        "relatorios/relatorio_casos_status.html",
        casos=report_data["casos"],
        data_emissao=report_data["data_emissao"],
        usuario=report_data["usuario"],
        datas=report_data["datas"],
    )


@relatorios_controller.route("/relatorio_plantao", methods=["GET", "POST"])
@login_required()
def relatorio_plantao():
    relatorio_service = RelatorioService()

    if request.method == "POST":
        result = relatorio_service.process_relatorio_plantao_request(request.form)
        if result:
            return result

    return render_template("relatorio_plantao.html")


@relatorios_controller.route("/relatorio_casos", methods=["GET", "POST"])
@login_required()
def relatorio_casos():
    relatorio_service = RelatorioService()

    if request.method == "POST":
        result = relatorio_service.process_relatorio_casos_request(request.form)
        if result:
            return result

    return render_template("relatorio_casos.html")


@relatorios_controller.route("/relatorio_usuarios", methods=["GET", "POST"])
@login_required()
def relatorio_usuarios():
    relatorio_service = RelatorioService()

    if request.method == "POST":
        report_data = relatorio_service.get_relatorio_usuarios_data(request.form)
        return render_template(
            "relatorio_usuarios.html",
            usuarios=report_data["usuarios"],
            data_inicio=report_data["data_inicio"],
            data_fim=report_data["data_fim"],
        )

    return render_template("relatorio_usuarios.html")
