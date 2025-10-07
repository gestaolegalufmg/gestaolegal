from datetime import date
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    pass


class EventoCreateInput(BaseModel):
    id_caso: int
    num_evento: int | None = None
    tipo: str
    descricao: str | None = None
    arquivo: str | None = None
    data_evento: date
    id_usuario_responsavel: int | None = None
    status: bool = True


class EventoUpdateInput(BaseModel):
    id_caso: int | None = None
    num_evento: int | None = None
    tipo: str | None = None
    descricao: str | None = None
    arquivo: str | None = None
    data_evento: date | None = None
    id_usuario_responsavel: int | None = None
    status: bool | None = None
