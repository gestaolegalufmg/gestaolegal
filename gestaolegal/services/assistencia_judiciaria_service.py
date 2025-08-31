from typing import Any, Callable, TypeVar

from sqlalchemy.orm import Query, Session, scoped_session

from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
from gestaolegal.plantao.models import AssistidoPessoaJuridica
from gestaolegal.plantao.views_util import filtro_busca_assistencia_judiciaria
from gestaolegal.schemas.assistido import AssistidoSchema as Assistido

T = TypeVar("T")


class AssistenciaJudiciariaService:
    session: Session | scoped_session[Session]

    def __init__(self, db_session: Session | scoped_session[Session]):
        self.session = db_session

    def find_by_id(self, id: int) -> AssistenciaJudiciaria | None:
        return (
            self.filter_active(self.session.query(AssistenciaJudiciaria))
            .filter(AssistenciaJudiciaria.id == id)
            .first()
        )

    def get_by_area_do_direito(
        self, area_do_direito: str
    ) -> AssistenciaJudiciaria | None:
        return (
            self.filter_active(self.session.query(AssistenciaJudiciaria))
            .filter(AssistenciaJudiciaria.area_direito == area_do_direito)
            .first()
        )

    def get_by_areas_atendida(
        self,
        area_atendida: str,
        nome: str | None = None,
        paginator: Callable[..., Any] | None = None,
    ):
        query = self.session.query(AssistenciaJudiciaria)

        if nome:
            query = query.filter(AssistenciaJudiciaria.nome == nome)

        if area_atendida == filtro_busca_assistencia_judiciaria["TODAS"][0]:
            query = self.filter_active(query).order_by(AssistenciaJudiciaria.nome.asc())

        query = (
            self.filter_active(query)
            .filter((AssistenciaJudiciaria.areas_atendidas.contains(area_atendida)))
            .order_by(AssistenciaJudiciaria.nome.asc())
        )

        if paginator:
            return paginator(query)

        return query.all()

    def get_by_name(self, name: str, paginator: Callable[..., Any] | None = None):
        query = (
            self.filter_active(self.session.query(AssistenciaJudiciaria))
            .filter(AssistenciaJudiciaria.nome == name)
            .order_by(AssistenciaJudiciaria.nome)
        )

        if paginator:
            return paginator(query)

        return query.first()

    def find_atendido_assistido_by_id(
        self, id_atendido: int
    ) -> tuple[AssistenciaJudiciaria, Assistido] | None:
        result = (
            self.filter_active(self.session.query(AssistenciaJudiciaria, Assistido))
            .where(AssistenciaJudiciaria.id == id_atendido)
            .first()
        )

        return result.tuple() if result else None

    def get_atendido_with_assistido_data(
        self, atendido_id: int
    ) -> (
        tuple[AssistenciaJudiciaria, Assistido | None, AssistidoPessoaJuridica | None]
        | None
    ):
        result = (
            self.filter_active(
                self.session.query(
                    AssistenciaJudiciaria, Assistido, AssistidoPessoaJuridica
                )
            )
            .outerjoin(
                Assistido, onclause=Assistido.id_atendido == AssistenciaJudiciaria.id
            )
            .outerjoin(
                AssistidoPessoaJuridica,
                onclause=AssistidoPessoaJuridica.id_assistido == Assistido.id,
            )
            .filter(AssistenciaJudiciaria.id == atendido_id)
            .first()
        )

        if not result:
            return None

        return result.tuple()

    def get_all(self, paginator: Callable[..., Any] | None = None):
        query = self.filter_active(self.session.query(AssistenciaJudiciaria)).order_by(
            AssistenciaJudiciaria.nome
        )

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
            self.session.query(AssistenciaJudiciaria)
            .filter(AssistenciaJudiciaria.nome.ilike(f"%{string}%"))
            .order_by(AssistenciaJudiciaria.nome)
        )

        if paginator:
            return paginator(result)

        return result.all()

    def filter_active(self, query: Query[T]) -> Query[T]:
        return query.filter(AssistenciaJudiciaria.status == True)
