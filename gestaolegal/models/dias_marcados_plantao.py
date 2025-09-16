from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.usuario import Usuario

if TYPE_CHECKING:
    from gestaolegal.schemas.dias_marcados_plantao import DiasMarcadosPlantaoSchema


@dataclass(frozen=True)
class DiasMarcadosPlantao(BaseModel):
    id: int
    data_marcada: date | None
    confirmacao: str
    status: bool
    id_usuario: int | None
    usuario: "Usuario | None"

    def __post_init__(self):
        return

    @classmethod
    def from_sqlalchemy(
        cls, schema: "DiasMarcadosPlantaoSchema", shallow: bool = False
    ) -> "DiasMarcadosPlantao":
        dias_marcados_plantao_items = schema.to_dict()

        if not shallow:
            dias_marcados_plantao_items["usuario"] = (
                Usuario.from_sqlalchemy(schema.usuario) if schema.usuario else None
            )
        else:
            dias_marcados_plantao_items["usuario"] = None

        return DiasMarcadosPlantao(**dias_marcados_plantao_items)
