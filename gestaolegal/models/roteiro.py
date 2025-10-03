from dataclasses import dataclass
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class Roteiro(BaseModel):
    id: int
    area_direito: str
    link: str

    def __post_init__(self):
        return
