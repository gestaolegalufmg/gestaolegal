from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class Plantao(BaseModel):
    id: int
    data_abertura: datetime | None
    data_fechamento: datetime | None

    def __post_init__(self):
        return
