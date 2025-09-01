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
        assistencia_judiciaria_x_orientacao_juridica: "AssistenciaJudiciaria_xOrientacaoJuridicaSchema",
    ) -> "AssistenciaJudiciaria_xOrientacaoJuridica":
        return AssistenciaJudiciaria_xOrientacaoJuridica(
            id=assistencia_judiciaria_x_orientacao_juridica.id,
            id_orientacaoJuridica=assistencia_judiciaria_x_orientacao_juridica.id_orientacaoJuridica,
            id_assistenciaJudiciaria=assistencia_judiciaria_x_orientacao_juridica.id_assistenciaJudiciaria,
            assistenciaJudiciaria=assistencia_judiciaria_x_orientacao_juridica.assistenciaJudiciaria,
            orientacaoJuridica=assistencia_judiciaria_x_orientacao_juridica.orientacaoJuridica,
        )
