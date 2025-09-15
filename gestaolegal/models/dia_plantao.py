from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.schemas.dia_plantao import DiaPlantaoSchema


@dataclass(frozen=True)
class DiaPlantao:
    id: int
    data: date | None
    status: bool

    def __post_init__(self):
        return

    @classmethod
    def from_sqlalchemy(
        cls, schema: "DiaPlantaoSchema", shallow: bool = False
    ) -> "DiaPlantao":
        dia_plantao_items = schema.to_dict()
        return DiaPlantao(**dia_plantao_items)
