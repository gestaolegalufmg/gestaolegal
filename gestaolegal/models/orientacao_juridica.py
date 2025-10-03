from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.user import User

if TYPE_CHECKING:
    from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
    from gestaolegal.models.atendido import Atendido


@dataclass(frozen=True)
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

    def __post_init__(self):
        return

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrientacaoJuridica":
        return OrientacaoJuridica(**data)
