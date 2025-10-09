from dataclasses import asdict, dataclass, is_dataclass
from typing import Generic, TypeVar

from gestaolegal.models.base_model import BaseModel

T = TypeVar("T")


@dataclass
class PaginatedResult(Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int

    @property
    def total_pages(self) -> int:
        if self.per_page == 0:
            return 0
        return (self.total + self.per_page - 1) // self.per_page

    @property
    def has_next_page(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous_page(self) -> bool:
        return self.page > 1

    def _serialize_item(self, item: T) -> dict[str, object]:
        if isinstance(item, BaseModel):
            return item.model_dump()
        elif is_dataclass(item) and not isinstance(item, type):
            return asdict(item)
        else:
            raise TypeError(
                f"Cannot serialize item of type {type(item).__name__}. Item must be a BaseModel, implement model_dump(), or be a dataclass."
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "items": [self._serialize_item(item) for item in self.items],
            "total": self.total,
            "page": self.page,
            "per_page": self.per_page,
            "total_pages": self.total_pages,
            "has_next_page": self.has_next_page,
            "has_previous_page": self.has_previous_page,
        }

