import logging
from dataclasses import dataclass

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user

from gestaolegal.common.constants import UserRole
from gestaolegal.forms import AbrirPlantaoForm, FecharPlantaoForm, SelecionarDuracaoPlantaoForm
from gestaolegal.services.plantao_service import PlantaoService
from gestaolegal.utils.decorators import login_required

logger = logging.getLogger(__name__)


@dataclass
class CardInfo:
    title: str
    body: dict[str, str | None] | str


plantao_controller = Blueprint(
    "plantao", __name__, template_folder="../../static/templates"
)


@plantao_controller.route("/pagina_plantao", methods=["POST", "GET"])
@login_required()
def pg_plantao():
    logger.info("Entering pg_plantao route")
    plantao_service = PlantaoService()

    try:
        page_data = plantao_service.get_plantao_page_data(
            current_user.id, current_user.urole
        )

        if not page_data["access_granted"]:
            flash(page_data["message"], "warning")
            return redirect(url_for("principal.index"))

        return render_template(
            "plantao/pagina_plantao.html",
            datas_plantao=page_data["dias_usuario_atual"],
            numero_plantao=page_data["numero_plantao"],
            data_atual=page_data["data_atual"],
        )
    except AttributeError:
        flash("O plantão não está aberto!")
        return redirect(url_for("principal.index"))


@plantao_controller.route("/editar_plantao", methods=["GET"])
@login_required()
def editar_plantao():
    plantao_service = PlantaoService()

    success, message = plantao_service.apagar_dias_marcados_usuario(current_user.id)

    if success:
        flash(message, "success")
    else:
        flash(message, "error")

    return redirect(url_for("plantao.pg_plantao"))


@plantao_controller.route("/registro_presenca")
@login_required()
def reg_presenca():
    plantao_service = PlantaoService()
    status_data = plantao_service.get_status_presenca_usuario(current_user.id)

    return render_template(
        "plantao/registro_presenca.html",
        data_hora_atual=status_data["data_hora_atual"],
        status_presenca=status_data["status_presenca"],
    )


@plantao_controller.route("/confirmar_presenca", methods=["POST", "GET"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.COLAB_PROJETO,
        UserRole.PROFESSOR,
    ]
)
def confirmar_presenca():
    plantao_service = PlantaoService()

    if request.method == "POST":
        dados_cru = request.form.to_dict()
        if not plantao_service.confirmar_presencas(dados_cru):
            flash("Erro ao confirmar presenças", "error")

    presencas_data = plantao_service.get_presencas_para_confirmacao()

    return render_template(
        "plantao/confirmar_presenca.html",
        presencas_registradas=presencas_data["presencas_registradas"],
        plantoes_registradas=presencas_data["plantoes_registradas"],
        data_ontem=presencas_data["data_ontem"],
    )


@plantao_controller.route("/configurar_abertura", methods=["POST", "GET"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.COLAB_PROJETO,
    ]
)
def configurar_abertura():
    plantao_service = PlantaoService()

    form_abrir = AbrirPlantaoForm()
    form_fechar = FecharPlantaoForm()
    _form = SelecionarDuracaoPlantaoForm()

    config_data = plantao_service.get_configuracao_abertura_data()

    if not config_data["access_granted"]:
        flash(config_data["message"], "warning")
        return redirect(url_for("principal.index"))

    plantao_service.populate_forms(form_abrir, form_fechar, config_data["plantao"])

    return render_template(
        "plantao/configurar_plantao.html",
        form_fechar=form_fechar,
        form_abrir=form_abrir,
        periodo=config_data["periodo"],
        form=_form,
        dias_front=config_data["dias_front"],
    )


@plantao_controller.route("/fila-atendimento", methods=["GET", "POST"])
@login_required()
def fila_atendimento():
    return render_template("plantao/fila_atendimento.html")
