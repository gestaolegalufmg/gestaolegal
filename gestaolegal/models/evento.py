from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.caso import Caso
    from gestaolegal.models.user import User


@dataclass
class Evento:
    id: int | None
    id_caso: int
    num_evento: int | None
    tipo: str
    descricao: str | None
    arquivo: str | None
    data_evento: date
    data_criacao: datetime
    id_criado_por: int
    id_usuario_responsavel: int | None
    status: bool

    caso: "Caso | None" = None
    criado_por: "User | None" = None
    usuario_responsavel: "User | None" = None
