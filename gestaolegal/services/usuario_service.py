from typing import Any, Callable, TypeVar

from sqlalchemy.orm import Query, Session, scoped_session

from gestaolegal.usuario.models import Usuario

T = TypeVar("T")


class UsuarioService:
    session: Session | scoped_session[Session]

    def __init__(self, db_session: Session | scoped_session[Session]):
        self.session = db_session

    def find_by_id(self, id: int) -> Usuario | None:
        return (
            self.filter_active(self.session.query(Usuario))
            .filter(Usuario.id == id)
            .first()
        )

    def find_by_email(self, email: str) -> Usuario | None:
        return (
            self.filter_active(self.session.query(Usuario))
            .filter(Usuario.email == email)
            .first()
        )

    def get_all(self, paginator: Callable[..., Any] | None = None):
        query = self.filter_active(self.session.query(Usuario)).order_by(Usuario.nome)

        if paginator:
            return paginator(query)

        return query.all()

    def search_by_str(self, string: str, paginator: Callable[..., Any] | None = None):
        result = (
            self.session.query(Usuario)
            .filter(Usuario.nome.ilike(f"%{string}%"))
            .order_by(Usuario.nome)
        )

        if paginator:
            return paginator(result)

        return result.all()

    def filter_active(self, query: Query[T]) -> Query[T]:
        return query.filter(Usuario.status == True)
