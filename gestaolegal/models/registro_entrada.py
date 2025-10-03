from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.user import User

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class RegistroEntrada(BaseModel):
    id: int
    data_entrada: datetime
    data_saida: datetime
    status: bool
    confirmacao: str
    id_usuario: int | None
    usuario: "User | None"

    def __post_init__(self):
        return
