import json
from datetime import datetime
from typing import Any

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from sqlalchemy import Select

from gestaolegal.common.constants import UserRole
from gestaolegal.database import get_db
from gestaolegal.forms.plantao.orientacao_juridica_form import (
    CadastroOrientacaoJuridicaForm,
    OrientacaoJuridicaForm,
)
from gestaolegal.schemas.assistencia_judiciaria_x_orientacao_juridica import (
    AssistenciaJudiciaria_xOrientacaoJuridicaSchema,
)
from gestaolegal.schemas.atendido import AtendidoSchema
from gestaolegal.schemas.atendido_x_orientacao_juridica import (
    Atendido_xOrientacaoJuridicaSchema,
)
from gestaolegal.schemas.orientacao_juridica import OrientacaoJuridicaSchema
from gestaolegal.schemas.usuario import UsuarioSchema
from gestaolegal.services.orientacao_juridica_service import OrientacaoJuridicaService
from gestaolegal.utils.decorators import login_required
from gestaolegal.utils.models import queryFiltradaStatus

orientacao_juridica_controller = Blueprint(
    "orientacao_juridica", __name__, template_folder="../templates/orientacao_juridica"
)


@orientacao_juridica_controller.route("/excluir_orientacao_juridica/", methods=["POST"])
@login_required(role=[UserRole.ADMINISTRADOR])
def excluir_oj():
    db = get_db()
    orientacao_juridica_service = OrientacaoJuridicaService()

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
@login_required(role=[UserRole.ADMINISTRADOR, UserRole.PROFESSOR])
def editar_orientacao_juridica(id_oj: int):
    db = get_db()

    orientacao_juridica_service = OrientacaoJuridicaService()

    def setDadosOrientacaoJuridica(
        entidade_orientacao: OrientacaoJuridicaSchema, form: OrientacaoJuridicaForm
    ):
        entidade_orientacao.area_direito = form.area_direito.data
        entidade_orientacao.descricao = form.descricao.data
        entidade_orientacao.setSubAreas(
            entidade_orientacao.area_direito,
            form.sub_area.data,
            form.sub_areaAdmin.data,
        )

    def setOrientacaoJuridicaForm(
        entidade_orientacao: OrientacaoJuridicaSchema, form: OrientacaoJuridicaForm
    ):
        form.area_direito.data = entidade_orientacao.area_direito
        form.sub_area.data = entidade_orientacao.sub_area
        form.descricao.data = entidade_orientacao.descricao

    ############################################# IMPLEMENTAÇÃO DA ROTA ##############################################################

    entidade_orientacao = orientacao_juridica_service.find_by_id(id_oj)

    if not entidade_orientacao:
        flash("Essa orientação não existe!", "warning")
        return redirect(url_for("orientacao_juridica.orientacoes_juridicas"))

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
    db = get_db()

    orientacao_juridica_service = OrientacaoJuridicaService()

    termo = request.form.get("termo", "")
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["ATENDIDOS_POR_PAGINA"]

    def paginator(query: Select[Any]):
        return db.paginate(query, page=page, per_page=per_page)

    orientacoes = orientacao_juridica_service.get_by_area_do_direito(termo, paginator)

    return render_template("orientacoes_juridicas.html", orientacoes=orientacoes)


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
    db = get_db()

    form = CadastroOrientacaoJuridicaForm()
    if request.method == "POST":
        if form.validate():
            orientacao = OrientacaoJuridicaSchema(
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
                            db.session.query(AtendidoSchema)
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
                    aj_oj = AssistenciaJudiciaria_xOrientacaoJuridicaSchema()
                    aj_oj.id_orientacaoJuridica = orientacao.id
                    aj_oj.id_assistenciaJudiciaria = int(assistencia_id)
                    db.session.add(aj_oj)

            db.session.commit()
            flash("Orientação jurídica cadastrada com sucesso!", "success")
            return redirect(url_for("orientacao_juridica.orientacoes_juridicas"))
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
        UserRole.ADMINISTRADOR,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.PROFESSOR,
    ]
)
def associacao_orientacao_juridica(id_orientacao, id_atendido):
    db = get_db()

    orientacao = (
        db.session.query(OrientacaoJuridicaSchema)
        .filter_by(id=id_orientacao, status=True)
        .first()
    )
    if not orientacao:
        abort(404)

    if id_atendido:
        try:
            atendido = (
                db.session.query(AtendidoSchema)
                .filter_by(id=id_atendido, status=True)
                .first()
            )
            if not atendido:
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return jsonify(
                        {"success": False, "message": "Atendido não encontrado"}
                    ), 404
                abort(404)

            if orientacao in atendido.orientacoesJuridicas:
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return jsonify(
                        {
                            "success": False,
                            "message": "Atendido já está associado a esta orientação jurídica",
                        }
                    ), 400
                flash(
                    "Atendido já está associado a esta orientação jurídica!", "warning"
                )
                return redirect(
                    url_for("orientacao_juridica.perfil_oj", id=id_orientacao)
                )

            atendido.orientacoesJuridicas.append(orientacao)
            db.session.commit()

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify(
                    {
                        "success": True,
                        "message": "Atendido associado à orientação jurídica com sucesso!",
                    }
                )

            flash("Atendido associado à orientação jurídica com sucesso!", "success")
            return redirect(url_for("orientacao_juridica.perfil_oj", id=id_orientacao))
        except Exception as e:
            db.session.rollback()
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify(
                    {
                        "success": False,
                        "message": f"Erro ao associar atendido: {str(e)}",
                    }
                ), 500
            flash(f"Erro ao associar atendido: {str(e)}", "error")
            return redirect(url_for("orientacao_juridica.perfil_oj", id=id_orientacao))

    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["ATENDIDOS_POR_PAGINA"]

    atendidos_query = (
        db.session.query(AtendidoSchema)
        .filter_by(status=True)
        .order_by(AtendidoSchema.nome)
    )
    pagination = db.paginate(
        atendidos_query, page=page, per_page=per_page, error_out=False
    )

    return render_template(
        "associa_orientacao_juridica.html",
        orientacao_entidade=orientacao,
        pagination=pagination,
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
    db = get_db()

    orientacao = (
        db.session.query(OrientacaoJuridicaSchema)
        .filter_by(id=id_orientacao, status=True)
        .first()
    )
    if not orientacao:
        abort(404)

    atendido = (
        db.session.query(AtendidoSchema).filter_by(id=id_atendido, status=True).first()
    )
    if not atendido:
        abort(404)

    atendido.orientacoesJuridicas.remove(orientacao)
    db.session.commit()
    flash("Atendido desassociado da orientação jurídica com sucesso!", "success")
    return redirect(url_for("orientacao_juridica.perfil_oj", id=id_orientacao))


@orientacao_juridica_controller.route("/orientacao_juridica/<id>")
@login_required()
def perfil_oj(id):
    db = get_db()

    orientacao = db.session.query(OrientacaoJuridicaSchema).get_or_404(id)

    atendidos_envolvidos = (
        db.session.query(AtendidoSchema)
        .join(Atendido_xOrientacaoJuridicaSchema)
        .filter(
            Atendido_xOrientacaoJuridicaSchema.id_orientacaoJuridica == orientacao.id,
            AtendidoSchema.status == True,
        )
        .order_by(AtendidoSchema.nome)
        .all()
    )

    usuario = None
    if orientacao.id_usuario:
        usuario = (
            db.session.query(UsuarioSchema).filter_by(id=orientacao.id_usuario).first()
        )

    assistencias_envolvidas = (
        db.session.query(AssistenciaJudiciaria_xOrientacaoJuridicaSchema)
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


@orientacao_juridica_controller.route("/buscar_atendidos_ajax")
@login_required()
def buscar_atendidos_ajax():
    db = get_db()

    termo = request.args.get("termo", "")
    orientacao_id = request.args.get("orientacao_id")
    template_type = request.args.get("template", "single")

    query = db.session.query(AtendidoSchema).filter(AtendidoSchema.status == True)

    if orientacao_id and orientacao_id != "0":
        query = query.outerjoin(Atendido_xOrientacaoJuridicaSchema).filter(
            (
                Atendido_xOrientacaoJuridicaSchema.id_orientacaoJuridica
                != int(orientacao_id)
            )
            | (Atendido_xOrientacaoJuridicaSchema.id_orientacaoJuridica.is_(None))
        )

    if termo:
        query = query.filter(
            (AtendidoSchema.nome.ilike(f"%{termo}%"))
            | (AtendidoSchema.cpf.ilike(f"%{termo}%"))
            | (AtendidoSchema.cnpj.ilike(f"%{termo}%"))
        )

    atendidos = query.order_by(AtendidoSchema.nome).limit(20).all()

    return render_template(
        "atendido/atendidos_lista_ajax.html",
        atendidos=atendidos,
        termo=termo,
        template_type=template_type,
    )


@orientacao_juridica_controller.route("/orientacoes_juridicas")
@login_required()
def orientacoes_juridicas():
    db = get_db()

    orientacao_juridica_service = OrientacaoJuridicaService()

    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["ATENDIDOS_POR_PAGINA"]

    def paginator(query: Select[Any]):
        return db.paginate(query, page=page, per_page=per_page)

    orientacoes = orientacao_juridica_service.get_all(paginator)

    return render_template("orientacoes_juridicas.html", orientacoes=orientacoes)


@orientacao_juridica_controller.route("/busca_oj/", defaults={"_busca": None})
@orientacao_juridica_controller.route("/busca_oj/<_busca>", methods=["GET"])
@login_required()
def busca_oj(_busca):
    db = get_db()

    orientacao_juridica_service = OrientacaoJuridicaService()

    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["ATENDIDOS_POR_PAGINA"]

    def paginator(query: Select[Any]):
        return db.paginate(query, page=page, per_page=per_page)

    orientacoes = orientacao_juridica_service.get_all(paginator)

    if _busca is None:
        orientacoes = orientacao_juridica_service.get_all(paginator)
    else:
        orientacoes = (
            queryFiltradaStatus(OrientacaoJuridicaSchema)
            .outerjoin(
                Atendido_xOrientacaoJuridicaSchema,
                OrientacaoJuridicaSchema.id
                == Atendido_xOrientacaoJuridicaSchema.id_orientacaoJuridica,
            )
            .outerjoin(
                AtendidoSchema,
                AtendidoSchema.id == Atendido_xOrientacaoJuridicaSchema.id_atendido,
            )
            .filter(
                (
                    (AtendidoSchema.nome.contains(_busca))
                    | (AtendidoSchema.cpf.contains(_busca))
                )
            )
            .order_by(OrientacaoJuridicaSchema.data_criacao.desc())
            .paginate(
                page=page,
                per_page=current_app.config["ATENDIDOS_POR_PAGINA"],
                error_out=False,
            )
        )

    return render_template("busca_orientacoes_juridicas.html", orientacoes=orientacoes)
