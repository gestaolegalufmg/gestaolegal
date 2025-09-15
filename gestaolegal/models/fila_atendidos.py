from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.atendido import Atendido
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
    atendido: "Atendido | None"

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(
        fila_atendidos_schema: "FilaAtendidosSchema",
    ) -> "FilaAtendidos":
        from gestaolegal.models.atendido import Atendido

        fila_atendidos_items = fila_atendidos_schema.to_dict()
        fila_atendidos_items["atendido"] = (
            Atendido.from_sqlalchemy(fila_atendidos_schema.atendido)
            if fila_atendidos_schema.atendido
            else None
        )
        return FilaAtendidos(**fila_atendidos_items)
