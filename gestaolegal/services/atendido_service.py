from typing import Any, Callable, TypeVar

from sqlalchemy.orm import Query, Session, scoped_session

from gestaolegal.models.atendido import Atendido
from gestaolegal.plantao.models import Assistido, AssistidoPessoaJuridica

T = TypeVar("T")


class AtendidoService:
    session: Session | scoped_session[Session]

    def __init__(self, db_session: Session | scoped_session[Session]):
        self.session = db_session

    def find_by_id(self, id: int) -> Atendido | None:
        return (
            self.filter_active(self.session.query(Atendido))
            .filter(Atendido.id == id)
            .first()
        )

    def find_by_email(self, email: str) -> Atendido | None:
        return (
            self.filter_active(self.session.query(Atendido))
            .filter(Atendido.email == email)
            .first()
        )

    def find_atendido_assistido_by_id(
        self, id_atendido: int
    ) -> tuple[Atendido, Assistido] | None:
        result = (
            self.filter_active(self.session.query(Atendido, Assistido))
            .where(Atendido.id == id_atendido)
            .first()
        )

        return result.tuple() if result else None

    def get_atendido_with_assistido_data(
        self, atendido_id: int
    ) -> tuple[Atendido, Assistido | None, AssistidoPessoaJuridica | None] | None:
        result = (
            self.filter_active(
                self.session.query(Atendido, Assistido, AssistidoPessoaJuridica)
            )
            .outerjoin(Assistido, onclause=Assistido.id_atendido == Atendido.id)
            .outerjoin(
                AssistidoPessoaJuridica,
                onclause=AssistidoPessoaJuridica.id_assistido == Assistido.id,
            )
            .filter(Atendido.id == atendido_id)
            .first()
        )

        if not result:
            return None

        return result.tuple()

    def get_all(self, paginator: Callable[..., Any] | None = None):
        query = self.filter_active(self.session.query(Atendido)).order_by(Atendido.nome)

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
            self.session.query(Atendido)
            .filter(Atendido.nome.ilike(f"%{string}%"))
            .order_by(Atendido.nome)
        )

        if paginator:
            return paginator(result)

        return result.all()

    def filter_active(self, query: Query[T]) -> Query[T]:
        return query.filter(Atendido.status == True)
