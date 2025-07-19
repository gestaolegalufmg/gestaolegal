from typing import Any

from flask import (
    Blueprint,
    abort,
    flash,
    json,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import Select

from gestaolegal import app, db, login_required
from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
from gestaolegal.models.endereco import Endereco
from gestaolegal.plantao.forms.assistencia_juridica_form import (
    AssistenciaJudiciariaForm,
)
from gestaolegal.plantao.models import (
    AssistenciaJudiciaria_xOrientacaoJuridica,
)
from gestaolegal.plantao.views_util import (
    busca_assistencias_judiciarias_modal,
    filtro_busca_assistencia_judiciaria,
)
from gestaolegal.services.assistencia_judiciaria_service import (
    AssistenciaJudiciariaService,
)
from gestaolegal.services.orientacao_juridica_service import OrientacaoJuridicaService
from gestaolegal.usuario.models import (
    usuario_urole_roles,
)

assistencia_judiciaria_controller = Blueprint(
    "assistencia_judiciaria", __name__, template_folder="templates"
)


@assistencia_judiciaria_controller.route(
    "/encaminha_assistencia_judiciaria/<int:id_orientacao>", methods=["POST", "GET"]
)
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
        usuario_urole_roles["PROFESSOR"][0],
    ]
)
def encaminha_assistencia_judiciaria(id_orientacao: int):
    orientacao_juridica_service = OrientacaoJuridicaService(db.session)
    orientacao = orientacao_juridica_service.find_by_id(id_orientacao)

    if not orientacao:
        abort(404)
    form = AssistenciaJudiciariaForm()
    if request.method == "POST":
        if form.validate():
            aj_oj = AssistenciaJudiciaria_xOrientacaoJuridica()
            aj_oj.id_orientacaoJuridica = orientacao.id
            aj_oj.id_assistenciaJudiciaria = form.areas_atendidas.data
            db.session.add(aj_oj)
            db.session.commit()
            flash("Assistência judiciária cadastrada com sucesso!", "success")
            return redirect(
                url_for("assistencia_judiciaria.listar_assistencias_judiciarias")
            )
    return render_template("cadastro_assistencia_judiciaria.html", form=form)


@assistencia_judiciaria_controller.route(
    "/ajax_multiselect_associa_aj_oj/<int:orientacao_id>", methods=["POST", "GET"]
)
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
        usuario_urole_roles["PROFESSOR"][0],
    ]
)
def ajax_multiselect_associa_aj_oj(orientacao_id: int):
    orientacao_juridica_service = OrientacaoJuridicaService(db.session)
    orientacao = orientacao_juridica_service.find_by_id(orientacao_id)

    if not orientacao:
        abort(404)

    assistencias = (
        db.session.query(AssistenciaJudiciaria)
        .filter(
            AssistenciaJudiciaria.area_direito == orientacao.area_direito,
            AssistenciaJudiciaria.status == True,
        )
        .all()
    )

    return json.dumps({"assistencias": [x.as_dict() for x in assistencias]})


# Excluir assistência judiciária
@assistencia_judiciaria_controller.route(
    "/excluir_assistencia_judiciaria/<int:id>", methods=["POST"]
)
@login_required(role=[usuario_urole_roles["ADMINISTRADOR"][0]])
def excluir_assistencia_judiciaria(id: int):
    assistencia_judiciaria_service = AssistenciaJudiciariaService(db.session)

    assistencia = assistencia_judiciaria_service.find_by_id(id)

    if not assistencia:
        flash("Assistência judiciária não encontrada!", "warning")
        return redirect(
            url_for("assistencia_judiciaria.listar_assistencias_judiciarias")
        )

    assistencia.status = False
    db.session.commit()
    flash("Assistência judiciária excluída com sucesso!", "success")
    return redirect(url_for("assistencia_judiciaria.listar_assistencias_judiciarias"))


# Busca da página de assistências judiciárias
@assistencia_judiciaria_controller.route(
    "/busca_assistencia_judiciaria/", methods=["GET", "POST"]
)
@login_required()
def busca_assistencia_judiciaria():
    assistencia_judiciaria_service = AssistenciaJudiciariaService(db.session)

    page = request.args.get("page", 1, type=int)
    per_page = app.config["ATENDIDOS_POR_PAGINA"]
    _busca = request.args.get("busca", "", type=str)
    filtro = request.args.get(
        "opcao_filtro", filtro_busca_assistencia_judiciaria["TODAS"][0], type=str
    )

    def paginator(query: Select[Any]):
        return db.paginate(query, page=page, per_page=per_page)

    assistencias = assistencia_judiciaria_service.get_by_areas_atendida(
        filtro, _busca, paginator
    )

    return render_template(
        "busca_assistencia_judiciaria.html", assistencias=assistencias
    )


# Perfil da assistência judiciária
@assistencia_judiciaria_controller.route("/perfil_assistencia_judiciaria/<_id>")
@login_required()
def perfil_assistencia_judiciaria(_id: int):
    aj = (
        db.session.query(AssistenciaJudiciaria, Endereco)
        .select_from(AssistenciaJudiciaria)
        .join(Endereco)
        .filter((AssistenciaJudiciaria.id == _id))
        .first()
    )
    if aj is None:
        flash("Assistência judiciária não encontrada.", "warning")
        return redirect(
            url_for("assistencia_judiciaria.listar_assistencias_judiciarias")
        )
    return render_template("visualizar_assistencia_judiciaria.html", aj=aj)


### Retorna lista de assistencia judiciaria
@assistencia_judiciaria_controller.route(
    "/todas-assistencias-judiciarias", methods=["GET", "POST"]
)
@login_required()
def pega_assistencias_judiciarias():
    assistencias_judiciarias = busca_assistencias_judiciarias_modal()
    return json.dumps(assistencias_judiciarias)


@assistencia_judiciaria_controller.route(
    "/assistencias_judiciarias/", methods=["POST", "GET"]
)
@login_required()
def listar_assistencias_judiciarias():
    assistencia_judiciaria_service = AssistenciaJudiciariaService(db.session)

    page = request.args.get("page", 1, type=int)
    per_page = app.config["ATENDIDOS_POR_PAGINA"]

    def paginator(query: Select[Any]):
        return db.paginate(query, page=page, per_page=per_page)

    assistencias = assistencia_judiciaria_service.get_all(paginator)

    return render_template(
        "lista_assistencia_judiciaria.html",
        assistencias=assistencias,
        filtro_busca_assistencia_judiciaria=filtro_busca_assistencia_judiciaria,
    )


@assistencia_judiciaria_controller.route(
    "/editar_assistencia_judiciaria/<int:id_assistencia_judiciaria>",
    methods=["POST", "GET"],
)
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["PROFESSOR"][0],
        usuario_urole_roles["COLAB_PROJETO"][0],
        usuario_urole_roles["COLAB_EXTERNO"][0],
    ]
)
def editar_assistencia_judiciaria(id_assistencia_judiciaria: int):
    assistencia_judiciaria_service = AssistenciaJudiciariaService(db.session)
    assistencia_juridica = assistencia_judiciaria_service.find_by_id(
        id_assistencia_judiciaria
    )

    if not assistencia_juridica:
        flash("Assistência judiciária não encontrada!", "warning")
        return redirect(
            url_for("assistencia_judiciaria.listar_assistencias_judiciarias")
        )

    form = AssistenciaJudiciariaForm()

    if form.validate_on_submit():
        assistencia_juridica.nome = form.nome.data
        assistencia_juridica.regiao = form.regiao.data
        assistencia_juridica.setAreas_atendidas(form.areas_atendidas.data)
        assistencia_juridica.telefone = form.telefone.data
        assistencia_juridica.email = form.email.data
        assistencia_juridica.endereco.logradouro = form.logradouro.data
        assistencia_juridica.endereco.numero = form.numero.data
        assistencia_juridica.endereco.complemento = form.complemento.data
        assistencia_juridica.endereco.bairro = form.bairro.data
        assistencia_juridica.endereco.cep = form.cep.data
        assistencia_juridica.endereco.cidade = form.cidade.data
        assistencia_juridica.endereco.estado = form.estado.data

        db.session.commit()
        flash("Assistência judiciária editada com sucesso!", "success")
        return redirect(
            url_for("assistencia_judiciaria.listar_assistencias_judiciarias")
        )

    # Pre-fill form with existing data
    form.nome.data = assistencia_juridica.nome
    form.regiao.data = assistencia_juridica.regiao
    form.areas_atendidas.data = assistencia_juridica.getAreas_atendidas()
    form.telefone.data = assistencia_juridica.telefone
    form.email.data = assistencia_juridica.email
    form.logradouro.data = assistencia_juridica.endereco.logradouro
    form.numero.data = assistencia_juridica.endereco.numero
    form.complemento.data = assistencia_juridica.endereco.complemento
    form.bairro.data = assistencia_juridica.endereco.bairro
    form.cep.data = assistencia_juridica.endereco.cep
    form.cidade.data = assistencia_juridica.endereco.cidade
    form.estado.data = assistencia_juridica.endereco.estado

    return render_template("editar_assistencia_juridica.html", form=form)


@assistencia_judiciaria_controller.route(
    "/cadastro_assistencia_judiciaria", methods=["GET", "POST"]
)
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["PROFESSOR"][0],
        usuario_urole_roles["COLAB_PROJETO"][0],
        usuario_urole_roles["COLAB_EXTERNO"][0],
    ]
)
def cadastro_assistencia_judiciaria():
    form = AssistenciaJudiciariaForm()
    if form.validate_on_submit():
        # Create Endereco
        endereco = Endereco(
            logradouro=form.logradouro.data,
            numero=form.numero.data,
            complemento=form.complemento.data,
            bairro=form.bairro.data,
            cep=form.cep.data,
            cidade=form.cidade.data,
            estado=form.estado.data,
        )
        db.session.add(endereco)
        db.session.flush()  # get endereco.id

        # Create AssistenciaJudiciaria
        assistencia = AssistenciaJudiciaria(
            nome=form.nome.data,
            regiao=form.regiao.data,
            telefone=form.telefone.data,
            email=form.email.data,
            status=1,
            endereco_id=endereco.id,
        )
        assistencia.setAreas_atendidas(form.areas_atendidas.data)
        db.session.add(assistencia)
        db.session.commit()
        flash("Assistência judiciária cadastrada com sucesso!", "success")
        return redirect(
            url_for("assistencia_judiciaria.listar_assistencias_judiciarias")
        )
    return render_template("cadastro_assistencia_judiciaria.html", form=form)


@assistencia_judiciaria_controller.route(
    "/buscar_assistencia_judiciaria", methods=["POST"]
)
@login_required()
def buscar_assistencia_judiciaria():
    assisistencia_judiciaria_service = AssistenciaJudiciariaService(db.session)

    termo = request.form.get("termo", "")
    page = request.args.get("page", 1, type=int)
    per_page = app.config["ATENDIDOS_POR_PAGINA"]

    def paginator(query: Select[Any]):
        return db.paginate(query, page=page, per_page=per_page)

    assistencias = assisistencia_judiciaria_service.get_by_name(termo, paginator)

    return render_template(
        "lista_assistencia_judiciaria.html",
        assistencias=assistencias,
        filtro_busca_assistencia_judiciaria=filtro_busca_assistencia_judiciaria,
    )
