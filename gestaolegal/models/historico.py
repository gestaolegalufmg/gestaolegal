from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.caso import Caso
from gestaolegal.models.user import User

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class Historico(BaseModel):
    id: int
    id_usuario: int
    usuario: "User"
    id_caso: int
    caso: "Caso"
    data: datetime

    def __post_init__(self):
        return
