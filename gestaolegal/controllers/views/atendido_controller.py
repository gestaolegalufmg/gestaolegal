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
from gestaolegal.common.constants.atendido import TipoBusca
from gestaolegal.forms.plantao.cadastro_atendido_form import CadastroAtendidoForm
from gestaolegal.forms.plantao.tornar_assistido_form import TornarAssistidoForm
from gestaolegal.repositories.base_repository import PageParams
from gestaolegal.services.atendido_service import AtendidoService
from gestaolegal.utils.decorators import login_required
from gestaolegal.utils.transforms import build_cards

logger = logging.getLogger(__name__)

atendido_controller = Blueprint(
    "atendido", __name__, template_folder="../../static/templates"
)


@atendido_controller.route("/atendidos_assistidos", methods=["GET"])
@login_required()
def listagem_atendidos():
    atendido_service = AtendidoService()

    valor_busca = request.args.get("valor_busca", default="", type=str)
    tipo_busca = request.args.get("tipo_busca", default=TipoBusca.TODOS, type=TipoBusca)
    page = request.args.get("page", default=1, type=int)
    per_page = int(current_app.config.get("ATENDIDOS_POR_PAGINA", 10))

    data = atendido_service.get(
        valor_busca, tipo_busca, page_params=PageParams(page=page, per_page=per_page)
    )

    template_data = {
        "data": data,
        "valor_busca": valor_busca,
        "tipo_busca": tipo_busca,
    }

    return render_template("atendidos/listagem_atendidos.html", **template_data)


@atendido_controller.route("/cadastrar_atendido", methods=["POST", "GET"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.COLAB_PROJETO,
        UserRole.ESTAGIARIO_DIREITO,
    ]
)
def cadastrar_atendido():
    if request.method == "GET":
        form = CadastroAtendidoForm()
        return render_template("atendidos/cadastrar_atendido.html", form=form)

    atendido_service = AtendidoService()
    form = CadastroAtendidoForm()

    if not form.validate():
        logger.warning("Form validation failed for atendido registration")
        flash("Dados do formulário inválidos", "warning")
        return render_template("atendidos/cadastrar_atendido.html", form=form)

    try:
        logger.info(f"Creating atendido with email: {form.email.data}")

        result = atendido_service.create(form.to_dict())

        logger.info(f"Atendido created successfully with ID: {result.id}")

        flash("Atendido cadastrado!", "success")
        return redirect(url_for("atendido.visualizar_atendido", atendido_id=result.id))

    except Exception as e:
        logger.error(f"Error in cadastrar_atendido: {str(e)}", exc_info=True)
        flash(e, "error")
        return render_template("atendidos/cadastrar_atendido.html", form=form)


@atendido_controller.route("/excluir_atendido/", methods=["POST"])
@login_required(role=[UserRole.ADMINISTRADOR])
def excluir_atendido():
    id_atendido = request.form.get("id")
    atendido_service = AtendidoService()

    try:
        atendido_service.soft_delete(id_atendido)
        flash("Atendido excluído com sucesso!", "success")
    except Exception as e:
        flash(str(e), "error")

    return redirect(url_for("atendido.listagem_atendidos"))


@atendido_controller.route("/buscar_atendido", methods=["POST"])
@login_required()
def buscar_atendido():
    atendido_service = AtendidoService()

    termo = request.form.get("termo", "")
    page = request.args.get("page", 1, type=int)

    page_params = PageParams(
        page=page, per_page=current_app.config["ATENDIDOS_POR_PAGINA"]
    )
    atendidos = atendido_service.get_paginated_search_results(termo, page_params)

    return render_template("atendidos/listagem_atendidos.html", atendidos=atendidos)


@atendido_controller.route("/<int:atendido_id>", methods=["GET"])
@login_required()
def visualizar_atendido(atendido_id: int):
    atendido_service = AtendidoService()

    try:
        result = atendido_service.find_by_id(atendido_id)
        if not result:
            abort(404)

        # Type assertion: we know resulte is not None after the check above
        assert result is not None
        assistido = result.assistido
        if assistido is None:
            assistido_pj = None
        else:
            assistido_pj = assistido.assistido_pessoa_juridica

        template_data = {
            "Atendido": result,
            "Assistido": assistido,
            "AssistidoPessoaJuridica": assistido_pj,
        }

        cards = build_cards(result, assistido, assistido_pj)

        return render_template(
            "atendidos/visualizar_atendido.html", assistido=template_data, cards=cards
        )
    except Exception as e:
        flash(f"Erro ao carregar perfil: {str(e)}", "error")
        return redirect(url_for("atendido.listagem_atendidos"))


@atendido_controller.route("/tornar_assistido/<id_atendido>", methods=["GET"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ESTAGIARIO_DIREITO,
    ]
)
def tornar_assistido_form(id_atendido: int):
    atendido_service = AtendidoService()

    try:
        atendido = atendido_service.find_by_id(id_atendido)
        if not atendido:
            abort(404)

        form = TornarAssistidoForm()

        return render_template(
            "atendidos/tornar_assistido.html", atendido=atendido, form=form
        )
    except ValueError:
        abort(404)


@atendido_controller.route("/tornar_assistido/<id_atendido>", methods=["POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ESTAGIARIO_DIREITO,
    ]
)
def tornar_assistido(id_atendido: int):
    atendido_service = AtendidoService()

    try:
        atendido = atendido_service.find_by_id(id_atendido)
        if not atendido:
            abort(404)

        # Type assertion: we know atendido is not None after the check above
        assert atendido is not None
        form = TornarAssistidoForm()

        if form.validate():
            assistido_data = TornarAssistidoForm.to_dict(form)

            atendido_service.create_assistido(atendido.id, assistido_data)
            flash("Assistido criado com sucesso!", "success")
            return redirect(
                url_for("atendido.visualizar_atendido", atendido_id=atendido.id)
            )
        else:
            return render_template(
                "atendidos/tornar_assistido.html", atendido=atendido, form=form
            )
    except Exception as e:
        flash("Erro inesperado ao tornar este atendido um assistido.", "error")
        raise e


@atendido_controller.route("/editar/<id_atendido>", methods=["GET", "POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.COLAB_PROJETO,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.PROFESSOR,
    ]
)
def editar_unificado(id_atendido: int):
    atendido_service = AtendidoService()

    try:
        atendido = atendido_service.find_by_id(id_atendido)
        if not atendido:
            abort(404)

        # Type assertion: we know atendido is not None after the check above
        assert atendido is not None

        if request.method == "GET":
            form_atendido = CadastroAtendidoForm(
                data=atendido.to_dict(inline_other_models=True)
            )
            form_assistido = (
                TornarAssistidoForm(data=atendido.assistido.to_dict())
                if atendido.assistido
                else None
            )

            return render_template(
                "atendidos/editar_atendido.html",
                atendido=atendido,
                form=form_atendido,
                form_assistido=form_assistido,
                assistido=atendido.assistido,
            )

        form_atendido = CadastroAtendidoForm()
        if atendido.assistido:
            form_assistido = TornarAssistidoForm()
            if form_atendido.validate() and form_assistido.validate():
                atendido_data = form_atendido.to_dict()
                assistido_data = form_assistido.to_dict()
                updated_assistido = atendido_service.update_assistido(
                    id_atendido, atendido_data, assistido_data
                )
                flash("Assistido editado com sucesso!", "success")
                return redirect(
                    url_for(
                        "atendido.visualizar_atendido",
                        atendido_id=updated_assistido.id_atendido,
                    )
                )
            return render_template(
                "atendidos/editar_atendido.html",
                atendido=atendido,
                form=form_atendido,
                form_assistido=form_assistido,
                assistido=atendido.assistido,
            )

        if form_atendido.validate():
            atendido_data = form_atendido.to_dict()
            updated_atendido = atendido_service.update(id_atendido, atendido_data)
            flash("Atendido editado com sucesso!", "success")
            return redirect(
                url_for("atendido.visualizar_atendido", atendido_id=updated_atendido.id)
            )
        return render_template(
            "atendidos/editar_atendido.html",
            atendido=atendido,
            form=form_atendido,
            form_assistido=None,
            assistido=None,
        )
    except ValueError:
        abort(404)
    except Exception as e:
        flash(f"Erro ao editar: {str(e)}", "error")
        return redirect(url_for("atendido.listagem_atendidos"))
