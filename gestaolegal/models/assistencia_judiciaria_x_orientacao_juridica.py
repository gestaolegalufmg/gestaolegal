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

    @staticmethod
    def from_sqlalchemy(
        assistencia_judiciaria_x_orientacao_juridica_schema: "AssistenciaJudiciaria_xOrientacaoJuridicaSchema",
    ) -> "AssistenciaJudiciaria_xOrientacaoJuridica":
        from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
        from gestaolegal.models.orientacao_juridica import OrientacaoJuridica

        assistencia_judiciaria_x_orientacao_juridica_items = (
            assistencia_judiciaria_x_orientacao_juridica_schema.to_dict()
        )
        assistencia_judiciaria_x_orientacao_juridica_items["assistenciaJudiciaria"] = (
            AssistenciaJudiciaria.from_sqlalchemy(
                assistencia_judiciaria_x_orientacao_juridica_schema.assistenciaJudiciaria
            )
            if assistencia_judiciaria_x_orientacao_juridica_schema.assistenciaJudiciaria
            else None
        )
        assistencia_judiciaria_x_orientacao_juridica_items["orientacaoJuridica"] = (
            OrientacaoJuridica.from_sqlalchemy(
                assistencia_judiciaria_x_orientacao_juridica_schema.orientacaoJuridica
            )
            if assistencia_judiciaria_x_orientacao_juridica_schema.orientacaoJuridica
            else None
        )
        return AssistenciaJudiciaria_xOrientacaoJuridica(
            **assistencia_judiciaria_x_orientacao_juridica_items
        )
