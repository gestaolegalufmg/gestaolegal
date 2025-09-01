import os
from datetime import datetime
from operator import and_

import pytz
from flask import (
    Blueprint,
    abort,
    current_app,
    json,
    render_template,
    request,
)
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import RequestEntityTooLarge

from gestaolegal.common.constants import UserRole, acoes, situacao_deferimento
from gestaolegal.forms.relatorio import (
    ArquivoCasoForm,
    CasoForm,
    EditarArquivoDeEventoForm,
    EventoForm,
    JustificativaIndeferimento,
    LembreteForm,
    NovoCasoForm,
    ProcessoForm,
    RoteiroForm,
)
from gestaolegal.models.notificacao import Notificacao
from gestaolegal.schemas.arquivo_caso import ArquivoCasoSchema
from gestaolegal.schemas.arquivos_evento import ArquivosEventoSchema
from gestaolegal.schemas.assistido import AssistidoSchema
from gestaolegal.schemas.atendido import AtendidoSchema
from gestaolegal.schemas.caso import CasoSchema
from gestaolegal.schemas.evento import EventoSchema
from gestaolegal.schemas.historico import HistoricoSchema
from gestaolegal.schemas.lembrete import LembreteSchema
from gestaolegal.schemas.notificacao import NotificacaoSchema
from gestaolegal.schemas.processo import ProcessoSchema
from gestaolegal.schemas.roteiro import RoteiroSchema
from gestaolegal.schemas.usuario import UsuarioSchema
from gestaolegal.utils.casos_utils import *
from gestaolegal.utils.decorators import login_required
from gestaolegal.utils.models import queryFiltradaStatus
from gestaolegal.utils.plantao_utils import *

casos_controller = Blueprint("casos", __name__, template_folder="../templates/casos")


@casos_controller.route("/")
@login_required()
def index():
    # ATUALIZAR TODOS OS NÚMEROS DO ÚLTIMO PROCESSO DE TODOS OS CASOS
    def atualizar_ultimo_processo_dos_casos():
        db = get_db()

        lista_de_casos = db.session.query(CasoSchema).all()

        for caso in lista_de_casos:
            processos = (
                db.session.query(ProcessoSchema)
                .filter_by(id_caso=caso.id, status=True)
                .all()
            )
            if processos:
                ultimo_processo = processos[-1:]
                caso.numero_ultimo_processo = ultimo_processo[0].numero

    page = request.args.get("page", 1, type=int)
    opcao_filtro = request.args.get(
        "opcao_filtro", opcoes_filtro_casos["TODOS"][0], type=str
    )

    db = get_db()
    casos = query_opcoes_filtro_casos(opcao_filtro)
    casos = db.paginate(
        casos,
        page=page,
        per_page=current_app.config["CASOS_POR_PAGINA"],
        error_out=False,
    )

    return render_template(
        "lista_casos.html",
        opcoes_filtro_casos=opcoes_filtro_casos,
        **params_busca_casos(casos, ROTA_PAGINACAO_CASOS, opcao_filtro),
    )


@casos_controller.route("/ajax_filtro_casos")
@login_required()
def ajax_filtro_casos():
    page = request.args.get("page", 1, type=int)
    opcao_filtro = request.args.get(
        "opcao_filtro", opcoes_filtro_casos["TODOS"][0], type=str
    )

    db = get_db()
    casos = query_opcoes_filtro_casos(opcao_filtro)
    casos = db.paginate(
        casos,
        page=page,
        per_page=current_app.config["CASOS_POR_PAGINA"],
        error_out=False,
    )

    return render_template(
        "busca_casos.html",
        **params_busca_casos(casos, ROTA_PAGINACAO_CASOS, opcao_filtro),
    )


@casos_controller.route("/novo_caso", methods=["GET", "POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.PROFESSOR,
    ]
)
def novo_caso():
    db = get_db()

    _form = NovoCasoForm()
    if _form.validate_on_submit():
        _caso = CasoSchema(
            area_direito=_form.area_direito.data,
            id_usuario_responsavel=current_user.id,
            data_criacao=datetime.now(tz=pytz.timezone("America/Sao_Paulo")),
            id_criado_por=current_user.id,
            data_modificacao=datetime.now(tz=pytz.timezone("America/Sao_Paulo")),
            id_modificado_por=current_user.id,
            descricao=_form.descricao.data,
            id_orientador=_form.orientador.data or None,
            id_estagiario=_form.estagiario.data or None,
            id_colaborador=_form.colaborador.data or None,
        )
        _caso.setSubAreasSchema(
            _form.area_direito.data, _form.sub_area.data, _form.sub_areaAdmin.data
        )

        if len(_caso.descricao) > 2000:
            flash("A descrição do caso não pode ter mais de 2000 caracteres", "warning")
            return redirect(url_for("casos.novo_caso"))

        for id_cliente in _form.clientes.data.split(sep=","):
            cliente = db.session.get(AtendidoSchema, int(id_cliente))
            _caso.clientes.append(cliente)

        db.session.add(_caso)
        db.session.commit()

        try:
            arquivo = request.files.get("arquivo")
        except RequestEntityTooLarge:
            flash("Tamanho de arquivo muito longo.")
            return render_template("caso.html", form=_form)

        if arquivo.filename:
            _, extensao_do_arquivo = os.path.splitext(arquivo.filename)
            if extensao_do_arquivo != ".pdf" and arquivo:
                flash("Extensão de arquivo não suportado.", "warning")
                return render_template("caso.html", form=_form)
            nome_arquivo = f"{arquivo.filename}"
            arquivo.save(
                os.path.join(current_app.root_path, "static", "casos", nome_arquivo)
            )
            caso_arquivo = ArquivoCasoSchema(
                link_arquivo=arquivo.filename if arquivo else None, id_caso=_caso.id
            )
            db.session.add(caso_arquivo)
            db.session.commit()

        _notificacao = NotificacaoSchema(
            acao=acoes["CAD_NOVO_CASO"].format(_caso.id),
            data=datetime.now(),
            id_executor_acao=current_user.id,
            id_usu_notificar=_caso.id_usuario_responsavel,
        )
        db.session.add(_notificacao)
        db.session.commit()

        flash("Caso criado com sucesso!", "success")

        return redirect(url_for("casos.visualizar_caso", id=_caso.id))

    return render_template("caso.html", form=_form, title="Novo Caso", caso=None)


@casos_controller.route(
    "/excluir_arquivo/<id_arquivo>/<id_caso>", methods=["GET", "POST"]
)
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ORIENTADOR,
        UserRole.PROFESSOR,
    ]
)
def excluir_arquivo_caso(id_arquivo, id_caso):
    db = get_db()

    arquivo = db.session.get(ArquivoCasoSchema, id_arquivo)
    if not arquivo:
        abort(404)

    db.session.delete(arquivo)
    db.session.commit()

    return redirect(url_for("casos.editar_caso", id_caso=id_caso))


# Visualizar caso
@casos_controller.route("/visualizar/<int:id>", methods=["GET"])
@login_required()
def visualizar_caso(id):
    db = get_db()

    _caso = db.session.query(CasoSchema).filter_by(status=True, id=id).first()

    if _caso == None:
        flash("Caso inexistente!", "warning")
        return redirect(url_for("casos.index"))

    arquivos = (
        db.session.query(ArquivoCasoSchema)
        .filter(ArquivoCasoSchema.id_caso == id)
        .all()
    )
    processos = (
        db.session.query(ProcessoSchema).filter_by(id_caso=id, status=True).all()
    )
    _lembrete = (
        db.session.query(LembreteSchema)
        .filter_by(status=True, id_caso=id)
        .order_by(LembreteSchema.data_criacao.desc())
        .first()
    )
    evento = (
        db.session.query(EventoSchema)
        .filter_by(status=True, id_caso=id)
        .order_by(EventoSchema.data_criacao.desc())
        .first()
    )
    return render_template(
        "visualizar_caso.html",
        caso=_caso,
        processos=processos,
        lembrete=_lembrete,
        arquivos=arquivos,
        evento=evento,
    )


@casos_controller.route("/deferir_caso/<int:id_caso>", methods=["POST", "GET"])
@login_required(
    role=[
        UserRole.PROFESSOR,
        UserRole.ADMINISTRADOR,
    ]
)
def deferir_caso(id_caso):
    db = get_db()

    entidade_caso = db.session.query(CasoSchema).filter_by(id=id_caso).first()
    if not entidade_caso:
        flash("Caso não encontrado.", "warning")
        return redirect(url_for("casos.index"))

    entidade_caso.situacao_deferimento = situacao_deferimento["ATIVO"][0]
    db.session.add(entidade_caso)
    db.session.commit()
    flash("Caso deferido!", "success")
    return redirect(url_for("casos.index"))


@casos_controller.route("/indeferir/<id_caso>", methods=["POST", "GET"])
@login_required(role=[UserRole.ADMINISTRADOR, UserRole.PROFESSOR])
def indeferir_caso(id_caso):
    db = get_db()

    _form = JustificativaIndeferimento()
    if request.method == "POST":
        _id = id_caso
        _justificativa = request.form["justificativa"]
        if not _justificativa:
            flash(
                "É necessário fornecer uma justificativa para o indeferimento!",
                "danger",
            )
            return redirect(url_for("visualizar_caso", id=_id))

        _caso = db.session.query(CasoSchema).filter_by(status=True, id=_id).first()
        _caso.situacao_deferimento = situacao_deferimento["INDEFERIDO"][0]
        _caso.justif_indeferimento = _justificativa

        db.session.add(_caso)
        db.session.commit()
        flash("Indeferimento realizado.", "success")
        return redirect(url_for("casos.index"))
    return render_template("justificativa.html", form=_form)


@casos_controller.route("/editar_caso/<id_caso>", methods=["GET", "POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.ORIENTADOR,
        UserRole.COLAB_EXTERNO,
        UserRole.ESTAGIARIO_DIREITO,
    ]
)
def editar_caso(id_caso):
    db = get_db()

    entidade_caso = db.session.query(CasoSchema).filter_by(id=id_caso).first()
    usuario = db.session.query(UsuarioSchema).filter_by(id=current_user.id).first()

    if (
        usuario.urole == UserRole.COLAB_EXTERNO
        and entidade_caso.id_colaborador != usuario.id
    ):
        flash("Você não tem permissão para editar esse caso.", "warning")
        return redirect(url_for("casos.index"))

    if (
        usuario.urole == UserRole.ESTAGIARIO_DIREITO
        and entidade_caso.id_estagiario != usuario.id
    ):
        flash("Você não tem permissão para editar esse caso.", "warning")
        return redirect(url_for("casos.index"))

    if not entidade_caso:
        flash("Não existe um caso com esse ID.", "warning")
        return redirect(url_for("casos.index"))

    arquivos = (
        db.session.query(ArquivoCasoSchema)
        .filter(ArquivoCasoSchema.id_caso == id_caso)
        .all()
    )
    form = CasoForm()

    if request.method == "POST":
        if not form.validate():
            return render_template("caso.html", form=form, caso=entidade_caso)
        else:
            if form.orientador.data == "":
                entidade_caso.id_orientador = None
            else:
                entidade_caso.id_orientador = int(form.orientador.data)

            if form.estagiario.data == "":
                entidade_caso.id_estagiario = None
            else:
                entidade_caso.id_estagiario = int(form.estagiario.data)

            if form.colaborador.data == "":
                entidade_caso.id_colaborador = None
            else:
                entidade_caso.id_colaborador = int(form.colaborador.data)

            entidade_caso.area_direito = form.area_direito.data
            entidade_caso.descricao = form.descricao.data
            entidade_caso.data_modificacao = datetime.now(
                tz=pytz.timezone("America/Sao_Paulo")
            )
            if entidade_caso.situacao_deferimento == situacao_deferimento["ATIVO"][0]:
                entidade_caso.situacao_deferimento = (
                    form.situacao_deferimento_ativo.data
                )
            if (
                entidade_caso.situacao_deferimento
                == situacao_deferimento["INDEFERIDO"][0]
            ):
                entidade_caso.situacao_deferimento = (
                    form.situacao_deferimento_indeferido.data
                )

            notificacoes = []
            if isinstance(entidade_caso.id_orientador, int):
                _notificacao = Notificacao(
                    acao=acoes["CAD_NOVO_CASO"].format(entidade_caso.id),
                    data=datetime.now(),
                    id_executor_acao=current_user.id,
                    id_usu_notificar=int(entidade_caso.id_orientador),
                )
                notificacoes.append(_notificacao)

            if isinstance(entidade_caso.id_estagiario, int):
                _notificacao = Notificacao(
                    acao=acoes["CAD_NOVO_CASO"].format(entidade_caso.id),
                    data=datetime.now(),
                    id_executor_acao=current_user.id,
                    id_usu_notificar=int(entidade_caso.id_estagiario),
                )
                notificacoes.append(_notificacao)

            if isinstance(entidade_caso.id_colaborador, int):
                _notificacao = Notificacao(
                    acao=acoes["CAD_NOVO_CASO"].format(entidade_caso.id),
                    data=datetime.now(),
                    id_executor_acao=current_user.id,
                    id_usu_notificar=int(entidade_caso.id_colaborador),
                )
                notificacoes.append(_notificacao)

            if notificacoes:
                db.session.bulk_save_objects(notificacoes)
                db.session.commit()

            try:
                arquivo = request.files.get("arquivo")
            except RequestEntityTooLarge:
                flash("Tamanho de arquivo muito longo.")
                return redirect(url_for("casos.editar_caso", id_caso=id_caso))
            if arquivo:
                nome_do_arquivo, extensao_do_arquivo = os.path.splitext(
                    arquivo.filename
                )
                if extensao_do_arquivo != ".pdf" and arquivo:
                    flash("Extensão de arquivo não suportado.", "warning")
                    return redirect(url_for("casos.editar_caso", id_caso=id_caso))
                arquivo_caso = ArquivoCasoSchema(
                    link_arquivo=arquivo.filename, id_caso=id_caso
                )
                db.session.add(arquivo_caso)
                nome_arquivo = f"{arquivo.filename}"
                arquivo.save(
                    os.path.join(current_app.root_path, "static", "casos", nome_arquivo)
                )

            db.session.commit()
            cadastrar_historico(
                current_user.id, id_caso
            )  # Cadastra um novo histórico de edição
            flash("Caso editado com sucesso!", "success")
            return redirect(url_for("casos.index"))

    if request.method == "GET":
        form.orientador.data = entidade_caso.id_orientador
        form.estagiario.data = entidade_caso.id_estagiario
        form.colaborador.data = entidade_caso.id_colaborador
        form.area_direito.data = entidade_caso.area_direito
        form.descricao.data = entidade_caso.descricao
        if entidade_caso.situacao_deferimento == situacao_deferimento["ATIVO"][0]:
            form.situacao_deferimento_ativo.data = entidade_caso.situacao_deferimento
        if entidade_caso.situacao_deferimento == situacao_deferimento["INDEFERIDO"][0]:
            form.situacao_deferimento_indeferido.data = (
                entidade_caso.situacao_deferimento
            )

        return render_template(
            "caso.html", form=form, caso=entidade_caso, arquivos=arquivos
        )


@casos_controller.route(
    "/excluir_assistido_caso/<id_caso>/<id_assistido>", methods=["POST", "GET"]
)
@login_required()
def excluir_assistido_caso(id_caso, id_assistido):
    db = get_db()

    entidade_caso = db.session.query(CasoSchema).filter_by(id=id_caso).first()
    cliente = db.session.query(AtendidoSchema).filter_by(id=id_assistido).first()
    entidade_caso.clientes.remove(cliente)
    db.session.commit()
    return redirect(url_for("casos.index"))


@casos_controller.route("/adicionar_assistido_caso/<id_caso>", methods=["POST", "GET"])
@login_required()
def adicionar_assistido_caso(id_caso):
    db = get_db()

    entidade_caso = db.session.query(CasoSchema).filter_by(id=id_caso).first()
    if request.method == "POST":
        clientes = request.form["adicao_assistido" + id_caso]
        if clientes != "":
            for id_cliente in clientes.split(sep=","):
                cliente = db.session.query(AtendidoSchema).get(int(id_cliente))
                entidade_caso.clientes.append(cliente)
        db.session.commit()
    return redirect(url_for("casos.index"))


@casos_controller.route("/api/buscar_assistido", methods=["GET"])
@login_required()
def api_casos_buscar_assistido():
    termo = request.args.get("q", type=str)
    db = get_db()

    # Se nada for digitado, retornar os 5 assistidos mais recentes
    if termo:
        _assistidos = (
            db.session.query(AtendidoSchema)
            .join(AssistidoSchema)
            .filter(
                or_(
                    AtendidoSchema.cpf.like(termo + "%"),
                    AtendidoSchema.cnpj.like(termo + "%"),
                    AtendidoSchema.nome.like(termo + "%"),
                )
            )
            .filter(AtendidoSchema.status.is_(True))
            .order_by(AtendidoSchema.nome)
            .all()
        )
    else:
        _assistidos = (
            db.session.query(AtendidoSchema)
            .join(AssistidoSchema)
            .filter(AtendidoSchema.status.is_(True))
            .order_by(AtendidoSchema.nome)
            .limit(5)
            .all()
        )

    # Dados formatados para o select2
    assistidos_clean = [
        {
            "id": assistido.id,
            "text": assistido.nome,
            "cpf": assistido.cpf,
            "cnpj": assistido.cnpj,
        }
        for assistido in _assistidos
    ]
    response = current_app.response_class(
        response=json.dumps({"results": assistidos_clean}),
        status=200,
        mimetype="application/json",
    )
    return response


@casos_controller.route("/api/buscar_usuario", methods=["GET"])
@login_required()
def api_casos_buscar_usuario():
    db = get_db()

    termo = request.args.get("q", type=str)
    if termo:
        _usuarios = (
            db.session.query(UsuarioSchema)
            .filter(UsuarioSchema.nome.like(termo + "%"))
            .filter(UsuarioSchema.status.is_(True))
            .order_by(UsuarioSchema.nome)
            .all()
        )
    else:
        _usuarios = (
            db.session.query(UsuarioSchema)
            .filter(UsuarioSchema.status.is_(True))
            .order_by(UsuarioSchema.nome)
            .limit(5)
            .all()
        )

    # Dados formatados para o select2
    usuarios_clean = [{"id": usuario.id, "text": usuario.nome} for usuario in _usuarios]
    response = current_app.response_class(
        response=json.dumps({"results": usuarios_clean}),
        status=200,
        mimetype="application/json",
    )
    return response


@casos_controller.route("/api/buscar_roteiro", methods=["GET"])
@login_required()
def api_casos_buscar_roteiro():
    db = get_db()

    termo = request.args.get("termo", type=str)
    if termo:
        _roteiro = db.session.query(RoteiroSchema).filter_by(area_direito=termo).first()
        if _roteiro:
            roteiro_clean = {"link": _roteiro.link}
        else:
            roteiro_clean = {"link": ""}
    else:
        roteiro_clean = {"link": ""}

    response = current_app.response_class(
        response=json.dumps(roteiro_clean), status=200, mimetype="application/json"
    )
    return response


@casos_controller.route("/api/buscar_casos", methods=["GET"])
@login_required()
def api_casos_buscar_casos():
    db = get_db()

    id_caso = request.args.get("q", type=str)
    if id_caso:
        _casos = (
            db.session.query(CasoSchema)
            .filter(CasoSchema.id.like(id_caso + "%"))
            .filter(CasoSchema.status.is_(True))
            .order_by(CasoSchema.id)
            .all()
        )
    else:
        _casos = (
            db.session.query(CasoSchema)
            .filter(CasoSchema.status.is_(True))
            .order_by(CasoSchema.id)
            .limit(5)
            .all()
        )

    if not _casos:
        response = current_app.response_class(
            response=json.dumps(
                {"id": 1, "text": "Não há casos cadastrados no sistema"}
            ),
            status=200,
            mimetype="application/json",
        )
        return response

        # Dados formatados para o select2
    casos_clean = [
        {"id": _casos[i].id, "text": "Caso " + str(_casos[i].id)}
        for i in range(0, len(_casos))
    ]

    response = current_app.response_class(
        response=json.dumps({"results": casos_clean}),
        status=200,
        mimetype="application/json",
    )
    return response


@casos_controller.route("/api/buscar_orientador", methods=["GET"])
@login_required()
def api_casos_buscar_orientador():
    db = get_db()

    termo = request.args.get("q", type=str)
    if termo:
        _usuarios = (
            db.session.query(UsuarioSchema)
            .filter(UsuarioSchema.nome.like(termo + "%"))
            .filter(UsuarioSchema.status.is_(True))
            .filter_by(urole="orient")
            .order_by(UsuarioSchema.nome)
            .all()
        )
    else:
        _usuarios = (
            db.session.query(UsuarioSchema)
            .filter(UsuarioSchema.status.is_(True))
            .filter_by(urole="orient")
            .order_by(UsuarioSchema.nome)
            .limit(5)
            .all()
        )

    # Dados formatados para o select2
    usuarios_clean = [{"id": usuario.id, "text": usuario.nome} for usuario in _usuarios]
    response = current_app.response_class(
        response=json.dumps({"results": usuarios_clean}),
        status=200,
        mimetype="application/json",
    )
    return response


@casos_controller.route("/api/buscar_estagiario", methods=["GET"])
@login_required()
def api_casos_buscar_estagiario():
    db = get_db()

    termo = request.args.get("q", type=str)
    if termo:
        _usuarios = (
            db.session.query(UsuarioSchema)
            .filter(UsuarioSchema.nome.like(termo + "%"))
            .filter(UsuarioSchema.status.is_(True))
            .filter_by(urole="estag_direito")
            .order_by(UsuarioSchema.nome)
            .all()
        )
    else:
        _usuarios = (
            db.session.query(UsuarioSchema)
            .filter(UsuarioSchema.status.is_(True))
            .filter_by(urole="estag_direito")
            .order_by(UsuarioSchema.nome)
            .limit(5)
            .all()
        )

    # Dados formatados para o select2
    usuarios_clean = [{"id": usuario.id, "text": usuario.nome} for usuario in _usuarios]
    response = current_app.response_class(
        response=json.dumps({"results": usuarios_clean}),
        status=200,
        mimetype="application/json",
    )
    return response


@casos_controller.route("/api/buscar_colaborador", methods=["GET"])
@login_required()
def api_casos_buscar_colaborador():
    db = get_db()

    termo = request.args.get("q", type=str)
    if termo:
        _usuarios = (
            db.session.query(UsuarioSchema)
            .filter(UsuarioSchema.nome.like(termo + "%"))
            .filter(UsuarioSchema.status.is_(True))
            .filter_by(urole="colab_ext")
            .order_by(UsuarioSchema.nome)
            .all()
        )
    else:
        _usuarios = (
            db.session.query(UsuarioSchema)
            .filter(UsuarioSchema.status.is_(True))
            .filter_by(urole="colab_ext")
            .order_by(UsuarioSchema.nome)
            .limit(5)
            .all()
        )

    # Dados formatados para o select2
    usuarios_clean = [{"id": usuario.id, "text": usuario.nome} for usuario in _usuarios]
    response = current_app.response_class(
        response=json.dumps({"results": usuarios_clean}),
        status=200,
        mimetype="application/json",
    )
    return response


# Cadastrar/editar links de roteiro
@casos_controller.route("/links_roteiro", methods=["GET", "POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_EXTERNO,
    ]
)
def editar_roteiro():
    db = get_db()

    _form = RoteiroForm()
    if _form.validate_on_submit():
        _roteiro = (
            db.session.query(RoteiroSchema)
            .filter_by(area_direito=_form.area_direito.data)
            .first()
            or RoteiroSchema()
        )

        _roteiro.area_direito = _form.area_direito.data
        _roteiro.link = _form.link.data

        db.session.add(_roteiro)
        db.session.commit()
        flash("Alteração realizada com sucesso!", "success")
        return redirect(url_for("casos.editar_roteiro"))

    _roteiros = db.session.query(RoteiroSchema).all()
    return render_template(
        "links_roteiro.html",
        form=_form,
        roteiros=_roteiros,
        assistencia_jud_areas_atendidas=assistencia_jud_areas_atendidas,
    )


# Rota para página de eventos
@casos_controller.route("/eventos/<id_caso>")
@login_required()
def eventos(id_caso):
    db = get_db()

    page = request.args.get("page", 1, type=int)
    opcao_filtro = request.args.get(
        "opcao_filtro", opcoes_filtro_eventos["TODOS"][0], type=str
    )

    _eventos = query_opcoes_filtro_eventos(id_caso, opcao_filtro)
    _eventos = db.paginate(
        _eventos,
        page=page,
        per_page=current_app.config["EVENTOS_POR_PAGINA"],
        error_out=False,
    )

    if not _eventos.items:
        flash("Não há eventos cadastrados para este caso.", "warning")
        return redirect(url_for("casos.visualizar_caso", id=id_caso))

    return render_template(
        "eventos.html",
        opcoes_filtro_eventos=opcoes_filtro_eventos,
        **params_busca_eventos(_eventos, ROTA_PAGINACAO_EVENTOS, id_caso, opcao_filtro),
    )


@casos_controller.route("/ajax_filtro_eventos/<id_caso>")
@login_required()
def ajax_filtro_eventos(id_caso):
    page = request.args.get("page", 1, type=int)
    opcao_filtro = request.args.get(
        "opcao_filtro", opcoes_filtro_meus_casos["ATIVO"][0], type=str
    )

    db = get_db()
    _eventos = query_opcoes_filtro_eventos(id_caso, opcao_filtro)
    _eventos = db.paginate(
        _eventos,
        page=page,
        per_page=current_app.config["EVENTOS_POR_PAGINA"],
        error_out=False,
    )

    return render_template(
        "busca_eventos.html",
        **params_busca_eventos(_eventos, ROTA_PAGINACAO_EVENTOS, id_caso, opcao_filtro),
    )


# Rota para página de lembretes
@casos_controller.route("/lembretes/<id_caso>")
@login_required()
def lembretes(id_caso):
    db = get_db()

    num_lembrete = request.args.get("num_lembrete", None)

    _lembretes = (
        db.session.query(LembreteSchema)
        .filter_by(status=True, id_caso=id_caso)
        .order_by(LembreteSchema.data_criacao.desc())
        .all()
    )

    _lembrete = (
        db.session.query(LembreteSchema)
        .filter(
            LembreteSchema.id_caso == id_caso,
            LembreteSchema.num_lembrete == num_lembrete,
        )
        .first()
    )

    caso = db.session.query(CasoSchema).get(id_caso)
    if (caso == None) or (caso.status == False):
        flash("Caso inexistente!", "warning")
        return redirect(url_for("casos.index", id_caso=id_caso))

    if (num_lembrete is not None) and (_lembrete.status == False):
        flash("Lembrete inexistente!", "warning")

    return render_template("lembretes.html", caso_id=id_caso, lembretes=_lembretes)


@casos_controller.route("/cadastrar_lembrete/<int:id_do_caso>", methods=["GET", "POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ORIENTADOR,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.COLAB_EXTERNO,
    ]
)
def cadastrar_lembrete(id_do_caso):
    db = get_db()

    _form = LembreteForm()

    if _form.validate_on_submit():
        _lembrete = LembreteSchema(
            id_caso=id_do_caso,
            num_lembrete=get_num_lembretes_atual(id_do_caso),
            id_usuario=int(_form.usuarios.data),
            data_lembrete=_form.data.data,
            descricao=_form.lembrete.data,
        )

        if len(_lembrete.descricao) > 2000:
            flash(
                "A descrição do lembrete não pode ter mais de 2000 caracteres",
                "warning",
            )
            return redirect(url_for("casos.cadastrar_lembrete", id_do_caso=id_do_caso))

        _lembrete.id_do_criador = current_user.id
        _lembrete.data_criacao = datetime.now()

        db.session.add(_lembrete)
        db.session.commit()
        flash("Lembrete enviado com sucesso!", "success")

        _notificacao = Notificacao(
            acao=acoes["LEMBRETE"].format(_lembrete.num_lembrete, id_do_caso),
            data=datetime.now(),
            id_executor_acao=current_user.id,
            id_usu_notificar=_lembrete.id_usuario,
        )
        db.session.add(_notificacao)
        db.session.commit()

        return redirect(url_for("casos.visualizar_caso", id=id_do_caso))

    return render_template("novo_lembrete.html", form=_form)


@casos_controller.route("/editar_lembrete/<id_lembrete>", methods=["GET", "POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ORIENTADOR,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.COLAB_EXTERNO,
    ]
)
def editar_lembrete(id_lembrete):
    db = get_db()

    def setValoresLembrete(_form: LembreteForm, entidade_lembrete: LembreteSchema):
        _form.usuarios.data = entidade_lembrete.id_usuario
        _form.data.data = entidade_lembrete.data_lembrete
        _form.lembrete.data = entidade_lembrete.descricao

    def setDadosLembrete(form: LembreteForm, entidade_lembrete: LembreteSchema):
        entidade_lembrete.id_usuario = int(_form.usuarios.data)
        entidade_lembrete.data_lembrete = _form.data.data
        entidade_lembrete.descricao = _form.lembrete.data

    ############################## IMPLEMENTAÇÃO DA ROTA ###########################################################

    entidade_lembrete = (
        db.session.query(LembreteSchema).filter_by(id=id_lembrete, status=True).first()
    )

    if not entidade_lembrete:
        flash("Não existe um lembrete com esse ID.", "warning")
        return redirect(url_for("casos.index"))

    _form = LembreteForm()

    if request.method == "POST":
        if not _form.validate():
            return render_template("editar_lembrete.html", form=_form)

        setDadosLembrete(_form, entidade_lembrete)
        db.session.commit()
        flash("Lembrete editado com sucesso!", "success")
        return redirect(url_for("casos.lembretes", id_caso=entidade_lembrete.id_caso))

    setValoresLembrete(_form, entidade_lembrete)
    entidade_usuario_notificado = (
        db.session.query(UsuarioSchema)
        .filter_by(id=entidade_lembrete.id_usuario, status=True)
        .first()
    )
    return render_template(
        "editar_lembrete.html", form=_form, usuario=entidade_usuario_notificado.nome
    )


@casos_controller.route("/excluir_lembrete/<id_lembrete>", methods=["GET", "POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ORIENTADOR,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.COLAB_EXTERNO,
    ]
)
def excluir_lembrete(id_lembrete):
    db = get_db()

    entidade_usuario = (
        db.session.query(UsuarioSchema)
        .filter_by(id=current_user.id, status=True)
        .first()
    )
    entidade_lembrete = db.session.query(LembreteSchema).get(id_lembrete)
    caso = entidade_lembrete.id_caso
    if entidade_usuario.urole != "admin":
        if entidade_lembrete.id_do_criador == entidade_usuario.id:
            entidade_lembrete.status = False
            db.session.commit()
            flash("Lembrete excluído com sucesso!", "success")
            return redirect((url_for("casos.lembretes", id_caso=caso)))
        else:
            flash("Você não possui autorização!", "warning")
            return redirect(
                (url_for("casos.lembretes", id_caso=entidade_lembrete.id_caso))
            )
    else:
        entidade_lembrete.status = False
        db.session.commit()
        flash("Lembrete excluído com sucesso!", "success")
        return redirect((url_for("casos.lembretes", id_caso=caso)))


# Função de cadastrar um novo histórico
def cadastrar_historico(id_usuario, id_caso):
    db = get_db()

    historico = HistoricoSchema()
    usuario = (
        db.session.query(UsuarioSchema).filter((UsuarioSchema.id == id_usuario)).first()
    )
    caso = db.session.query(CasoSchema).filter((CasoSchema.id == id_caso)).first()

    historico.id_usuario = usuario.id
    historico.id_caso = caso.id
    historico.data = datetime.now()

    try:
        db.session.add(historico)
        db.session.commit()
    except SQLAlchemyError as e:
        erro = str(e.__dict__["orig"])
        flash(erro, "danger")
        return False

    return True


# Rota para visualização de um novo histórico
@casos_controller.route("/historico/<id_caso>")
def historico(id_caso):
    db = get_db()

    page = request.args.get("page", 1, type=int)
    historicos = (
        db.session.query(HistoricoSchema, CasoSchema, UsuarioSchema)
        .select_from(HistoricoSchema)
        .join(CasoSchema)
        .filter(
            (CasoSchema.id == id_caso)
            & (UsuarioSchema.id == HistoricoSchema.id_usuario)
        )
        .order_by(HistoricoSchema.data.desc())
        .paginate(
            page=page,
            per_page=current_app.config["HISTORICOS_POR_PAGINA"],
            error_out=False,
        )
    )
    return render_template("historico.html", historicos=historicos, caso_id=id_caso)


# Meus casos
@casos_controller.route("/meus_casos")
@login_required()
def meus_casos():
    page = request.args.get("page", 1, type=int)
    opcao_filtro = request.args.get(
        "opcao_filtro", opcoes_filtro_meus_casos["ATIVO"][0], type=str
    )

    db = get_db()
    casos = query_opcoes_filtro_meus_casos(current_user.id, opcao_filtro)
    casos = db.paginate(
        casos,
        page=page,
        per_page=current_app.config["CASOS_POR_PAGINA"],
        error_out=False,
    )

    titulo_total = titulo_total_meus_casos(casos.total)

    return render_template(
        "listar_meus_casos.html",
        opcoes_filtro_meus_casos=opcoes_filtro_meus_casos,
        titulo_total=titulo_total,
        **params_busca_casos(casos, ROTA_PAGINACAO_MEUS_CASOS, opcao_filtro),
    )


@casos_controller.route("/ajax_filtro_meus_casos")
@login_required()
def ajax_filtro_meus_casos():
    page = request.args.get("page", 1, type=int)
    opcao_filtro = request.args.get(
        "opcao_filtro", opcoes_filtro_meus_casos["ATIVO"][0], type=str
    )

    db = get_db()
    casos = query_opcoes_filtro_meus_casos(current_user.id, opcao_filtro)
    casos = db.paginate(
        casos,
        page=page,
        per_page=current_app.config["CASOS_POR_PAGINA"],
        error_out=False,
    )

    titulo_total = titulo_total_meus_casos(casos.total)

    return render_template(
        "busca_casos.html",
        titulo_total=titulo_total,
        **params_busca_casos(casos, ROTA_PAGINACAO_MEUS_CASOS, opcao_filtro),
    )


@casos_controller.route("/novo_evento/<int:id_caso>", methods=["GET", "POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ORIENTADOR,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.COLAB_EXTERNO,
    ]
)
def novo_evento(id_caso):
    db = get_db()

    _form = EventoForm()
    if _form.validate_on_submit():
        if _form.usuario.data:
            _evento = EventoSchema(
                id_caso=id_caso,
                num_evento=get_num_eventos_atual(id_caso),
                tipo=_form.tipo.data,
                descricao=_form.descricao.data,
                data_evento=_form.data_evento.data,
                data_criacao=datetime.now(),
                id_criado_por=current_user.id,
                id_usuario_responsavel=_form.usuario.data,
            )
        else:
            _evento = EventoSchema(
                id_caso=id_caso,
                num_evento=get_num_eventos_atual(id_caso),
                tipo=_form.tipo.data,
                descricao=_form.descricao.data,
                data_evento=_form.data_evento.data,
                data_criacao=datetime.now(),
                id_criado_por=current_user.id,
                id_usuario_responsavel=None,
            )

        db.session.add(_evento)
        db.session.commit()

        if _form.usuario.data:
            _notificacao = Notificacao(
                acao=acoes["EVENTO"].format(_evento.num_evento, id_caso),
                data=datetime.now(),
                id_executor_acao=current_user.id,
                id_usu_notificar=_form.usuario.data,
            )
            db.session.add(_notificacao)
            db.session.commit()

        if request.files.get("arquivos"):
            arquivos = request.files.getlist("arquivos")

            for arq in arquivos:
                if arq.filename:
                    try:
                        _, extensao_do_arq = os.path.splitext(arq.filename)
                        if extensao_do_arq != ".pdf" and arq:
                            flash("Extensão de arq não suportado.", "warning")
                            return render_template(
                                "novo_evento.html", form=_form, id_caso=id_caso
                            )
                        nome_arq = f"{arq.filename}"
                        arq.save(
                            os.path.join(
                                current_app.root_path, "static", "casos", nome_arq
                            )
                        )
                        caso_arq = ArquivosEventoSchema(
                            link_arquivo=arq.filename if arq else None,
                            id_caso=_evento.id_caso,
                            id_evento=_evento.id,
                        )
                    except RequestEntityTooLarge:
                        flash("Tamanho de arquivo muito longo.")
                        return render_template(
                            "novo_evento.html", form=_form, id_caso=id_caso
                        )
                db.session.add(caso_arq)
                db.session.commit()

        flash("Evento criado com sucesso!", "success")
        return redirect(url_for("casos.visualizar_caso", id=id_caso))

    return render_template("novo_evento.html", form=_form, id_caso=id_caso)


# Rota para página de editar eventos
@casos_controller.route("/editar_evento/<id_evento>", methods=["POST", "GET"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ORIENTADOR,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.COLAB_EXTERNO,
    ]
)
def editar_evento(id_evento):
    db = get_db()

    def setValoresEvento(form: EventoForm, entidade_evento: EventoSchema):
        form.tipo.data = entidade_evento.tipo
        form.descricao.data = entidade_evento.descricao
        form.data_evento.data = entidade_evento.data_evento
        form.usuario.data = entidade_evento.id_usuario_responsavel

    def setDadosEvento(form: EventoForm, entidade_evento: EventoSchema):
        if form.usuario.data:
            entidade_evento.tipo = form.tipo.data
            entidade_evento.descricao = form.descricao.data
            entidade_evento.data_evento = form.data_evento.data
            entidade_evento.id_usuario_responsavel = form.usuario.data
        else:
            entidade_evento.tipo = form.tipo.data
            entidade_evento.descricao = form.descricao.data
            entidade_evento.data_evento = form.data_evento.data
            entidade_evento.id_usuario_responsavel = None

    entidade_evento = (
        db.session.query(EventoSchema).filter_by(id=id_evento, status=True).first()
    )
    if not entidade_evento:
        flash("Esse evento não existe!", "warning")
        return redirect(url_for("casos.index"))

    arquivos_evento = (
        db.session.query(ArquivosEventoSchema)
        .filter(ArquivosEventoSchema.id_evento == id_evento)
        .all()
    )

    form = EventoForm()
    if request.method == "POST":
        if not form.validate():
            return render_template(
                "editar_evento.html", form=form, entidade_evento=entidade_evento
            )

        if request.files.get("arquivos"):
            arquivos = request.files.getlist("arquivos")

            for arq in arquivos:
                if arq.filename:
                    try:
                        _, extensao_do_arq = os.path.splitext(arq.filename)
                        if extensao_do_arq != ".pdf" and arq:
                            flash("Extensão de arq não suportado.", "warning")
                            return render_template(
                                "editar_evento.html",
                                form=form,
                                entidade_evento=entidade_evento,
                            )
                        nome_arq = f"{arq.filename}"
                        arq.save(
                            os.path.join(
                                current_app.root_path, "static", "casos", nome_arq
                            )
                        )
                        caso_arq = ArquivosEventoSchema(
                            link_arquivo=arq.filename if arq else None,
                            id_caso=entidade_evento.id_caso,
                            id_evento=id_evento,
                        )
                    except RequestEntityTooLarge:
                        flash("Tamanho de arquivo muito longo.")
                        if entidade_evento.usuario_responsavel:
                            return render_template(
                                "editar_evento.html",
                                form=form,
                                entidade_evento=entidade_evento,
                                usuario=entidade_evento.usuario_responsavel.nome,
                                arquivos=arquivos_evento,
                            )
                        else:
                            return render_template(
                                "editar_evento.html",
                                form=form,
                                entidade_evento=entidade_evento,
                                usuario=None,
                                arquivos=arquivos_evento,
                            )
                db.session.add(caso_arq)
                db.session.commit()

        setDadosEvento(form, entidade_evento)

        db.session.commit()
        flash("Evento editado com sucesso!", "success")
        return redirect(url_for("casos.eventos", id_caso=entidade_evento.id_caso))

    setValoresEvento(form, entidade_evento)

    if entidade_evento.usuario_responsavel:
        nome_usuario = entidade_evento.usuario_responsavel.nome

    else:
        nome_usuario = "Não Há"

    return render_template(
        "editar_evento.html",
        form=form,
        entidade_evento=entidade_evento,
        usuario=nome_usuario,
        arquivos=arquivos_evento,
    )


@casos_controller.route("/excluir_evento/<id_evento>", methods=["GET", "POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ORIENTADOR,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.COLAB_EXTERNO,
    ]
)
def excluir_evento(id_evento):
    db = get_db()

    entidade_usuario = (
        db.session.query(UsuarioSchema)
        .filter_by(id=current_user.id, status=True)
        .first()
    )
    entidade_evento = db.session.query(EventoSchema).get(id_evento)

    if entidade_usuario.urole != "admin":
        if entidade_evento.id_criado_por == entidade_usuario.id:
            entidade_evento.status = False

            if entidade_evento.arquivo != None:
                local_arquivo = os.path.join(
                    current_app.root_path,
                    "static",
                    "eventos",
                    "evento_{}_{}".format(entidade_evento.id, entidade_evento.arquivo),
                )
                if os.path.exists(local_arquivo):
                    os.remove(local_arquivo)

                entidade_evento.arquivo = None

            db.session.commit()
            flash("Evento excluído com sucesso!", "success")
            return redirect((url_for("casos.eventos", id_caso=entidade_evento.id_caso)))
        else:
            flash("Você não possui autorização!", "warning")
            return redirect((url_for("casos.eventos", id_caso=entidade_evento.id_caso)))
    else:
        entidade_evento.status = False

        if entidade_evento.arquivo != None:
            local_arquivo = os.path.join(
                current_app.root_path,
                "static",
                "eventos",
                "evento_{}_{}".format(entidade_evento.id, entidade_evento.arquivo),
            )
            if os.path.exists(local_arquivo):
                os.remove(local_arquivo)

            entidade_evento.arquivo = None

        db.session.commit()
        flash("Evento excluído com sucesso!", "success")
        return redirect((url_for("casos.eventos", id_caso=entidade_evento.id_caso)))


# Rota para a página de visualizar eventos
@casos_controller.route("/visualizar_evento/<num_evento>")
@login_required()
def visualizar_evento(num_evento):
    db = get_db()

    id_caso = request.args.get("id_caso", None)
    entidade_evento = (
        db.session.query(EventoSchema)
        .filter(EventoSchema.num_evento == num_evento, EventoSchema.id_caso == id_caso)
        .first()
    )
    caso = db.session.query(CasoSchema).get(id_caso)
    if (caso == None) or (caso.status == False):
        flash("Caso inexistente!", "warning")
        return redirect(url_for("casos.index", id_caso=id_caso))

    if (not entidade_evento) or (entidade_evento.status == False):
        flash("Evento inexistente!", "warning")
        return redirect(url_for("casos.eventos", id_caso=id_caso))

    arquivos = (
        db.session.query(ArquivosEventoSchema)
        .filter(ArquivosEventoSchema.id_evento == entidade_evento.id)
        .all()
    )

    return render_template(
        "visualizar_evento.html", entidade_evento=entidade_evento, arquivos=arquivos
    )


@casos_controller.route("/novo_processo/<id_caso>", methods=["POST", "GET"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ORIENTADOR,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.COLAB_EXTERNO,
        UserRole.PROFESSOR,
    ]
)
def novo_processo(id_caso):
    db = get_db()

    entidade_caso = (
        db.session.query(CasoSchema).filter_by(id=id_caso, status=True).first()
    )
    if not entidade_caso:
        flash("Não é possível associar um processo a esse caso!", "warning")
        return redirect(url_for("casos.index"))

    form = ProcessoForm()
    if request.method == "POST":
        if not form.validate():
            return render_template("novo_processo.html", form=form)

        entidade_processo = ProcessoSchema(
            especie=form.especie.data,
            numero=form.numero.data,
            identificacao=form.identificacao.data,
            vara=form.vara.data,
            link=form.link.data,
            probabilidade=form.probabilidade.data,
            posicao_assistido=form.posicao_assistido.data,
            valor_causa_inicial=form.valor_causa.data,
            valor_causa_atual=form.valor_causa.data,
            data_distribuicao=form.data_distribuicao.data,
            data_transito_em_julgado=form.data_transito_em_julgado.data,
            obs=form.obs.data,
            id_caso=entidade_caso.id,
            id_criado_por=current_user.id,
        )

        if (
            db.session.query(ProcessoSchema)
            .filter_by(numero=int(form.numero.data))
            .count()
            > 0
        ):
            flash("O número deste processo já está cadastrado no sistema", "warning")
            return render_template("novo_processo.html", form=form)

        caso = (
            db.session.query(CasoSchema).filter_by(id=entidade_processo.id_caso).first()
        )
        caso.numero_ultimo_processo = entidade_processo.numero

        try:
            db.session.add(entidade_processo)
            db.session.commit()
            flash("Processo associado com sucesso!", "success")
        except SQLAlchemyError as error:
            db.session.rollback()
            error_message = error.args[0]
            if (
                "Out of range value for column 'numero_ultimo_processo' at row 1"
                in error_message
            ):
                flash(
                    "O número deste processo excede o valor máximo permitido", "warning"
                )
                return render_template("novo_processo.html", form=form)
            else:
                return error.args[0]

        return redirect(url_for("casos.visualizar_caso", id=id_caso))

    return render_template("novo_processo.html", form=form)


@casos_controller.route("/processo/<int:id_processo>", methods=["GET"])
@login_required()
def visualizar_processo(id_processo):
    db = get_db()

    id_caso = request.args.get("id_caso", -1, type=int)
    _processo = (
        db.session.query(ProcessoSchema)
        .filter(and_(ProcessoSchema.id == id_processo, ProcessoSchema.status == True))
        .first()
    )

    if not _processo:
        abort(404)

    return render_template(
        "visualizar_processo.html", processo=_processo, id_caso=id_caso
    )


# visualizar um processo apenas com o numero do processo
@casos_controller.route(
    "/visualizar_processo_com_numero/<int:numero_processo>", methods=["GET"]
)
@login_required()
def visualizar_processo_com_numero(numero_processo):
    db = get_db()

    _processo = (
        db.session.query(ProcessoSchema)
        .filter(
            and_(
                ProcessoSchema.numero == numero_processo, ProcessoSchema.status == True
            )
        )
        .first()
    )

    return render_template(
        "visualizar_processo.html", processo=_processo, id_caso=_processo.id_caso
    )


@casos_controller.route("/excluir_caso/<id_caso>", methods=["GET", "POST"])
@login_required(role=[UserRole.ADMINISTRADOR])
def excluir_caso(id_caso):
    db = get_db()

    rota_paginacao = request.args.get("rota_paginacao", ROTA_PAGINACAO_CASOS, type=str)

    caso = db.session.query(CasoSchema).get(id_caso)
    arquivos = db.session.query(ArquivoCasoSchema).filter(
        ArquivoCasoSchema.id_caso == id_caso
    )

    caso.status = False

    for arquivo in arquivos:
        if arquivo != None:
            local_arquivo = os.path.join(
                current_app.root_path, "static", "casos", arquivo.link_arquivo or ""
            )
            if os.path.exists(local_arquivo):
                os.remove(local_arquivo)

        db.session.delete(arquivo)

    db.session.commit()

    flash("Caso excluído com sucesso!", "success")

    if rota_paginacao:
        return redirect(url_for(rota_paginacao))
    else:
        return redirect(url_for("casos.index"))


@casos_controller.route("/excluir_processo/<id_processo>", methods=["GET", "POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ORIENTADOR,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.COLAB_EXTERNO,
    ]
)
def excluir_processo(id_processo):
    db = get_db()

    def validaExclusao(processo: ProcessoSchema):
        if current_user.urole == UserRole.ADMINISTRADOR:
            return True
        if current_user.id == processo.id_criado_por:
            return True

        return False

    def atualizarUltimoProcesso(id_do_caso):
        processos = (
            db.session.query(ProcessoSchema)
            .filter_by(id_caso=id_do_caso, status=True)
            .all()
        )
        entidade_caso = (
            db.session.query(CasoSchema).filter_by(id=id_do_caso, status=True).first()
        )
        if processos:
            ultimo_processo = processos[-1:]
            entidade_caso.numero_ultimo_processo = ultimo_processo[0].numero
            db.session.commit()
        else:
            entidade_caso.numero_ultimo_processo = None
            db.session.commit()

    id_caso = request.args.get("id_caso", -1, type=int)

    processo = queryFiltradaStatus(ProcessoSchema).filter_by(id=id_processo).first()

    if validaExclusao(processo):
        processo.status = False
        db.session.commit()
        atualizarUltimoProcesso(id_caso)
        flash("Processo excluído!", "success")
    else:
        flash("Você não pode excluir este processo.", "warning")
    return redirect(url_for("casos.visualizar_caso", id=id_caso))


@casos_controller.route("/editar_processo/<id_processo>", methods=["POST", "GET"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ORIENTADOR,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.COLAB_EXTERNO,
    ]
)
def editar_processo(id_processo):
    db = get_db()

    def setValoresProcesso(form: ProcessoForm, entidade_processo: ProcessoSchema):
        form.especie.data = entidade_processo.especie
        form.numero.data = entidade_processo.numero
        form.identificacao.data = entidade_processo.identificacao
        form.vara.data = entidade_processo.vara
        form.link.data = entidade_processo.link
        form.probabilidade.data = entidade_processo.probabilidade
        form.posicao_assistido.data = entidade_processo.posicao_assistido
        form.valor_causa.data = entidade_processo.valor_causa_atual
        form.data_distribuicao.data = entidade_processo.data_distribuicao
        form.data_transito_em_julgado.data = entidade_processo.data_transito_em_julgado
        form.obs.data = entidade_processo.obs

    def setDadosProcesso(form: ProcessoForm, entidade_processo: ProcessoSchema):
        entidade_processo.especie = form.especie.data
        entidade_processo.numero = form.numero.data
        entidade_processo.identificacao = form.identificacao.data
        entidade_processo.vara = form.vara.data
        entidade_processo.link = form.link.data
        entidade_processo.probabilidade = form.probabilidade.data
        entidade_processo.posicao_assistido = form.posicao_assistido.data
        entidade_processo.valor_causa_atual = form.valor_causa.data
        entidade_processo.data_distribuicao = form.data_distribuicao.data
        entidade_processo.data_transito_em_julgado = form.data_transito_em_julgado.data
        entidade_processo.obs = form.obs.data

    entidade_processo = (
        db.session.query(ProcessoSchema).filter_by(id=id_processo, status=True).first()
    )
    if not entidade_processo:
        flash("Esse processo não existe!", "warning")
        return redirect(url_for("casos.index"))
    form = ProcessoForm()
    if request.method == "POST":
        if not form.validate():
            return render_template(
                "editar_processo.html", form=form, id_processo=id_processo
            )
        setDadosProcesso(form, entidade_processo)
        db.session.commit()
        flash("Processo editado com sucesso!", "success")
        return redirect(
            url_for(
                "casos.visualizar_processo",
                id_processo=id_processo,
                id_caso=entidade_processo.id_caso,
            )
        )

    setValoresProcesso(form, entidade_processo)
    return render_template("editar_processo.html", form=form, id_processo=id_processo)


@casos_controller.route(
    "/editar_arquivo_caso/<id_arquivo>/<id_caso>", methods=["GET", "POST"]
)
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_PROJETO,
        UserRole.COLAB_EXTERNO,
        UserRole.ORIENTADOR,
    ]
)
def editar_arquivo_caso(id_arquivo, id_caso):
    db = get_db()

    _form = ArquivoCasoForm()
    _arquivo = db.session.get(ArquivoCasoSchema, id_arquivo)
    if not _arquivo:
        abort(404)

    try:
        arquivo = request.files.get("arquivo")
    except RequestEntityTooLarge:
        flash("Tamanho de arquivo muito longo.")
        return render_template(
            "editar_arquivo_caso.html",
            form=_form,
            id_arquivo=id_arquivo,
            id_caso=id_caso,
        )
    if arquivo:
        nome_do_arquivo, extensao_do_arquivo = os.path.splitext(arquivo.filename)
        if extensao_do_arquivo != ".pdf" and arquivo:
            flash("Extensão de arquivo não suportado.", "warning")
            return render_template(
                "editar_arquivo_caso.html",
                form=_form,
                id_arquivo=id_arquivo,
                id_caso=id_caso,
            )
        _arquivo.link_arquivo = arquivo.filename
        nome_arquivo = f"{arquivo.filename}"
        arquivo.save(
            os.path.join(current_app.root_path, "static", "casos", nome_arquivo)
        )

        db.session.commit()
        flash("Arquivo editado com sucesso", "success")
        return redirect(url_for("casos.editar_caso", id_caso=id_caso))

    return render_template("editar_arquivo_caso.html", form=_form)


@casos_controller.route(
    "/editar_arquivo_evento/<id_arquivo>/<id_evento>", methods=["GET", "POST"]
)
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_PROJETO,
        UserRole.COLAB_EXTERNO,
        UserRole.ORIENTADOR,
    ]
)
def editar_arquivo_evento(id_arquivo, id_evento):
    db = get_db()

    _form = EditarArquivoDeEventoForm()
    _arquivo = db.session.get(ArquivosEventoSchema, id_arquivo)
    if not _arquivo:
        abort(404)

    try:
        arquivo = request.files.get("arquivo")
    except RequestEntityTooLarge:
        flash("Tamanho de arquivo muito longo.")
        return render_template(
            "editar_arquivo_evento.html",
            form=_form,
            id_arquivo=id_arquivo,
            id_evento=id_evento,
        )
    if arquivo:
        nome_do_arquivo, extensao_do_arquivo = os.path.splitext(arquivo.filename)
        if extensao_do_arquivo != ".pdf" and arquivo:
            flash("Extensão de arquivo não suportado.", "warning")
            return render_template(
                "editar_arquivo_evento.html",
                form=_form,
                id_arquivo=id_arquivo,
                id_evento=id_evento,
            )
        _arquivo.link_arquivo = arquivo.filename
        nome_arquivo = f"{arquivo.filename}"
        arquivo.save(
            os.path.join(current_app.root_path, "static", "casos", nome_arquivo)
        )

        db.session.commit()
        flash("Arquivo editado com sucesso", "success")
        return redirect(url_for("casos.editar_evento", id_evento=id_evento))

    return render_template("editar_arquivo_evento.html", form=_form)


@casos_controller.route(
    "/excluir_arquivo_evento/<id_arquivo>/<id_evento>", methods=["GET", "POST"]
)
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ORIENTADOR,
        UserRole.PROFESSOR,
    ]
)
def excluir_arquivo_evento(id_arquivo, id_evento):
    db = get_db()

    arquivo = db.session.get(ArquivosEventoSchema, id_arquivo)
    if not arquivo:
        abort(404)

    db.session.delete(arquivo)
    db.session.commit()

    return redirect(url_for("casos.editar_evento", id_evento=id_evento))
