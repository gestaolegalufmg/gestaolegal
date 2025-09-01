from typing import Any, Callable, TypeVar

from sqlalchemy.orm import Query

from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
from gestaolegal.schemas.assistencia_judiciaria import AssistenciaJudiciariaSchema
from gestaolegal.schemas.assistido import AssistidoSchema as Assistido
from gestaolegal.schemas.assistido_pessoa_juridica import (
    AssistidoPessoaJuridicaSchema as AssistidoPessoaJuridica,
)
from gestaolegal.services.base_service import BaseService
from gestaolegal.utils.plantao_utils import filtro_busca_assistencia_judiciaria

T = TypeVar("T")


class AssistenciaJudiciariaService(
    BaseService[AssistenciaJudiciariaSchema, AssistenciaJudiciaria]
):
    def __init__(self):
        super().__init__(AssistenciaJudiciariaSchema)

    def find_by_id(self, id: int) -> AssistenciaJudiciariaSchema | None:
        return (
            self.filter_active(self.session.query(AssistenciaJudiciariaSchema))
            .filter(AssistenciaJudiciariaSchema.id == id)
            .first()
        )

    def get_by_area_do_direito(
        self, area_do_direito: str
    ) -> AssistenciaJudiciariaSchema | None:
        return (
            self.filter_active(self.session.query(AssistenciaJudiciariaSchema))
            .filter(AssistenciaJudiciariaSchema.area_direito == area_do_direito)
            .first()
        )

    def get_by_areas_atendida(
        self,
        area_atendida: str,
        nome: str | None = None,
        paginator: Callable[..., Any] | None = None,
    ):
        query = self.session.query(AssistenciaJudiciariaSchema)

        if nome:
            query = query.filter(AssistenciaJudiciariaSchema.nome == nome)

        if area_atendida == filtro_busca_assistencia_judiciaria["TODAS"][0]:
            query = self.filter_active(query).order_by(
                AssistenciaJudiciariaSchema.nome.asc()
            )

        query = (
            self.filter_active(query)
            .filter(
                (AssistenciaJudiciariaSchema.areas_atendidas.contains(area_atendida))
            )
            .order_by(AssistenciaJudiciariaSchema.nome.asc())
        )

        if paginator:
            return paginator(query)

        return query.all()

    def get_by_name(self, name: str, paginator: Callable[..., Any] | None = None):
        query = (
            self.filter_active(self.session.query(AssistenciaJudiciariaSchema))
            .filter(AssistenciaJudiciariaSchema.nome == name)
            .order_by(AssistenciaJudiciariaSchema.nome)
        )

        if paginator:
            return paginator(query)

        return query.first()

    def find_atendido_assistido_by_id(
        self, id_atendido: int
    ) -> tuple[AssistenciaJudiciariaSchema, Assistido] | None:
        result = (
            self.filter_active(
                self.session.query(AssistenciaJudiciariaSchema, Assistido)
            )
            .where(AssistenciaJudiciariaSchema.id == id_atendido)
            .first()
        )

        return result.tuple() if result else None

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
            self.filter_active(
                self.session.query(
                    AssistenciaJudiciariaSchema, Assistido, AssistidoPessoaJuridica
                )
            )
            .outerjoin(
                Assistido,
                onclause=Assistido.id_atendido == AssistenciaJudiciariaSchema.id,
            )
            .outerjoin(
                AssistidoPessoaJuridica,
                onclause=AssistidoPessoaJuridica.id_assistido == Assistido.id,
            )
            .filter(AssistenciaJudiciariaSchema.id == atendido_id)
            .first()
        )

        if not result:
            return None

        return result.tuple()

    def get_all(self, paginator: Callable[..., Any] | None = None):
        query = self.filter_active(
            self.session.query(AssistenciaJudiciariaSchema)
        ).order_by(AssistenciaJudiciariaSchema.nome)

        if paginator:
            return paginator(query)

        return query.all()

    def get_assistidos_by_id_atendido(self, atendido_ids: list[int]) -> list[Assistido]:
        return (
            self.filter_active(self.session.query(Assistido))
            .where(Assistido.id_atendido.in_(atendido_ids))
            .all()
        )

    def search_by_str(self, string: str, paginator: Callable[..., Any] | None = None):
        result = (
            self.session.query(AssistenciaJudiciariaSchema)
            .filter(AssistenciaJudiciariaSchema.nome.ilike(f"%{string}%"))
            .order_by(AssistenciaJudiciariaSchema.nome)
        )

        if paginator:
            return paginator(result)

        return result.all()

    def filter_active(self, query: Query[T]) -> Query[T]:
        return query.filter(AssistenciaJudiciariaSchema.status == True)
