from collections.abc import Sequence
from typing import Any, Generic, Literal, TypeGuard, TypeVar, cast

from sqlalchemy import (
    Column,
    ColumnElement,
    UnaryExpression,
    and_,
    asc,
    desc,
    or_,
)
from sqlalchemy.orm import Query

from gestaolegal.common import PageParams
from gestaolegal.database import get_db
from gestaolegal.models.base_model import BaseModel
from gestaolegal.schemas.base import Base as BaseSchema
from gestaolegal.services import PaginatedResult

ModelType = TypeVar("ModelType", bound=BaseModel)
SchemaType = TypeVar("SchemaType", bound=BaseSchema)


def _has_status(schema_cls: type[SchemaType]) -> TypeGuard[type[SchemaType]]:
    return hasattr(schema_cls, "status")


QueryOperation = (
    Literal[
        "eq",
        "ne",
        "lt",
        "lte",
        "gt",
        "gte",
        "like",
        "ilike",
        "in",
        "not_in",
        "is_null",
        "is_not_null",
        "between",
        "contains",
        "icontains",
        "startswith",
        "istartswith",
        "endswith",
        "iendswith",
    ]
    | str
)

OrderableColumn = Column[Any] | UnaryExpression[Any] | str
OrderByList = list[OrderableColumn] | OrderableColumn | None


ExpressionOperator = Literal["and", "or"]

SimpleCondition = tuple[str, str, Any]  # basedpyright: ignore[reportExplicitAny]
ConditionWithOperator = dict[ExpressionOperator, list[SimpleCondition]]
WhereConditions = list[ConditionWithOperator | SimpleCondition]


DeleteMode = Literal["auto", "soft", "hard"]


class BaseRepository(Generic[SchemaType, ModelType]):
    schema_class: type[SchemaType]
    model_class: type[ModelType]

    _has_status_field: bool
    _delete_mode: DeleteMode

    def __init__(
        self,
        schema_class: type[SchemaType],
        model_class: type[ModelType],
        delete_mode: DeleteMode = "auto",
    ):
        self.schema_class = schema_class
        self.model_class = model_class

        self.session = get_db().session
        self._has_status_field = _has_status(self.schema_class)
        self._delete_mode = delete_mode

    def _apply_status_filter(
        self, query: Query[SchemaType], active_only: bool = True
    ) -> Query[SchemaType]:
        if active_only and hasattr(self.schema_class, "status"):
            return query.filter(self.schema_class.status)  # type: ignore[attr-defined]
        return query

    def get(
        self,
        active_only: bool = True,
        page_params: PageParams | None = None,
        order_by: OrderByList | None = None,
        where_conditions: WhereConditions
        | SimpleCondition
        | ConditionWithOperator
        | None = None,
        order_desc: bool = False,
    ) -> PaginatedResult[ModelType]:
        query = self._create_query()
        query = self._apply_status_filter(query, active_only)

        if where_conditions:
            if not isinstance(where_conditions, list):
                where_conditions = [where_conditions]
            query = self._apply_where(query, where_conditions)

        if order_by is not None:
            query = self._apply_order(query, order_by, order_desc)

        total = query.count()

        if page_params:
            query = query.offset(
                (page_params["page"] - 1) * page_params["per_page"]
            ).limit(page_params["per_page"])
            page = page_params["page"] or 1
            per_page = page_params["per_page"] or total
        else:
            page = 1
            per_page = total if total > 0 else 1

        result = query.all()

        items = [self._build_model(entity) for entity in result]
        return PaginatedResult[ModelType](items, total, page, per_page)

    def find(
        self,
        where_conditions: WhereConditions
        | SimpleCondition
        | ConditionWithOperator
        | None = None,
        active_only: bool = True,
    ) -> ModelType | None:
        query = self._create_query()
        query = self._apply_status_filter(query, active_only)

        if where_conditions:
            if not isinstance(where_conditions, list):
                where_conditions = [where_conditions]
            query = self._apply_where(query, where_conditions)

        result = query.first()
        return self._build_model(result) if result else None

    def find_by_id(self, id: int, active_only: bool = True) -> ModelType | None:
        if not hasattr(self.schema_class, "id"):
            raise ValueError(
                f"Schema {self.schema_class.__name__} does not have an id field"
            )

        where = ("id", "eq", id)
        return self.find(where_conditions=where, active_only=active_only)

    def count(
        self, where_conditions: WhereConditions | None = None, active_only: bool = True
    ) -> int:
        query = self.session.query(self.schema_class)
        query = self._apply_status_filter(query, active_only)
        if where_conditions:
            query = self._apply_where(query, where_conditions)

        return query.count()

    def create(self, data: ModelType | dict[str, Any]) -> ModelType:
        if isinstance(data, dict):
            schema = self.schema_class(**data)
        else:
            schema = self.schema_class(**data.to_dict())

        self.session.add(schema)
        self.session.commit()
        return self._build_model(schema)

    def update(
        self, id: int, data: dict[str, Any], active_only: bool = True
    ) -> ModelType:
        query = self._create_query(id)
        query = self._apply_status_filter(query, active_only)
        entity = query.first()

        if not entity:
            raise ValueError(f"Entity with id {id} not found")

        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        self.session.commit()
        return self._build_model(entity)

    def delete(
        self, id: int, hard_delete: bool = False, active_only: bool = True
    ) -> bool:
        query = self._create_query(id)
        query = self._apply_status_filter(query, active_only)
        entity = query.first()

        if not entity:
            raise ValueError(f"Entity with id {id} not found")

        if not hasattr(entity, "status") or hard_delete:
            self.session.delete(entity)
        else:
            entity.status = False

        self.session.commit()
        return True

    def soft_delete(self, id: int, active_only: bool = True) -> bool:
        if not self._has_status_field:
            raise ValueError(
                f"Schema {self.schema_class.__name__} does not have a status field"
            )

        query = self._create_query(id)
        query = self._apply_status_filter(query, active_only)
        entity = query.first()

        if not entity:
            return False

        entity.status = False # type: ignore[attr-defined]
        self.session.commit() 
        return True

    def _create_query(self, id: int | None = None) -> Query[SchemaType]:
        query = self.session.query(self.schema_class)
        if id:
            if not hasattr(self.schema_class, "id"):
                raise ValueError(
                    f"Schema {self.schema_class.__name__} does not have an id field"
                )

            query = query.filter(self.schema_class.id == id)  # type: ignore[attr-defined]
        return query

    def _build_model(
        self, query_result: SchemaType | tuple[SchemaType, ...]
    ) -> ModelType:
        if not query_result:
            raise ValueError("Query result is None when calling _build_model")

        if isinstance(query_result, tuple):
            if not query_result[0]:
                raise ValueError("Query result is None when calling _build_model")

            primary_schema = query_result[0]
        else:
            primary_schema = query_result

        return cast(ModelType, self.model_class.from_sqlalchemy(primary_schema))

    def _apply_order(
        self, query: Query[SchemaType], order_by: OrderByList, order_desc: bool
    ) -> Query[SchemaType]:
        if order_by is None:
            return query

        if not isinstance(order_by, Sequence):
            order_by = [order_by]

        order_expressions: list[ColumnElement[Any]] = []

        for column in order_by:
            if isinstance(column, UnaryExpression):
                order_expressions.append(column)
            elif order_desc:
                order_expressions.append(desc(column))
            else:
                order_expressions.append(asc(column))

        return query.order_by(*order_expressions)

    def _apply_where(
        self, query: Query[SchemaType], where_conditions: WhereConditions
    ) -> Query[SchemaType]:
        if not where_conditions:
            return query

        for condition in where_conditions:
            if isinstance(condition, dict):
                operator = list(condition.keys())[0]
                conditions = condition[operator]
                expressions = [
                    self._build_expression(condition) for condition in conditions
                ]

                if operator == "and":
                    query = query.filter(and_(*expressions))
                elif operator == "or":
                    query = query.filter(or_(*expressions))

            elif isinstance(condition, list):
                expressions = [
                    self._build_expression(condition) for condition in condition
                ]
                query = query.filter(and_(*expressions))

            else:
                expression = self._build_expression(condition)
                query = query.filter(expression)

        return query

    def _build_expression(self, condition: SimpleCondition) -> ColumnElement[bool]:
        column, query_operator, value = condition
        column_ref: ColumnElement[Any] = getattr(self.schema_class, column)

        if query_operator == "eq":
            return column_ref == value
        elif query_operator == "ne":
            return column_ref != value
        elif query_operator == "lt":
            return column_ref < value
        elif query_operator == "lte":
            return column_ref <= value
        elif query_operator == "gt":
            return column_ref > value
        elif query_operator == "gte":
            return column_ref >= value
        elif query_operator == "like":
            return column_ref.like(value)
        elif query_operator == "ilike":
            return column_ref.ilike(value)
        elif query_operator == "in":
            return column_ref.in_(value)
        elif query_operator == "not_in":
            return column_ref.not_in(value)
        elif query_operator == "is_null":
            return column_ref.is_(None)
        elif query_operator == "is_not_null":
            return column_ref.is_not(None)
        elif query_operator == "between":
            return column_ref.between(value[0], value[1])
        elif query_operator == "contains":
            return column_ref.contains(value)
        elif query_operator == "icontains":
            return column_ref.ilike(value)
        elif query_operator == "startswith":
            return column_ref.startswith(value)
        elif query_operator == "istartswith":
            return column_ref.ilike(value)
        elif query_operator == "endswith":
            return column_ref.endswith(value)
        elif query_operator == "iendswith":
            return column_ref.ilike(value)
        else:
            raise ValueError(f"Invalid query operator: {query_operator}")
