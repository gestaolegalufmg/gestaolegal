from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.caso import Caso
from gestaolegal.models.usuario import Usuario

if TYPE_CHECKING:
    from gestaolegal.schemas.historico import HistoricoSchema


@dataclass(frozen=True)
class Historico(BaseModel):
    id: int
    id_usuario: int
    usuario: "Usuario"
    id_caso: int
    caso: "Caso"
    data: datetime

    def __post_init__(self):
        return

    @classmethod
    def from_sqlalchemy(
        cls, schema: "HistoricoSchema", shallow: bool = False
    ) -> "Historico":
        historico_items = schema.to_dict()

        if not shallow:
            historico_items["usuario"] = (
                Usuario.from_sqlalchemy(schema.usuario) if schema.usuario else None
            )
            historico_items["caso"] = (
                Caso.from_sqlalchemy(schema.caso, shallow=True) if schema.caso else None
            )
        else:
            historico_items["usuario"] = None
            historico_items["caso"] = None

        return Historico(**historico_items)
