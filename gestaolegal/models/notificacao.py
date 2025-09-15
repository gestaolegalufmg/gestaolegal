from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.usuario import Usuario

if TYPE_CHECKING:
    from gestaolegal.schemas.notificacao import NotificacaoSchema


@dataclass(frozen=True)
class Notificacao(BaseModel):
    id: int
    id_executor_acao: int | None
    id_usu_notificar: int | None
    acao: str
    data: datetime

    executor_acao: "Usuario | None"
    usu_notificar: "Usuario | None"

    def __post_init__(self):
        return

    @classmethod
    def from_sqlalchemy(
        cls, schema: "NotificacaoSchema", shallow: bool = False
    ) -> "Notificacao":
        notificacao_items = schema.to_dict()

        if not shallow:
            notificacao_items["executor_acao"] = (
                Usuario.from_sqlalchemy(schema.executor_acao)
                if schema.executor_acao
                else None
            )
            notificacao_items["usu_notificar"] = (
                Usuario.from_sqlalchemy(schema.usu_notificar)
                if schema.usu_notificar
                else None
            )
        else:
            notificacao_items["executor_acao"] = None
            notificacao_items["usu_notificar"] = None

        return Notificacao(**notificacao_items)
