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

    @classmethod
    def from_sqlalchemy(
        cls, schema: "FilaAtendidosSchema", shallow: bool = False
    ) -> "FilaAtendidos":
        fila_atendidos_items = schema.to_dict()

        if not shallow:
            from gestaolegal.models.atendido import Atendido

            fila_atendidos_items["atendido"] = (
                Atendido.from_sqlalchemy(schema.atendido, shallow=True)
                if schema.atendido
                else None
            )
        else:
            fila_atendidos_items["atendido"] = None

        return FilaAtendidos(**fila_atendidos_items)
