import logging

from sqlalchemy import select

from gestaolegal.common import PageParams
from gestaolegal.database import get_db
from gestaolegal.models.orientacao_juridica import OrientacaoJuridica
from gestaolegal.repositories.base_repository import BaseRepository, PaginatedResult
from gestaolegal.repositories.table_definitions import orientacao_juridica

logger = logging.getLogger(__name__)


class OrientacaoJuridicaRepository(BaseRepository[OrientacaoJuridica]):
    def __init__(self):
        super().__init__(orientacao_juridica, OrientacaoJuridica)

    def search(
        self, search: str = "", page_params: PageParams | None = None
    ) -> PaginatedResult[OrientacaoJuridica]:
        stmt = select(self.table)

        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                (self.table.c.area_direito.ilike(search_pattern))
                | (self.table.c.sub_area.ilike(search_pattern))
                | (self.table.c.descricao.ilike(search_pattern))
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

        stmt = stmt.order_by(self.table.c.data_criacao.desc())

        result = get_db().session.execute(stmt)
        rows = result.fetchall()
        items = [self._row_to_model(row) for row in rows]

        return PaginatedResult(
            items=items, total=total_count, page=page, per_page=per_page
        )

