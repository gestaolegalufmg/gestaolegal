from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.user import UserInfo


@dataclass
class Historico:
    id_usuario: int
    id_caso: int
    data: datetime
    acao: str | None = None
    descricao: str | None = None
    id: int | None = None


@dataclass
class HistoricoListItem:
    id: int
    data: datetime
    acao: str | None
    descricao: str | None
    usuario: "UserInfo | None"
