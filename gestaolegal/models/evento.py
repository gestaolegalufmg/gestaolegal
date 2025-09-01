from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.caso import Caso
    from gestaolegal.models.usuario import Usuario
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
    def from_sqlalchemy(evento: "EventoSchema") -> "Evento":
        return Evento(
            id=evento.id,
            id_caso=evento.id_caso,
            caso=evento.caso,
            num_evento=evento.num_evento,
            tipo=evento.tipo,
            descricao=evento.descricao,
            arquivo=evento.arquivo,
            data_evento=evento.data_evento,
            data_criacao=evento.data_criacao,
            id_criado_por=evento.id_criado_por,
            id_usuario_responsavel=evento.id_usuario_responsavel,
            usuario_responsavel=evento.usuario_responsavel,
            criado_por=evento.criado_por,
            status=evento.status,
        )
