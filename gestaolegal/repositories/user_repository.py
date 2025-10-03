import logging

from sqlalchemy import select

from gestaolegal.common import PageParams
from gestaolegal.database import get_db
from gestaolegal.models.user import User
from gestaolegal.repositories.base_repository import BaseRepository, PaginatedResult
from gestaolegal.repositories.table_definitions import usuarios

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(usuarios, User)

    def search(
        self,
        search_term: str = "",
        role: str = "all",
        status: str = "1",
        page_params: PageParams | None = None,
    ) -> PaginatedResult[User]:
        stmt = select(self.table)

        if status != "all":
            stmt = stmt.where(self.table.c.status == (status == "1"))

        if role != "all":
            stmt = stmt.where(self.table.c.urole == role)

        if search_term:
            stmt = stmt.where(self.table.c.nome.ilike(f"%{search_term}%"))

        count_stmt = select(stmt.alias().c.id.label("id"))
        total = get_db().session.execute(count_stmt).fetchall()
        total_count = len(total)

        if page_params:
            page = page_params.get("page", 1)
            per_page = page_params.get("per_page", 10)
            offset = (page - 1) * per_page
            stmt = stmt.limit(per_page).offset(offset)
        else:
            page = 1
            per_page = total_count

        stmt = stmt.order_by(self.table.c.nome)

        result = get_db().session.execute(stmt)
        rows = result.fetchall()
        items = [self._row_to_model(row) for row in rows]

        return PaginatedResult(
            items=items, total=total_count, page=page, per_page=per_page
        )

