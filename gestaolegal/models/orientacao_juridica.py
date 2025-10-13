from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.atendido import Atendido
    from gestaolegal.models.user import UserInfo


@dataclass
class OrientacaoJuridica:
    area_direito: str
    sub_area: str | None
    descricao: str
    status: int
    data_criacao: datetime
    id: int | None = None
    id_usuario: int | None = None

    atendidos: list["Atendido"] | None = None
    usuario: "UserInfo | None" = None


@dataclass
class OrientacaoJuridicaDetail:
    id: int
    area_direito: str
    sub_area: str | None
    data_criacao: datetime
    status: bool
    atendidos: list["Atendido"]
    descricao: str
    usuario: "UserInfo | None"


@dataclass
class OrientacaoJuridicaListItem:
    id: int
    area_direito: str
    sub_area: str | None
    descricao: str
    atendidos: list[str]
    usuario: "UserInfo | None"
    data_criacao: datetime
    status: bool
