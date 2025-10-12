from typing import Any

from sqlalchemy import insert, select
from sqlalchemy import update as sql_update
from sqlalchemy.orm import Session

from gestaolegal.database.tables import arquivos_caso
from gestaolegal.models.arquivo_caso import ArquivoCaso
from gestaolegal.repositories.repository import BaseRepository
from gestaolegal.utils.dataclass_utils import from_dict


class ArquivoCasoRepository(BaseRepository):
    session: Session

    def __init__(self):
        super().__init__()

    def find_by_id(self, id: int) -> ArquivoCaso | None:
        stmt = select(arquivos_caso).where(arquivos_caso.c.id == id)
        result = self.session.execute(stmt).one_or_none()

        if not result:
            return None

        return from_dict(ArquivoCaso, dict(result._mapping))

    def find_by_caso_id(self, caso_id: int) -> list[ArquivoCaso]:
        stmt = select(arquivos_caso).where(arquivos_caso.c.id_caso == caso_id)
        results = self.session.execute(stmt).all()

        return [from_dict(ArquivoCaso, dict(row._mapping)) for row in results]

    def create(self, data: dict[str, Any]) -> int:
        stmt = insert(arquivos_caso).values(**data)
        result = self.session.execute(stmt)
        self.session.flush()
        return result.lastrowid

    def delete(self, id: int) -> bool:
        stmt = sql_update(arquivos_caso).where(arquivos_caso.c.id == id)
        result = self.session.execute(stmt)
        return result.rowcount > 0
