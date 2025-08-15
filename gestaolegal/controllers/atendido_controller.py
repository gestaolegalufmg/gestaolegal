import json
from typing import Any, cast

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import Select

from gestaolegal import app, db, login_required
from gestaolegal.models.atendido import (
    Atendido,
)
from gestaolegal.plantao.forms.cadastro_atendido_form import CadastroAtendidoForm
from gestaolegal.plantao.forms.tornar_assistido_form import TornarAssistidoForm
from gestaolegal.plantao.models import Assistido
from gestaolegal.plantao.transforms import (
    build_address_from_form_data,
    build_assistido_from_form_data,
    build_atendido_from_form_data,
    build_cards,
    update_assistido_from_form_data,
    update_atendido_from_form_data,
)
from gestaolegal.plantao.views_util import (
    busca_todos_atendidos_assistidos,
    setValoresFormAssistido,
    setValoresFormAtendido,
    tipos_busca_atendidos,
)
from gestaolegal.services.atendido_service import AtendidoService
from gestaolegal.usuario.models import usuario_urole_roles

atendido_controller = Blueprint("atendido", __name__)


def valida_dados_form(form: CadastroAtendidoForm):
    atendido_service = AtendidoService(db.session)
    email_repetido = atendido_service.find_by_email(form.email.data)

    if not form.validate() or email_repetido:
        return False
    return True


def cria_atendido(form: CadastroAtendidoForm):
    entidade_endereco = build_address_from_form_data(form)
    db.session.add(entidade_endereco)
    db.session.flush()

    entidade_atendido = build_atendido_from_form_data(form, entidade_endereco)

    return entidade_atendido


@atendido_controller.route("/atendidos_assistidos", methods=["GET", "POST"])
@login_required()
def atendidos_assistidos():
    atendido_service = AtendidoService(db.session)

    page = request.args.get("page", 1, type=int)
    per_page = cast(int, app.config["ATENDIDOS_POR_PAGINA"])

    def paginator(query: Select[Any]):
        return db.paginate(query, page=page, per_page=per_page)

    pagination = cast(
        Pagination,
        atendido_service.get_all(paginator=paginator),
    )

    id_atendidos = [atendido.id for atendido in pagination.items]
    assistidos = atendido_service.get_assistidos_by_id_atendido(id_atendidos)
    assistidos_map = {assistido.id_atendido: assistido for assistido in assistidos}

    atendidos_assistidos = []
    for atendido in pagination.items:
        assistido = assistidos_map.get(atendido.id)
        atendidos_assistidos.append(
            {
                "id": atendido.id,
                "nome": atendido.nome,
                "cpf": atendido.cpf,
                "cnpj": atendido.cnpj,
                "telefone": atendido.telefone,
                "id_atendido": assistido.id_atendido if assistido else None,
                "is_assistido": assistido is not None,
            }
        )

    return render_template(
        "atendido/atendidos_assistidos.html",
        atendidos_assistidos=atendidos_assistidos,
        tipos_busca_atendidos=tipos_busca_atendidos,
        pagination=pagination,
        iter_pages=pagination.iter_pages,
    )


@atendido_controller.route("/busca_atendidos_assistidos", methods=["GET", "POST"])
@login_required()
def busca_atendidos_assistidos():
    if request.method == "GET":
        valor_busca = request.args.get("valor_busca", "")
        tipo_busca = request.args.get("tipo_busca", "todos")
        page = request.args.get("page", 1, type=int)

        pagination = cast(
            Pagination, busca_todos_atendidos_assistidos(valor_busca, page)
        )

        if tipo_busca == "assistidos":
            filtered_items = []
            for atendido, assistido in pagination.items:
                if assistido is not None:
                    filtered_items.append((atendido, assistido))
            pagination.items = filtered_items
        elif tipo_busca == "atendidos":
            filtered_items = []
            for atendido, assistido in pagination.items:
                if assistido is None:
                    filtered_items.append((atendido, assistido))
            pagination.items = filtered_items

        return render_template(
            "atendido/busca_atendidos_assistidos.html", atendidos_assistidos=pagination
        )

    elif request.method == "POST":
        atendido_service = AtendidoService(db.session)
        termo = request.form["termo"]
        atendidos = atendido_service.search_by_str(termo)
        return json.dumps({"atendidos": [x.as_dict() for x in atendidos]})


@atendido_controller.route("/novo_atendimento", methods=["GET", "POST"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["COLAB_PROJETO"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
    ]
)
def cadastro_na():
    atendido_service = AtendidoService(db.session)
    form = CadastroAtendidoForm()

    if request.method == "POST":
        if not valida_dados_form(form):
            return render_template("atendido/cadastro_novo_atendido.html", form=form)

        db.session.add(cria_atendido(form))
        db.session.commit()

        flash("Atendido cadastrado!", "success")
        atendido = atendido_service.find_by_email(form.email.data)
        if not atendido:
            abort(500)

        _id = atendido.id
        return redirect(url_for("atendido.perfil_assistido", _id=_id))

    return render_template("atendido/cadastro_novo_atendido.html", form=form)


@atendido_controller.route("/excluir_atendido/", methods=["POST", "GET"])
@login_required(role=[usuario_urole_roles["ADMINISTRADOR"][0]])
def excluir_atendido():
    id_atendido = request.form.get("id")
    atendido = db.session.get(Atendido, id_atendido)
    if not atendido:
        abort(404)
    atendido.status = False
    db.session.commit()
    flash("Atendido excluído com sucesso!", "success")
    return redirect(url_for("atendido.atendidos_assistidos"))


@atendido_controller.route("/buscar_atendido", methods=["POST", "GET"])
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

    return render_template("atendido/lista_atendidos.html", atendidos=atendidos)


@atendido_controller.route("/perfil_assistido/<int:_id>", methods=["GET"])
@login_required()
def perfil_assistido(_id: int):
    atendido_service = AtendidoService(db.session)
    result = atendido_service.get_atendido_with_assistido_data(_id)

    if not result:
        abort(404)

    cards = build_cards(*result)

    return render_template("atendido/perfil_assistidos.html", assistido=result, cards=cards)


@atendido_controller.route("/editar_atendido/<id_atendido>", methods=["POST", "GET"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["COLAB_PROJETO"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
        usuario_urole_roles["PROFESSOR"][0],
    ]
)
def editar_atendido(id_atendido: int):
    atendido_service = AtendidoService(db.session)
    atendido = atendido_service.find_by_id(id_atendido)

    if not atendido:
        abort(404)

    form = CadastroAtendidoForm()

    if request.method == "POST":
        if form.validate():
            atendido = update_atendido_from_form_data(form, atendido)
            db.session.commit()

            flash("Atendido editado com sucesso!", "success")
            return redirect(url_for("atendido.perfil_assistido", _id=atendido.id))

    setValoresFormAtendido(atendido, form)
    return render_template("atendido/editar_atendido.html", atendido=atendido, form=form)


@atendido_controller.route("/tornar_assistido/<id_atendido>", methods=["POST", "GET"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
    ]
)
def tornar_assistido(id_atendido: int):
    atendido_service = AtendidoService(db.session)
    atendido = atendido_service.find_by_id(id_atendido)

    if not atendido:
        abort(404)

    form = TornarAssistidoForm()
    if request.method == "POST":
        if form.validate():
            assistido = build_assistido_from_form_data(form, atendido)
            db.session.add(assistido)
            db.session.commit()
            return redirect(url_for("atendido.perfil_assistido", _id=atendido.id))

    return render_template("atendido/tornar_assistido.html", atendido=atendido, form=form)


@atendido_controller.route("/editar_assistido/<id_atendido>/", methods=["POST", "GET"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["COLAB_PROJETO"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
        usuario_urole_roles["PROFESSOR"][0],
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

    if request.method == "POST":
        if form_atendido.validate() and form_assistido.validate():
            atendido, assistido = update_assistido_from_form_data(
                atendido, assistido, form_atendido, form_assistido
            )
            db.session.commit()
            flash("Assistido editado com sucesso!", "success")
            return redirect(
                url_for("atendido.perfil_assistido", _id=assistido.id_atendido)
            )

    setValoresFormAtendido(assistido.atendido, form_atendido)
    setValoresFormAssistido(assistido, form_assistido)

    return render_template(
        "atendido/editar_assistido.html",
        form=form_atendido,
        form_assistido=form_assistido,
        atendido=assistido.atendido,
        assistido=assistido,
    )


@atendido_controller.route("/tornar_assistido_modal/", methods=["GET", "POST"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
    ]
)
def tornar_assistido_modal():
    if request.method == "GET":
        return json.dumps({"hello": "world"})
    data = request.get_json(silent=True, force=True)
    if data["action"] == "modal":
        entidade_assistido = Assistido()
        entidade_assistido.id_atendido = data["id_atendido"]
        entidade_assistido.sexo = data["sexo"]
        entidade_assistido.raca = data["raca"]
        entidade_assistido.profissao = data["profissao"]
        entidade_assistido.rg = data["rg"]
        entidade_assistido.grau_instrucao = data["grau_instrucao"]
        entidade_assistido.salario = data["salario"]
        entidade_assistido.beneficio = data["beneficio"]
        entidade_assistido.qual_beneficio = data["qual_beneficio"]
        entidade_assistido.contribui_inss = data["contribui_inss"]
        entidade_assistido.qtd_pessoas_moradia = data["qtd_pessoas_moradia"]
        entidade_assistido.renda_familiar = data["renda_familiar"]
        entidade_assistido.participacao_renda = data["participacao_renda"]
        entidade_assistido.tipo_moradia = data["tipo_moradia"]
        entidade_assistido.possui_outros_imoveis = (
            True if data["possui_outros_imoveis"] == "True" else False
        )
        entidade_assistido.quantos_imoveis = (
            0 if data["quantos_imoveis"] == "" else data["quantos_imoveis"]
        )
        entidade_assistido.possui_veiculos = (
            True if data["possui_veiculos"] == "True" else False
        )
        entidade_assistido.doenca_grave_familia = data["doenca_grave_familia"]
        entidade_assistido.obs = data["obs_assistido"]

        entidade_assistido.setCamposVeiculo(
            entidade_assistido.possui_veiculos,
            data["possui_veiculos_obs"],
            0 if data["quantos_veiculos"] == "" else data["quantos_veiculos"],
            data["ano_veiculo"],
        )
        entidade_assistido.setCamposDoenca(
            entidade_assistido.doenca_grave_familia,
            data["pessoa_doente"],
            data["pessoa_doente_obs"],
            0 if data["gastos_medicacao"] == "" else data["gastos_medicacao"],
        )
        db.session.add(entidade_assistido)
        db.session.commit()

        return json.dumps(
            {
                "status": "success",
                "message": "Assistido cadastrado com sucesso!",
                "id": data["id_atendido"],
            }
        )
    else:
        return json.dumps(
            {"status": "error", "message": "Campo de ação não encontrado"}
        )
