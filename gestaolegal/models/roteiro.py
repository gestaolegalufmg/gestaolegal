from dataclasses import dataclass
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    from gestaolegal.schemas.roteiro import RoteiroSchema


@dataclass(frozen=True)
class Roteiro(BaseModel):
    id: int
    area_direito: str
    link: str

    def __post_init__(self):
        return

    @classmethod
    def from_sqlalchemy(
        cls, schema: "RoteiroSchema", shallow: bool = False
    ) -> "Roteiro":
        roteiro_items = schema.to_dict()
        return Roteiro(**roteiro_items)
