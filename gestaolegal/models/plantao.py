from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from gestaolegal.schemas.plantao import PlantaoSchema


@dataclass(frozen=True)
class Plantao:
    id: int
    data_abertura: datetime | None
    data_fechamento: datetime | None

    def __post_init__(self):
        return

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "data_abertura": self.data_abertura,
            "data_fechamento": self.data_fechamento,
        }

    @staticmethod
    def from_sqlalchemy(plantao: "PlantaoSchema") -> "Plantao":
        return Plantao(
            id=plantao.id,
            data_abertura=plantao.data_abertura,
            data_fechamento=plantao.data_fechamento,
        )
