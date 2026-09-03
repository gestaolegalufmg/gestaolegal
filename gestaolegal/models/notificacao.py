from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

TipoNotificacao = Literal["caso", "evento", "lembrete", "plantao"]


@dataclass
class Notificacao:
    acao: str
    data: date
    id_executor_acao: int | None = None
    id_usu_notificar: int | None = None  # None = aviso geral
    tipo: str | None = None
    id_caso: int | None = None
    id_referencia: int | None = None
    lida: bool = False
    data_criacao: datetime | None = None
    id: int | None = None


@dataclass
class NotificacaoListItem(Notificacao):
    executor: str | None = None
