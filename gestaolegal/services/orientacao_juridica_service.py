import logging
from typing import Any, Callable, TypeVar

from sqlalchemy.orm import Query

from gestaolegal.models.orientacao_juridica import OrientacaoJuridica
from gestaolegal.schemas.orientacao_juridica import OrientacaoJuridicaSchema
from gestaolegal.services.base_service import BaseService

T = TypeVar("T")

logger = logging.getLogger(__name__)


class OrientacaoJuridicaService(
    BaseService[OrientacaoJuridicaSchema, OrientacaoJuridica]
):
    def __init__(self):
        super().__init__(OrientacaoJuridicaSchema)

    def find_by_id(self, id: int) -> OrientacaoJuridicaSchema | None:
        return (
            self.filter_active(self.session.query(OrientacaoJuridicaSchema))
            .filter(OrientacaoJuridicaSchema.id == id)
            .first()
        )

    def get_by_area_do_direito(
        self, area_do_direito: str, paginator: Callable[..., Any] | None = None
    ) -> list[OrientacaoJuridicaSchema]:
        query = (
            self.filter_active(self.session.query(OrientacaoJuridicaSchema))
            .filter(OrientacaoJuridicaSchema.area_direito == area_do_direito)
            .filter(OrientacaoJuridicaSchema.area_direito.ilike(f"%{area_do_direito}%"))
            .order_by(OrientacaoJuridicaSchema.data_criacao.desc())
        )

        if paginator:
            paginator(query)

        return query.all()

    def get_all(self, paginator: Callable[..., Any] | None = None):
        query = self.filter_active(
            self.session.query(OrientacaoJuridicaSchema)
        ).order_by(OrientacaoJuridicaSchema.data_criacao.desc())

        if paginator:
            return paginator(query)

        return query.all()

    def filter_active(self, query: Query[T]) -> Query[T]:
        return query.filter(OrientacaoJuridicaSchema.status)
