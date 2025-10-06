import logging

from flask import Blueprint, request

from gestaolegal.services.assistencia_judiciaria_service import (
    AssistenciaJudiciariaService,
)
from gestaolegal.services.atendido_service import AtendidoService
from gestaolegal.services.caso_service import CasoService
from gestaolegal.services.orientacao_juridica_service import OrientacaoJuridicaService
from gestaolegal.services.usuario_service import UsuarioService
from gestaolegal.utils.api_decorators import api_auth_required

logger = logging.getLogger(__name__)

search_controller = Blueprint("search_api", __name__)


@search_controller.route("/", methods=["GET"])
@api_auth_required
def global_search():
    logger.info(f"Global search query: {request.args.get('q')}")
    query = request.args.get("q", default="", type=str)
    limit = request.args.get("limit", default=5, type=int)

    if not query or len(query.strip()) < 2:
        return {
            "results": {
                "atendidos": [],
                "casos": [],
                "orientacoes_juridicas": [],
                "assistencias_judiciarias": [],
                "usuarios": [],
            }
        }

    atendido_service = AtendidoService()
    caso_service = CasoService()
    orientacao_service = OrientacaoJuridicaService()
    assistencia_service = AssistenciaJudiciariaService()
    usuario_service = UsuarioService()

    from gestaolegal.common import PageParams

    page_params = PageParams(page=1, per_page=limit)

    atendidos_result = atendido_service.search(
        search=query, page_params=page_params, tipo_busca="todos", show_inactive=False
    )

    casos_result = caso_service.search(
        search=query, page_params=page_params, show_inactive=False
    )

    orientacoes_result = orientacao_service.search(
        search=query, page_params=page_params, show_inactive=False
    )

    assistencias_result = assistencia_service.search(
        search=query, page_params=page_params, show_inactive=False
    )

    usuarios_result = usuario_service.search(
        search=query, page_params=page_params, show_inactive=False
    )

    return {
        "query": query,
        "results": {
            "atendidos": {
                "items": [
                    item if isinstance(item, dict) else item.model_dump()
                    for item in atendidos_result.items
                ],
                "total": atendidos_result.total,
            },
            "casos": {
                "items": [item.model_dump() for item in casos_result.items],
                "total": casos_result.total,
            },
            "orientacoes_juridicas": {
                "items": [item.model_dump() for item in orientacoes_result.items],
                "total": orientacoes_result.total,
            },
            "assistencias_judiciarias": {
                "items": [item.model_dump() for item in assistencias_result.items],
                "total": assistencias_result.total,
            },
            "usuarios": {
                "items": [item.model_dump() for item in usuarios_result.items],
                "total": usuarios_result.total,
            },
        },
    }
