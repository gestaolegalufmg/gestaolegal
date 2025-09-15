from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.usuario import Usuario

if TYPE_CHECKING:
    from gestaolegal.schemas.notificacao import NotificacaoSchema


@dataclass(frozen=True)
class Notificacao:
    id: int
    id_executor_acao: int | None
    id_usu_notificar: int | None
    acao: str
    data: datetime

    executor_acao: "Usuario | None"
    usu_notificar: "Usuario | None"

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(notificacao_schema: "NotificacaoSchema") -> "Notificacao":
        notificacao_items = notificacao_schema.to_dict()
        notificacao_items["executor_acao"] = (
            Usuario.from_sqlalchemy(notificacao_schema.executor_acao)
            if notificacao_schema.executor_acao
            else None
        )
        notificacao_items["usu_notificar"] = (
            Usuario.from_sqlalchemy(notificacao_schema.usu_notificar)
            if notificacao_schema.usu_notificar
            else None
        )
        return Notificacao(**notificacao_items)
