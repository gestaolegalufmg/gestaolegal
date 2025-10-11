from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.atendido import Atendido
    from gestaolegal.models.processo import Processo
    from gestaolegal.models.user import User


@dataclass
class Caso:
    id_usuario_responsavel: int
    area_direito: str
    data_criacao: datetime
    id_criado_por: int
    situacao_deferimento: str
    status: bool

    id: int | None = None
    sub_area: str | None = None
    id_orientador: int | None = None
    id_estagiario: int | None = None
    id_colaborador: int | None = None
    data_modificacao: datetime | None = None
    id_modificado_por: int | None = None
    justif_indeferimento: str | None = None
    descricao: str | None = None
    numero_ultimo_processo: int | None = None
    usuario_responsavel: "User | None" = None
    clientes: list["Atendido"] | None = None
    orientador: "User | None" = None
    estagiario: "User | None" = None
    colaborador: "User | None" = None
    criado_por: "User | None" = None
    modificado_por: "User | None" = None
    processos: list["Processo"] | None = None
