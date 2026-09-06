from typing import Any, NoReturn
import re

from sqlalchemy import func, insert, select
from sqlalchemy import update as sql_update
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from gestaolegal.common import PaginatedResult
from gestaolegal.database.tables import processos
from gestaolegal.models.processo import Processo
from gestaolegal.exceptions import ValidationException
from gestaolegal.repositories.repository import (
    BaseRepository,
    CountParams,
    SearchParams,
)
from gestaolegal.utils.dataclass_utils import from_dict


def _tratar_numero_duplicado(error: IntegrityError) -> NoReturn:
    """Traduz apenas a restrição do número; outros erros continuam técnicos."""
    message = str(error.orig)
    args = getattr(error.orig, "args", ())
    mysql_duplicate = (
        args and args[0] == 1062
        and re.search(r"for key ['`](?:processos\.)?numero['`]", message)
    )
    sqlite_duplicate = message == "UNIQUE constraint failed: processos.numero"
    if mysql_duplicate or sqlite_duplicate:
        raise ValidationException(
            "Já existe um processo cadastrado com esse número.", field="numero"
        ) from error
    raise error


class ProcessoRepository(BaseRepository):
    session: Session

    def __init__(self):
        super().__init__()

    def find_by_id(self, id: int) -> Processo | None:
        stmt = select(processos).where(processos.c.id == id)
        result = self.session.execute(stmt).one_or_none()
        return from_dict(Processo, dict(result._mapping)) if result else None

    def find_by_caso_id(self, caso_id: int) -> list[Processo]:
        stmt = select(processos).where(processos.c.id_caso == caso_id)
        results = self.session.execute(stmt).all()
        return [from_dict(Processo, dict(row._mapping)) for row in results]

    def search(self, params: SearchParams) -> PaginatedResult[Processo]:
        stmt = select(processos, func.count().over().label("total_count"))

        stmt = self._apply_where_clause(stmt, params.get("where"), processos)
        stmt = stmt.order_by(processos.c.id.desc())
        stmt = self._apply_pagination(stmt, params.get("page_params"))

        results = self.session.execute(stmt).all()
        total = results[0].total_count if results else 0

        items = [from_dict(Processo, dict(row._mapping)) for row in results]
        page_params = params.get("page_params")
        return PaginatedResult(
            items=items,
            total=total,
            page=page_params["page"] if page_params else 1,
            per_page=page_params["per_page"] if page_params else total,
        )

    def find_one(self, params: SearchParams) -> Processo | None:
        stmt = select(processos)
        stmt = self._apply_where_clause(stmt, params.get("where"), processos)
        result = self.session.execute(stmt).one_or_none()
        return from_dict(Processo, dict(result._mapping)) if result else None

    def count(self, params: CountParams) -> int:
        stmt = select(func.count()).select_from(processos)
        stmt = self._apply_where_clause(stmt, params.get("where"), processos)

        result = self.session.execute(stmt).scalar()
        return result or 0

    def create(self, data: dict[str, Any]) -> int:
        stmt = insert(processos).values(**data)
        try:
            result = self.session.execute(stmt)
            self.session.flush()
        except IntegrityError as error:
            _tratar_numero_duplicado(error)
        return result.lastrowid

    def update(self, id: int, data: dict[str, Any]) -> None:
        stmt = sql_update(processos).where(processos.c.id == id).values(**data)
        try:
            self.session.execute(stmt)
        except IntegrityError as error:
            _tratar_numero_duplicado(error)

    def delete(self, id: int) -> bool:
        stmt = sql_update(processos).where(processos.c.id == id).values(status=False)
        result = self.session.execute(stmt)
        return result.rowcount > 0
