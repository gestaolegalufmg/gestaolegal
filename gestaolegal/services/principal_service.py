import logging
from typing import Any

from gestaolegal.repositories.atendido_repository import AtendidoRepository
from gestaolegal.repositories.base_repository import PageParams
from gestaolegal.repositories.caso_repository import CasoRepository
from gestaolegal.repositories.orientacao_juridica_repository import (
    OrientacaoJuridicaRepository,
)
from gestaolegal.repositories.user_repository import UserRepository
from gestaolegal.schemas.atendido import AtendidoSchema
from gestaolegal.schemas.caso import CasoSchema
from gestaolegal.schemas.orientacao_juridica import OrientacaoJuridicaSchema

logger = logging.getLogger(__name__)


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


class PrincipalService:
    def __init__(self):
        self.atendido_repo = AtendidoRepository()
        self.usuario_repo = UserRepository()
        self.caso_repo = CasoRepository()
        self.orientacao_repo = OrientacaoJuridicaRepository()

    def busca_geral(
        self,
        busca: str,
        page_assistido_pfisica: int = 1,
        page_assistido_pjuridica: int = 1,
        page_usuario: int = 1,
        page_caso: int = 1,
        per_page_assistido: int = 10,
        per_page_usuario: int = 10,
        per_page_caso: int = 10,
    ) -> dict[str, Any]:
        """Perform general search across all entities."""
        from gestaolegal.repositories.base_repository import PageParams

        assistidos_page_params = PageParams(
            page=page_assistido_pfisica, per_page=per_page_assistido
        )
        assistidos = self.atendido_repo.search_assistidos_pfisica(
            busca, assistidos_page_params
        )

        assistidos_pjuridica_page_params = PageParams(
            page=page_assistido_pjuridica, per_page=per_page_assistido
        )
        assistidos_pjuridica = self.atendido_repo.search_assistidos_pjuridica(
            busca, assistidos_pjuridica_page_params
        )

        usuarios_page_params = PageParams(page=page_usuario, per_page=per_page_usuario)
        usuarios = self.usuario_repo.search_general(busca, usuarios_page_params)

        casos = None
        orientacoes_juridicas = None

        if busca.isdigit():
            caso = self.caso_repo.find_by_id(int(busca))
            if caso:
                casos = SimplePagination([caso], page_caso, per_page_caso, 1)
        elif busca.strip():
            casos_page_params = PageParams(page=page_caso, per_page=per_page_caso)
            casos = self.search_casos_by_atendido_name(busca, casos_page_params)

            orientacoes_page_params = PageParams(page=page_caso, per_page=per_page_caso)
            orientacoes_juridicas = self.search_orientacoes_juridicas_by_atendido_name(
                busca, orientacoes_page_params
            )

        return {
            "assistidos": assistidos,
            "assistidos_pjuridica": assistidos_pjuridica,
            "usuarios": usuarios,
            "casos": casos,
            "orientacoes_juridicas": orientacoes_juridicas,
        }

    def search_casos_by_atendido_name(self, busca: str, page_params: PageParams):
        query = self.caso_repo._create_query()
        query = query.join(AtendidoSchema).join(CasoSchema.clientes)

        query = self.caso_repo._apply_status_filter(query, True)
        query = query.where(AtendidoSchema.nome.ilike(f"%{busca}%"))
        query = query.order_by(CasoSchema.id)

        total = query.count()

        query = query.offset(page_params["page"] - 1).limit(page_params["per_page"])
        result = query.all()

        items = [self.caso_repo._build_model(entity) for entity in result]
        return self.caso_repo._create_paginated_result(items, total, page_params)

    def search_orientacoes_juridicas_by_atendido_name(
        self, busca: str, page_params: PageParams
    ):
        query = self.orientacao_repo._create_query()
        query = query.join(AtendidoSchema).join(AtendidoSchema.orientacoesJuridicas)

        query = self.orientacao_repo._apply_status_filter(query, True)
        query = query.where(AtendidoSchema.nome.ilike(f"%{busca}%"))
        query = query.order_by(OrientacaoJuridicaSchema.id)

        total = query.count()

        query = query.offset(page_params["page"] - 1).limit(page_params["per_page"])
        result = query.all()

        items = [self.orientacao_repo._build_model(entity) for entity in result]
        return self.orientacao_repo._create_paginated_result(items, total, page_params)
