from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from gestaolegal.models.usuario import Usuario

if TYPE_CHECKING:
    from gestaolegal.schemas.dias_marcados_plantao import DiasMarcadosPlantaoSchema


@dataclass(frozen=True)
class DiasMarcadosPlantao:
    id: int
    data_marcada: date | None
    confirmacao: str
    status: bool
    id_usuario: int | None
    usuario: "Usuario | None"

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(
        dias_marcados_plantao_schema: "DiasMarcadosPlantaoSchema",
    ) -> "DiasMarcadosPlantao":
        dias_marcados_plantao_items = dias_marcados_plantao_schema.to_dict()
        dias_marcados_plantao_items["usuario"] = (
            Usuario.from_sqlalchemy(dias_marcados_plantao_schema.usuario)
            if dias_marcados_plantao_schema.usuario
            else None
        )
        return DiasMarcadosPlantao(**dias_marcados_plantao_items)
