from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.orientacao_juridica import OrientacaoJuridica
    from gestaolegal.schemas.atendido import AtendidoSchema
    from gestaolegal.schemas.atendido_x_orientacao_juridica import (
        Atendido_xOrientacaoJuridicaSchema,
    )


@dataclass(frozen=True)
class Atendido_xOrientacaoJuridica:
    id: int
    id_orientacaoJuridica: int
    id_atendido: int
    atendido: "AtendidoSchema | None"
    orientacaoJuridica: "OrientacaoJuridica | None"

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(
        atendido_x_orientacao_juridica: "Atendido_xOrientacaoJuridicaSchema",
    ) -> "Atendido_xOrientacaoJuridica":
        if not atendido_x_orientacao_juridica:
            raise ValueError("atendido_x_orientacao_juridica cannot be None")
        
        return Atendido_xOrientacaoJuridica(
            id=atendido_x_orientacao_juridica.id or 0,
            id_orientacaoJuridica=atendido_x_orientacao_juridica.id_orientacaoJuridica or 0,
            id_atendido=atendido_x_orientacao_juridica.id_atendido or 0,
            atendido=atendido_x_orientacao_juridica.atendido or None,
            orientacaoJuridica=atendido_x_orientacao_juridica.orientacaoJuridica or None,
        )
