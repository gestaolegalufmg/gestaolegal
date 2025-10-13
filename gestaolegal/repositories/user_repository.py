import logging
from typing import Any

from sqlalchemy import func, insert, select
from sqlalchemy import update as sql_update
from sqlalchemy.orm import Session

from gestaolegal.common import PaginatedResult
from gestaolegal.database.tables import usuarios
from gestaolegal.models.user import User
from gestaolegal.repositories.repository import (
    BaseRepository,
    CountParams,
    GetParams,
    SearchParams,
)
from gestaolegal.utils.dataclass_utils import from_dict

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    session: Session

    def __init__(self):
        super().__init__()

    def find_by_id(self, id: int) -> User | None:
        stmt = select(usuarios).where(usuarios.c.id == id)
        result = self.session.execute(stmt).one_or_none()
        return from_dict(User, dict(result._mapping)) if result else None

    def find_by_email(self, email: str) -> User | None:
        stmt = select(usuarios).where(usuarios.c.email == email)
        result = self.session.execute(stmt).one_or_none()
        return from_dict(User, dict(result._mapping)) if result else None

    def get(self, params: GetParams) -> list[User]:
        stmt = select(usuarios)
        stmt = self._apply_where_clause(stmt, params.get("where"), usuarios)
        result = self.session.execute(stmt).all()
        return [from_dict(User, dict(row._mapping)) for row in result]

    def get_by_ids(self, ids: list[int]) -> list[User]:
        if not ids:
            return []
        stmt = select(usuarios).where(usuarios.c.id.in_(ids))
        results = self.session.execute(stmt).all()
        return [from_dict(User, dict(row._mapping)) for row in results]

    def search(self, params: SearchParams) -> PaginatedResult[User]:
        stmt = select(usuarios, func.count().over().label("total_count"))

        stmt = self._apply_where_clause(stmt, params.get("where"), usuarios)
        stmt = stmt.order_by(usuarios.c.nome)
        stmt = self._apply_pagination(stmt, params.get("page_params"))

        results = self.session.execute(stmt).all()
        total = results[0].total_count if results else 0

        items = [from_dict(User, dict(row._mapping)) for row in results]
        page_params = params.get("page_params")

        return PaginatedResult(
            items=items,
            total=total,
            page=page_params["page"] if page_params else 1,
            per_page=page_params["per_page"] if page_params else total,
        )

    def find_one(self, params: SearchParams) -> User | None:
        stmt = select(usuarios)
        stmt = self._apply_where_clause(stmt, params.get("where"), usuarios)
        result = self.session.execute(stmt).one_or_none()
        return from_dict(User, dict(result._mapping)) if result else None

    def count(self, params: CountParams) -> int:
        stmt = select(func.count()).select_from(usuarios)
        stmt = self._apply_where_clause(stmt, params.get("where"), usuarios)

        result = self.session.execute(stmt).scalar()
        return result or 0

    def create(self, data: dict[str, Any]) -> int:
        stmt = insert(usuarios).values(**data)
        result = self.session.execute(stmt)
        self.session.flush()
        return result.lastrowid

    def update(self, id: int, data: dict[str, Any]) -> None:
        stmt = sql_update(usuarios).where(usuarios.c.id == id).values(**data)
        self.session.execute(stmt)

    def delete(self, id: int) -> bool:
        stmt = sql_update(usuarios).where(usuarios.c.id == id).values(status=False)
        result = self.session.execute(stmt)
        return result.rowcount > 0
