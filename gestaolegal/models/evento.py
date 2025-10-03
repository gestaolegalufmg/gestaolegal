from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.user import User

if TYPE_CHECKING:
    from gestaolegal.models.caso import Caso


@dataclass(frozen=True)
class Evento(BaseModel):
    id: int
    id_caso: int
    caso: "Caso"
    num_evento: int
    tipo: str
    descricao: str | None
    arquivo: str | None
    data_evento: date
    data_criacao: datetime
    id_criado_por: int
    id_usuario_responsavel: int | None
    usuario_responsavel: "User | None"
    criado_por: "User"
    status: bool

    def __post_init__(self):
        return
