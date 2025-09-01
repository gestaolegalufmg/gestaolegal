from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.schemas.roteiro import RoteiroSchema


@dataclass(frozen=True)
class Roteiro:
    id: int
    area_direito: str
    link: str

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(roteiro: "RoteiroSchema") -> "Roteiro":
        return Roteiro(
            id=roteiro.id,
            area_direito=roteiro.area_direito,
            link=roteiro.link,
        )
