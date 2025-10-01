from gestaolegal.models.atendido import Atendido
from gestaolegal.repositories.base_repository import (
    BaseRepository,
    PageParams,
    PaginatedResult,
    WhereConditions,
)
from gestaolegal.schemas.atendido import AtendidoSchema
import logging

logger = logging.getLogger(__name__)

class AtendidoRepository(BaseRepository[AtendidoSchema, Atendido]):
    def __init__(self):
        super().__init__(AtendidoSchema, Atendido)

    def search(
        self,
        search_term: str = "",
        search_type: str | None = None,
        page_params: PageParams | None = None,
        show_inactive: bool = False,
    ):
        where_conditions: WhereConditions = []
        if search_term:
            where_conditions.append(
                {
                    "or": [
                        ("nome", "ilike", f"%{search_term}%"),
                        ("cpf", "ilike", f"%{search_term}%"),
                        ("cnpj", "ilike", f"%{search_term}%"),
                    ]
                }
            )

        if search_type == "assistidos":
            where_conditions.append(("id", "is_not_null", None))

        elif search_type == "atendidos":
            where_conditions.append(("id", "is_null", None))

        return self.get(
            page_params=page_params,
            where_conditions=where_conditions,
            order_by=["nome"],
            active_only=not show_inactive,
        )

    def search_assistidos_pfisica(
        self, busca: str, page_params: PageParams | None = None
    ):
        where_conditions: WhereConditions = [
            {
                "or": [
                    ("nome", "ilike", f"%{busca}%"),
                    ("cpf", "contains", busca),
                ]
            }
        ]

        return self.get(
            page_params=page_params,
            where_conditions=where_conditions,
            order_by=["nome"],
        )

    def search_assistidos_pjuridica(
        self, busca: str, page_params: PageParams | None = None
    ):
        where_conditions: WhereConditions = [
            {
                "or": [
                    ("nome", "contains", busca),
                    ("cpf", "contains", busca),
                ]
            }
        ]

        return self.get(
            page_params=page_params,
            where_conditions=where_conditions,
            order_by=["nome"],
        )

    def _create_paginated_result(self, items, total, page_params):
        return PaginatedResult(
            items, total, page_params["page"] or 1, page_params["per_page"] or total
        )
