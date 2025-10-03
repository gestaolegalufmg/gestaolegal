from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    from gestaolegal.models.atendido import Atendido


@dataclass(frozen=True)
class FilaAtendidos(BaseModel):
    id: int
    psicologia: int
    prioridade: int
    data_criacao: datetime | None
    senha: str
    status: int
    id_atendido: int | None
    atendido: "Atendido | None"

    def __post_init__(self):
        return
