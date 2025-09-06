import logging
from typing import Any

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    json,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import Select

from gestaolegal.common.constants import UserRole
from gestaolegal.database import get_db
from gestaolegal.forms.plantao.assistencia_juridica_form import (
    AssistenciaJudiciariaForm,
)
from gestaolegal.schemas.assistencia_judiciaria import AssistenciaJudiciariaSchema
from gestaolegal.schemas.assistencia_judiciaria_x_orientacao_juridica import (
    AssistenciaJudiciaria_xOrientacaoJuridicaSchema,
)
from gestaolegal.schemas.endereco import EnderecoSchema
from gestaolegal.services.assistencia_judiciaria_service import (
    AssistenciaJudiciariaService,
)
from gestaolegal.services.orientacao_juridica_service import OrientacaoJuridicaService
from gestaolegal.utils.decorators import login_required
from gestaolegal.utils.plantao_utils import (
    busca_assistencias_judiciarias_modal,
    filtro_busca_assistencia_judiciaria,
)

logger = logging.getLogger(__name__)

assistencia_judiciaria_controller = Blueprint(
    "assistencia_judiciaria",
    __name__,
    template_folder="../static/templates",
)


@assistencia_judiciaria_controller.route(
    "/encaminha_assistencia_judiciaria/<int:id_orientacao>", methods=["POST", "GET"]
)
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.PROFESSOR,
    ]
)
def encaminha_assistencia_judiciaria(id_orientacao: int):
    db = get_db()
    orientacao_juridica_service = OrientacaoJuridicaService()
    orientacao = orientacao_juridica_service.find_by_id(id_orientacao)

    if not orientacao:
        abort(404)

    if request.method == "GET":
        form = AssistenciaJudiciariaForm()
        return render_template(
            "assistencia_judiciaria/encaminhar_assistencia.html",
            form=form,
            id_orientacao=id_orientacao,
        )

    form = AssistenciaJudiciariaForm()

    if form.validate():
        endereco = EnderecoSchema(
            logradouro=form.logradouro.data,
            numero=form.numero.data,
            complemento=form.complemento.data,
            bairro=form.bairro.data,
            cep=form.cep.data,
            cidade=form.cidade.data,
            estado=form.estado.data,
        )
        db.session.add(endereco)
        db.session.flush()

        assistencia = AssistenciaJudiciariaSchema(
            nome=form.nome.data,
            regiao=form.regiao.data,
            telefone=form.telefone.data,
            email=form.email.data,
            status=1,
            endereco_id=endereco.id,
        )
        assistencia.setAreas_atendidas(form.areas_atendidas.data)
        db.session.add(assistencia)
        db.session.flush()

        aj_oj = AssistenciaJudiciaria_xOrientacaoJuridicaSchema()
        aj_oj.id_orientacaoJuridica = orientacao.id
        aj_oj.id_assistenciaJudiciaria = assistencia.id
        db.session.add(aj_oj)

        db.session.commit()
        flash("Assistência judiciária cadastrada e associada com sucesso!", "success")
        return redirect(
            url_for("assistencia_judiciaria.listar_assistencias_judiciarias")
        )

    return render_template(
        "assistencia_judiciaria/encaminhar_assistencia.html",
        form=form,
        id_orientacao=id_orientacao,
    )


@assistencia_judiciaria_controller.route(
    "/ajax_multiselect_associa_aj_oj/<int:orientacao_id>", methods=["POST", "GET"]
)
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.PROFESSOR,
    ]
)
def ajax_multiselect_associa_aj_oj(orientacao_id: int):
    db = get_db()

    orientacao_juridica_service = OrientacaoJuridicaService()
    orientacao = orientacao_juridica_service.find_by_id(orientacao_id)

    if not orientacao:
        abort(404)

    assistencias = (
        db.session.query(AssistenciaJudiciariaSchema)
        .filter(
            AssistenciaJudiciariaSchema.area_direito == orientacao.area_direito,
            AssistenciaJudiciariaSchema.status,
        )
        .all()
    )

    return json.dumps({"assistencias": [x.as_dict() for x in assistencias]})


# Excluir assistência judiciária
@assistencia_judiciaria_controller.route(
    "/excluir_assistencia_judiciaria/<int:id>", methods=["POST"]
)
@login_required(role=[UserRole.ADMINISTRADOR])
def excluir_assistencia_judiciaria(id: int):
    db = get_db()

    assistencia_judiciaria_service = AssistenciaJudiciariaService()

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
    db = get_db()

    assistencia_judiciaria_service = AssistenciaJudiciariaService()

    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["ATENDIDOS_POR_PAGINA"]
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
        "assistencia_judiciaria/buscar_assistencia.html", assistencias=assistencias
    )


# Perfil da assistência judiciária
@assistencia_judiciaria_controller.route("/perfil_assistencia_judiciaria/<_id>")
@login_required()
def perfil_assistencia_judiciaria(_id: int):
    db = get_db()

    aj = (
        db.session.query(AssistenciaJudiciariaSchema, EnderecoSchema)
        .select_from(AssistenciaJudiciariaSchema)
        .join(EnderecoSchema)
        .filter((AssistenciaJudiciariaSchema.id == _id))
        .first()
    )
    if aj is None:
        flash("Assistência judiciária não encontrada.", "warning")
        return redirect(
            url_for("assistencia_judiciaria.listar_assistencias_judiciarias")
        )
    return render_template("assistencia_judiciaria/visualizar_assistencia.html", aj=aj)


### Retorna lista de assistencia judiciaria
@assistencia_judiciaria_controller.route(
    "/todas-assistencias-judiciarias", methods=["GET", "POST"]
)
@login_required()
def pega_assistencias_judiciarias():
    get_db()

    assistencias_judiciarias = busca_assistencias_judiciarias_modal()
    return json.dumps(assistencias_judiciarias)


@assistencia_judiciaria_controller.route(
    "/assistencias_judiciarias/", methods=["POST", "GET"]
)
@login_required()
def listar_assistencias_judiciarias():
    db = get_db()

    assistencia_judiciaria_service = AssistenciaJudiciariaService()

    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["ATENDIDOS_POR_PAGINA"]

    def paginator(query: Select[Any]):
        return db.paginate(query, page=page, per_page=per_page)

    assistencias = assistencia_judiciaria_service.get_all(paginator)

    return render_template(
        "assistencia_judiciaria/listagem_assistencias.html",
        assistencias=assistencias,
        filtro_busca_assistencia_judiciaria=filtro_busca_assistencia_judiciaria,
    )


@assistencia_judiciaria_controller.route(
    "/editar_assistencia_judiciaria/<int:id_assistencia_judiciaria>",
    methods=["POST", "GET"],
)
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_PROJETO,
        UserRole.COLAB_EXTERNO,
    ]
)
def editar_assistencia_judiciaria(id_assistencia_judiciaria: int):
    db = get_db()

    assistencia_judiciaria_service = AssistenciaJudiciariaService()
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

    return render_template("assistencia_judiciaria/editar_assistencia.html", form=form)


@assistencia_judiciaria_controller.route(
    "/cadastro_assistencia_judiciaria", methods=["GET", "POST"]
)
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_PROJETO,
        UserRole.COLAB_EXTERNO,
    ]
)
def cadastro_assistencia_judiciaria():
    db = get_db()

    form = AssistenciaJudiciariaForm()
    if form.validate_on_submit():
        # Create Endereco
        endereco = EnderecoSchema(
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
        assistencia = AssistenciaJudiciariaSchema(
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
    return render_template(
        "assistencia_judiciaria/cadastrar_assistencia.html", form=form
    )


@assistencia_judiciaria_controller.route(
    "/buscar_assistencia_judiciaria", methods=["POST"]
)
@login_required()
def buscar_assistencia_judiciaria():
    db = get_db()

    assisistencia_judiciaria_service = AssistenciaJudiciariaService()

    termo = request.form.get("termo", "")
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["ATENDIDOS_POR_PAGINA"]

    def paginator(query: Select[Any]):
        return db.paginate(query, page=page, per_page=per_page)

    assistencias = assisistencia_judiciaria_service.get_by_name(termo, paginator)

    return render_template(
        "assistencia_judiciaria/listagem_assistencias.html",
        assistencias=assistencias,
        filtro_busca_assistencia_judiciaria=filtro_busca_assistencia_judiciaria,
    )
