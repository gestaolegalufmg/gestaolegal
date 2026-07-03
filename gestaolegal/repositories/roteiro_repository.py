from typing import Any

from sqlalchemy import insert, select
from sqlalchemy import update as sql_update
from sqlalchemy.orm import Session

from gestaolegal.database.tables import documentos_roteiro
from gestaolegal.models.roteiro import Roteiro
from gestaolegal.repositories.repository import BaseRepository
from gestaolegal.utils.dataclass_utils import from_dict


class RoteiroRepository(BaseRepository):
    session: Session

    def __init__(self):
        super().__init__()

    def get_all(self) -> list[Roteiro]:
        stmt = select(documentos_roteiro).order_by(documentos_roteiro.c.area_direito.asc())
        results = self.session.execute(stmt).all()
        return [from_dict(Roteiro, dict(row._mapping)) for row in results]

    def find_by_area(self, area_direito: str) -> Roteiro | None:
        stmt = select(documentos_roteiro).where(
            documentos_roteiro.c.area_direito == area_direito
        )
        result = self.session.execute(stmt).one_or_none()
        return from_dict(Roteiro, dict(result._mapping)) if result else None

    def create(self, data: dict[str, Any]) -> int:
        stmt = insert(documentos_roteiro).values(**data)
        result = self.session.execute(stmt)
        self.session.flush()
        return result.lastrowid

    def update(self, id: int, data: dict[str, Any]) -> None:
        stmt = (
            sql_update(documentos_roteiro)
            .where(documentos_roteiro.c.id == id)
            .values(**data)
        )
        self.session.execute(stmt)
