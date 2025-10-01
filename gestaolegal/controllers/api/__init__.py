import json
import logging

from flask import Blueprint, current_app, flash, jsonify, redirect, request, url_for
from flask_login import current_user
from flask_wtf.csrf import CSRFProtect

from gestaolegal.common import PageParams
from gestaolegal.common.constants import UserRole, situacao_deferimento, tipo_evento
from gestaolegal.services.assistencia_judiciaria_service import (
    AssistenciaJudiciariaService,
)
from gestaolegal.services.casos_service import CasosService
from gestaolegal.services.orientacao_juridica_service import OrientacaoJuridicaService
from gestaolegal.services.plantao_service import PlantaoService
from gestaolegal.services.relatorio_service import RelatorioService
from gestaolegal.services.usuario_service import UsuarioService
from gestaolegal.utils import api_error, api_paginated, api_success
from gestaolegal.utils.decorators import login_required
from gestaolegal.controllers.api.atendido_controller import atendido_controller
from gestaolegal.controllers.api.user_controller import user_controller
from gestaolegal.controllers.api.caso_controller import caso_controller
from gestaolegal.controllers.api.arquivo_controller import arquivo_controller
from gestaolegal.controllers.api.notificacao_controller import notificacao_controller
from gestaolegal.controllers.api.relatorio_controller import relatorio_controller
from gestaolegal.controllers.api.unified_controller import unified_controller
from gestaolegal.controllers.api.plantao_controller import plantao_controller

csrf = CSRFProtect()

opcoes_filtro_casos = situacao_deferimento.copy()
opcoes_filtro_casos["TODOS"] = ("todos", "Todos Casos", "primary")

opcoes_filtro_meus_casos = {
    "CADASTRADO_POR_MIM": ("cad_por_mim", "Cadastrado por mim", "info")
}
opcoes_filtro_meus_casos["ATIVO"] = situacao_deferimento["ATIVO"]
opcoes_filtro_meus_casos["ARQUIVADO"] = situacao_deferimento["ARQUIVADO"]
opcoes_filtro_meus_casos["AGUARDANDO_DEFERIMENTO"] = situacao_deferimento[
    "AGUARDANDO_DEFERIMENTO"
]
opcoes_filtro_meus_casos["INDEFERIDO"] = situacao_deferimento["INDEFERIDO"]

opcoes_filtro_eventos = tipo_evento.copy()
opcoes_filtro_eventos["TODOS"] = ("todos", "Todos")

logger = logging.getLogger(__name__)
api_controller = Blueprint("api", __name__)


@api_controller.route("/casos/filtro")
@login_required()
def filtro_casos():
    logger.info("Entering api_filtro_casos route")
    casos_service = CasosService()
    page = request.args.get("page", 1, type=int)
    opcao_filtro = request.args.get(
        "opcao_filtro", opcoes_filtro_casos["TODOS"][0], type=str
    )

    page_params = PageParams(page=page, per_page=current_app.config["CASOS_POR_PAGINA"])
    casos = casos_service.get_casos_with_filters(opcao_filtro, page_params)

    params = casos_service.params_busca_casos(casos, "casos.index", opcao_filtro)
    return api_success(
        {
            "items": [
                {"id": c.id, "titulo": getattr(c, "titulo", None)}
                for c in params.get("casos").items
            ],
            "total": params.get("casos").total,
            "page": params.get("casos").page,
            "pages": params.get("casos").pages,
        }
    )


@api_controller.route("/casos/meus_casos/filtro")
@login_required()
def filtro_meus_casos():
    casos_service = CasosService()
    page = request.args.get("page", 1, type=int)
    opcao_filtro = request.args.get(
        "opcao_filtro", opcoes_filtro_meus_casos["ATIVO"][0], type=str
    )

    page_params = PageParams(page=page, per_page=current_app.config["CASOS_POR_PAGINA"])
    casos = casos_service.get_meus_casos(current_user.id, opcao_filtro, page_params)

    titulo_total = casos_service.titulo_total_meus_casos(casos.total)

    params = casos_service.params_busca_casos(casos, "casos.meus_casos", opcao_filtro)
    return api_success(
        {
            "items": [
                {"id": c.id, "titulo": getattr(c, "titulo", None)}
                for c in params.get("casos").items
            ],
            "total": params.get("casos").total,
            "page": params.get("casos").page,
            "pages": params.get("casos").pages,
            "titulo_total": titulo_total,
        }
    )


@api_controller.route("/casos/buscar_usuario")
@login_required()
def casos_buscar_usuario():
    usuario_service = UsuarioService()
    termo = request.args.get("q", type=str)

    result = usuario_service.search_usuarios(termo)
    usuarios_clean = [{"id": usuario.id, "text": usuario.nome} for usuario in result]

    response = current_app.response_class(
        response=json.dumps({"results": usuarios_clean}),
        status=200,
        mimetype="application/json",
    )
    return response


@api_controller.route("/casos/buscar_casos")
@login_required()
def casos_buscar_casos():
    casos_service = CasosService()
    id_caso = request.args.get("q", type=str)

    casos_clean = casos_service.search_casos(id_caso)

    if (
        len(casos_clean) == 1
        and casos_clean[0].get("text") == "Não há casos cadastrados no sistema"
    ):
        response = current_app.response_class(
            response=json.dumps(casos_clean[0]),
            status=200,
            mimetype="application/json",
        )
    else:
        response = current_app.response_class(
            response=json.dumps({"results": casos_clean}),
            status=200,
            mimetype="application/json",
        )
    return response


@api_controller.route("/casos/buscar_orientador")
@login_required()
def casos_buscar_orientador():
    CasosService()
    termo = request.args.get("q", type=str)

    usuario_service = UsuarioService()
    result = usuario_service.search_usuarios_by_role(termo, "orient")
    usuarios_clean = [{"id": usuario.id, "text": usuario.nome} for usuario in result]

    response = current_app.response_class(
        response=json.dumps({"results": usuarios_clean}),
        status=200,
        mimetype="application/json",
    )
    return response


@api_controller.route("/casos/buscar_estagiario")
@login_required()
def casos_buscar_estagiario():
    CasosService()
    termo = request.args.get("q", type=str)

    usuario_service = UsuarioService()
    result = usuario_service.search_usuarios_by_role(termo, "estag_direito")
    usuarios_clean = [{"id": usuario.id, "text": usuario.nome} for usuario in result]

    response = current_app.response_class(
        response=json.dumps({"results": usuarios_clean}),
        status=200,
        mimetype="application/json",
    )
    return response


@api_controller.route("/casos/buscar_colaborador")
@login_required()
def casos_buscar_colaborador():
    CasosService()
    termo = request.args.get("q", type=str)

    usuario_service = UsuarioService()
    result = usuario_service.search_usuarios_by_role(termo, "colab_ext")
    usuarios_clean = [{"id": usuario.id, "text": usuario.nome} for usuario in result]

    response = current_app.response_class(
        response=json.dumps({"results": usuarios_clean}),
        status=200,
        mimetype="application/json",
    )
    return response


@api_controller.route("/casos/filtro_eventos/<id_caso>")
@login_required()
def filtro_eventos(id_caso):
    casos_service = CasosService()
    page = request.args.get("page", 1, type=int)
    opcao_filtro = request.args.get(
        "opcao_filtro", opcoes_filtro_meus_casos["ATIVO"][0], type=str
    )

    page_params = PageParams(
        page=page, per_page=current_app.config["EVENTOS_POR_PAGINA"]
    )
    _eventos = casos_service.get_eventos_by_caso(
        int(id_caso), opcao_filtro, page_params
    )

    params = casos_service.params_busca_eventos(
        _eventos, "casos.eventos", id_caso, opcao_filtro
    )
    return api_success(
        {
            "items": [
                {"id": e.id, "descricao": getattr(e, "descricao", None)}
                for e in params.get("eventos").items
            ],
            "total": params.get("eventos").total,
            "page": params.get("eventos").page,
            "pages": params.get("eventos").pages,
        }
    )


@api_controller.route("/orientacao_juridica/buscar_atendidos")
@login_required()
def orientacao_buscar_atendidos():
    orientacao_juridica_service = OrientacaoJuridicaService()

    atendidos = orientacao_juridica_service.buscar_atendidos(
        termo=request.args.get("termo", ""),
        orientacao_id=request.args.get("orientacao_id"),
    )
    return api_success(
        {
            "results": [
                {"id": a.id, "nome": a.nome, "cpf": getattr(a, "cpf", None)}
                for a in atendidos
            ]
        }
    )


@api_controller.route("/orientacao_juridica/associar_atendido")
@login_required()
def orientacao_associar_atendido():
    orientacao_juridica_service = OrientacaoJuridicaService()

    try:
        orientacao_id = request.form.get("orientacao_id")
        atendido_id = request.form.get("atendido_id")

        success = orientacao_juridica_service.associar_atendido(
            orientacao_id, atendido_id
        )

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            if success:
                return api_success({"message": "Atendido associado com sucesso!"})
            return api_error("Erro ao associar atendido", status_code=400)

        if success:
            flash("Atendido associado com sucesso!", "success")
        else:
            flash("Erro ao associar atendido", "error")
    except Exception as e:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return api_error(str(e), status_code=400)
        flash(str(e), "error")


@api_controller.route("/plantao/obter_escala_plantao")
@login_required()
def obter_escala_plantao():
    plantao_service = PlantaoService()
    escala = plantao_service.get_escala_plantao()
    return api_success(escala)


@api_controller.route("/plantao/obter_duracao_plantao", methods=["GET", "POST"])
@login_required()
def obter_duracao_plantao():
    plantao_service = PlantaoService()
    dias_duracao = plantao_service.get_duracao_plantao()
    return api_success(dias_duracao)


@api_controller.route("/plantao/confirma_data_plantao", methods=["POST", "GET"])
@login_required()
def confirma_data_plantao():
    plantao_service = PlantaoService()

    if not plantao_service.check_plantao_access(current_user.urole):
        flash("O plantão não está aberto!")
        return redirect(url_for("principal.index"))

    ano = request.args.get("ano")
    mes = request.args.get("mes")
    dia = request.args.get("dia")

    resultado = plantao_service.confirmar_data_plantao(
        ano, mes, dia, current_user.id, current_user.urole
    )

    return api_success(resultado)


@api_controller.route("/plantao/disponibilidade_de_vagas", methods=["POST", "GET"])
@login_required()
def disponibilidade_de_vagas():
    ano = request.args.get("ano")
    mes = request.args.get("mes")

    plantao_service = PlantaoService()
    dias = plantao_service.get_disponibilidade_vagas_mes(ano, mes, current_user.urole)

    return api_success(dias)


@api_controller.route("/plantao/vagas_disponiveis", methods=["POST", "GET"])
@login_required()
def vagas_disponiveis():
    ano = request.args.get("ano")
    mes = request.args.get("mes")
    dia = request.args.get("dia")

    plantao_service = PlantaoService()
    index = plantao_service.get_vagas_disponiveis_dia(ano, mes, dia, current_user.urole)

    return api_success(index)


@api_controller.route("/plantao/registra_presenca", methods=["POST"])
@login_required()
def registra_presenca():
    plantao_service = PlantaoService()
    resposta = plantao_service.registrar_presenca(current_user.id, request.json)
    return api_success(resposta)


@api_controller.route("/plantao/busca_presencas_data", methods=["POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.COLAB_PROJETO,
        UserRole.PROFESSOR,
    ]
)
def busca_presencas_data():
    plantao_service = PlantaoService()
    resposta = plantao_service.buscar_presencas_por_data(request.json)
    return api_success(resposta)


@api_controller.route("/plantao/salva_config_plantao", methods=["GET", "POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.COLAB_PROJETO,
    ]
)
def salva_config_plantao():
    plantao_service = PlantaoService()
    resposta = plantao_service.salvar_configuracao_plantao(
        request.json, current_user.id
    )
    return api_success(resposta)


@api_controller.route("/plantao/criar_fila", methods=["GET", "POST"])
@login_required()
def criar_fila():
    if request.method == "GET":
        return api_error("error to access the page", status_code=405)

    plantao_service = PlantaoService()
    resultado = plantao_service.criar_fila_atendimento(request)
    return api_success(resultado)


@api_controller.route("/plantao/fila_atendimento", methods=["GET", "PUT"])
@login_required()
def fila_atendimento():
    plantao_service = PlantaoService()

    if request.method == "PUT":
        resultado = plantao_service.atualizar_status_fila(request)
        return api_success(resultado)

    fila_obj = plantao_service.get_atendimentos_hoje()
    return api_success(fila_obj)


@api_controller.route("/usuarios/buscar_legacy")
@login_required()
def usuarios_buscar_legacy():
    usuario_service = UsuarioService()
    valor_busca = request.args.get("valor_busca", "")
    funcao = request.args.get("funcao", "all")
    status = request.args.get("status", "1")

    usuarios = usuario_service.search_users_by_filters(valor_busca, funcao, status)
    return jsonify({"users": [x.as_dict() for x in usuarios]})


@api_controller.route("/usuarios/api/listar/")
@login_required()
def usuarios_api_listar():
    usuario_service = UsuarioService()

    funcao = request.args.get("funcao")
    status = request.args.get("status")

    usuarios = usuario_service.get_users_by_filters(funcao, status)
    return jsonify({"users": [x.as_dict() for x in usuarios]})


@api_controller.route("/relatorios/buscar_usuarios")
@login_required()
def relatorios_buscar_usuarios():
    relatorio_service = RelatorioService()

    termo = request.args.get("q", type=str)
    usuarios = relatorio_service.buscar_usuarios(termo)
    usuarios_clean = [{"id": usuario.id, "text": usuario.nome} for usuario in usuarios]

    response = current_app.response_class(
        response=json.dumps({"results": usuarios_clean}),
        status=200,
        mimetype="application/json",
    )
    return response


@api_controller.route("/relatorios/buscar_area_direito")
@login_required()
def relatorios_buscar_area_direito():
    relatorio_service = RelatorioService()

    termo = request.args.get("q", type=str)
    areas_direito = relatorio_service.buscar_areas_direito(termo)
    areas_direito_clean = [{"id": area.id, "text": area.nome} for area in areas_direito]

    response = current_app.response_class(
        response=json.dumps({"results": areas_direito_clean}),
        status=200,
        mimetype="application/json",
    )
    return response


@api_controller.route("/assistencia_judiciaria/buscar_assistencias")
@login_required()
def assistencia_buscar_assistencias():
    assistencia_judiciaria_service = AssistenciaJudiciariaService()
    orientacao_id = request.args.get("orientacao_id")
    assistencias = assistencia_judiciaria_service.get_by_orientacao_juridica(
        orientacao_id
    )

    return api_success({"assistencias": [x.as_dict() for x in assistencias]})


@api_controller.route("/assistencia_judiciaria/pega_assistencias_judiciarias")
@login_required()
def pega_assistencias_judiciarias():
    assistencia_judiciaria_service = AssistenciaJudiciariaService()
    assistencias_judiciarias = assistencia_judiciaria_service.get_all()
    return api_success([x.as_dict() for x in assistencias_judiciarias.items])


@api_controller.route("/plantao/fila-atendimento/criar", methods=["GET", "POST"])
@login_required()
def criar_fila_plantao():
    if request.method == "GET":
        return api_error("error to access the page", status_code=405)

    plantao_service = PlantaoService()
    resultado = plantao_service.criar_fila_atendimento(request)

    return api_success(resultado)


@api_controller.route("/plantao/fila-atendimento/hoje", methods=["GET", "PUT"])
@login_required()
def pegar_atendimentos_plantao():
    logger.info("Entering pegar_atendimentos route")
    plantao_service = PlantaoService()

    if request.method == "PUT":
        resultado = plantao_service.atualizar_status_fila(request)
        return api_success(resultado)

    fila_obj = plantao_service.get_atendimentos_hoje()
    return api_success(fila_obj)


@api_controller.route(
    "/orientacao_juridica/associa_orientacao_juridica_ajax/<int:id_orientacao>/<int:id_atendido>",
    methods=["POST"],
)
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.ESTAGIARIO_DIREITO,
        UserRole.PROFESSOR,
    ]
)
def associacao_orientacao_juridica_ajax(id_orientacao, id_atendido):
    orientacao_juridica_service = OrientacaoJuridicaService()

    # Check if orientacao exists
    if not orientacao_juridica_service.validate_orientacao_exists(id_orientacao):
        return api_error("Orientação jurídica não encontrada", status_code=404)

    if id_atendido:
        try:
            success = orientacao_juridica_service.associate_atendido_to_orientacao(
                id_orientacao=id_orientacao,
                id_atendido=id_atendido,
            )

            if success:
                return api_success({"message": "Atendido associado com sucesso!"})
            return api_error("Erro ao associar atendido", status_code=400)

        except Exception as e:
            return api_error(str(e), status_code=400)


@api_controller.route("/usuarios/buscar_ajax", methods=["GET"])
@login_required()
def busca_usuarios_ajax():
    usuario_service = UsuarioService()

    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    funcao = request.args.get("funcao", "all")
    status = request.args.get("status", "1")

    if search or funcao != "all" or status != "1":
        usuarios = usuario_service.search_users_by_filters(
            search,
            funcao,
            status,
            page_params=PageParams(
                page=page, per_page=current_app.config["USUARIOS_POR_PAGINA"]
            ),
        )
    else:
        usuarios = usuario_service.search(
            page_params=PageParams(
                page=page, per_page=current_app.config["USUARIOS_POR_PAGINA"]
            )
        )

    users_data = [x.as_dict() for x in usuarios.items]
    return api_paginated(
        users_data,
        total=usuarios.total,
        page=usuarios.page,
        pages=usuarios.pages,
    )
