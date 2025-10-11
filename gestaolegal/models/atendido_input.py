from dataclasses import dataclass
from datetime import date

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.endereco import Endereco


@dataclass
class ListAtendido:
    id: int
    nome: str
    cpf: str
    telefone: str
    celular: str
    email: str
    data_nascimento: date
    status: bool
    is_assistido: bool

    endereco: Endereco


class AtendidoCreateInput(BaseModel):
    nome: str
    data_nascimento: date
    cpf: str
    cnpj: str | None = None
    telefone: str | None = None
    celular: str
    email: str
    estado_civil: str
    como_conheceu: str
    indicacao_orgao: str | None = None
    procurou_outro_local: str
    procurou_qual_local: str | None = None
    obs: str | None = None
    pj_constituida: str
    repres_legal: bool | None = None
    nome_repres_legal: str | None = None
    cpf_repres_legal: str | None = None
    contato_repres_legal: str | None = None
    rg_repres_legal: str | None = None
    nascimento_repres_legal: date | None = None
    pretende_constituir_pj: str | None = None

    endereco: Endereco | None = None


class AtendidoUpdateInput(BaseModel):
    nome: str | None = None
    data_nascimento: date | None = None
    cpf: str | None = None
    cnpj: str | None = None
    telefone: str | None = None
    celular: str | None = None
    email: str | None = None
    estado_civil: str | None = None
    como_conheceu: str | None = None
    indicacao_orgao: str | None = None
    procurou_outro_local: str | None = None
    procurou_qual_local: str | None = None
    obs: str | None = None
    pj_constituida: str | None = None
    repres_legal: bool | None = None
    nome_repres_legal: str | None = None
    cpf_repres_legal: str | None = None
    contato_repres_legal: str | None = None
    rg_repres_legal: str | None = None
    nascimento_repres_legal: date | None = None
    pretende_constituir_pj: str | None = None

    endereco: Endereco | None = None
