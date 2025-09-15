from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.caso import Caso
from gestaolegal.models.usuario import Usuario

if TYPE_CHECKING:
    from gestaolegal.schemas.historico import HistoricoSchema


@dataclass(frozen=True)
class Historico:
    id: int
    id_usuario: int
    usuario: "Usuario"
    id_caso: int
    caso: "Caso"
    data: datetime

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(historico_schema: "HistoricoSchema") -> "Historico":
        historico_items = historico_schema.to_dict()
        historico_items["usuario"] = (
            Usuario.from_sqlalchemy(historico_schema.usuario)
            if historico_schema.usuario
            else None
        )
        historico_items["caso"] = (
            Caso.from_sqlalchemy(historico_schema.caso)
            if historico_schema.caso
            else None
        )
        return Historico(**historico_items)
