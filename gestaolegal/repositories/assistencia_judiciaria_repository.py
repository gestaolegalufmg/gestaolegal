from typing import Any

from gestaolegal.common.constants import assistencia_jud_areas_atendidas
from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
from gestaolegal.repositories.base_repository import (
    BaseRepository,
    PageParams,
    WhereConditions,
)
from gestaolegal.schemas.assistencia_judiciaria import AssistenciaJudiciariaSchema
from gestaolegal.schemas.assistido import AssistidoSchema as Assistido
from gestaolegal.schemas.assistido_pessoa_juridica import (
    AssistidoPessoaJuridicaSchema as AssistidoPessoaJuridica,
)

# Filter options for legal assistance
filtro_busca_assistencia_judiciaria = assistencia_jud_areas_atendidas.copy()
filtro_busca_assistencia_judiciaria["TODAS"] = ("todas", "Todas")


class AssistenciaJudiciariaRepository(
    BaseRepository[AssistenciaJudiciariaSchema, AssistenciaJudiciaria]
):
    def __init__(self):
        super().__init__(AssistenciaJudiciariaSchema, AssistenciaJudiciaria)

    def get_by_area_do_direito(self, area_do_direito: str):
        result = self.get(where_conditions=[("area_direito", "eq", area_do_direito)])
        return result.items

    def get_by_areas_atendida(
        self,
        area_atendida: str,
        nome: str | None = None,
        page_params: PageParams | None = None,
    ):
        where_conditions: WhereConditions = [
            ("areas_atendidas", "contains", area_atendida)
        ]
        if nome:
            where_conditions.append(("nome", "eq", nome))
        if area_atendida == filtro_busca_assistencia_judiciaria["TODAS"][0]:
            where_conditions.append(("status", "eq", True))

        return self.get(
            where_conditions=where_conditions,
            order_by=["nome"],
            page_params=page_params,
        )

    def get_by_nome(self, nome: str):
        result = self.get(where_conditions=[("nome", "eq", nome)])
        return result.items

    def find_atendido_assistido_by_id(
        self, id_atendido: int
    ) -> tuple[AssistenciaJudiciariaSchema, Assistido] | None:
        result = (
            self.session.query(AssistenciaJudiciariaSchema, Assistido)
            .outerjoin(
                Assistido,
                onclause=Assistido.id_atendido == AssistenciaJudiciariaSchema.id,
            )
            .filter(AssistenciaJudiciariaSchema.status)
            .filter(AssistenciaJudiciariaSchema.id == id_atendido)
            .first()
        )
        return result if result else None

    def get_atendido_with_assistido_data(
        self, atendido_id: int
    ) -> (
        tuple[
            AssistenciaJudiciariaSchema,
            Assistido | None,
            AssistidoPessoaJuridica | None,
        ]
        | None
    ):
        result = (
            self.session.query(
                AssistenciaJudiciariaSchema, Assistido, AssistidoPessoaJuridica
            )
            .outerjoin(
                Assistido,
                onclause=Assistido.id_atendido == AssistenciaJudiciariaSchema.id,
            )
            .outerjoin(
                AssistidoPessoaJuridica,
                onclause=AssistidoPessoaJuridica.id_assistido == Assistido.id,
            )
            .filter(AssistenciaJudiciariaSchema.status)
            .filter(AssistenciaJudiciariaSchema.id == atendido_id)
            .first()
        )
        return result if result else None

    def get_all_with_pagination(
        self, page_params: PageParams | None = None
    ) -> list[AssistenciaJudiciariaSchema] | Any:
        return self.get(order_by=["nome"], page_params=page_params)

    def search_by_string(
        self, search_string: str, page_params: PageParams | None = None
    ) -> list[AssistenciaJudiciariaSchema] | Any:
        return self.get(
            where_conditions=[("nome", "ilike", f"%{search_string}%")],
            order_by=["nome"],
            page_params=page_params,
        )
