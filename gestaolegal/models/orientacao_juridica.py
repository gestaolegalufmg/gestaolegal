from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.user import User

if TYPE_CHECKING:
    from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
    from gestaolegal.models.atendido import Atendido
    from gestaolegal.schemas.orientacao_juridica import OrientacaoJuridicaSchema


@dataclass(frozen=True)
class OrientacaoJuridica(BaseModel):
    id: int
    area_direito: str
    sub_area: str | None
    descricao: str
    data_criacao: datetime | None
    status: int
    assistencias_judiciarias: list["AssistenciaJudiciaria"]
    atendidos: list["Atendido"]
    id_usuario: int | None
    usuario: "User | None"

    def __post_init__(self):
        return

    @classmethod
    def from_sqlalchemy(
        cls, schema: "OrientacaoJuridicaSchema", shallow: bool = False
    ) -> "OrientacaoJuridica":
        orientacao_juridica_items = schema.to_dict()

        if not shallow:
            from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
            from gestaolegal.models.atendido import Atendido

            orientacao_juridica_items["assistencias_judiciarias"] = [
                AssistenciaJudiciaria.from_sqlalchemy(aj)
                for aj in schema.assistenciasJudiciarias
                if aj is not None
            ]
            orientacao_juridica_items["atendidos"] = [
                Atendido.from_sqlalchemy(atendido, shallow=True)
                for atendido in schema.atendidos
                if atendido is not None
            ]
            orientacao_juridica_items["usuario"] = (
                User.from_sqlalchemy(schema.usuario) if schema.usuario else None
            )
        else:
            orientacao_juridica_items["assistencias_judiciarias"] = []
            orientacao_juridica_items["atendidos"] = []
            orientacao_juridica_items["usuario"] = None

        return OrientacaoJuridica(**orientacao_juridica_items)
