from flask import Blueprint, current_app, flash, redirect, render_template, request
from sqlalchemy import and_, or_

from gestaolegal.database import get_db
from gestaolegal.models.assistido_pessoa_juridica import AssistidoPessoaJuridica
from gestaolegal.models.atendido import Atendido
from gestaolegal.schemas import associacao_casos_atendidos
from gestaolegal.schemas.assistido import AssistidoSchema
from gestaolegal.schemas.atendido import AtendidoSchema
from gestaolegal.schemas.atendido_x_orientacao_juridica import (
    Atendido_xOrientacaoJuridicaSchema,
)
from gestaolegal.schemas.caso import CasoSchema
from gestaolegal.schemas.orientacao_juridica import OrientacaoJuridicaSchema
from gestaolegal.schemas.usuario import UsuarioSchema
from gestaolegal.utils.decorators import login_required

principal_controller = Blueprint(
    "principal", __name__, template_folder="../templates/principal"
)


@principal_controller.route("/")
@login_required()
def index():
    return render_template("home.html")


@principal_controller.errorhandler(404)
def error_404(error):
    return render_template("erros/404.html"), 404


@principal_controller.errorhandler(413)
def error_413(error):
    flash("Arquivo muito grande. O tamanho máximo permitido é de 10MB.")
    return redirect(request.url, code=302)


@principal_controller.errorhandler(403)
def error_403(error):
    return render_template("erros/403.html"), 403


@principal_controller.errorhandler(500)
def error_500(error):
    return render_template("erros/500.html"), 403


@principal_controller.route("/termos_de_uso")
@login_required()
def termos():
    return render_template("termos_de_uso.html")


from sqlalchemy import func, select


class SimplePagination:
    def __init__(self, items, page, per_page, total):
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = (total + per_page - 1) // per_page if total > 0 else 0
        self.has_next = page < self.pages if self.pages > 0 else False
        self.has_prev = page > 1 and self.pages > 0
        self.next_num = page + 1 if self.has_next else None
        self.prev_num = page - 1 if self.has_prev else None


@principal_controller.route("/busca_geral", methods=["GET", "POST"])
@login_required()
def busca_geral():
    db = get_db()

    page_assistido_pfisica = request.args.get("page_assistido_pfisica", 1, type=int)
    page_assistido_pjuridica = request.args.get("page_assistido_pjuridica", 1, type=int)
    page_usuario = request.args.get("page_usuario", 1, type=int)
    page_caso = request.args.get("page_caso", 1, type=int)

    if request.method == "POST":
        busca = request.form["busca_geral"]
    else:
        busca = request.args.get("busca_atual", "", type=str)

    def create_pagination(stmt, page, per_page):
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.session.execute(count_stmt).scalar()

        offset = (page - 1) * per_page
        paginated_stmt = stmt.offset(offset).limit(per_page)
        items = db.session.execute(paginated_stmt).scalars().all()

        return SimplePagination(items, page, per_page, total)

    assistidos_stmt = (
        select(AtendidoSchema)
        .join(AssistidoSchema)
        .where(AtendidoSchema.status == True)
        .where(
            or_(
                AtendidoSchema.nome.ilike(f"%{busca}%"),
                AtendidoSchema.cpf.contains(busca),
            )
        )
        .order_by(AtendidoSchema.nome)
    )
    assistidos = create_pagination(
        assistidos_stmt,
        page_assistido_pfisica,
        current_app.config["ATENDIDOS_POR_PAGINA"],
    )

    assistidos_pjuridica_stmt = (
        select(AssistidoSchema)
        .join(AtendidoSchema)
        .join(AssistidoPessoaJuridica)
        .where(AtendidoSchema.status == True)
        .where(
            or_(AtendidoSchema.nome.contains(busca), AtendidoSchema.cpf.contains(busca))
        )
        .order_by(Atendido.nome)
    )
    assistidos_pjuridica = create_pagination(
        assistidos_pjuridica_stmt,
        page_assistido_pjuridica,
        current_app.config["ATENDIDOS_POR_PAGINA"],
    )

    usuarios_stmt = (
        select(UsuarioSchema)
        .where(
            or_(
                and_(UsuarioSchema.nome.contains(busca), UsuarioSchema.status != False),
                and_(UsuarioSchema.cpf.contains(busca), UsuarioSchema.status != False),
            )
        )
        .order_by(UsuarioSchema.nome)
    )
    usuarios = create_pagination(
        usuarios_stmt, page_usuario, current_app.config["USUARIOS_POR_PAGINA"]
    )

    casos = None
    orientacoes_juridicas = None

    if busca.isdigit():
        casos_stmt = select(CasoSchema).where(
            and_(CasoSchema.status == True, CasoSchema.id == int(busca))
        )
        casos = create_pagination(
            casos_stmt, page_caso, current_app.config["CASOS_POR_PAGINA"]
        )
    elif busca.strip():
        casos_stmt = (
            select(CasoSchema)
            .join(associacao_casos_atendidos)
            .join(Atendido)
            .where(CasoSchema.status == True)
            .where(Atendido.status == True)
            .where(Atendido.nome.ilike(f"%{busca}%"))
            .order_by(CasoSchema.id)
        )
        casos = create_pagination(
            casos_stmt, page_caso, current_app.config["CASOS_POR_PAGINA"]
        )

        # Busca orientações jurídicas que tenham atendidos com nome similar ao termo de busca
        orientacoes_stmt = (
            select(OrientacaoJuridicaSchema)
            .join(Atendido_xOrientacaoJuridicaSchema)
            .join(Atendido)
            .where(OrientacaoJuridicaSchema.status == True)
            .where(Atendido.status == True)
            .where(Atendido.nome.ilike(f"%{busca}%"))
            .order_by(OrientacaoJuridicaSchema.id)
        )
        orientacoes_juridicas = create_pagination(
            orientacoes_stmt, page_caso, current_app.config["CASOS_POR_PAGINA"]
        )

    return render_template(
        "busca_geral.html",
        assistidos=assistidos,
        assistidos_pjuridica=assistidos_pjuridica,
        usuarios=usuarios,
        casos=casos,
        orientacoes_juridicas=orientacoes_juridicas,
        busca_atual=busca,
    )
