import json
import logging
from typing import Any, cast

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
from sqlalchemy import Select

from gestaolegal.common.constants import UserRole
from gestaolegal.database import get_db
from gestaolegal.forms.plantao.cadastro_atendido_form import CadastroAtendidoForm
from gestaolegal.forms.plantao.tornar_assistido_form import TornarAssistidoForm
from gestaolegal.forms.usuario import EnderecoForm
from gestaolegal.models.assistido import Assistido
from gestaolegal.services.assistido_service import AssistidoService
from gestaolegal.services.atendido_service import AtendidoService
from gestaolegal.utils.decorators import login_required
from gestaolegal.utils.transforms import build_cards

logger = logging.getLogger(__name__)

atendido_controller = Blueprint(
    "atendido", __name__, template_folder="../static/templates"
)


@atendido_controller.route("/atendidos_assistidos", methods=["GET"])
@login_required()
def atendidos_assistidos():
    db = get_db()
    atendido_service = AtendidoService()

    valor_busca = request.args.get("valor_busca", "")
    tipo_busca = request.args.get("tipo_busca", "todos")
    page = request.args.get("page", 1, type=int)
    per_page = cast(int, current_app.config["ATENDIDOS_POR_PAGINA"])

    def paginator(query):
        return db.paginate(
            query,
            page=page,
            per_page=per_page,
            error_out=False,
        )

    atendidos_assistidos = atendido_service.get_search_results_with_pagination(
        valor_busca, tipo_busca, paginator
    )

    if (
        hasattr(atendidos_assistidos, "items")
        and not atendidos_assistidos.items
        and page == 1
    ):
        flash("Não há atendidos cadastrados no sistema.", "info")

    template_data = {
        "atendidos_assistidos": atendidos_assistidos,
        "valor_busca": valor_busca,
        "tipo_busca": tipo_busca,
    }

    return render_template("atendidos/listagem_atendidos.html", **template_data)


@atendido_controller.route("/novo_atendimento", methods=["GET"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.COLAB_PROJETO,
        UserRole.ESTAGIARIO_DIREITO,
    ]
)
def cadastro_na_form():
    form = CadastroAtendidoForm()
    return render_template("atendidos/cadastrar_atendido.html", form=form)


@atendido_controller.route("/novo_atendimento", methods=["POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.COLAB_PROJETO,
        UserRole.ESTAGIARIO_DIREITO,
    ]
)
def cadastro_na():
    atendido_service = AtendidoService()
    form = CadastroAtendidoForm()

    if not form.validate():
        flash("Dados do formulário inválidos", "warning")
        return render_template("atendidos/cadastrar_atendido.html", form=form)

    is_valid, error_message = atendido_service.validate_email_uniqueness(
        form.email.data
    )
    if not is_valid:
        flash(error_message, "warning")
        return render_template("atendidos/cadastrar_atendido.html", form=form)

    try:
        atendido_data = CadastroAtendidoForm.to_dict(form)
        endereco_data = EnderecoForm.to_dict(form)

        atendido = atendido_service.create_with_endereco(atendido_data, endereco_data)
        flash("Atendido cadastrado!", "success")
        return redirect(url_for("atendido.perfil_assistido", _id=atendido.id))
    except Exception as e:
        logger.error(f"Error in cadastro_na: {str(e)}", exc_info=True)
        return render_template("atendidos/cadastrar_atendido.html", form=form)


@atendido_controller.route("/excluir_atendido/", methods=["POST"])
@login_required(role=[UserRole.ADMINISTRADOR])
def excluir_atendido():
    id_atendido = request.form.get("id")
    atendido_service = AtendidoService()

    try:
        atendido_service.delete(id_atendido)
        flash("Atendido excluído com sucesso!", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Erro ao excluir atendido: {str(e)}", "error")

    return redirect(url_for("atendido.atendidos_assistidos"))


@atendido_controller.route("/buscar_atendido", methods=["POST"])
@login_required()
def buscar_atendido():
    db = get_db()

    atendido_service = AtendidoService()

    termo = request.form.get("termo", "")
    page = request.args.get("page", 1, type=int)

    def paginator(query: Select[Any]):
        return db.paginate(
            query,
            page=page,
            per_page=current_app.config["ATENDIDOS_POR_PAGINA"],
            error_out=False,
        )

    atendidos = atendido_service.get_paginated_search_results(
        termo, page, current_app.config["ATENDIDOS_POR_PAGINA"], paginator
    )

    return render_template("atendidos/listagem_atendidos.html", atendidos=atendidos)


@atendido_controller.route("/perfil_assistido/<int:_id>", methods=["GET"])
@login_required()
def perfil_assistido(_id: int):
    atendido_service = AtendidoService()

    try:
        result = atendido_service.get_atendido_with_assistido_data(_id)
        if not result:
            abort(404)

        atendido_model, assistido_model, assistido_pj = result

        template_data = {
            "Atendido": atendido_model,
            "Assistido": assistido_model,
            "AssistidoPessoaJuridica": assistido_pj,
        }

        cards = build_cards(atendido_model, assistido_model, assistido_pj)

        return render_template(
            "atendidos/perfil_atendido.html", assistido=template_data, cards=cards
        )
    except Exception as e:
        flash(f"Erro ao carregar perfil: {str(e)}", "error")
        return redirect(url_for("atendido.atendidos_assistidos"))


@atendido_controller.route("/editar_atendido/<id_atendido>", methods=["GET"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.COLAB_PROJETO,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.PROFESSOR,
    ]
)
def editar_atendido_form(id_atendido: int):
    atendido_service = AtendidoService()

    try:
        atendido = atendido_service.find_by_id(id_atendido)
        form = CadastroAtendidoForm()
        form.populate_from_atendido(atendido)

        return render_template(
            "atendidos/editar_atendido.html", atendido=atendido, form=form
        )
    except ValueError:
        abort(404)


@atendido_controller.route("/editar_atendido/<id_atendido>", methods=["POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.COLAB_PROJETO,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.PROFESSOR,
    ]
)
def editar_atendido(id_atendido: int):
    atendido_service = AtendidoService()

    try:
        atendido = atendido_service.find_by_id(id_atendido)
        form = CadastroAtendidoForm()

        if form.validate():
            atendido_data = CadastroAtendidoForm.to_dict(form)
            endereco_data = EnderecoForm.to_dict(form)

            updated_atendido = atendido_service.update_with_endereco(
                id_atendido, atendido_data, endereco_data
            )
            flash("Atendido editado com sucesso!", "success")
            return redirect(
                url_for("atendido.perfil_assistido", _id=updated_atendido.id)
            )
        else:
            return render_template(
                "atendidos/editar_atendido.html", atendido=atendido, form=form
            )
    except ValueError:
        abort(404)
    except Exception as e:
        flash(f"Erro ao editar atendido: {str(e)}", "error")
        return render_template(
            "atendidos/editar_atendido.html", atendido=atendido, form=form
        )


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
        form = TornarAssistidoForm()

        if form.validate():
            assistido_service = AssistidoService()

            assistido_data = TornarAssistidoForm.to_dict(form)

            assistido_data["id_atendido"] = atendido.id
            assistido = assistido_service.create(assistido_data)
            flash("Assistido criado com sucesso!", "success")
            return redirect(url_for("atendido.perfil_assistido", _id=atendido.id))
        else:
            return render_template(
                "atendidos/tornar_assistido.html", atendido=atendido, form=form
            )
    except ValueError:
        abort(404)
    except Exception as e:
        flash(f"Erro ao criar assistido: {str(e)}", "error")
        return render_template(
            "atendidos/tornar_assistido.html", atendido=atendido, form=form
        )


@atendido_controller.route("/editar_assistido/<id_atendido>/", methods=["GET"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.COLAB_PROJETO,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.PROFESSOR,
    ]
)
def editar_assistido_form(id_atendido: int):
    atendido_service = AtendidoService()

    try:
        atendido, assistido = atendido_service.ensure_atendido_assistido_exists(
            id_atendido
        )

        form_atendido = CadastroAtendidoForm()
        form_assistido = TornarAssistidoForm()

        form_atendido.populate_from_atendido(atendido)
        form_assistido.populate_from_assistido(assistido)

        return render_template(
            "atendidos/editar_assistido.html",
            form=form_atendido,
            form_assistido=form_assistido,
            atendido=atendido,
            assistido=assistido,
        )
    except ValueError:
        abort(404)


@atendido_controller.route("/editar_assistido/<id_atendido>/", methods=["POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.COLAB_PROJETO,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.PROFESSOR,
    ]
)
def editar_assistido(id_atendido: int):
    atendido_service = AtendidoService()

    try:
        atendido, assistido = atendido_service.ensure_atendido_assistido_exists(
            id_atendido
        )

        form_atendido = CadastroAtendidoForm()
        form_assistido = TornarAssistidoForm()

        if form_atendido.validate() and form_assistido.validate():
            assistido_service = AssistidoService()

            atendido_data = CadastroAtendidoForm.to_dict(form_atendido)
            endereco_data = EnderecoForm.to_dict(form_atendido)
            assistido_data = TornarAssistidoForm.to_dict(form_assistido)

            updated_atendido = atendido_service.update_with_endereco(
                id_atendido, atendido_data, endereco_data
            )
            updated_assistido = assistido_service.update(assistido.id, assistido_data)

            flash("Assistido editado com sucesso!", "success")
            return redirect(
                url_for("atendido.perfil_assistido", _id=updated_assistido.id_atendido)
            )
        else:
            form_atendido.populate_from_atendido(atendido)
            form_assistido.populate_from_assistido(assistido)

            return render_template(
                "atendidos/editar_assistido.html",
                form=form_atendido,
                form_assistido=form_assistido,
                atendido=atendido,
                assistido=assistido,
            )
    except ValueError:
        abort(404)
    except Exception as e:
        flash(f"Erro ao editar assistido: {str(e)}", "error")
        return render_template(
            "atendidos/editar_assistido.html",
            form=form_atendido,
            form_assistido=form_assistido,
            atendido=atendido,
            assistido=assistido,
        )


@atendido_controller.route("/tornar_assistido_modal/", methods=["POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ESTAGIARIO_DIREITO,
    ]
)
def tornar_assistido_modal():
    assistido_service = AssistidoService()

    try:
        data = request.get_json(silent=True, force=True)
        assistido = assistido_service.create(Assistido(**data))

        return json.dumps(
            {
                "status": "success",
                "message": "Assistido cadastrado com sucesso!",
                "id": assistido.id,
            }
        )
    except Exception as e:
        return json.dumps(
            {
                "status": "error",
                "message": f"Erro ao cadastrar assistido: {str(e)}",
            }
        )
