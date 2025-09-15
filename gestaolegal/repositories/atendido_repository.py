from gestaolegal.models.atendido import Atendido
from gestaolegal.repositories.base_repository import (
    BaseRepository,
    ConditionList,
    PageParams,
    PaginatedResult,
)
from gestaolegal.schemas.assistido import AssistidoSchema
from gestaolegal.schemas.assistido_pessoa_juridica import AssistidoPessoaJuridicaSchema
from gestaolegal.schemas.atendido import AtendidoSchema


class AtendidoRepository(BaseRepository[AtendidoSchema, Atendido]):
    def __init__(self):
        super().__init__(AtendidoSchema, Atendido)

    def search(
        self,
        search_term: str = "",
        search_type: str | None = None,
        page_params: PageParams | None = None,
    ):
        where_conditions: ConditionList = []
        if search_term:
            where_conditions.extend([
                ("nome", "ilike", f"%{search_term}%"),
                ("cpf", "ilike", f"%{search_term}%"),
                ("cnpj", "ilike", f"%{search_term}%")
            ])

        if search_type == "assistidos":
            where_conditions.append(("id", "is_not_null", None))

        elif search_type == "atendidos":
            where_conditions.append(("id", "is_null", None))

        return self.get(
            page_params=page_params,
            where_conditions=where_conditions,
            order_by=["nome"],
        )

    def search_assistidos_pfisica(
        self, busca: str, page_params: PageParams | None = None
    ):
        where_conditions: ConditionList = {
            "or": [
                ("nome", "ilike", f"%{busca}%"),
                ("cpf", "contains", busca),
            ]
        }

        return self.get(
            page_params=page_params,
            where_conditions=where_conditions,
            order_by=["nome"],
        )

    def search_assistidos_pjuridica(
        self, busca: str, page_params: PageParams | None = None
    ):
        where_conditions: ConditionList = {
            "or": [
                ("nome", "contains", busca),
                ("cpf", "contains", busca),
            ]
        }

        return self.get(
            page_params=page_params,
            where_conditions=where_conditions,
            order_by=["nome"],
        )

    def _create_paginated_result(self, items, total, page_params):
        return PaginatedResult(
            items, total, page_params["page"] or 1, page_params["per_page"] or total
        )
