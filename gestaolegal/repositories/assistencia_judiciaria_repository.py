from sqlalchemy import func, insert, select
from sqlalchemy import update as sql_update
from sqlalchemy.orm import Session

from gestaolegal.database.tables import assistencias_judiciarias
from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
from gestaolegal.repositories.pagination_result import PaginatedResult
from gestaolegal.repositories.repository import (
    BaseRepository,
    CountParams,
    SearchParams,
)


class AssistenciaJudiciariaRepository(BaseRepository):
    session: Session

    def __init__(self):
        super().__init__()

    def find_by_id(self, id: int) -> AssistenciaJudiciaria | None:
        stmt = select(assistencias_judiciarias).where(
            assistencias_judiciarias.c.id == id
        )
        result = self.session.execute(stmt).one_or_none()
        return AssistenciaJudiciaria.model_validate(result) if result else None

    def search(self, params: SearchParams) -> PaginatedResult[AssistenciaJudiciaria]:
        stmt = select(
            assistencias_judiciarias, func.count().over().label("total_count")
        )

        stmt = self._apply_where_clause(
            stmt, params.get("where"), assistencias_judiciarias
        )
        stmt = stmt.order_by(assistencias_judiciarias.c.nome)
        stmt = self._apply_pagination(stmt, params.get("page_params"))

        results = self.session.execute(stmt).all()
        total = results[0].total_count if results else 0

        items = [AssistenciaJudiciaria.model_validate(row) for row in results]

        page_params = params.get("page_params")
        return PaginatedResult(
            items=items,
            total=total,
            page=page_params["page"] if page_params else 1,
            per_page=page_params["per_page"] if page_params else total,
        )

    def find_one(self, params: SearchParams) -> AssistenciaJudiciaria | None:
        stmt = select(assistencias_judiciarias)
        stmt = self._apply_where_clause(
            stmt, params.get("where"), assistencias_judiciarias
        )
        result = self.session.execute(stmt).one_or_none()
        return AssistenciaJudiciaria.model_validate(result) if result else None

    def count(self, params: CountParams) -> int:
        stmt = select(func.count()).select_from(assistencias_judiciarias)
        stmt = self._apply_where_clause(
            stmt, params.get("where"), assistencias_judiciarias
        )

        result = self.session.execute(stmt).scalar()
        return result or 0

    def create(self, data: AssistenciaJudiciaria) -> int:
        assistencia_dict = data.model_dump(
            exclude={"id", "endereco", "orientacoes_juridicas"}
        )
        stmt = insert(assistencias_judiciarias).values(**assistencia_dict)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.lastrowid

    def update(self, id: int, data: AssistenciaJudiciaria) -> None:
        assistencia_dict = data.model_dump(
            exclude={"id", "endereco", "orientacoes_juridicas"}
        )
        stmt = (
            sql_update(assistencias_judiciarias)
            .where(assistencias_judiciarias.c.id == id)
            .values(**assistencia_dict)
        )
        self.session.execute(stmt)
        self.session.commit()

    def delete(self, id: int) -> bool:
        stmt = (
            sql_update(assistencias_judiciarias)
            .where(assistencias_judiciarias.c.id == id)
            .values(status=0)
        )
        result = self.session.execute(stmt)
        self.session.commit()

        return result.rowcount > 0
