import logging
from datetime import datetime

from flask import (
    Blueprint,
    current_app,
    json,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from sqlalchemy import func

from gestaolegal import csrf
from gestaolegal.common.constants import UserRole, situacao_deferimento
from gestaolegal.forms.relatorio import RelatorioForm
from gestaolegal.schemas.caso import CasoSchema
from gestaolegal.schemas.dias_marcados_plantao import DiasMarcadosPlantaoSchema
from gestaolegal.schemas.orientacao_juridica import OrientacaoJuridicaSchema
from gestaolegal.schemas.registro_entrada import RegistroEntradaSchema
from gestaolegal.schemas.usuario import UsuarioSchema
from gestaolegal.utils.casos_utils import *
from gestaolegal.utils.decorators import login_required
from gestaolegal.utils.plantao_utils import *

logger = logging.getLogger(__name__)

relatorios_controller = Blueprint(
    "relatorios", __name__, template_folder="../static/templates"
)


@relatorios_controller.route("/", methods=["POST", "GET"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_EXTERNO,
    ]
)
def index():  # vai listar os dados como o select2 entende
    form = RelatorioForm()
    if request.method == "POST":
        inicio = form.data_inicio.data
        final = form.data_final.data
        if form.area_direito.data == "":
            areas = "all"
        else:
            areas = form.area_direito.data
        if form.usuarios.data == "":
            usuarios = "all"
        else:
            usuarios = form.usuarios.data
        if form.tipo_relatorio.data == "horario_usuarios":
            return redirect(
                url_for(
                    "relatorios.relatorio_horarios",
                    inicio=inicio,
                    final=final,
                    usuarios=usuarios,
                )
            )
        if form.tipo_relatorio.data == "casos_orientacao":
            return redirect(
                url_for(
                    "relatorios.casos_orientacao_juridica",
                    inicio=inicio,
                    final=final,
                    areas=areas,
                )
            )
        if form.tipo_relatorio.data == "casos_cadastrados":
            return redirect(
                url_for(
                    "relatorios.casos_cadastrados",
                    inicio=inicio,
                    final=final,
                    areas=areas,
                )
            )
        if form.tipo_relatorio.data == "casos_arquiv_soluc_ativ":
            return redirect(
                url_for(
                    "relatorios.casos_arq_sol_ativ",
                    inicio=inicio,
                    final=final,
                    areas=areas,
                )
            )
    return render_template("relatorios/pagina_relatorios.html", form=form)


@relatorios_controller.route("/casos_orientacao_juridica/<inicio>/<final>/<areas>")
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_EXTERNO,
    ]
)
def casos_orientacao_juridica(inicio, final, areas):
    db = get_db()

    datas = [inicio, final]
    area_direito = [] if areas == "all" else areas.split(sep=",")
    orientacoes_juridicas = db.session.query(
        OrientacaoJuridicaSchema.area_direito,
        func.count(OrientacaoJuridicaSchema.area_direito),
    ).filter(
        OrientacaoJuridicaSchema.status,
        OrientacaoJuridicaSchema.data_criacao >= inicio,
        OrientacaoJuridicaSchema.data_criacao <= final,
    )

    if area_direito:
        orientacoes_juridicas = orientacoes_juridicas.filter(
            OrientacaoJuridicaSchema.area_direito.in_(area_direito)
        )

    orientacoes_juridicas = orientacoes_juridicas.group_by(
        OrientacaoJuridicaSchema.area_direito
    ).all()

    data_emissao = datetime.now().date().strftime("%d/%m/%Y")
    usuario = current_user.nome

    return render_template(
        "relatorios/relatorio_casos_orientacao.html",
        orientacoes_juridicas=orientacoes_juridicas,
        data_emissao=data_emissao,
        usuario=usuario,
        datas=datas,
    )


@relatorios_controller.route(
    "/casos_cadastrados/<inicio>/<final>/<areas>", methods=["POST", "GET"]
)
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_EXTERNO,
    ]
)
def casos_cadastrados(inicio, final, areas):
    db = get_db()

    datas = [inicio, final]
    if areas == "all":
        casos = (
            db.session.query(
                CasoSchema.area_direito, func.count(CasoSchema.area_direito)
            )
            .filter(
                CasoSchema.status,
                CasoSchema.data_criacao >= inicio,
                CasoSchema.data_criacao <= final,
            )
            .group_by(CasoSchema.area_direito)
            .all()
        )
    else:
        area_direito = areas.split(sep=",")
        casos = (
            db.session.query(
                CasoSchema.area_direito, func.count(CasoSchema.area_direito)
            )
            .filter(
                CasoSchema.status,
                CasoSchema.data_criacao >= inicio,
                CasoSchema.data_criacao <= final,
                CasoSchema.area_direito.in_(area_direito),
            )
            .group_by(CasoSchema.area_direito)
            .all()
        )
    data_emissao = datetime.now().date().strftime("%d/%m/%Y")
    usuario = current_user.nome
    return render_template(
        "relatorios/relatorio_casos_cadastrados.html",
        casos=casos,
        data_emissao=data_emissao,
        usuario=usuario,
        datas=datas,
    )


@relatorios_controller.route("/relatorio_horarios/<inicio>/<final>/<usuarios>")
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_EXTERNO,
    ]
)
def relatorio_horarios(inicio, final, usuarios):
    db = get_db()

    datas = [inicio, final]
    if usuarios == "all":
        usuarios = db.session.query(UsuarioSchema).all()
        lista_usuarios = []
        horarios = (
            db.session.query(RegistroEntradaSchema)
            .select_from(RegistroEntradaSchema)
            .join(UsuarioSchema)
            .filter(
                not RegistroEntradaSchema.status,
                RegistroEntradaSchema.data_saida >= inicio,
                RegistroEntradaSchema.data_saida <= final,
            )
            .all()
        )
        for usuario in usuarios:
            lista_usuarios.append(usuario.id)
        horarios_plantao = (
            db.session.query(DiasMarcadosPlantaoSchema)
            .filter(
                DiasMarcadosPlantaoSchema.data_marcada >= inicio,
                DiasMarcadosPlantaoSchema.data_marcada <= final,
                DiasMarcadosPlantaoSchema.id_usuario.in_(lista_usuarios),
            )
            .all()
        )
    else:
        usuarios = usuarios.split(sep=",")
        horarios = (
            db.session.query(RegistroEntradaSchema)
            .filter(
                not RegistroEntradaSchema.status,
                RegistroEntradaSchema.data_saida >= inicio,
                RegistroEntradaSchema.data_saida <= final,
                RegistroEntradaSchema.id_usuario.in_(usuarios),
            )
            .all()
        )
        horarios_plantao = (
            db.session.query(DiasMarcadosPlantaoSchema)
            .filter(
                DiasMarcadosPlantaoSchema.data_marcada >= inicio,
                DiasMarcadosPlantaoSchema.data_marcada <= final,
                DiasMarcadosPlantaoSchema.id_usuario.in_(usuarios),
            )
            .all()
        )

    data_emissao = datetime.now().date().strftime("%d/%m/%Y")
    usuario = current_user.nome
    return render_template(
        "relatorios/relatorio_horarios.html",
        data_emissao=data_emissao,
        usuario=usuario,
        horarios=horarios,
        datas=datas,
        horarios_plantao=horarios_plantao,
    )


@relatorios_controller.route("/casos_arq_sol_ativ/<inicio>/<final>/<areas>")
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_EXTERNO,
    ]
)
def casos_arq_sol_ativ(inicio, final, areas):
    db = get_db()

    datas = [inicio, final]
    casos_por_area = []
    if areas == "all":
        area_direito = []
        for area in assistencia_jud_areas_atendidas:
            area_direito.append(assistencia_jud_areas_atendidas[area][0])
        casos = (
            db.session.query(CasoSchema)
            .filter(
                CasoSchema.status,
                CasoSchema.data_criacao >= inicio,
                CasoSchema.data_criacao <= final,
                CasoSchema.situacao_deferimento.in_(
                    [
                        situacao_deferimento["ATIVO"][0],
                        situacao_deferimento["ARQUIVADO"][0],
                        situacao_deferimento["SOLUCIONADO"][0],
                    ]
                ),
            )
            .all()
        )
    else:
        area_direito = areas.split(sep=",")
        casos = (
            db.session.query(CasoSchema)
            .filter(
                CasoSchema.status,
                CasoSchema.area_direito.in_(area_direito),
                CasoSchema.data_criacao >= inicio,
                CasoSchema.data_criacao <= final,
                CasoSchema.situacao_deferimento.in_(
                    [
                        situacao_deferimento["ATIVO"][0],
                        situacao_deferimento["ARQUIVADO"][0],
                        situacao_deferimento["SOLUCIONADO"][0],
                    ]
                ),
            )
            .all()
        )
    for area in area_direito:
        casos_por_area.append([area, 0, 0, 0])
    for caso in casos:
        i = 0
        for area in area_direito:
            if caso.area_direito == area:
                break
            else:
                i += 1
        if caso.situacao_deferimento == situacao_deferimento["ARQUIVADO"][0]:
            j = 1
        if caso.situacao_deferimento == situacao_deferimento["SOLUCIONADO"][0]:
            j = 2
        if caso.situacao_deferimento == situacao_deferimento["ATIVO"][0]:
            j = 3
        casos_por_area[i][j] += 1
    data_emissao = datetime.now().date().strftime("%d/%m/%Y")
    usuario = current_user.nome
    return render_template(
        "relatorios/relatorio_casos_status.html",
        casos=casos_por_area,
        data_emissao=data_emissao,
        usuario=usuario,
        datas=datas,
    )


@relatorios_controller.route("/api/buscar_usuarios", methods=["GET"])
@csrf.exempt
@login_required()
def api_relatorios_buscar_usuarios():
    termo = request.args.get("q", type=str)
    db = get_db()

    # Se nada for digitado, retornar os 5 assistidos mais recentes
    if termo:
        usuarios = (
            db.session.query(UsuarioSchema)
            .filter(UsuarioSchema.status)
            .filter(UsuarioSchema.nome.like(termo + "%"))
            .order_by(UsuarioSchema.nome)
            .all()
        )
    else:
        usuarios = (
            db.session.query(UsuarioSchema)
            .filter(UsuarioSchema.status)
            .order_by(UsuarioSchema.nome)
            .all()
        )

    # Dados formatados para o select2
    usuarios_clean = [{"id": usuario.id, "text": usuario.nome} for usuario in usuarios]

    response = current_app.response_class(
        response=json.dumps({"results": usuarios_clean}),
        status=200,
        mimetype="application/json",
    )
    return response


@relatorios_controller.route("/api/buscar_area_direito", methods=["GET"])
@csrf.exempt
@login_required()
def api_relatorios_buscar_area_direito():
    termo = request.args.get("q", type=str)
    areas_direito_clean = []

    if not termo:
        areas_direito_clean = [
            {
                "id": assistencia_jud_areas_atendidas[area][0],
                "text": assistencia_jud_areas_atendidas[area][1],
            }
            for area in assistencia_jud_areas_atendidas
        ]

    else:
        area_direito_front = {}

        for area in assistencia_jud_areas_atendidas:
            if (termo in assistencia_jud_areas_atendidas[area][1]) or (termo in area):
                area_direito_front[area] = assistencia_jud_areas_atendidas[area][1]

        areas_direito_clean = [
            {
                "id": assistencia_jud_areas_atendidas[area][0],
                "text": area_direito_front[area],
            }
            for area in area_direito_front
        ]

    response = current_app.response_class(
        response=json.dumps({"results": areas_direito_clean}),
        status=200,
        mimetype="application/json",
    )
    return response


@relatorios_controller.route("/relatorio_plantao", methods=["GET", "POST"])
@login_required()
def relatorio_plantao():
    db = get_db()

    (
        db.session.query(DiasMarcadosPlantaoSchema)
        .filter(
            DiasMarcadosPlantaoSchema.data >= data_inicio,
            DiasMarcadosPlantaoSchema.data <= data_fim,
        )
        .all()
    )


@relatorios_controller.route("/relatorio_casos", methods=["GET", "POST"])
@login_required()
def relatorio_casos():
    db = get_db()

    (
        db.session.query(CasoSchema)
        .filter(
            CasoSchema.data_criacao >= data_inicio,
            CasoSchema.data_criacao <= data_fim,
        )
        .all()
    )


@relatorios_controller.route("/relatorio_usuarios", methods=["GET", "POST"])
@login_required()
def relatorio_usuarios():
    db = get_db()

    if request.method == "POST":
        data_inicio = request.form["data_inicio"]
        data_fim = request.form["data_fim"]
        usuarios = (
            db.session.query(UsuarioSchema)
            .filter(UsuarioSchema.status)
            .order_by(UsuarioSchema.nome)
            .all()
        )
        return render_template(
            "relatorio_usuarios.html",
            usuarios=usuarios,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )
    return render_template("relatorio_usuarios.html")
