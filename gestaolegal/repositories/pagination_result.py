from dataclasses import dataclass
from typing import Generic, TypeVar

from gestaolegal.models.base_model import BaseModel

T = TypeVar("T", bound=BaseModel)


@dataclass
class PaginatedResult(Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int

    def to_dict(self):
        return {
            "items": [item.model_dump() for item in self.items],
            "total": self.total,
            "page": self.page,
            "per_page": self.per_page,
        }
