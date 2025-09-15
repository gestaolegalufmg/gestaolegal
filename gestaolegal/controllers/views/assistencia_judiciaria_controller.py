import logging

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from gestaolegal.common.constants import UserRole, assistencia_jud_areas_atendidas
from gestaolegal.forms.plantao.assistencia_juridica_form import (
    AssistenciaJudiciariaForm,
)
from gestaolegal.common import PageParams
from gestaolegal.services.assistencia_judiciaria_service import AssistenciaJudiciariaService
from gestaolegal.utils.decorators import login_required

filtro_busca_assistencia_judiciaria = assistencia_jud_areas_atendidas.copy()
filtro_busca_assistencia_judiciaria["TODAS"] = ("todas", "Todas")

logger = logging.getLogger(__name__)

assistencia_judiciaria_controller = Blueprint(
    "assistencia_judiciaria",
    __name__,
    template_folder="../../static/templates",
)


@assistencia_judiciaria_controller.route(
    "/encaminha_assistencia_judiciaria/<int:id_orientacao>", methods=["POST", "GET"]
)
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.PROFESSOR,
    ]
)
def encaminha_assistencia_judiciaria(id_orientacao: int):
    assistencia_judiciaria_service = AssistenciaJudiciariaService()

    if request.method == "GET":
        form_data = assistencia_judiciaria_service.get_encaminhar_assistencia_data(
            id_orientacao
        )

        if not form_data["success"]:
            abort(404)

        return render_template(
            "assistencia_judiciaria/encaminhar_assistencia.html",
            form=form_data["form"],
            id_orientacao=id_orientacao,
        )

    try:
        form = AssistenciaJudiciariaForm()
        form_data = form.to_dict()

        assistencia_judiciaria_service.create(form_data)

        flash("Assistência judiciária cadastrada e associada com sucesso!", "success")
        return render_template(
            "assistencia_judiciaria/lista_assistencias_judiciarias.html"
        )

    except Exception as e:
        logger.error(
            f"Error in encaminha_assistencia_judiciaria: {str(e)}", exc_info=True
        )
        flash(f"Erro ao encaminhar assistência judiciária: {str(e)}", "error")
        return render_template(
            "assistencia_judiciaria/encaminhar_assistencia.html",
            form=form,
            id_orientacao=id_orientacao,
        )


@assistencia_judiciaria_controller.route(
    "/excluir_assistencia_judiciaria/<int:id>", methods=["POST"]
)
@login_required(role=[UserRole.ADMINISTRADOR])
def excluir_assistencia_judiciaria(id: int):
    assistencia_judiciaria_service = AssistenciaJudiciariaService()

    assistencia = assistencia_judiciaria_service.find_by_id(id)

    if not assistencia:
        flash("Assistência judiciária não encontrada!", "warning")
        return redirect(
            url_for("assistencia_judiciaria.listar_assistencias_judiciarias")
        )

    assistencia_judiciaria_service.soft_delete(id)
    flash("Assistência judiciária excluída com sucesso!", "success")
    return redirect(url_for("assistencia_judiciaria.listar_assistencias_judiciarias"))


@assistencia_judiciaria_controller.route(
    "/busca_assistencia_judiciaria/", methods=["GET", "POST"]
)
@login_required()
def busca_assistencia_judiciaria():
    assistencia_judiciaria_service = AssistenciaJudiciariaService()

    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["ATENDIDOS_POR_PAGINA"]
    page_params = PageParams(page=page, per_page=per_page)

    _busca = request.args.get("busca", "", type=str)
    filtro = request.args.get(
        "opcao_filtro", filtro_busca_assistencia_judiciaria["TODAS"][0], type=str
    )

    assistencias = assistencia_judiciaria_service.get_by_areas_atendida(
        filtro, _busca, page_params=page_params
    )

    return render_template(
        "assistencia_judiciaria/buscar_assistencia.html", assistencias=assistencias
    )


@assistencia_judiciaria_controller.route("/perfil_assistencia_judiciaria/<_id>")
@login_required()
def perfil_assistencia_judiciaria(_id: int):
    assistencia_judiciaria_service = AssistenciaJudiciariaService()
    assistencia_judiciaria = assistencia_judiciaria_service.find_by_id(_id)

    if assistencia_judiciaria is None:
        flash("Assistência judiciária não encontrada.", "warning")
        return redirect(
            url_for("assistencia_judiciaria.listar_assistencias_judiciarias")
        )
    return render_template(
        "assistencia_judiciaria/visualizar_assistencia.html", aj=assistencia_judiciaria
    )


@assistencia_judiciaria_controller.route(
    "/assistencias_judiciarias/", methods=["POST", "GET"]
)
@login_required()
def listar_assistencias_judiciarias():
    assistencia_judiciaria_service = AssistenciaJudiciariaService()

    page = request.args.get("page", 1, type=int)
    busca = request.args.get("busca", "", type=str)
    opcao_filtro = request.args.get(
        "opcao_filtro", filtro_busca_assistencia_judiciaria["TODAS"][0], type=str
    )
    per_page = current_app.config["ATENDIDOS_POR_PAGINA"]
    page_params = PageParams(page=page, per_page=per_page)

    if busca or opcao_filtro != filtro_busca_assistencia_judiciaria["TODAS"][0]:
        assistencias = assistencia_judiciaria_service.get_by_areas_atendida(
            opcao_filtro, busca, page_params=page_params
        )
    else:
        assistencias = assistencia_judiciaria_service.get_all(page_params=page_params)

    return render_template(
        "assistencia_judiciaria/listagem_assistencias.html",
        assistencias=assistencias,
        filtro_busca_assistencia_judiciaria=filtro_busca_assistencia_judiciaria,
        busca=busca,
        opcao_filtro=opcao_filtro,
    )


@assistencia_judiciaria_controller.route(
    "/editar_assistencia_judiciaria/<int:id_assistencia_judiciaria>",
    methods=["POST", "GET"],
)
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_PROJETO,
        UserRole.COLAB_EXTERNO,
    ]
)
def editar_assistencia_judiciaria(id_assistencia_judiciaria: int):
    assistencia_judiciaria_service = AssistenciaJudiciariaService()

    if request.method == "POST":
        form = AssistenciaJudiciariaForm()
        assistencia_judiciaria_data = form.to_dict()

        assistencia_judiciaria_service.update(
            id_assistencia_judiciaria=id_assistencia_judiciaria,
            assistencia_judiciaria_data=assistencia_judiciaria_data,
        )

        flash("Assistência judiciária editada com sucesso!", "success")
        return redirect(
            url_for("assistencia_judiciaria.listar_assistencias_judiciarias")
        )

    assistencia = assistencia_judiciaria_service.find_by_id(id_assistencia_judiciaria)
    if not assistencia:
        abort(404)

    # Type assertion: we know assistencia is not None after the check above
    assert assistencia is not None
    form = AssistenciaJudiciariaForm(data=assistencia.to_dict())

    return render_template("assistencia_judiciaria/editar_assistencia.html", form=form)


@assistencia_judiciaria_controller.route(
    "/cadastro_assistencia_judiciaria", methods=["GET", "POST"]
)
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_PROJETO,
        UserRole.COLAB_EXTERNO,
    ]
)
def cadastro_assistencia_judiciaria():
    assistencia_judiciaria_service = AssistenciaJudiciariaService()
    form = AssistenciaJudiciariaForm()

    if request.method == "POST":
        try:
            assistencia_judiciaria_service.create(form)
            flash("Assistência judiciária cadastrada com sucesso!", "success")
            return redirect(
                url_for("assistencia_judiciaria.listar_assistencias_judiciarias")
            )
        except Exception as e:
            flash(str(e), "error")

    return render_template(
        "assistencia_judiciaria/cadastrar_assistencia.html", form=form
    )


@assistencia_judiciaria_controller.route(
    "/buscar_assistencia_judiciaria", methods=["POST"]
)
@login_required()
def buscar_assistencia_judiciaria():
    assisistencia_judiciaria_service = AssistenciaJudiciariaService()

    termo = request.form.get("termo", "")
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["ATENDIDOS_POR_PAGINA"]

    page_params = PageParams(page=page, per_page=per_page)

    assistencias = assisistencia_judiciaria_service.get_by_name(
        termo, page_params=page_params
    )

    return render_template(
        "assistencia_judiciaria/listagem_assistencias.html",
        assistencias=assistencias,
        filtro_busca_assistencia_judiciaria=filtro_busca_assistencia_judiciaria,
    )
