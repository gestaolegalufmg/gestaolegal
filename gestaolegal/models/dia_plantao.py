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

    @staticmethod
    def from_sqlalchemy(dia_plantao: "DiaPlantaoSchema") -> "DiaPlantao":
        return DiaPlantao(
            id=dia_plantao.id,
            data=dia_plantao.data,
            status=dia_plantao.status,
        )
