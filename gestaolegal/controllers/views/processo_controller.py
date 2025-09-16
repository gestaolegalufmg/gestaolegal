import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from gestaolegal.common.constants import UserRole
from gestaolegal.forms.relatorio import ProcessoForm
from gestaolegal.services.processo_service import ProcessoService
from gestaolegal.utils.decorators import login_required

logger = logging.getLogger(__name__)

processo_controller = Blueprint(
    "processo", __name__, template_folder="../../static/templates"
)


@processo_controller.route("/novo_processo/<id_caso>", methods=["POST", "GET"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ORIENTADOR,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.COLAB_EXTERNO,
        UserRole.PROFESSOR,
    ]
)
def novo_processo(id_caso):
    processo_service = ProcessoService()

    form = ProcessoForm()

    if request.method == "POST":
        try:
            processo_service.create(
                processo_data=form.to_dict(),
            )

            flash("Processo associado com sucesso!", "success")
            return redirect(url_for("casos.visualizar_caso", id=id_caso))
        except Exception as e:
            flash(e, "error")
            return render_template("casos/processos/cadastrar_processo.html", form=form)

    return render_template("casos/processos/cadastrar_processo.html", form=form)


@processo_controller.route("/processo/<int:id_processo>", methods=["GET"])
@login_required()
def visualizar_processo(id_processo):
    processo_service = ProcessoService()

    id_caso = request.args.get("id_caso", -1, type=int)

    processo = processo_service.find_by_id(int(id_processo))

    return render_template(
        "casos/processos/visualizar_processo.html", processo=processo, id_caso=id_caso
    )


@processo_controller.route(
    "/visualizar_processo_com_numero/<int:numero_processo>", methods=["GET"]
)
@login_required()
def visualizar_processo_com_numero(numero_processo):
    processo_service = ProcessoService()
    processo = processo_service.get_processo_by_numero(int(numero_processo))

    return render_template(
        "casos/processos/visualizar_processo.html",
        processo=processo,
        id_caso=processo.id_caso,
    )


@processo_controller.route("/excluir_processo/<id_processo>", methods=["GET", "POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ORIENTADOR,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.COLAB_EXTERNO,
    ]
)
def excluir_processo(id_processo):
    processo_service = ProcessoService()

    id_caso = request.args.get("id_caso", -1, type=int)

    if not processo_service.validate_processo_permission(
        int(id_processo), current_user.id, current_user.urole
    ):
        flash("Você não pode excluir este processo.", "warning")
        return redirect(url_for("casos.visualizar_caso", id=id_caso))

    try:
        processo_service.delete(int(id_processo))
        flash("Processo excluído!", "success")
    except Exception as e:
        logger.error(f"Error deleting processo: {str(e)}", exc_info=True)
        flash("Erro ao excluir processo. Tente novamente.", "danger")

    return redirect(url_for("casos.visualizar_caso", id=id_caso))


@processo_controller.route("/editar_processo/<id_processo>", methods=["POST", "GET"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ORIENTADOR,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.COLAB_EXTERNO,
    ]
)
def editar_processo(id_processo):
    processo_service = ProcessoService()

    if request.method == "POST":
        try:
            processo = processo_service.update_processo(
                processo_id=int(id_processo),
                processo_data=request.form.to_dict(),
            )

            flash("Processo editado com sucesso!", "success")
            return redirect(
                url_for(
                    "casos.visualizar_processo",
                    id_processo=id_processo,
                    id_caso=processo.id_caso,
                )
            )
        except Exception as e:
            logger.error(f"Error updating processo: {str(e)}", exc_info=True)
            flash(f"Erro ao editar processo: {str(e)}", "error")
            return redirect(url_for("casos.editar_processo", id_processo=id_processo))

    processo_data = processo_service.find_by_id(int(id_processo))
    form = ProcessoForm(data=processo_data.to_dict())

    return render_template(
        "casos/processos/editar_processo.html",
        form=form,
        id_processo=id_processo,
    )
