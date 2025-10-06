import logging

from sqlalchemy import func, insert, select
from sqlalchemy import update as sql_update
from sqlalchemy.orm import Session

from gestaolegal.database.tables import usuarios
from gestaolegal.models.user import User
from gestaolegal.repositories.pagination_result import PaginatedResult
from gestaolegal.repositories.repository import BaseRepository, CountParams, GetParams

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    session: Session

    def __init__(self):
        super().__init__()

    def find_by_id(self, id: int) -> User | None:
        stmt = select(usuarios).where(usuarios.c.id == id)
        result = self.session.execute(stmt).one_or_none()
        return User.model_validate(result) if result else None

    def find_by_email(self, email: str) -> User | None:
        stmt = select(usuarios).where(usuarios.c.email == email)
        result = self.session.execute(stmt).one_or_none()
        return User.model_validate(result) if result else None

    def search(self, params: GetParams) -> PaginatedResult[User]:
        stmt = select(usuarios, func.count().over().label("total_count"))

        stmt = self._apply_where_clause(stmt, params.get("where"), usuarios)
        stmt = stmt.order_by(usuarios.c.nome)
        stmt = self._apply_pagination(stmt, params.get("page_params"))

        results = self.session.execute(stmt).all()
        total = results[0].total_count if results else 0

        items = [User.model_validate(row) for row in results]
        page_params = params.get("page_params")

        return PaginatedResult(
            items=items,
            total=total,
            page=page_params["page"] if page_params else 1,
            per_page=page_params["per_page"] if page_params else total,
        )

    def find_one(self, params: GetParams) -> User | None:
        stmt = select(usuarios)
        stmt = self._apply_where_clause(stmt, params.get("where"), usuarios)
        result = self.session.execute(stmt).one_or_none()
        return User.model_validate(result) if result else None

    def count(self, params: CountParams) -> int:
        stmt = select(func.count()).select_from(usuarios)
        stmt = self._apply_where_clause(stmt, params.get("where"), usuarios)

        result = self.session.execute(stmt).scalar()
        return result or 0

    def create(self, data: User) -> int:
        user_dict = data.model_dump(exclude={"id", "endereco"})
        stmt = insert(usuarios).values(**user_dict)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.lastrowid

    def update(self, id: int, data: User) -> None:
        user_dict = data.model_dump(exclude={"id", "endereco"})
        stmt = sql_update(usuarios).where(usuarios.c.id == id).values(**user_dict)
        self.session.execute(stmt)
        self.session.commit()

    def delete(self, id: int) -> bool:
        stmt = sql_update(usuarios).where(usuarios.c.id == id).values(status=0)
        result = self.session.execute(stmt)
        self.session.commit()

        return result.rowcount > 0
