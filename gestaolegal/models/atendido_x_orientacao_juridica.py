from dataclasses import dataclass
from typing import TYPE_CHECKING

from gestaolegal.models.atendido import Atendido
from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    from gestaolegal.models.orientacao_juridica import OrientacaoJuridica
    from gestaolegal.schemas.atendido import AtendidoSchema
    from gestaolegal.schemas.atendido_x_orientacao_juridica import (
        Atendido_xOrientacaoJuridicaSchema,
    )


@dataclass(frozen=True)
class Atendido_xOrientacaoJuridica(BaseModel):
    id: int
    id_orientacaoJuridica: int
    id_atendido: int
    atendido: "AtendidoSchema | None"
    orientacaoJuridica: "OrientacaoJuridica | None"

    def __post_init__(self):
        return

    @classmethod
    def from_sqlalchemy(
        cls, schema: "Atendido_xOrientacaoJuridicaSchema", shallow: bool = False
    ) -> "Atendido_xOrientacaoJuridica":
        from gestaolegal.models.orientacao_juridica import OrientacaoJuridica

        atendido_x_orientacao_juridica_items = schema.to_dict()

        if not shallow:
            atendido_x_orientacao_juridica_items["atendido"] = (
                Atendido.from_sqlalchemy(schema.atendido, shallow=True)
                if schema.atendido
                else None
            )
            atendido_x_orientacao_juridica_items["orientacaoJuridica"] = (
                OrientacaoJuridica.from_sqlalchemy(
                    schema.orientacaoJuridica, shallow=True
                )
                if schema.orientacaoJuridica
                else None
            )
        else:
            atendido_x_orientacao_juridica_items["atendido"] = None
            atendido_x_orientacao_juridica_items["orientacaoJuridica"] = None

        return Atendido_xOrientacaoJuridica(**atendido_x_orientacao_juridica_items)
