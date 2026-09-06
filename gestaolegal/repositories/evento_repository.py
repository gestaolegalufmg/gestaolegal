from typing import Any

from sqlalchemy import delete, func, insert, select
from sqlalchemy import update as sql_update
from sqlalchemy.orm import Session

from gestaolegal.common import PageParams, PaginatedResult
from gestaolegal.database.tables import eventos, arquivos_evento
from gestaolegal.models.evento import Evento
from gestaolegal.repositories.repository import (
    BaseRepository,
    CountParams,
    SearchParams,
)
from gestaolegal.utils.dataclass_utils import from_dict


class EventoRepository(BaseRepository):
    session: Session

    def __init__(self):
        super().__init__()

    def find_by_id(self, id: int, unidade_id: int | None = None) -> Evento | None:
        stmt = select(eventos).where(eventos.c.id == id)
        if unidade_id is not None:
            stmt = stmt.where(eventos.c.unidade_id == unidade_id)
        result = self.session.execute(stmt).one_or_none()
        return from_dict(Evento, dict(result._mapping)) if result else None

    def listar_arquivos(self, evento_id: int) -> list[dict]:
        return [dict(row) for row in self.session.execute(
            select(arquivos_evento).where(arquivos_evento.c.id_evento == evento_id)
            .order_by(arquivos_evento.c.id)
        ).mappings()]

    def adicionar_arquivo(self, evento_id: int, caso_id: int, ref: str) -> int:
        result = self.session.execute(insert(arquivos_evento).values(
            id_evento=evento_id, id_caso=caso_id, link_arquivo=ref))
        return result.lastrowid

    def remover_arquivo(self, arquivo_id: int, evento_id: int) -> None:
        self.session.execute(delete(arquivos_evento).where(
            arquivos_evento.c.id == arquivo_id, arquivos_evento.c.id_evento == evento_id))

    def referencia_em_uso(self, ref: str) -> bool:
        return bool(self.session.execute(select(arquivos_evento.c.id).where(
            arquivos_evento.c.link_arquivo == ref).limit(1)).first() or
            self.session.execute(select(eventos.c.id).where(eventos.c.arquivo == ref).limit(1)).first())

    def find_by_caso_id(self, caso_id: int) -> list[Evento]:
        stmt = select(eventos).where(eventos.c.id_caso == caso_id)
        results = self.session.execute(stmt).all()
        return [from_dict(Evento, dict(row._mapping)) for row in results]

    def find_by_caso_id_paginated(
        self,
        caso_id: int,
        page_params: PageParams,
        tipo: str | None = None,
        unidade_id: int | None = None,
    ) -> PaginatedResult[Evento]:
        """Eventos ativos do caso, opcionalmente filtrados por tipo.

        Eventos excluídos (status=False) ficam fora da listagem, mas continuam
        acessíveis por id para preservar o histórico.
        """
        stmt = select(eventos, func.count().over().label("total_count"))
        stmt = stmt.where(eventos.c.id_caso == caso_id, eventos.c.status.is_(True))
        if unidade_id is not None:
            stmt = stmt.where(eventos.c.unidade_id == unidade_id)
        if tipo:
            stmt = stmt.where(eventos.c.tipo == tipo)
        stmt = stmt.order_by(eventos.c.data_evento.desc())
        stmt = self._apply_pagination(stmt, page_params)

        results = self.session.execute(stmt).all()
        total = results[0].total_count if results else 0

        items = [from_dict(Evento, dict(row._mapping)) for row in results]

        return PaginatedResult(
            items=items,
            total=total,
            page=page_params["page"],
            per_page=page_params["per_page"],
        )

    def search(self, params: SearchParams) -> PaginatedResult[Evento]:
        stmt = select(eventos, func.count().over().label("total_count"))

        stmt = self._apply_where_clause(stmt, params.get("where"), eventos)
        stmt = stmt.order_by(eventos.c.data_evento.desc())
        stmt = self._apply_pagination(stmt, params.get("page_params"))

        results = self.session.execute(stmt).all()
        total = results[0].total_count if results else 0

        items = [from_dict(Evento, dict(row._mapping)) for row in results]

        page_params = params.get("page_params")
        return PaginatedResult(
            items=items,
            total=total,
            page=page_params["page"] if page_params else 1,
            per_page=page_params["per_page"] if page_params else total,
        )

    def find_one(self, params: SearchParams) -> Evento | None:
        stmt = select(eventos)
        stmt = self._apply_where_clause(stmt, params.get("where"), eventos)
        result = self.session.execute(stmt).one_or_none()
        return from_dict(Evento, dict(result._mapping)) if result else None

    def count(self, params: CountParams) -> int:
        stmt = select(func.count()).select_from(eventos)
        stmt = self._apply_where_clause(stmt, params.get("where"), eventos)

        result = self.session.execute(stmt).scalar()
        return result or 0

    def create(self, data: dict[str, Any]) -> int:
        stmt = insert(eventos).values(**data)
        result = self.session.execute(stmt)
        self.session.flush()
        return result.lastrowid

    def update(self, id: int, data: dict[str, Any]) -> None:
        stmt = sql_update(eventos).where(eventos.c.id == id).values(**data)
        self.session.execute(stmt)

    def delete(self, id: int) -> bool:
        stmt = sql_update(eventos).where(eventos.c.id == id).values(status=False)
        result = self.session.execute(stmt)
        return result.rowcount > 0

    def count_by_caso_id(self, caso_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(eventos)
            .where(eventos.c.id_caso == caso_id)
        )
        result = self.session.execute(stmt).scalar()
        return result or 0
