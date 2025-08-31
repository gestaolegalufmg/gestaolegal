import json
from typing import Any, cast

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from sqlalchemy import Select

from gestaolegal import app, db, login_required
from gestaolegal.models.assistido import Assistido
from gestaolegal.plantao.forms.cadastro_atendido_form import CadastroAtendidoForm
from gestaolegal.plantao.forms.tornar_assistido_form import TornarAssistidoForm
from gestaolegal.plantao.transforms import build_cards
from gestaolegal.services.atendido_service import AtendidoService, PageParams
from gestaolegal.usuario.models import UserRole

atendido_controller = Blueprint(
    "atendido", __name__, template_folder="../templates/atendido"
)


def valida_dados_form(form: CadastroAtendidoForm):
    atendido_service = AtendidoService(db.session)
    email_repetido = atendido_service.find_by_email(form.email.data)

    if not form.validate() or email_repetido:
        return False
    return True


@atendido_controller.route("/atendidos_assistidos", methods=["GET"])
@login_required()
def atendidos_assistidos():
    atendido_service = AtendidoService(db.session)

    valor_busca = request.args.get("valor_busca", "")
    tipo_busca = request.args.get("tipo_busca", "todos")
    page = request.args.get("page", 0, type=int)
    per_page = cast(int, app.config["ATENDIDOS_POR_PAGINA"])

    result = atendido_service.search_by_str(
        valor_busca,
        search_type=tipo_busca,
        page_params=PageParams(page=page, per_page=per_page),
    )

    template_data = {
        "atendidos_assistidos": result,
        "valor_busca": valor_busca,
        "tipo_busca": tipo_busca,
        "page": page,
        "per_page": per_page,
    }

    return render_template("atendidos_assistidos.html", **template_data)


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
    return render_template("cadastro_novo_atendido.html", form=form)


@atendido_controller.route("/novo_atendimento", methods=["POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.COLAB_PROJETO,
        UserRole.ESTAGIARIO_DIREITO,
    ]
)
def cadastro_na():
    atendido_service = AtendidoService(db.session)
    form = CadastroAtendidoForm()

    if not valida_dados_form(form):
        return render_template("cadastro_novo_atendido.html", form=form)

    atendido_service.create_atendido(form)

    flash("Atendido cadastrado!", "success")
    atendido = atendido_service.find_by_email(form.email.data)
    if not atendido:
        abort(500)

    _id = atendido.id
    return redirect(url_for("atendido.perfil_assistido", _id=_id))


@atendido_controller.route("/excluir_atendido/", methods=["POST"])
@login_required(role=[UserRole.ADMINISTRADOR])
def excluir_atendido():
    id_atendido = request.form.get("id")
    atendido_service = AtendidoService(db.session)
    atendido_service.delete_atendido(id_atendido)

    flash("Atendido excluído com sucesso!", "success")
    return redirect(url_for("atendido.atendidos_assistidos"))


@atendido_controller.route("/buscar_atendido", methods=["POST"])
@login_required()
def buscar_atendido():
    atendido_service = AtendidoService(db.session)

    termo = request.form.get("termo", "")
    page = request.args.get("page", 1, type=int)

    def paginator(query: Select[Any]):
        return db.paginate(
            query,
            page=page,
            per_page=app.config["ATENDIDOS_POR_PAGINA"],
            error_out=False,
        )

    atendidos = atendido_service.search_by_str(termo, paginator)

    return render_template("lista_atendidos.html", atendidos=atendidos)


@atendido_controller.route("/perfil_assistido/<int:_id>", methods=["GET"])
@login_required()
def perfil_assistido(_id: int):
    atendido_service = AtendidoService(db.session)
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
        "perfil_assistidos.html", assistido=template_data, cards=cards
    )


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
    atendido_service = AtendidoService(db.session)
    atendido = atendido_service.find_by_id(id_atendido)

    if not atendido:
        abort(404)

    form = CadastroAtendidoForm()
    form.populate_from_atendido(atendido)

    return render_template("editar_atendido.html", atendido=atendido, form=form)


@atendido_controller.route("/editar_atendido/<id_atendido>", methods=["POST"])
@login_required(role=[])
def editar_atendido(id_atendido: int):
    atendido_service = AtendidoService(db.session)
    atendido = atendido_service.find_by_id(id_atendido)

    if not atendido:
        abort(404)

    form = CadastroAtendidoForm()

    if form.validate():
        atendido = atendido_service.update_atendido(id_atendido, form)

        flash("Atendido editado com sucesso!", "success")
        return redirect(url_for("atendido.perfil_assistido", _id=atendido.id))

    return render_template("editar_atendido.html", atendido=atendido, form=form)


@atendido_controller.route("/tornar_assistido/<id_atendido>", methods=["GET"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ESTAGIARIO_DIREITO,
    ]
)
def tornar_assistido_form(id_atendido: int):
    atendido_service = AtendidoService(db.session)
    atendido = atendido_service.find_by_id(id_atendido)

    if not atendido:
        abort(404)

    form = TornarAssistidoForm()

    return render_template("tornar_assistido.html", atendido=atendido, form=form)


@atendido_controller.route("/tornar_assistido/<id_atendido>", methods=["POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ESTAGIARIO_DIREITO,
    ]
)
def tornar_assistido(id_atendido: int):
    atendido_service = AtendidoService(db.session)
    atendido = atendido_service.find_by_id(id_atendido)

    if not atendido:
        abort(404)

    form = TornarAssistidoForm()

    if form.validate():
        data = request.form.to_dict()

        data["id"] = None
        data["id_atendido"] = atendido.id
        del data["csrf_token"]

        boolean_fields = ["possui_outros_imoveis", "possui_veiculos"]
        for field in boolean_fields:
            if field in data and isinstance(data[field], str):
                data[field] = data[field] == "True"

        assistido = atendido_service.create_assistido(Assistido(**data))
        return redirect(url_for("atendido.perfil_assistido", _id=atendido.id))

    return render_template("tornar_assistido.html", atendido=atendido, form=form)


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
    atendido_service = AtendidoService(db.session)
    result = atendido_service.find_atendido_assistido_by_id(id_atendido)

    if not result:
        abort(404)

    atendido, assistido = result

    form_atendido = CadastroAtendidoForm()
    form_assistido = TornarAssistidoForm()

    form_atendido.populate_from_atendido(assistido.atendido)
    form_assistido.populate_from_assistido(assistido)

    return render_template(
        "editar_assistido.html",
        form=form_atendido,
        form_assistido=form_assistido,
        atendido=assistido.atendido,
        assistido=assistido,
    )


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
    atendido_service = AtendidoService(db.session)
    result = atendido_service.find_atendido_assistido_by_id(id_atendido)

    if not result:
        abort(404)

    atendido, assistido = result

    form_atendido = CadastroAtendidoForm()
    form_assistido = TornarAssistidoForm()

    if form_atendido.validate() and form_assistido.validate():
        atendido = atendido_service.update_atendido(id_atendido, form_atendido)
        assistido = atendido_service.update_assistido(assistido.id, form_assistido)

        flash("Assistido editado com sucesso!", "success")
        return redirect(url_for("atendido.perfil_assistido", _id=assistido.id_atendido))

    form_atendido.populate_from_atendido(assistido.atendido)
    form_assistido.populate_from_assistido(assistido)

    return render_template(
        "editar_assistido.html",
        form=form_atendido,
        form_assistido=form_assistido,
        atendido=assistido.atendido,
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
    atendido_service = AtendidoService(db.session)

    data = request.get_json(silent=True, force=True)
    assistido = atendido_service.create_assistido(Assistido(**data))

    return json.dumps(
        {
            "status": "success",
            "message": "Assistido cadastrado com sucesso!",
            "id": assistido.id,
        }
    )
