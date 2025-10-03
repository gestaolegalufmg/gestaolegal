from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.user import User

if TYPE_CHECKING:
    from gestaolegal.models.caso import Caso


@dataclass(frozen=True)
class Lembrete(BaseModel):
    id: int
    num_lembrete: int
    id_do_criador: int
    criador: "User"
    id_caso: int
    caso: "Caso"
    id_usuario: int
    usuario: "User"
    data_criacao: datetime
    data_lembrete: datetime
    descricao: str
    status: bool

    def __post_init__(self):
        return
