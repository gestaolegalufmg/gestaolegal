from typing import Any

from sqlalchemy import delete as sql_delete
from sqlalchemy import func, insert, or_, select
from sqlalchemy import update as sql_update
from sqlalchemy.orm import Session

from gestaolegal.common import PageParams, PaginatedResult
from gestaolegal.database.tables import arquivos, usuarios
from gestaolegal.models.arquivo import Arquivo
from gestaolegal.repositories.repository import BaseRepository
from gestaolegal.utils.dataclass_utils import from_dict


class ArquivoRepository(BaseRepository):
    session: Session

    def __init__(self):
        super().__init__()

    def find_by_id(self, id: int) -> Arquivo | None:
        stmt = select(arquivos).where(arquivos.c.id == id)
        result = self.session.execute(stmt).one_or_none()
        return from_dict(Arquivo, dict(result._mapping)) if result else None

    def search(self, page_params: PageParams, search: str) -> PaginatedResult[dict]:
        """Lista paginada com o nome de quem cadastrou, mais recentes primeiro."""
        stmt = (
            select(
                arquivos,
                usuarios.c.nome.label("criado_por"),
                func.count().over().label("total_count"),
            )
            .select_from(arquivos.outerjoin(usuarios, usuarios.c.id == arquivos.c.id_criado_por))
            .order_by(arquivos.c.data_criacao.desc(), arquivos.c.id.desc())
        )
        if search:
            termo = f"%{search}%"
            stmt = stmt.where(
                or_(arquivos.c.titulo.ilike(termo), arquivos.c.descricao.ilike(termo))
            )
        stmt = self._apply_pagination(stmt, page_params)

        rows = self.session.execute(stmt).mappings().all()
        total = rows[0]["total_count"] if rows else 0
        items = [
            {k: v for k, v in dict(row).items() if k != "total_count"} for row in rows
        ]
        return PaginatedResult(
            items=items,
            total=total,
            page=page_params["page"],
            per_page=page_params["per_page"],
        )

    def create(self, data: dict[str, Any]) -> int:
        result = self.session.execute(insert(arquivos).values(**data))
        self.session.flush()
        return result.lastrowid

    def update(self, id: int, data: dict[str, Any]) -> None:
        self.session.execute(sql_update(arquivos).where(arquivos.c.id == id).values(**data))

    def delete(self, id: int) -> bool:
        result = self.session.execute(sql_delete(arquivos).where(arquivos.c.id == id))
        return result.rowcount > 0
