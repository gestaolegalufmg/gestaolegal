import logging
from typing import Any, Generic, TypeVar

from sqlalchemy import Table, delete, insert, select, update
from sqlalchemy.sql import Select

from gestaolegal.common import PageParams
from gestaolegal.database import get_db
from gestaolegal.models.base_model import BaseModel

TModel = TypeVar("TModel", bound=BaseModel)

WhereCondition = tuple[str, str, Any]
WhereConditions = list[WhereCondition] | WhereCondition

logger = logging.getLogger(__name__)


class PaginatedResult(Generic[TModel]):
    def __init__(self, items: list[TModel], total: int, page: int, per_page: int):
        self.items = items
        self.total = total
        self.page = page
        self.per_page = per_page
        self.total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0

    def to_dict(self):
        return {
            "items": self.items,
            "total": self.total,
            "page": self.page,
            "per_page": self.per_page,
        }


class BaseRepository(Generic[TModel]):
    def __init__(self, table: Table, model_class: type[TModel]):
        self.table = table
        self.model_class = model_class
        self.db = get_db()

    def _build_where_clause(self, stmt: Select, where_conditions: WhereConditions | None):
        if not where_conditions:
            return stmt

        if isinstance(where_conditions, tuple):
            where_conditions = [where_conditions]

        for condition in where_conditions:
            field, operator, value = condition
            column = self.table.c[field]

            if operator == "eq":
                stmt = stmt.where(column == value)
            elif operator == "ne":
                stmt = stmt.where(column != value)
            elif operator == "gt":
                stmt = stmt.where(column > value)
            elif operator == "gte":
                stmt = stmt.where(column >= value)
            elif operator == "lt":
                stmt = stmt.where(column < value)
            elif operator == "lte":
                stmt = stmt.where(column <= value)
            elif operator == "like":
                stmt = stmt.where(column.like(value))
            elif operator == "ilike":
                stmt = stmt.where(column.ilike(value))
            elif operator == "in":
                stmt = stmt.where(column.in_(value))
            elif operator == "not_in":
                stmt = stmt.where(column.not_in(value))
            elif operator == "is_null":
                stmt = stmt.where(column.is_(None))
            elif operator == "is_not_null":
                stmt = stmt.where(column.isnot(None))

        return stmt

    def _row_to_model(self, row: Any) -> TModel:
        if row is None:
            return None
        row_dict = dict(row._mapping)
        return self.model_class.from_dict(row_dict)

    def find_by_id(self, id: int) -> TModel | None:
        stmt = select(self.table).where(self.table.c.id == id)
        result = self.db.session.execute(stmt)
        row = result.fetchone()
        return self._row_to_model(row)

    def find(self, where_conditions: WhereConditions) -> TModel | None:
        stmt = select(self.table)
        stmt = self._build_where_clause(stmt, where_conditions)
        result = self.db.session.execute(stmt)
        row = result.fetchone()
        return self._row_to_model(row)

    def get(
        self,
        where_conditions: WhereConditions | None = None,
        page_params: PageParams | None = None,
        order_by: list[str] | None = None,
        active_only: bool = False,
    ) -> PaginatedResult[TModel]:
        stmt = select(self.table)

        if active_only and "status" in self.table.c:
            stmt = stmt.where(self.table.c.status == True)

        stmt = self._build_where_clause(stmt, where_conditions)

        if order_by:
            for field in order_by:
                if field.startswith("-"):
                    stmt = stmt.order_by(self.table.c[field[1:]].desc())
                else:
                    stmt = stmt.order_by(self.table.c[field])

        count_stmt = select(stmt.alias().c.id.label("id"))
        total = self.db.session.execute(count_stmt).fetchall()
        total_count = len(total)

        if page_params:
            page = page_params.get("page", 1)
            per_page = page_params.get("per_page", 10)
            offset = (page - 1) * per_page
            stmt = stmt.limit(per_page).offset(offset)
        else:
            page = 1
            per_page = total_count

        result = self.db.session.execute(stmt)
        rows = result.fetchall()
        items = [self._row_to_model(row) for row in rows]

        return PaginatedResult(
            items=items, total=total_count, page=page, per_page=per_page
        )

    def create(self, data: dict[str, Any] | TModel) -> TModel:
        if isinstance(data, BaseModel):
            data = data.to_dict()

        data_copy = {k: v for k, v in data.items() if k in self.table.c and v is not None}

        stmt = insert(self.table).values(**data_copy)
        result = self.db.session.execute(stmt)
        self.db.session.commit()

        created_id = result.inserted_primary_key[0]
        return self.find_by_id(created_id)

    def update(self, id: int, data: dict[str, Any] | TModel) -> TModel:
        if isinstance(data, BaseModel):
            data = data.to_dict()

        data_copy = {k: v for k, v in data.items() if k in self.table.c and k != "id"}

        stmt = update(self.table).where(self.table.c.id == id).values(**data_copy)
        self.db.session.execute(stmt)
        self.db.session.commit()

        return self.find_by_id(id)

    def delete(self, id: int) -> bool:
        stmt = delete(self.table).where(self.table.c.id == id)
        result = self.db.session.execute(stmt)
        self.db.session.commit()
        return result.rowcount > 0

    def soft_delete(self, id: int) -> bool:
        if "status" not in self.table.c:
            raise ValueError(f"Table {self.table.name} does not support soft delete")

        stmt = update(self.table).where(self.table.c.id == id).values(status=False)
        result = self.db.session.execute(stmt)
        self.db.session.commit()
        return result.rowcount > 0

