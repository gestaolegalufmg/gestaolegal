from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    from gestaolegal.schemas.plantao import PlantaoSchema


@dataclass(frozen=True)
class Plantao(BaseModel):
    id: int
    data_abertura: datetime | None
    data_fechamento: datetime | None

    def __post_init__(self):
        return

    @classmethod
    def from_sqlalchemy(
        cls, schema: "PlantaoSchema", shallow: bool = False
    ) -> "Plantao":
        plantao_items = schema.to_dict()
        return Plantao(**plantao_items)
