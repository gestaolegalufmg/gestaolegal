from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING

from gestaolegal.models.usuario import Usuario

if TYPE_CHECKING:
    from gestaolegal.models.caso import Caso
    from gestaolegal.schemas.evento import EventoSchema


@dataclass(frozen=True)
class Evento:
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
    usuario_responsavel: "Usuario | None"
    criado_por: "Usuario"
    status: bool

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(evento_schema: "EventoSchema") -> "Evento":
        from gestaolegal.models.caso import Caso

        evento_items = evento_schema.to_dict()
        evento_items["caso"] = Caso.from_sqlalchemy(evento_schema.caso)
        evento_items["usuario_responsavel"] = (
            Usuario.from_sqlalchemy(evento_schema.usuario_responsavel)
            if evento_schema.usuario_responsavel
            else None
        )
        evento_items["criado_por"] = Usuario.from_sqlalchemy(evento_schema.criado_por)
        return Evento(**evento_items)
