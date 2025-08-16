from typing import Any, Callable, TypeVar

from sqlalchemy.orm import Query, Session, scoped_session

from gestaolegal.models.orientacao_juridica import OrientacaoJuridica

T = TypeVar("T")


class OrientacaoJuridicaService:
    session: Session | scoped_session[Session]

    def __init__(self, db_session: Session | scoped_session[Session]):
        self.session = db_session

    def find_by_id(self, id: int) -> OrientacaoJuridica | None:
        return (
            self.filter_active(self.session.query(OrientacaoJuridica))
            .filter(OrientacaoJuridica.id == id)
            .first()
        )

    def get_by_area_do_direito(
        self, area_do_direito: str, paginator: Callable[..., Any] | None = None
    ) -> list[OrientacaoJuridica]:
        query = (
            self.filter_active(self.session.query(OrientacaoJuridica))
            .filter(OrientacaoJuridica.area_direito == area_do_direito)
            .filter(OrientacaoJuridica.area_direito.ilike(f"%{area_do_direito}%"))
            .order_by(OrientacaoJuridica.data_criacao.desc())
        )

        if paginator:
            paginator(query)

        return query.all()

    def get_all(self, paginator: Callable[..., Any] | None = None):
        query = self.filter_active(self.session.query(OrientacaoJuridica)).order_by(
            OrientacaoJuridica.data_criacao.desc()
        )

        if paginator:
            return paginator(query)

        return query.all()

    def filter_active(self, query: Query[T]) -> Query[T]:
        return query.filter(OrientacaoJuridica.status == True)
