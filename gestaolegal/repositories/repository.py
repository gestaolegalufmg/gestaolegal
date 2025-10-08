from typing import Literal, Protocol, TypedDict, TypeVar

from sqlalchemy import ColumnElement, Select, Table, and_, or_
from sqlalchemy.orm import Session

from gestaolegal.common import PageParams
from gestaolegal.database.session import get_session
from gestaolegal.models.base_model import BaseModel
from gestaolegal.repositories.pagination_result import PaginatedResult

T = TypeVar("T", bound=BaseModel)


class WhereClause(TypedDict):
    column: str
    operator: str
    value: (
        str
        | int
        | float
        | bool
        | list[str]
        | list[int]
        | list[float]
        | list[bool]
        | None
    )


class ComplexWhereClause(TypedDict):
    clauses: list[WhereClause]
    operator: Literal["and", "or"]


class GetParams(TypedDict):
    where: WhereClause | ComplexWhereClause | None


class SearchParams(TypedDict):
    where: WhereClause | ComplexWhereClause | None
    page_params: PageParams | None


class CountParams(TypedDict):
    where: WhereClause | ComplexWhereClause | None


Q = TypeVar("Q", bound=tuple[object, ...])


class BaseRepository:
    session: Session

    def __init__(self):
        self.session = get_session()

    def _apply_where_clause(
        self,
        stmt: Select[Q],
        where: WhereClause | ComplexWhereClause | None,
        table: Table,
    ) -> Select[Q]:
        if not where:
            return stmt

        if "clauses" in where:
            complex_where = where
            conditions = [
                self._build_condition(clause, table)
                for clause in complex_where["clauses"]
            ]

            if not conditions:
                return stmt

            if complex_where["operator"] == "and":
                return stmt.where(and_(*conditions))
            else:
                return stmt.where(or_(*conditions))
        else:
            simple_where = where
            condition = self._build_condition(simple_where, table)
            return stmt.where(condition)

    def _build_condition(
        self, clause: WhereClause, table: Table
    ) -> ColumnElement[bool]:
        column = table.c[clause["column"]]
        operator = clause["operator"]
        value = clause["value"]

        if operator == "==":
            return column == value
        elif operator == "!=":
            return column != value
        elif operator == ">":
            return column > value
        elif operator == ">=":
            return column >= value
        elif operator == "<":
            return column < value
        elif operator == "<=":
            return column <= value
        elif operator == "like":
            return column.like(value)
        elif operator == "ilike":
            return column.ilike(value)
        elif operator == "in" and isinstance(value, list):
            return column.in_(value)
        elif operator == "not_in" and isinstance(value, list):
            return column.not_in(value)
        elif operator == "is_null":
            return column.is_(None)
        elif operator == "is_not_null":
            return column.is_not(None)
        else:
            raise ValueError(f"Invalid operator: {operator}")

    def _apply_pagination(
        self, stmt: Select[Q], page_params: PageParams | None
    ) -> Select[Q]:
        if not page_params:
            return stmt

        offset = (page_params["page"] - 1) * page_params["per_page"]
        return stmt.offset(offset).limit(page_params["per_page"])


class Repository(Protocol[T]):
    def find_by_id(self, id: int) -> T | None: ...

    def find_by_email(self, email: str) -> T | None: ...

    def find_one(self, params: SearchParams) -> T | None: ...

    def search(self, params: SearchParams) -> PaginatedResult[T]: ...

    def count(self, params: CountParams) -> int: ...

    def create(self, data: T) -> int: ...

    def update(self, id: int, data: T) -> None: ...

    def delete(self, id: int) -> bool: ...
