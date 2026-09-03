from typing import Any

from sqlalchemy import func, insert, select
from sqlalchemy.orm import Session

from gestaolegal.common import PaginatedResult
from gestaolegal.database.tables import historicos
from gestaolegal.models.historico import Historico
from gestaolegal.repositories.repository import BaseRepository, SearchParams
from gestaolegal.utils.dataclass_utils import from_dict


class HistoricoRepository(BaseRepository):
    session: Session

    def __init__(self):
        super().__init__()

    def create(self, data: dict[str, Any]) -> int:
        stmt = insert(historicos).values(**data)
        result = self.session.execute(stmt)
        self.session.flush()
        return result.lastrowid

    def get_by_caso(self, caso_id: int, params: SearchParams) -> PaginatedResult[Historico]:
        stmt = select(historicos, func.count().over().label("total_count")).where(
            historicos.c.id_caso == caso_id
        )
        stmt = stmt.order_by(historicos.c.data.desc())
        stmt = self._apply_pagination(stmt, params.get("page_params"))

        results = self.session.execute(stmt).all()
        total = results[0].total_count if results else 0
        items = [from_dict(Historico, dict(row._mapping)) for row in results]

        page_params = params.get("page_params")
        return PaginatedResult(
            items=items,
            total=total,
            page=page_params["page"] if page_params else 1,
            per_page=page_params["per_page"] if page_params else total,
        )
