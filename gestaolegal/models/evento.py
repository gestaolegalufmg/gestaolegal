from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.caso import Caso
    from gestaolegal.models.user import User


@dataclass
class Evento:
    id_caso: int
    tipo: str
    data_evento: date
    data_criacao: datetime
    id_criado_por: int
    status: bool

    id: int | None = None
    num_evento: int | None = None
    descricao: str | None = None
    arquivo: str | None = None
    id_usuario_responsavel: int | None = None
    caso: "Caso | None" = None
    criado_por: "User | None" = None
    usuario_responsavel: "User | None" = None
