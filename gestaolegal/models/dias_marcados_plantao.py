from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.usuario import Usuario
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
        dias_marcados_plantao: "DiasMarcadosPlantaoSchema",
    ) -> "DiasMarcadosPlantao":
        return DiasMarcadosPlantao(
            id=dias_marcados_plantao.id,
            data_marcada=dias_marcados_plantao.data_marcada,
            confirmacao=dias_marcados_plantao.confirmacao,
            status=dias_marcados_plantao.status,
            id_usuario=dias_marcados_plantao.id_usuario,
            usuario=dias_marcados_plantao.usuario,
        )
