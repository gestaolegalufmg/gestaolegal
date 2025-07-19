from typing import Any

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from sqlalchemy import Select

from gestaolegal import app, db, login_required
from gestaolegal.models.orientacao_juridica import OrientacaoJuridica
from gestaolegal.plantao.forms.orientacao_juridica_form import (
    CadastroOrientacaoJuridicaForm,
    OrientacaoJuridicaForm,
)
from gestaolegal.plantao.models import AssistenciaJudiciaria_xOrientacaoJuridica
from gestaolegal.services.orientacao_juridica_service import OrientacaoJuridicaService
from gestaolegal.usuario.models import usuario_urole_roles
from gestaolegal.utils.models import queryFiltradaStatus

orientacao_juridica_controller = Blueprint(
    "orientacao_juridica", __name__, template_folder="templates"
)


@orientacao_juridica_controller.route("/excluir_orientacao_juridica/", methods=["POST"])
@login_required(role=[usuario_urole_roles["ADMINISTRADOR"][0]])
def excluir_oj():
    orientacao_juridica_service = OrientacaoJuridicaService(db.session)

    id_orientacao = request.form.get("id_orientacao")
    orientacao = orientacao_juridica_service.find_by_id(id_orientacao)
    if not orientacao:
        abort(404)
    orientacao.status = False
    db.session.commit()
    flash("Orientação jurídica excluída com sucesso!", "success")
    return redirect(url_for("orientacao_juridica.orientacoes_juridicas"))


@orientacao_juridica_controller.route(
    "/editar_orientacao_juridica/<id_oj>", methods=["POST", "GET"]
)
@login_required(
    role=[usuario_urole_roles["ADMINISTRADOR"][0], usuario_urole_roles["PROFESSOR"][0]]
)
def editar_orientacao_juridica(id_oj: int):
    orientacao_juridica_service = OrientacaoJuridicaService(db.session)

    def setDadosOrientacaoJuridica(
        entidade_orientacao: OrientacaoJuridica, form: OrientacaoJuridicaForm
    ):
        entidade_orientacao.area_direito = form.area_direito.data
        entidade_orientacao.descricao = form.descricao.data
        entidade_orientacao.setSubAreas(
            entidade_orientacao.area_direito,
            form.sub_area.data,
            form.sub_areaAdmin.data,
        )

    def setOrientacaoJuridicaForm(
        entidade_orientacao: OrientacaoJuridica, form: OrientacaoJuridicaForm
    ):
        form.area_direito.data = entidade_orientacao.area_direito
        form.sub_area.data = entidade_orientacao.sub_area
        form.descricao.data = entidade_orientacao.descricao

    ############################################# IMPLEMENTAÇÃO DA ROTA ##############################################################

    entidade_orientacao = orientacao_juridica_service.find_by_id(id_oj)

    if not entidade_orientacao:
        flash("Essa orientação não existe!", "warning")
        return redirect(url_for("orientacoes_juridica.orientacoes_juridicas"))

    form = OrientacaoJuridicaForm()
    if request.method == "POST":
        if not form.validate():
            return render_template("editar_orientacao_juridica.html", form=form)

        setDadosOrientacaoJuridica(entidade_orientacao, form)
        db.session.commit()
        flash("Orientação Jurídica editada com sucesso!", "success")
        return redirect(url_for("orientacao_juridica.orientacoes_juridicas"))

    setOrientacaoJuridicaForm(entidade_orientacao, form)
    return render_template(
        "editar_orientacao_juridica.html", form=form, orientacao=entidade_orientacao
    )


@orientacao_juridica_controller.route("/buscar_orientacao_juridica", methods=["POST"])
@login_required()
def buscar_orientacao_juridica():
    orientacao_juridica_service = OrientacaoJuridicaService(db.session)

    termo = request.form.get("termo", "")
    page = request.args.get("page", 1, type=int)

    def paginator(query: Select[Any]):
        return db.paginate(query, page=page, per_page=per_page)

    orientacoes = orientacao_juridica_service.get_by_area_do_direito(termo, paginator)

    return render_template("orientacoes_juridicas.html", orientacoes=orientacoes)


@orientacao_juridica_controller.route(
    "/cadastro_orientacao_juridica/", methods=["POST", "GET"]
)
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
    ]
)
def cadastro_orientacao_juridica():
    form = CadastroOrientacaoJuridicaForm()
    if request.method == "POST":
        if form.validate():
            orientacao = OrientacaoJuridica(
                area_direito=form.area_direito.data,
                descricao=form.descricao.data,
                data_criacao=datetime.now(),
                status=1,
                id_usuario=current_user.id,
            )

            orientacao.setSubAreas(
                form.area_direito.data,
                form.sub_area.data,
                form.sub_areaAdmin.data,
            )

            db.session.add(orientacao)
            db.session.flush()

            lista_atendidos = request.form.get("listaAtendidos")
            if lista_atendidos:
                try:
                    atendidos_data = json.loads(lista_atendidos)
                    atendidos_ids = atendidos_data.get("id", [])
                    for atendido_id in atendidos_ids:
                        atendido = (
                            db.session.query(Atendido)
                            .filter_by(id=atendido_id, status=True)
                            .first()
                        )
                        if atendido:
                            orientacao.atendidos.append(atendido)
                except (json.JSONDecodeError, KeyError):
                    pass

            if form.encaminhar_outras_aj.data:
                assistencia_id = request.form.get("assistencia_judiciaria")
                if assistencia_id:
                    aj_oj = AssistenciaJudiciaria_xOrientacaoJuridica()
                    aj_oj.id_orientacaoJuridica = orientacao.id
                    aj_oj.id_assistenciaJudiciaria = int(assistencia_id)
                    db.session.add(aj_oj)

            db.session.commit()
            flash("Orientação jurídica cadastrada com sucesso!", "success")
            return redirect(url_for("orientacoes_juridica.orientacoes_juridicas"))
    return render_template("cadastro_orientacao_juridica.html", form=form)


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
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
        usuario_urole_roles["PROFESSOR"][0],
    ]
)
def associacao_orientacao_juridica(id_orientacao, id_atendido):
    orientacao = (
        db.session.query(OrientacaoJuridica)
        .filter_by(id=id_orientacao, status=True)
        .first()
    )
    if not orientacao:
        abort(404)

    if id_atendido:
        atendido = (
            db.session.query(Atendido).filter_by(id=id_atendido, status=True).first()
        )
        if not atendido:
            abort(404)
        atendido.orientacoes_juridicas.append(orientacao)
        db.session.commit()
        flash("Atendido associado à orientação jurídica com sucesso!", "success")

    return redirect(url_for("orientacoes_juridica.perfil_oj", id=id_orientacao))


@orientacao_juridica_controller.route(
    "/desassociar_orientacao_juridica/<int:id_orientacao>/<int:id_atendido>",
    methods=["POST", "GET"],
)
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
        usuario_urole_roles["PROFESSOR"][0],
    ]
)
def desassociar_orientacao_juridica(id_atendido, id_orientacao):
    orientacao = (
        db.session.query(OrientacaoJuridica)
        .filter_by(id=id_orientacao, status=True)
        .first()
    )
    if not orientacao:
        abort(404)

    atendido = db.session.query(Atendido).filter_by(id=id_atendido, status=True).first()
    if not atendido:
        abort(404)

    atendido.orientacoes_juridicas.remove(orientacao)
    db.session.commit()
    flash("Atendido desassociado da orientação jurídica com sucesso!", "success")
    return redirect(url_for("orientacao_juridica.perfil_oj", id=id_orientacao))


@orientacao_juridica_controller.route("/orientacao_juridica/<id>")
@login_required()
def perfil_oj(id):
    orientacao = db.session.query(OrientacaoJuridica).get_or_404(id)

    atendidos_envolvidos = (
        db.session.query(Atendido)
        .join(Atendido_xOrientacaoJuridica)
        .filter(
            Atendido_xOrientacaoJuridica.id_orientacaoJuridica == orientacao.id,
            Atendido.status == True,
        )
        .order_by(Atendido.nome)
        .all()
    )

    usuario = None
    if orientacao.id_usuario:
        usuario = db.session.query(Usuario).filter_by(id=orientacao.id_usuario).first()

    assistencias_envolvidas = (
        db.session.query(AssistenciaJudiciaria_xOrientacaoJuridica)
        .filter_by(id_orientacaoJuridica=orientacao.id)
        .all()
    )

    return render_template(
        "perfil_orientacao_juridica.html",
        orientacao=orientacao,
        atendidos=atendidos_envolvidos,
        assistencias=assistencias_envolvidas,
        usuario=usuario or {"nome": "--"},
    )


@orientacao_juridica_controller.route("/orientacoes_juridicas")
@login_required()
def orientacoes_juridicas():
    orientacao_juridica_service = OrientacaoJuridicaService(db.session)

    page = request.args.get("page", 1, type=int)
    per_page = app.config["ATENDIDOS_POR_PAGINA"]

    def paginator(query: Select[Any]):
        return db.paginate(query, page=page, per_page=per_page)

    orientacoes = orientacao_juridica_service.get_all(paginator)

    return render_template("orientacoes_juridicas.html", orientacoes=orientacoes)


@orientacao_juridica_controller.route("/busca_oj/", defaults={"_busca": None})
@orientacao_juridica_controller.route("/busca_oj/<_busca>", methods=["GET"])
@login_required()
def busca_oj(_busca):
    orientacao_juridica_service = OrientacaoJuridicaService(db.session)

    page = request.args.get("page", 1, type=int)
    per_page = app.config["ATENDIDOS_POR_PAGINA"]

    def paginator(query: Select[Any]):
        return db.paginate(query, page=page, per_page=per_page)

    orientacoes = orientacao_juridica_service.get_all(paginator)

    if _busca is None:
        orientacoes = orientacao_juridica_service.get_all(paginator)
    else:
        orientacoes = (
            queryFiltradaStatus(OrientacaoJuridica)
            .outerjoin(
                Atendido_xOrientacaoJuridica,
                OrientacaoJuridica.id
                == Atendido_xOrientacaoJuridica.id_orientacaoJuridica,
            )
            .outerjoin(
                Atendido, Atendido.id == Atendido_xOrientacaoJuridica.id_atendido
            )
            .filter(
                ((Atendido.nome.contains(_busca)) | (Atendido.cpf.contains(_busca)))
            )
            .order_by(OrientacaoJuridica.id.desc())
            .paginate(
                page=page, per_page=app.config["ATENDIDOS_POR_PAGINA"], error_out=False
            )
        )

    return render_template("busca_orientacoes_juridicas.html", orientacoes=orientacoes)
