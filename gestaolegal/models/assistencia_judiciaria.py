from dataclasses import dataclass
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.endereco import Endereco
from gestaolegal.models.orientacao_juridica import OrientacaoJuridica

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class AssistenciaJudiciaria(BaseModel):
    id: int
    nome: str
    regiao: str
    areas_atendidas: str
    endereco_id: int | None
    endereco: "Endereco | None"
    telefone: str
    email: str
    status: int
    orientacoes_juridicas: list["OrientacaoJuridica"]

    def __post_init__(self):
        return
