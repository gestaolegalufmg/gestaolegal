from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.usuario import Usuario
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
    def from_sqlalchemy(notificacao: "NotificacaoSchema") -> "Notificacao":
        return Notificacao(
            id=notificacao.id,
            id_executor_acao=notificacao.id_executor_acao,
            id_usu_notificar=notificacao.id_usu_notificar,
            acao=notificacao.acao,
            data=notificacao.data,
            executor_acao=notificacao.executor_acao,
            usu_notificar=notificacao.usu_notificar,
        )
