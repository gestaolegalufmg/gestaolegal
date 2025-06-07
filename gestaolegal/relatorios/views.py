from datetime import datetime

from flask import (
    Blueprint,
    json,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from sqlalchemy import func

from gestaolegal import app, db, login_required
from gestaolegal.casos.models import (
    Caso,
    situacao_deferimento,
)
from gestaolegal.casos.views_utils import *
from gestaolegal.plantao.models import (
    OrientacaoJuridica,
    RegistroEntrada,
    assistencia_jud_areas_atendidas,
    DiasMarcadosPlantao,
)
from gestaolegal.plantao.views_util import *
from gestaolegal.relatorios.forms import RelatorioForm
from gestaolegal.usuario.models import Usuario, usuario_urole_roles

relatorios = Blueprint("relatorios", __name__, template_folder="templates")


@relatorios.route("/", methods=["POST", "GET"])
@login_required()
def index():  # vai listar os dados como o select2 entende
    form = RelatorioForm(
        role=[
            usuario_urole_roles["ADMINISTRADOR"][0],
            usuario_urole_roles["PROFESSOR"][0],
            usuario_urole_roles["COLAB_EXTERNO"][0],
        ]
    )
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
    return render_template("relatorios.html", form=form)


@relatorios.route("/casos_orientacao_juridica/<inicio>/<final>/<areas>")
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["PROFESSOR"][0],
        usuario_urole_roles["COLAB_EXTERNO"][0],
    ]
)
def casos_orientacao_juridica(inicio, final, areas):
    datas = [inicio, final]
    area_direito = [] if areas == "all" else areas.split(sep=",")
    orientacoes_juridicas = db.session.query(
        OrientacaoJuridica.area_direito, func.count(OrientacaoJuridica.area_direito)
    ).filter(
        OrientacaoJuridica.status == True,
        OrientacaoJuridica.data_criacao >= inicio,
        OrientacaoJuridica.data_criacao <= final,
    )

    if area_direito:
        orientacoes_juridicas = orientacoes_juridicas.filter(
            OrientacaoJuridica.area_direito.in_(area_direito)
        )

    orientacoes_juridicas = orientacoes_juridicas.group_by(
        OrientacaoJuridica.area_direito
    ).all()

    data_emissao = datetime.now().date().strftime("%d/%m/%Y")
    usuario = current_user.nome

    return render_template(
        "casos_orientacao_juridica.html",
        orientacoes_juridicas=orientacoes_juridicas,
        data_emissao=data_emissao,
        usuario=usuario,
        datas=datas,
    )


@relatorios.route(
    "/casos_cadastrados/<inicio>/<final>/<areas>", methods=["POST", "GET"]
)
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["PROFESSOR"][0],
        usuario_urole_roles["COLAB_EXTERNO"][0],
    ]
)
def casos_cadastrados(inicio, final, areas):
    datas = [inicio, final]
    if areas == "all":
        casos = (
            db.session.query(Caso.area_direito, func.count(Caso.area_direito))
            .filter(
                Caso.status == True,
                Caso.data_criacao >= inicio,
                Caso.data_criacao <= final,
            )
            .group_by(Caso.area_direito)
            .all()
        )
    else:
        area_direito = areas.split(sep=",")
        casos = (
            db.session.query(Caso.area_direito, func.count(Caso.area_direito))
            .filter(
                Caso.status == True,
                Caso.data_criacao >= inicio,
                Caso.data_criacao <= final,
                Caso.area_direito.in_(area_direito),
            )
            .group_by(Caso.area_direito)
            .all()
        )
    data_emissao = datetime.now().date().strftime("%d/%m/%Y")
    usuario = current_user.nome
    return render_template(
        "casos_cadastrados.html",
        casos=casos,
        data_emissao=data_emissao,
        usuario=usuario,
        datas=datas,
    )


@relatorios.route("/relatorio_horarios/<inicio>/<final>/<usuarios>")
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["PROFESSOR"][0],
        usuario_urole_roles["COLAB_EXTERNO"][0],
    ]
)
def relatorio_horarios(inicio, final, usuarios):
    datas = [inicio, final]
    if usuarios == "all":
        usuarios = db.session.query(Usuario).all()
        lista_usuarios = []
        horarios = (
            db.session.query(RegistroEntrada).select_from(RegistroEntrada)
            .join(Usuario)
            .filter(
                RegistroEntrada.status == False,
                RegistroEntrada.data_saida >= inicio,
                RegistroEntrada.data_saida <= final,
            )
            .all()
        )
        for usuario in usuarios:
            lista_usuarios.append(usuario.id)
        horarios_plantao = db.session.query(DiasMarcadosPlantao).filter(
            DiasMarcadosPlantao.data_marcada >= inicio,
            DiasMarcadosPlantao.data_marcada <= final,
            DiasMarcadosPlantao.id_usuario.in_(lista_usuarios),
        ).all()
    else:
        usuarios = usuarios.split(sep=",")
        horarios = db.session.query(RegistroEntrada).filter(
            RegistroEntrada.status == False,
            RegistroEntrada.data_saida >= inicio,
            RegistroEntrada.data_saida <= final,
            RegistroEntrada.id_usuario.in_(usuarios),
        ).all()
        horarios_plantao = db.session.query(DiasMarcadosPlantao).filter(
            DiasMarcadosPlantao.data_marcada >= inicio,
            DiasMarcadosPlantao.data_marcada <= final,
            DiasMarcadosPlantao.id_usuario.in_(usuarios),
        ).all()

    data_emissao = datetime.now().date().strftime("%d/%m/%Y")
    usuario = current_user.nome
    return render_template(
        "relatorio_horarios.html",
        data_emissao=data_emissao,
        usuario=usuario,
        horarios=horarios,
        datas=datas,
        horarios_plantao=horarios_plantao,
    )


@relatorios.route("/casos_arq_sol_ativ/<inicio>/<final>/<areas>")
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["PROFESSOR"][0],
        usuario_urole_roles["COLAB_EXTERNO"][0],
    ]
)
def casos_arq_sol_ativ(inicio, final, areas):
    datas = [inicio, final]
    casos_por_area = []
    if areas == "all":
        area_direito = []
        for area in assistencia_jud_areas_atendidas:
            area_direito.append(assistencia_jud_areas_atendidas[area][0])
        casos = db.session.query(Caso).filter(
            Caso.status == True,
            Caso.data_criacao >= inicio,
            Caso.data_criacao <= final,
            Caso.situacao_deferimento.in_(
                [
                    situacao_deferimento["ATIVO"][0],
                    situacao_deferimento["ARQUIVADO"][0],
                    situacao_deferimento["SOLUCIONADO"][0],
                ]
            ),
        ).all()
    else:
        area_direito = areas.split(sep=",")
        casos = db.session.query(Caso).filter(
            Caso.status == True,
            Caso.area_direito.in_(area_direito),
            Caso.data_criacao >= inicio,
            Caso.data_criacao <= final,
            Caso.situacao_deferimento.in_(
                [
                    situacao_deferimento["ATIVO"][0],
                    situacao_deferimento["ARQUIVADO"][0],
                    situacao_deferimento["SOLUCIONADO"][0],
                ]
            ),
        ).all()
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
        "casos_arq_sol_ativ.html",
        casos=casos_por_area,
        data_emissao=data_emissao,
        usuario=usuario,
        datas=datas,
    )


@relatorios.route("/api/buscar_usuarios", methods=["GET"])
@login_required()
def api_relatorios_buscar_usuarios():
    termo = request.args.get("q", type=str)

    # Se nada for digitado, retornar os 5 assistidos mais recentes
    if termo:
        usuarios = (
            db.session.query(Usuario).filter(Usuario.status)
            .filter(Usuario.nome.like(termo + "%"))
            .order_by(Usuario.nome)
            .all()
        )
    else:
        usuarios = db.session.query(Usuario).filter(Usuario.status).order_by(Usuario.nome).all()

    # Dados formatados para o select2
    usuarios_clean = [{"id": usuario.id, "text": usuario.nome} for usuario in usuarios]

    response = app.response_class(
        response=json.dumps({"results": usuarios_clean}),
        status=200,
        mimetype="application/json",
    )
    return response


@relatorios.route("/api/buscar_area_direito", methods=["GET"])
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

    response = app.response_class(
        response=json.dumps({"results": areas_direito_clean}),
        status=200,
        mimetype="application/json",
    )
    return response


@relatorios.route("/relatorio_plantao", methods=["GET", "POST"])
@login_required()
def relatorio_plantao():
    horarios_plantao = db.session.query(DiasMarcadosPlantao).filter(
        DiasMarcadosPlantao.data >= data_inicio,
        DiasMarcadosPlantao.data <= data_fim,
    ).all()


@relatorios.route("/relatorio_casos", methods=["GET", "POST"])
@login_required()
def relatorio_casos():
    casos = db.session.query(Caso).filter(
        Caso.data_criacao >= data_inicio,
        Caso.data_criacao <= data_fim,
    ).all()


@relatorios.route("/relatorio_usuarios", methods=["GET", "POST"])
@login_required()
def relatorio_usuarios():
    if request.method == "POST":
        data_inicio = request.form["data_inicio"]
        data_fim = request.form["data_fim"]
        usuarios = db.session.query(Usuario).filter(Usuario.status).order_by(Usuario.nome).all()
        return render_template(
            "relatorio_usuarios.html",
            usuarios=usuarios,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )
    return render_template("relatorio_usuarios.html")
