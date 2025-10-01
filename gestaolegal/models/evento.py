from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.user import User

if TYPE_CHECKING:
    from gestaolegal.models.caso import Caso
    from gestaolegal.schemas.evento import EventoSchema


@dataclass(frozen=True)
class Evento(BaseModel):
    id: int
    id_caso: int
    caso: "Caso"
    num_evento: int
    tipo: str
    descricao: str | None
    arquivo: str | None
    data_evento: date
    data_criacao: datetime
    id_criado_por: int
    id_usuario_responsavel: int | None
    usuario_responsavel: "User | None"
    criado_por: "User"
    status: bool

    def __post_init__(self):
        return

    @classmethod
    def from_sqlalchemy(cls, schema: "EventoSchema", shallow: bool = False) -> "Evento":
        evento_items = schema.to_dict()

        if not shallow:
            from gestaolegal.models.caso import Caso

            evento_items["caso"] = Caso.from_sqlalchemy(schema.caso, shallow=True)
            evento_items["usuario_responsavel"] = (
                User.from_sqlalchemy(schema.usuario_responsavel)
                if schema.usuario_responsavel
                else None
            )
            evento_items["criado_por"] = User.from_sqlalchemy(schema.criado_por)
        else:
            evento_items["caso"] = None
            evento_items["usuario_responsavel"] = None
            evento_items["criado_por"] = None

        return Evento(**evento_items)
