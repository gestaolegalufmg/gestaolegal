from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.schemas.atendido import AtendidoSchema
    from gestaolegal.schemas.fila_atendidos import FilaAtendidosSchema


@dataclass(frozen=True)
class FilaAtendidos:
    id: int
    psicologia: int
    prioridade: int
    data_criacao: datetime | None
    senha: str
    status: int
    id_atendido: int | None
    atendido: "AtendidoSchema | None"

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(fila_atendidos: "FilaAtendidosSchema") -> "FilaAtendidos":
        return FilaAtendidos(
            id=fila_atendidos.id,
            psicologia=fila_atendidos.psicologia,
            prioridade=fila_atendidos.prioridade,
            data_criacao=fila_atendidos.data_criacao,
            senha=fila_atendidos.senha,
            status=fila_atendidos.status,
            id_atendido=fila_atendidos.id_atendido,
            atendido=fila_atendidos.atendido,
        )
