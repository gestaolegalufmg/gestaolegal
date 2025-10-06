from typing import Any

from sqlalchemy import insert, select
from sqlalchemy import update as sql_update

from gestaolegal.database.tables import enderecos
from gestaolegal.models.endereco import Endereco
from gestaolegal.repositories.repository import BaseRepository


class EnderecoRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def find_by_id(self, id: int) -> Endereco | None:
        stmt = select(enderecos).where(enderecos.c.id == id)
        result = self.session.execute(stmt).one_or_none()
        return Endereco.model_validate(result) if result else None

    def get_by_ids(self, ids: list[int]) -> list[Endereco]:
        if not ids:
            return []
        stmt = select(enderecos).where(enderecos.c.id.in_(ids))
        results = self.session.execute(stmt).all()
        return [Endereco.model_validate(row) for row in results]

    def create(self, endereco_data: dict[str, Any]) -> int:
        stmt = insert(enderecos).values(**endereco_data)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.lastrowid

    def update(self, id: int, endereco_data: dict[str, Any]) -> None:
        stmt = sql_update(enderecos).where(enderecos.c.id == id).values(**endereco_data)
        self.session.execute(stmt)
        self.session.commit()
