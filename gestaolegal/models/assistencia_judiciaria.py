from dataclasses import dataclass
from typing import TYPE_CHECKING

from gestaolegal.models.endereco import Endereco

if TYPE_CHECKING:
    pass


@dataclass
class AssistenciaJudiciaria:
    nome: str
    regiao: str
    areas_atendidas: str
    telefone: str
    email: str
    status: int
    id: int | None = None
    endereco_id: int | None = None

    endereco: Endereco | None = None


@dataclass
class OrientacaoJuridicaResumo:
    id: int
    area_direito: str
    sub_area: str | None
    descricao: str


@dataclass
class AssistenciaJudiciariaDetail:
    id: int
    nome: str
    regiao: str
    areas_atendidas: list[str]
    telefone: str
    email: str
    status: bool
    endereco: Endereco | None
    orientacoes: list[OrientacaoJuridicaResumo]


@dataclass
class AssistenciaJudiciariaListItem:
    id: int
    nome: str
    regiao: str
    areas_atendidas: list[str]
    telefone: str
    email: str
    status: bool
    cidade: str | None
