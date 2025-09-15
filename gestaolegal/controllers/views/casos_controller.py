import logging

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from werkzeug.exceptions import RequestEntityTooLarge

from gestaolegal.common.constants import (
    UserRole,
    assistencia_jud_areas_atendidas,
    situacao_deferimento,
    tipo_evento,
)
from gestaolegal.forms.relatorio import (
    ArquivoCasoForm,
    CasoForm,
    EditarArquivoDeEventoForm,
    EventoForm,
    JustificativaIndeferimento,
    LembreteForm,
    NovoCasoForm,
    RoteiroForm,
)
from gestaolegal.repositories.base_repository import PageParams
from gestaolegal.services.arquivo_service import ArquivoService
from gestaolegal.services.casos_service import CasosService
from gestaolegal.services.notificacao_service import NotificacaoService
from gestaolegal.services.processo_service import ProcessoService
from gestaolegal.utils.decorators import login_required

opcoes_filtro_casos = {}
for key, value in situacao_deferimento.items():
    opcoes_filtro_casos[key] = (value[0], value[1])
opcoes_filtro_casos["TODOS"] = ("todos", "Todos Casos")

opcoes_filtro_meus_casos = {"CADASTRADO_POR_MIM": ("cad_por_mim", "Cadastrado por mim")}
opcoes_filtro_meus_casos["ATIVO"] = (situacao_deferimento["ATIVO"][0], situacao_deferimento["ATIVO"][1])
opcoes_filtro_meus_casos["ARQUIVADO"] = (situacao_deferimento["ARQUIVADO"][0], situacao_deferimento["ARQUIVADO"][1])
opcoes_filtro_meus_casos["AGUARDANDO_DEFERIMENTO"] = (situacao_deferimento["AGUARDANDO_DEFERIMENTO"][0], situacao_deferimento["AGUARDANDO_DEFERIMENTO"][1])
opcoes_filtro_meus_casos["INDEFERIDO"] = (situacao_deferimento["INDEFERIDO"][0], situacao_deferimento["INDEFERIDO"][1])

opcoes_filtro_eventos = tipo_evento.copy()
opcoes_filtro_eventos["TODOS"] = ("todos", "Todos")

logger = logging.getLogger(__name__)

casos_controller = Blueprint(
    "casos", __name__, template_folder="../../static/templates"
)


@casos_controller.route("/")
@login_required()
def index():
    casos_service = CasosService()
    processo_service = ProcessoService()
    processo_service.update_ultimo_processo_dos_casos()

    page = request.args.get("page", 1, type=int)
    opcao_filtro = request.args.get(
        "opcao_filtro", opcoes_filtro_casos["TODOS"][0], type=str
    )

    page_params = PageParams(page=page, per_page=current_app.config["CASOS_POR_PAGINA"])
    casos = casos_service.get_casos_with_filters(opcao_filtro, page_params)

    return render_template(
        "casos/listagem_casos.html",
        opcoes_filtro_casos=opcoes_filtro_casos,
        opcao_filtro=opcao_filtro,
        casos=casos,
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
    logger.info("Entering novo_caso route - Starting new case creation process")
    casos_service = CasosService()

    _form = NovoCasoForm()

    if request.method == "POST":
        if _form.validate_on_submit():
            try:
                data = _form.to_dict()
                data["id_usuario_responsavel"] = current_user.id
                data["id_criado_por"] = current_user.id
                data["id_modificado_por"] = current_user.id

                caso = casos_service.create(data)

                arquivo = request.files.get("arquivo")
                if arquivo and arquivo.filename:
                    try:
                        nome_arquivo = casos_service.save_arquivo(arquivo)
                        arquivo_service = ArquivoService()
                        arquivo_service.create_arquivo_caso(caso.id, nome_arquivo)
                    except ValueError as e:
                        flash(str(e), "warning")
                    except RequestEntityTooLarge:
                        flash("Tamanho de arquivo muito longo.", "warning")

                notification_service = NotificacaoService()
                notification_service.create_notificacao(
                    acao=f"Cadastrou novo caso {caso.id}",
                    id_executor_acao=current_user.id,
                    id_usu_notificar=caso.id_usuario_responsavel,
                )

                flash("Caso criado com sucesso!", "success")
                return redirect(url_for("casos.visualizar_caso", id=caso.id))
            except Exception as e:
                logger.error(f"Error creating case: {str(e)}", exc_info=True)
                flash("Erro ao criar caso. Tente novamente.", "danger")
        else:
            flash("Dados inválidos.", "warning")

        return render_template(
            "casos/cadastrar_caso.html",
            form=_form,
            title="Novo Caso",
            caso=None,
        )

    return render_template(
        "casos/cadastrar_caso.html", form=_form, title="Novo Caso", caso=None
    )


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
    CasosService()
    try:
        arquivo_service = ArquivoService()
        arquivo_service.delete_arquivo_caso(int(id_arquivo))
        return redirect(url_for("casos.editar_caso", id_caso=id_caso))
    except ValueError:
        abort(404)


@casos_controller.route("/visualizar/<int:id>", methods=["GET"])
@login_required()
def visualizar_caso(id):
    casos_service = CasosService()
    _caso = casos_service.find_by_id(id)

    if _caso is None:
        flash("Caso inexistente!", "warning")
        return redirect(url_for("casos.index"))

    arquivos = casos_service.get_arquivos_by_caso(id)
    processo_service = ProcessoService()
    processos = processo_service.get_processos_by_caso(id)
    lembretes = casos_service.get_lembretes_by_caso(id)

    _lembrete = lembretes[0] if lembretes else None
    eventos_query = casos_service.get_eventos_by_caso(id, "todos")
    eventos_list = list(eventos_query)
    evento = eventos_list[0] if eventos_list else None

    return render_template(
        "casos/visualizar_caso.html",
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
    casos_service = CasosService()
    try:
        casos_service.deferir_caso(id_caso)
        flash("Caso deferido!", "success")
        return redirect(url_for("casos.index"))
    except ValueError:
        flash("Caso não encontrado.", "warning")
        return redirect(url_for("casos.index"))


@casos_controller.route("/indeferir/<id_caso>", methods=["POST", "GET"])
@login_required(role=[UserRole.ADMINISTRADOR, UserRole.PROFESSOR])
def indeferir_caso(id_caso):
    casos_service = CasosService()
    _form = JustificativaIndeferimento()

    if request.method == "POST":
        try:
            justificativa = request.form.get("justificativa", "")
            casos_service.indeferir_caso(id_caso, justificativa)
            flash("Indeferimento realizado.", "success")
            return redirect(url_for("casos.index"))
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("casos.visualizar_caso", id=id_caso))

    return render_template("casos/justificativa.html", form=_form)


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
    casos_service = CasosService()
    caso = casos_service.find_by_id(int(id_caso))

    if not caso:
        flash("Caso inexistente!", "warning")
        return redirect(url_for("casos.index"))

    has_perm, msg = casos_service.validate_caso_edit_permission(
        caso, current_user.id, current_user.urole
    )
    if not has_perm:
        flash(msg, "warning")
        return redirect(url_for("casos.index"))

    if request.method == "POST":
        form = CasoForm()
        if not form.validate_on_submit():
            flash("Dados inválidos.", "warning")
            return render_template(
                "casos/editar_caso.html",
                form=form,
                caso=caso,
                arquivos=casos_service.get_arquivos_by_caso(int(id_caso)),
            )
        try:
            data = form.to_dict()
            data["id_modificado_por"] = current_user.id
            casos_service.update(int(id_caso), data)
            flash("Caso editado com sucesso!", "success")
            return redirect(url_for("casos.index"))
        except Exception as e:
            flash(str(e), "danger")
            return redirect(url_for("casos.editar_caso", id_caso=id_caso))

    form = CasoForm()
    form.orientador.data = caso.id_orientador
    form.estagiario.data = caso.id_estagiario
    form.colaborador.data = caso.id_colaborador
    form.area_direito.data = caso.area_direito
    form.descricao.data = caso.descricao

    arquivos = casos_service.get_arquivos_by_caso(int(id_caso))

    return render_template(
        "casos/editar_caso.html", form=form, caso=caso, arquivos=arquivos
    )


@casos_controller.route(
    "/excluir_assistido_caso/<id_caso>/<id_assistido>", methods=["POST", "GET"]
)
@login_required()
def excluir_assistido_caso(id_caso, id_assistido):
    casos_service = CasosService()
    try:
        casos_service.remove_cliente_from_caso(int(id_caso), int(id_assistido))
        return redirect(url_for("casos.index"))
    except ValueError as e:
        flash(str(e), "warning")
        return redirect(url_for("casos.index"))


@casos_controller.route("/adicionar_assistido_caso/<id_caso>", methods=["POST", "GET"])
@login_required()
def adicionar_assistido_caso(id_caso):
    casos_service = CasosService()
    if request.method == "POST":
        try:
            casos_service.adicionar_assistidos_ao_caso(id_caso, request.form)
            flash("Assistidos adicionados com sucesso!", "success")
        except Exception as e:
            flash(str(e), "warning")
    return redirect(url_for("casos.index"))


@casos_controller.route("/links_roteiro", methods=["GET", "POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_EXTERNO,
    ]
)
def editar_roteiro():
    casos_service = CasosService()
    _form = RoteiroForm()
    if _form.validate_on_submit():
        try:
            casos_service.create_or_update_roteiro(
                _form.area_direito.data, _form.link.data
            )
            flash("Alteração realizada com sucesso!", "success")
            return redirect(url_for("casos.editar_roteiro"))
        except Exception as e:
            logger.error(f"Error updating roteiro: {str(e)}", exc_info=True)
            flash("Erro ao atualizar roteiro. Tente novamente.", "danger")

    _roteiros = casos_service.get_all_roteiros()
    return render_template(
        "casos/links_roteiro.html",
        form=_form,
        roteiros=_roteiros,
        assistencia_jud_areas_atendidas=assistencia_jud_areas_atendidas,
    )


@casos_controller.route("/eventos/<id_caso>")
@login_required()
def eventos(id_caso):
    casos_service = CasosService()
    page = request.args.get("page", 1, type=int)
    opcao_filtro = request.args.get(
        "opcao_filtro", opcoes_filtro_eventos["TODOS"][0], type=str
    )

    page_params = PageParams(
        page=page, per_page=current_app.config["EVENTOS_POR_PAGINA"]
    )
    _eventos = casos_service.get_eventos_by_caso(
        int(id_caso), opcao_filtro, page_params
    )

    if not _eventos.items:
        flash("Não há eventos cadastrados para este caso.", "warning")
        return redirect(url_for("casos.visualizar_caso", id=id_caso))

    return render_template(
        "casos/eventos/listagem_eventos.html",
        opcoes_filtro_eventos=opcoes_filtro_eventos,
        **casos_service.params_busca_eventos(
            _eventos, "casos.eventos", id_caso, opcao_filtro
        ),
    )


@casos_controller.route("/lembretes/<id_caso>")
@login_required()
def lembretes(id_caso):
    casos_service = CasosService()
    num_lembrete = request.args.get("num_lembrete", None)

    _lembretes = casos_service.get_lembretes_by_caso(int(id_caso))

    _lembrete = None
    if num_lembrete:
        _lembrete = casos_service.get_lembrete_by_numero(
            int(id_caso), int(num_lembrete)
        )

    caso = casos_service.find_by_id(int(id_caso))
    if not caso:
        flash("Caso inexistente!", "warning")
        return redirect(url_for("casos.index", id_caso=id_caso))

    if (num_lembrete is not None) and (not _lembrete or not _lembrete.status):
        flash("Lembrete inexistente!", "warning")

    return render_template(
        "casos/lembretes/listagem_lembretes.html", caso_id=id_caso, lembretes=_lembretes
    )


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
    casos_service = CasosService()
    _form = LembreteForm()

    if request.method == "POST":
        try:
            casos_service.create_lembrete_with_notification(
                form=_form,
                caso_id=id_do_caso,
                current_user_id=current_user.id,
            )
            flash("Lembrete enviado com sucesso!", "success")
            return redirect(url_for("casos.visualizar_caso", id=id_do_caso))
        except Exception as e:
            flash(str(e), "error")

    return render_template("casos/lembretes/cadastrar_lembrete.html", form=_form)


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
    casos_service = CasosService()

    if request.method == "POST":
        try:
            lembrete = casos_service.update_lembrete(
                id_lembrete=int(id_lembrete), form=request.form
            )
            flash("Lembrete editado com sucesso!", "success")
            return redirect(url_for("casos.lembretes", id_caso=lembrete.id_caso))
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("casos.index"))

    form_data = casos_service.get_editar_lembrete_data(int(id_lembrete))

    if not form_data:
        flash("Lembrete não encontrado", "warning")
        return redirect(url_for("casos.index"))

    return render_template(
        "casos/lembretes/editar_lembrete.html",
        form=form_data["form"],
        usuario=form_data["usuario"],
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
    casos_service = CasosService()
    if not casos_service.validate_lembrete_permission(
        int(id_lembrete), current_user.id, current_user.urole
    ):
        flash("Você não possui autorização!", "warning")
        return redirect(url_for("casos.index"))

    try:
        lembrete = casos_service.get_lembrete_by_id(int(id_lembrete))
        caso_id = lembrete.id_caso
        casos_service.delete_lembrete(int(id_lembrete))
        flash("Lembrete excluído com sucesso!", "success")
        return redirect(url_for("casos.lembretes", id_caso=caso_id))
    except ValueError:
        flash("Lembrete não encontrado!", "warning")
        return redirect(url_for("casos.index"))


def cadastrar_historico(id_usuario, id_caso):
    casos_service = CasosService()
    return casos_service.create_historico(id_usuario, id_caso)


@casos_controller.route("/historico/<id_caso>")
def historico(id_caso):
    casos_service = CasosService()
    page = request.args.get("page", 1, type=int)

    page_params = PageParams(
        page=page, per_page=current_app.config["HISTORICOS_POR_PAGINA"]
    )
    historicos = casos_service.get_historico_by_caso(
        int(id_caso),
        page_params=page_params,
    )

    return render_template(
        "casos/historico.html", historicos=historicos, caso_id=id_caso
    )


@casos_controller.route("/meus_casos")
@login_required()
def meus_casos():
    casos_service = CasosService()
    page = request.args.get("page", 1, type=int)
    opcao_filtro = request.args.get(
        "opcao_filtro", opcoes_filtro_meus_casos["ATIVO"][0], type=str
    )

    page_params = PageParams(page=page, per_page=current_app.config["CASOS_POR_PAGINA"])
    casos = casos_service.get_meus_casos(current_user.id, opcao_filtro, page_params)

    titulo_total = casos_service.titulo_total_meus_casos(casos.total)

    return render_template(
        "casos/meus_casos.html",
        opcoes_filtro_meus_casos=opcoes_filtro_meus_casos,
        titulo_total=titulo_total,
        **casos_service.params_busca_casos(casos, "casos.meus_casos", opcao_filtro),
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
    casos_service = CasosService()
    _form = EventoForm()

    if request.method == "POST":
        try:
            casos_service.create_evento_with_files_and_notification(
                form=_form,
                caso_id=id_caso,
                current_user_id=current_user.id,
                request=request,
            )
            flash("Evento criado com sucesso!", "success")
            return redirect(url_for("casos.visualizar_caso", id=id_caso))
        except Exception as e:
            flash(str(e), "error")
            return render_template(
                "casos/eventos/cadastrar_evento.html",
                form=_form,
                id_caso=id_caso,
            )

    return render_template(
        "casos/eventos/cadastrar_evento.html", form=_form, id_caso=id_caso
    )


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
    casos_service = CasosService()

    if request.method == "POST":
        try:
            evento = casos_service.update_evento_with_files(
                evento_id=int(id_evento),
                form=request.form,
                request=request,
            )
            flash("Evento editado com sucesso!", "success")
            return redirect(url_for("casos.eventos", id_caso=evento.id_caso))
        except Exception as e:
            flash(str(e), "error")
            form_data = casos_service.get_editar_evento_data(int(id_evento))
            return render_template(
                "casos/eventos/editar_evento.html",
                form=form_data.get("form", {}),
                entidade_evento=form_data.get("evento"),
                usuario=form_data.get("usuario", {}),
                arquivos=form_data.get("arquivos", []),
            )

    # GET request - prepare form data
    form_data = casos_service.get_editar_evento_data(int(id_evento))

    if not form_data:
        flash("Evento não encontrado", "warning")
        return redirect(url_for("casos.index"))

    return render_template(
        "casos/eventos/editar_evento.html",
        form=form_data.get("form", {}),
        entidade_evento=form_data.get("evento"),
        usuario=form_data.get("usuario", {}),
        arquivos=form_data.get("arquivos", []),
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
    casos_service = CasosService()
    entidade_evento = casos_service.get_evento_by_id(int(id_evento))
    if not entidade_evento:
        flash("Evento não encontrado!", "warning")
        return redirect(url_for("casos.index"))

    if not casos_service.validate_evento_permission(
        int(id_evento), current_user.id, current_user.urole
    ):
        flash("Você não possui autorização!", "warning")
        return redirect(url_for("casos.eventos", id_caso=entidade_evento.id_caso))

    try:
        casos_service.delete_evento(int(id_evento))
        flash("Evento excluído com sucesso!", "success")
    except ValueError as e:
        flash(str(e), "warning")
    except Exception as e:
        logger.error(f"Error deleting evento: {str(e)}", exc_info=True)
        flash("Erro ao excluir evento. Tente novamente.", "danger")

    return redirect(url_for("casos.eventos", id_caso=entidade_evento.id_caso))


@casos_controller.route("/visualizar_evento/<num_evento>")
@login_required()
def visualizar_evento(num_evento):
    casos_service = CasosService()
    id_caso = request.args.get("id_caso", None)

    if not id_caso:
        flash("ID do caso não fornecido!", "warning")
        return redirect(url_for("casos.index"))

    entidade_evento, arquivos = casos_service.get_evento_with_arquivos(
        int(num_evento), int(id_caso)
    )

    if not entidade_evento:
        flash("Evento inexistente!", "warning")
        return redirect(url_for("casos.eventos", id_caso=id_caso))

    return render_template(
        "casos/eventos/visualizar_evento.html",
        entidade_evento=entidade_evento,
        arquivos=arquivos,
    )


@casos_controller.route("/excluir_caso/<id_caso>", methods=["GET", "POST"])
@login_required(role=[UserRole.ADMINISTRADOR])
def excluir_caso(id_caso):
    casos_service = CasosService()
    rota_paginacao = request.args.get("rota_paginacao", "casos.index", type=str)

    try:
        casos_service.delete_caso(int(id_caso))
        flash("Caso excluído com sucesso!", "success")
    except ValueError as e:
        flash(str(e), "warning")
    except Exception as e:
        logger.error(f"Error deleting caso: {str(e)}", exc_info=True)
        flash("Erro ao excluir caso. Tente novamente.", "danger")

    if rota_paginacao:
        return redirect(url_for(rota_paginacao))
    else:
        return redirect(url_for("casos.index"))


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
    casos_service = CasosService()
    _form = ArquivoCasoForm()

    if request.method == "POST":
        try:
            casos_service.update_arquivo_caso(
                id_arquivo=int(id_arquivo),
                request=request,
            )
            flash("Arquivo editado com sucesso", "success")
            return redirect(url_for("casos.editar_caso", id_caso=id_caso))
        except Exception as e:
            flash(str(e), "error")
            return render_template(
                "editar_arquivo_casos/editar_caso.html",
                form=_form,
                id_arquivo=id_arquivo,
                id_caso=id_caso,
            )

    # Check if arquivo exists
    if not casos_service.validate_arquivo_exists(int(id_arquivo)):
        abort(404)

    return render_template("editar_arquivo_casos/editar_caso.html", form=_form)


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
    casos_service = CasosService()
    _form = EditarArquivoDeEventoForm()

    if request.method == "POST":
        try:
            casos_service.update_arquivo_evento(
                id_arquivo=int(id_arquivo),
                request=request,
            )
            flash("Arquivo editado com sucesso", "success")
            return redirect(url_for("casos.editar_evento", id_evento=id_evento))
        except Exception as e:
            flash(str(e), "error")
            return render_template(
                "casos/arquivos/editar_arquivo_evento.html",
                form=_form,
                id_arquivo=id_arquivo,
                id_evento=id_evento,
            )

    # Check if arquivo exists
    if not casos_service.validate_arquivo_evento_exists(int(id_arquivo)):
        abort(404)

    return render_template("casos/arquivos/editar_arquivo_evento.html", form=_form)


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
    casos_service = CasosService()
    try:
        casos_service.delete_arquivo_evento(int(id_arquivo))
        return redirect(url_for("casos.editar_evento", id_evento=id_evento))
    except ValueError:
        abort(404)
