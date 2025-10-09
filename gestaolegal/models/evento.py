from datetime import date, datetime
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    from gestaolegal.models.caso import Caso
    from gestaolegal.models.user import User


class Evento(BaseModel):
    id: int | None = None

    id_caso: int
    caso: "Caso | None" = None

    num_evento: int | None
    tipo: str
    descricao: str | None
    arquivo: str | None
    data_evento: date
    data_criacao: datetime

    id_criado_por: int
    criado_por: "User | None" = None

    id_usuario_responsavel: int | None
    usuario_responsavel: "User | None" = None

    status: bool
