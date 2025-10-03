from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.user import User

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class DiasMarcadosPlantao(BaseModel):
    id: int
    data_marcada: date | None
    confirmacao: str
    status: bool
    id_usuario: int | None
    usuario: "User | None"

    def __post_init__(self):
        return
