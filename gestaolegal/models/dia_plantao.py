from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class DiaPlantao(BaseModel):
    id: int
    data: date | None
    status: bool

    def __post_init__(self):
        return
