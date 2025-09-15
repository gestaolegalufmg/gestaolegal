from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.usuario import Usuario

if TYPE_CHECKING:
    from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
    from gestaolegal.models.atendido import Atendido
    from gestaolegal.schemas.orientacao_juridica import OrientacaoJuridicaSchema


@dataclass(frozen=True)
class OrientacaoJuridica:
    id: int
    area_direito: str
    sub_area: str | None
    descricao: str
    data_criacao: datetime | None
    status: int
    assistencias_judiciarias: list["AssistenciaJudiciaria"]
    atendidos: list["Atendido"]
    id_usuario: int | None
    usuario: "Usuario | None"

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(
        orientacao_juridica_schema: "OrientacaoJuridicaSchema",
    ) -> "OrientacaoJuridica":
        from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
        from gestaolegal.models.atendido import Atendido

        orientacao_juridica_items = orientacao_juridica_schema.to_dict()
        orientacao_juridica_items["assistencias_judiciarias"] = (
            [
                AssistenciaJudiciaria.from_sqlalchemy(aj)
                for aj in orientacao_juridica_schema.assistencias_judiciarias
            ]
            if orientacao_juridica_schema.assistencias_judiciarias
            else []
        )
        orientacao_juridica_items["atendidos"] = (
            [
                Atendido.from_sqlalchemy(atendido)
                for atendido in orientacao_juridica_schema.atendidos
            ]
            if orientacao_juridica_schema.atendidos
            else []
        )
        orientacao_juridica_items["usuario"] = (
            Usuario.from_sqlalchemy(orientacao_juridica_schema.usuario)
            if orientacao_juridica_schema.usuario
            else None
        )
        return OrientacaoJuridica(**orientacao_juridica_items)
