from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
    from gestaolegal.models.orientacao_juridica import OrientacaoJuridica
    from gestaolegal.schemas.assistencia_judiciaria_x_orientacao_juridica import (
        AssistenciaJudiciaria_xOrientacaoJuridicaSchema,
    )


@dataclass(frozen=True)
class AssistenciaJudiciaria_xOrientacaoJuridica:
    id: int
    id_orientacaoJuridica: int
    id_assistenciaJudiciaria: int
    assistenciaJudiciaria: "AssistenciaJudiciaria"
    orientacaoJuridica: "OrientacaoJuridica"

    def __post_init__(self):
        return

    @classmethod
    def from_sqlalchemy(
        cls,
        schema: "AssistenciaJudiciaria_xOrientacaoJuridicaSchema",
        shallow: bool = False,
    ) -> "AssistenciaJudiciaria_xOrientacaoJuridica":
        assistencia_judiciaria_x_orientacao_juridica_items = schema.to_dict()

        if not shallow:
            from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
            from gestaolegal.models.orientacao_juridica import OrientacaoJuridica

            assistencia_judiciaria_x_orientacao_juridica_items[
                "assistenciaJudiciaria"
            ] = (
                AssistenciaJudiciaria.from_sqlalchemy(
                    schema.assistenciaJudiciaria, shallow=True
                )
                if schema.assistenciaJudiciaria
                else None
            )
            assistencia_judiciaria_x_orientacao_juridica_items["orientacaoJuridica"] = (
                OrientacaoJuridica.from_sqlalchemy(
                    schema.orientacaoJuridica, shallow=True
                )
                if schema.orientacaoJuridica
                else None
            )
        else:
            assistencia_judiciaria_x_orientacao_juridica_items[
                "assistenciaJudiciaria"
            ] = None
            assistencia_judiciaria_x_orientacao_juridica_items["orientacaoJuridica"] = (
                None
            )

        return AssistenciaJudiciaria_xOrientacaoJuridica(
            **assistencia_judiciaria_x_orientacao_juridica_items
        )
