from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
    from gestaolegal.models.orientacao_juridica import OrientacaoJuridica


@dataclass(frozen=True)
class AssistenciaJudiciaria_xOrientacaoJuridica:
    id: int
    id_orientacaoJuridica: int
    id_assistenciaJudiciaria: int
    assistenciaJudiciaria: "AssistenciaJudiciaria"
    orientacaoJuridica: "OrientacaoJuridica"

    def __post_init__(self):
        return
