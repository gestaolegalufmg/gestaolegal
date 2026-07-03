from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.user import UserInfo


@dataclass
class Lembrete:
    id_do_criador: int
    id_caso: int
    id_usuario: int
    data_criacao: datetime
    data_lembrete: datetime
    descricao: str
    status: bool
    num_lembrete: int | None = None
    id: int | None = None


@dataclass
class LembreteListItem:
    id: int
    num_lembrete: int | None
    id_caso: int
    data_criacao: datetime
    data_lembrete: datetime
    descricao: str
    status: bool
    criador: "UserInfo | None"
    usuario: "UserInfo | None"
