from typing import Any

from sqlalchemy import delete as sql_delete
from sqlalchemy import func, insert, select
from sqlalchemy import update as sql_update
from sqlalchemy.orm import Session

from gestaolegal.common import PaginatedResult
from gestaolegal.database.tables import casos, casos_atendidos
from gestaolegal.models.caso import Caso
from gestaolegal.repositories.repository import (
    BaseRepository,
    CountParams,
    SearchParams,
)
from gestaolegal.utils.dataclass_utils import from_dict


class CasoRepository(BaseRepository):
    session: Session

    def __init__(self):
        super().__init__()

    def find_by_id(self, id: int) -> Caso | None:
        stmt = select(casos).where(casos.c.id == id)
        result = self.session.execute(stmt).one_or_none()
        return from_dict(Caso, dict(result._mapping)) if result else None

    def search(self, params: SearchParams) -> PaginatedResult[Caso]:
        stmt = select(casos, func.count().over().label("total_count"))

        stmt = self._apply_where_clause(stmt, params.get("where"), casos)
        stmt = stmt.order_by(casos.c.data_criacao.desc())
        stmt = self._apply_pagination(stmt, params.get("page_params"))

        results = self.session.execute(stmt).all()
        total = results[0].total_count if results else 0

        items = [from_dict(Caso, dict(row._mapping)) for row in results]
        page_params = params.get("page_params")
        return PaginatedResult(
            items=items,
            total=total,
            page=page_params["page"] if page_params else 1,
            per_page=page_params["per_page"] if page_params else total,
        )

    def find_one(self, params: SearchParams) -> Caso | None:
        stmt = select(casos)
        stmt = self._apply_where_clause(stmt, params.get("where"), casos)
        result = self.session.execute(stmt).one_or_none()
        return from_dict(Caso, dict(result._mapping)) if result else None

    def count(self, params: CountParams) -> int:
        stmt = select(func.count()).select_from(casos)
        stmt = self._apply_where_clause(stmt, params.get("where"), casos)

        result = self.session.execute(stmt).scalar()
        return result or 0

    def create(self, data: dict[str, Any]) -> int:
        stmt = insert(casos).values(**data)
        result = self.session.execute(stmt)
        self.session.flush()
        return result.lastrowid

    def update(self, id: int, data: dict[str, Any]) -> None:
        stmt = sql_update(casos).where(casos.c.id == id).values(**data)
        self.session.execute(stmt)

    def delete(self, id: int) -> bool:
        stmt = sql_update(casos).where(casos.c.id == id).values(status=False)
        result = self.session.execute(stmt)
        return result.rowcount > 0

    def link_atendidos(self, caso_id: int, atendido_ids: list[int]) -> None:
        stmt = sql_delete(casos_atendidos).where(casos_atendidos.c.id_caso == caso_id)
        self.session.execute(stmt)

        for atendido_id in atendido_ids:
            stmt = insert(casos_atendidos).values(
                id_caso=caso_id, id_atendido=atendido_id
            )
            self.session.execute(stmt)

    def get_atendido_ids_by_caso_id(self, caso_id: int) -> list[int]:
        stmt = select(casos_atendidos.c.id_atendido).where(
            casos_atendidos.c.id_caso == caso_id
        )
        results = self.session.execute(stmt).all()
        return [row.id_atendido for row in results]
