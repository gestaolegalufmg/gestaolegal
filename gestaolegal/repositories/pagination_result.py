from dataclasses import asdict, dataclass
from typing import Generic, TypeVar, cast

from gestaolegal.models.base_model import BaseModel

T = TypeVar("T")


@dataclass
class PaginatedResult(Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int

    def to_dict(self):
        if not self.items or len(self.items) == 0:
            items = []
        elif isinstance(self.items[0], BaseModel):
            items = [cast(BaseModel, item).model_dump() for item in self.items]
        else:  # TODO: Estamos presumindo que os items sao dataclasses aqui, mas poderiamos melhorar a logica como um todo
            items = [asdict(item) for item in self.items]

        return {
            "items": items,
            "total": self.total,
            "page": self.page,
            "per_page": self.per_page,
        }
