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

from gestaolegal.common.constants import UserRole
from gestaolegal.forms.plantao.orientacao_juridica_form import (
    CadastroOrientacaoJuridicaForm,
)
from gestaolegal.common import PageParams
from gestaolegal.services.orientacao_juridica_service import OrientacaoJuridicaService
from gestaolegal.utils.decorators import login_required

logger = logging.getLogger(__name__)

orientacao_juridica_controller = Blueprint(
    "orientacao_juridica", __name__, template_folder="../../static/templates"
)


@orientacao_juridica_controller.route("/excluir_orientacao_juridica/", methods=["POST"])
@login_required(role=[UserRole.ADMINISTRADOR])
def excluir_oj():
    orientacao_juridica_service = OrientacaoJuridicaService()

    id_orientacao = request.form.get("id_orientacao")
    orientacao = orientacao_juridica_service.find_by_id(id_orientacao)
    if not orientacao:
        abort(404)
    orientacao_juridica_service.soft_delete(id_orientacao)
    flash("Orientação jurídica excluída com sucesso!", "success")
    return redirect(url_for("orientacao_juridica.orientacoes_juridicas"))


@orientacao_juridica_controller.route(
    "/editar_orientacao_juridica/<id_oj>", methods=["POST", "GET"]
)
@login_required(role=[UserRole.ADMINISTRADOR, UserRole.PROFESSOR])
def editar_orientacao_juridica(id_oj: int):
    orientacao_juridica_service = OrientacaoJuridicaService()

    if request.method == "POST":
        try:
            orientacao_juridica_service.update_orientacao_juridica(
                id_oj=id_oj, form=request.form
            )
            flash("Orientação jurídica editada com sucesso!", "success")
            return redirect(url_for("orientacao_juridica.orientacoes_juridicas"))
        except Exception as e:
            flash(str(e), "warning")
            form_data = orientacao_juridica_service.get_editar_orientacao_data(id_oj)
            return render_template(
                "orientacao_juridica/editar_orientacao.html",
                form=form_data["form"],
                orientacao=form_data["orientacao"],
            )

    form_data = orientacao_juridica_service.get_editar_orientacao_data(id_oj)

    if not form_data:
        flash("Orientação jurídica não encontrada", "warning")
        return redirect(url_for("orientacao_juridica.orientacoes_juridicas"))

    return render_template(
        "orientacao_juridica/editar_orientacao.html",
        form=form_data["form"],
        orientacao=form_data["orientacao"],
    )


@orientacao_juridica_controller.route("/buscar_orientacao_juridica", methods=["POST"])
@login_required()
def buscar_orientacao_juridica():
    orientacao_juridica_service = OrientacaoJuridicaService()

    termo = request.form.get("termo", "")
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["ATENDIDOS_POR_PAGINA"]

    orientacoes = orientacao_juridica_service.get_by_area_do_direito(
        termo, page_params=PageParams(page=page, per_page=per_page)
    )

    return render_template(
        "orientacao_juridica/listagem_orientacoes.html", orientacoes=orientacoes
    )


@orientacao_juridica_controller.route(
    "/cadastro_orientacao_juridica/", methods=["POST", "GET"]
)
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ESTAGIARIO_DIREITO,
    ]
)
def cadastro_orientacao_juridica():
    orientacao_juridica_service = OrientacaoJuridicaService()
    form = CadastroOrientacaoJuridicaForm()

    if request.method == "POST":
        try:
            orientacao_juridica_service.create_orientacao_with_atendidos(
                form=form, request=request
            )
            flash("Orientação jurídica cadastrada com sucesso!", "success")
            return redirect(url_for("orientacao_juridica.orientacoes_juridicas"))
        except Exception as e:
            flash(str(e), "error")

    return render_template("orientacao_juridica/cadastrar_orientacao.html", form=form)


@orientacao_juridica_controller.route(
    "/associa_orientacao_juridica/<int:id_orientacao>",
    defaults={"id_atendido": 0},
    methods=["POST", "GET"],
)
@orientacao_juridica_controller.route(
    "/associa_orientacao_juridica/<int:id_orientacao>/<int:id_atendido>",
    methods=["POST", "GET"],
)
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.PROFESSOR,
    ]
)
def associacao_orientacao_juridica(id_orientacao, id_atendido):
    orientacao_juridica_service = OrientacaoJuridicaService()

    # Check if orientacao exists
    if not orientacao_juridica_service.validate_orientacao_exists(id_orientacao):
        abort(404)

    if id_atendido:
        try:
            success = orientacao_juridica_service.associate_atendido_to_orientacao(
                id_orientacao=id_orientacao,
                id_atendido=id_atendido,
            )

            if success:
                flash(
                    "Atendido associado à orientação jurídica com sucesso!", "success"
                )
            else:
                flash("Erro ao associar atendido", "error")
        except Exception as e:
            flash(str(e), "error")

        return redirect(url_for("orientacao_juridica.perfil_oj", id=id_orientacao))

    page_data = orientacao_juridica_service.get_associacao_page_data(
        orientacao_id=id_orientacao
    )

    return render_template(
        "orientacao_juridica/associar_orientacao.html",
        orientacao_entidade=page_data["orientacao"],
        pagination=page_data["pagination"],
        encaminhar_outras_aj=False,
    )


@orientacao_juridica_controller.route(
    "/desassociar_orientacao_juridica/<int:id_orientacao>/<int:id_atendido>",
    methods=["POST", "GET"],
)
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.PROFESSOR,
    ]
)
def desassociar_orientacao_juridica(id_atendido, id_orientacao):
    orientacao_juridica_service = OrientacaoJuridicaService()

    try:
        success = orientacao_juridica_service.disassociate_atendido(
            id_orientacao, id_atendido
        )
        if not success:
            flash("Erro ao desassociar atendido", "error")
            abort(404)
    except Exception as e:
        flash(str(e), "error")
        abort(404)

    flash("Atendido desassociado da orientação jurídica com sucesso!", "success")
    return redirect(url_for("orientacao_juridica.perfil_oj", id=id_orientacao))


@orientacao_juridica_controller.route("/orientacao_juridica/<id>")
@login_required()
def perfil_oj(id):
    orientacao_juridica_service = OrientacaoJuridicaService()

    perfil_data = orientacao_juridica_service.get_perfil_data(id)

    return render_template(
        "orientacao_juridica/visualizar_orientacao.html",
        orientacao=perfil_data["orientacao"],
        atendidos=perfil_data["atendidos"],
        assistencias=perfil_data["assistencias"],
        usuario=perfil_data["usuario"],
    )


@orientacao_juridica_controller.route("/orientacoes_juridicas")
@login_required()
def orientacoes_juridicas():
    orientacao_juridica_service = OrientacaoJuridicaService()

    page = request.args.get("page", 1, type=int)
    busca = request.args.get("busca", "", type=str)

    if busca:
        orientacoes = (
            orientacao_juridica_service.buscar_orientacoes_por_atendido_or_all(
                busca=busca,
                page=page,
                per_page=current_app.config["ATENDIDOS_POR_PAGINA"],
            )
        )
    else:
        orientacoes = orientacao_juridica_service.get_paginated_orientacoes(
            page=page,
            per_page=current_app.config["ATENDIDOS_POR_PAGINA"],
        )

    return render_template(
        "orientacao_juridica/listagem_orientacoes.html",
        orientacoes=orientacoes,
        busca=busca,
    )


@orientacao_juridica_controller.route("/busca_oj/", defaults={"_busca": None})
@orientacao_juridica_controller.route("/busca_oj/<_busca>", methods=["GET"])
@login_required()
def busca_oj(_busca):
    orientacao_juridica_service = OrientacaoJuridicaService()

    orientacoes = orientacao_juridica_service.buscar_orientacoes_por_atendido_or_all(
        busca=_busca,
        page=request.args.get("page", 1, type=int),
        per_page=current_app.config["ATENDIDOS_POR_PAGINA"],
    )

    return render_template(
        "busca_orientacao_juridica/listagem_orientacoes.html", orientacoes=orientacoes
    )
