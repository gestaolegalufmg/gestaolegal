from typing import Any

from sqlalchemy import func, insert, select
from sqlalchemy import update as sql_update
from sqlalchemy.orm import Session

from gestaolegal.database.tables import lembretes
from gestaolegal.models.lembrete import Lembrete
from gestaolegal.repositories.repository import BaseRepository
from gestaolegal.utils.dataclass_utils import from_dict


class LembreteRepository(BaseRepository):
    session: Session

    def __init__(self):
        super().__init__()

    def find_by_id(self, id: int) -> Lembrete | None:
        stmt = select(lembretes).where(lembretes.c.id == id)
        result = self.session.execute(stmt).one_or_none()
        return from_dict(Lembrete, dict(result._mapping)) if result else None

    def get_by_caso(self, caso_id: int, include_inactive: bool = False) -> list[Lembrete]:
        stmt = select(lembretes).where(lembretes.c.id_caso == caso_id)
        if not include_inactive:
            stmt = stmt.where(lembretes.c.status == True)  # noqa: E712
        stmt = stmt.order_by(lembretes.c.data_criacao.desc())
        results = self.session.execute(stmt).all()
        return [from_dict(Lembrete, dict(row._mapping)) for row in results]

    def count_by_caso(self, caso_id: int) -> int:
        stmt = select(func.count()).select_from(lembretes).where(
            lembretes.c.id_caso == caso_id
        )
        return self.session.execute(stmt).scalar() or 0

    def create(self, data: dict[str, Any]) -> int:
        stmt = insert(lembretes).values(**data)
        result = self.session.execute(stmt)
        self.session.flush()
        return result.lastrowid

    def update(self, id: int, data: dict[str, Any]) -> None:
        stmt = sql_update(lembretes).where(lembretes.c.id == id).values(**data)
        self.session.execute(stmt)

    def delete(self, id: int) -> None:
        stmt = sql_update(lembretes).where(lembretes.c.id == id).values(status=False)
        self.session.execute(stmt)
