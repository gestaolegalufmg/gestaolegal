from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
    from gestaolegal.models.orientacao_juridica import OrientacaoJuridica


class AssistenciaJudiciaria_xOrientacaoJuridica(BaseModel):
    id: int
    id_orientacaoJuridica: int
    id_assistenciaJudiciaria: int
    assistenciaJudiciaria: "AssistenciaJudiciaria"
    orientacaoJuridica: "OrientacaoJuridica"
