from dataclasses import dataclass, field
from datetime import date, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.caso import Caso
    from gestaolegal.models.user import UserInfo


@dataclass
class ArquivoEvento:
    id: int
    nome: str


@dataclass
class Evento:
    id_caso: int
    tipo: str
    data_evento: date
    data_criacao: datetime
    id_criado_por: int
    status: bool

    id: int | None = None
    unidade_id: int | None = None
    num_evento: int | None = None
    descricao: str | None = None
    arquivos: list[ArquivoEvento] = field(default_factory=list)
    id_usuario_responsavel: int | None = None
    caso: "Caso | None" = None
    criado_por: "UserInfo | None" = None
    usuario_responsavel: "UserInfo | None" = None


@dataclass
class ListEvento:
    id: int
    tipo: str
    data_evento: date
    data_criacao: datetime
    status: bool

    criado_por: str | None = None
    id_criado_por: int | None = None
    usuario_responsavel: str | None = None
    num_evento: int | None = None
    descricao: str | None = None
