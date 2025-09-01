from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
    from gestaolegal.models.atendido import Atendido
    from gestaolegal.models.usuario import Usuario
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
        orientacao_juridica: "OrientacaoJuridicaSchema",
    ) -> "OrientacaoJuridica":
        return OrientacaoJuridica(
            id=orientacao_juridica.id,
            area_direito=orientacao_juridica.area_direito,
            sub_area=orientacao_juridica.sub_area,
            descricao=orientacao_juridica.descricao,
            data_criacao=orientacao_juridica.data_criacao,
            status=orientacao_juridica.status,
            assistencias_judiciarias=orientacao_juridica.assistenciasJudiciarias,
            atendidos=orientacao_juridica.atendidos,
            id_usuario=orientacao_juridica.id_usuario,
            usuario=orientacao_juridica.usuario,
        )
