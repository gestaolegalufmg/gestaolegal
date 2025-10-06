from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.user import User

if TYPE_CHECKING:
    from gestaolegal.models.atendido import Atendido


class Caso(BaseModel):
    id: int | None = None

    id_usuario_responsavel: int
    usuario_responsavel: "User | None" = None
    area_direito: str
    sub_area: str | None
    clientes: list["Atendido"] | None = None

    id_orientador: int | None
    orientador: "User | None" = None
    id_estagiario: int | None
    estagiario: "User | None" = None
    id_colaborador: int | None
    colaborador: "User | None" = None

    data_criacao: datetime
    id_criado_por: int
    criado_por: "User | None" = None

    data_modificacao: datetime | None
    id_modificado_por: int | None
    modificado_por: "User | None" = None

    situacao_deferimento: str
    justif_indeferimento: str | None
    status: bool
    descricao: str | None
    numero_ultimo_processo: int | None
