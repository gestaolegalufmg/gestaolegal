import logging
from typing import Any, Callable, Generic, Optional, TypeVar

from sqlalchemy.orm import Query

from gestaolegal.database import get_db

T = TypeVar("T")
SchemaType = TypeVar("SchemaType")
ModelType = TypeVar("ModelType")

logger = logging.getLogger(__name__)


class BaseService(Generic[SchemaType, ModelType]):
    def __init__(
        self,
        schema_class: type[SchemaType],
    ):
        self.session = get_db().session
        self.schema_class = schema_class

    def find_by_id(self, id: int) -> Optional[ModelType]:
        logger.debug(
            f"BaseService.find_by_id called for {self.schema_class.__name__} with id: {id}"
        )
        result = (
            self.filter_active(self.session.query(self.schema_class))
            .filter(self.schema_class.id == id)
            .first()
        )
        return self._to_model(result) if result else None

    def find_by_field(self, field_name: str, value: Any) -> Optional[ModelType]:
        result = (
            self.filter_active(self.session.query(self.schema_class))
            .filter(getattr(self.schema_class, field_name) == value)
            .first()
        )
        return self._to_model(result) if result else None

    def get_all(
        self,
        paginator: Optional[Callable[..., Any]] = None,
        include_inactive: bool = False,
        order_by: Optional[str] = None,
    ) -> list[ModelType] | Any:
        query = self.session.query(self.schema_class)

        if not include_inactive:
            query = self.filter_active(query)

        if order_by:
            query = query.order_by(getattr(self.schema_class, order_by))

        if paginator:
            result = paginator(query)
            if hasattr(result, "items"):
                result.items = [self._to_model(item) for item in result.items]
                return result
            else:
                return [self._to_model(item) for item in result]

        results = query.all()
        return [self._to_model(result) for result in results]

    def search_by_str(
        self,
        search_term: str,
        search_fields: list[str],
        paginator: Optional[Callable[..., Any]] = None,
        order_by: Optional[str] = None,
    ) -> list[ModelType] | Any:
        query = self.session.query(self.schema_class)

        if search_term:
            search_conditions = []
            for field in search_fields:
                search_conditions.append(
                    getattr(self.schema_class, field).ilike(f"%{search_term}%")
                )
            query = query.filter(*search_conditions)

        if order_by:
            query = query.order_by(getattr(self.schema_class, order_by))

        if paginator:
            result = paginator(query)
            if hasattr(result, "items"):
                result.items = [self._to_model(item) for item in result.items]
                return result
            else:
                return [self._to_model(item) for item in result]

        results = query.all()
        return [self._to_model(result) for result in results]

    def create(self, data: dict) -> ModelType:
        logger.info(f"BaseService.create called for {self.schema_class.__name__}")
        entity = self.schema_class(**data)
        self.session.add(entity)
        self.session.commit()
        logger.info(f"Created {self.schema_class.__name__} with ID: {entity.id}")
        return self._to_model(entity)

    def update(self, entity_id: int, data: dict) -> ModelType:
        entity = self.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"Entity with id {entity_id} not found")

        db_entity = (
            self.session.query(self.schema_class)
            .filter(self.schema_class.id == entity_id)
            .first()
        )

        for key, value in data.items():
            if hasattr(db_entity, key):
                setattr(db_entity, key, value)

        self.session.commit()
        return self._to_model(db_entity)

    def delete(self, entity_id: int) -> None:
        entity = self.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"Entity with id {entity_id} not found")

        db_entity = (
            self.session.query(self.schema_class)
            .filter(self.schema_class.id == entity_id)
            .first()
        )

        if hasattr(db_entity, "status"):
            db_entity.status = False
            self.session.commit()
        else:
            raise ValueError("Entity does not support soft deletion")

    def ensure_exists(self, entity_id: int) -> ModelType:
        entity = self.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"Entity with id {entity_id} not found")
        return entity

    def filter_active(self, query: Query[T]) -> Query[T]:
        if hasattr(self.schema_class, "status"):
            return query.filter(self.schema_class.status)

        return query

    def _to_model(self, schema_instance: SchemaType) -> ModelType:
        if hasattr(schema_instance, "from_sqlalchemy"):
            return schema_instance.from_sqlalchemy(schema_instance)
        return schema_instance
