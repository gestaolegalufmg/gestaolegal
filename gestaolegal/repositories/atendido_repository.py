import logging

from sqlalchemy import select

from gestaolegal.common import PageParams
from gestaolegal.database import get_db
from gestaolegal.models.atendido import Atendido
from gestaolegal.repositories.base_repository import BaseRepository, PaginatedResult
from gestaolegal.repositories.table_definitions import atendidos

logger = logging.getLogger(__name__)


class AtendidoRepository(BaseRepository[Atendido]):
    def __init__(self):
        super().__init__(atendidos, Atendido)

    def search(
        self,
        search_term: str = "",
        search_type: str | None = None,
        page_params: PageParams | None = None,
        show_inactive: bool = False,
    ) -> PaginatedResult[Atendido]:
        stmt = select(self.table)

        if not show_inactive:
            stmt = stmt.where(self.table.c.status == 1)

        if search_term:
            if search_type == "nome":
                stmt = stmt.where(self.table.c.nome.ilike(f"%{search_term}%"))
            elif search_type == "cpf":
                stmt = stmt.where(self.table.c.cpf.like(f"%{search_term}%"))
            elif search_type == "cnpj":
                stmt = stmt.where(self.table.c.cnpj.like(f"%{search_term}%"))
            else:
                stmt = stmt.where(
                    (self.table.c.nome.ilike(f"%{search_term}%"))
                    | (self.table.c.cpf.like(f"%{search_term}%"))
                    | (self.table.c.cnpj.like(f"%{search_term}%"))
                )

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

    def soft_delete(self, id: int) -> bool:
        from sqlalchemy import update

        stmt = update(self.table).where(self.table.c.id == id).values(status=0)
        result = get_db().session.execute(stmt)
        get_db().session.commit()
        return result.rowcount > 0

