from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
    from gestaolegal.models.atendido import Atendido
    from gestaolegal.models.user import User


class OrientacaoJuridica(BaseModel):
    area_direito: str
    sub_area: str | None
    descricao: str
    atendidos: list["Atendido"] | None = None
    usuario: "User | None" = None
    assistencias_judiciarias: list["AssistenciaJudiciaria"] | None = None

    id: int | None = None
    id_usuario: int | None = None
    status: int = 1
    data_criacao: datetime = datetime.now()


@dataclass
class OrientacaoJuridicaDetail:
    id: int
    area_direito: str
    sub_area: str | None
    data_criacao: datetime
    status: bool
    atendidos: list["Atendido"]
    descricao: str
    usuario: "User | None"


@dataclass
class OrientacaoJuridicaListItem:
    id: int
    area_direito: str
    sub_area: str | None
    descricao: str
    atendidos: list[str]
    usuario: "User | None"
    data_criacao: datetime
    status: bool
