from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from gestaolegal.schemas.base import Base as BaseSchema


class BaseModel(ABC):
    def to_dict(
        self, exclude_fields: list[str] = [], inline_other_models: bool = False
    ) -> dict[str, Any]:
        if inline_other_models:
            base = dict(self.__dict__)
            for _field, value in list(base.items()):
                if isinstance(value, BaseModel):
                    child_data = value.to_dict(
                        exclude_fields=exclude_fields,
                        inline_other_models=inline_other_models,
                    )
                    base.update(child_data)
            for field in exclude_fields:
                base.pop(field, None)
            return base

        base = dict(self.__dict__)
        for field in exclude_fields:
            base.pop(field, None)
        return base

    @abstractmethod
    @staticmethod
    def from_sqlalchemy(schema: "BaseSchema") -> Self:
        pass

