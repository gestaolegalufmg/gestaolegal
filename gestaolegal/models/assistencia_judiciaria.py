from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    from gestaolegal.models.endereco import Endereco
    from gestaolegal.models.orientacao_juridica import OrientacaoJuridica


class AssistenciaJudiciaria(BaseModel):
    id: int | None = None
    nome: str
    regiao: str
    areas_atendidas: str
    endereco_id: int | None
    endereco: "Endereco | None" = None
    telefone: str
    email: str
    status: int
    orientacoes_juridicas: list["OrientacaoJuridica"] | None = None
