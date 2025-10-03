from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.user import User

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class Notificacao(BaseModel):
    id: int
    id_executor_acao: int | None
    id_usu_notificar: int | None
    acao: str
    data: datetime

    executor_acao: "User | None"
    usu_notificar: "User | None"

    def __post_init__(self):
        return
