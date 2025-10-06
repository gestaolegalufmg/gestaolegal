from gestaolegal.models.base_model import BaseModel


class AssistenciaJudiciariaCreateInput(BaseModel):
    nome: str
    regiao: str
    areas_atendidas: str
    telefone: str
    email: str
    logradouro: str
    numero: str
    complemento: str | None = None
    bairro: str
    cep: str
    cidade: str
    estado: str


class AssistenciaJudiciariaUpdateInput(BaseModel):
    nome: str | None = None
    regiao: str | None = None
    areas_atendidas: str | None = None
    telefone: str | None = None
    email: str | None = None
    logradouro: str | None = None
    numero: str | None = None
    complemento: str | None = None
    bairro: str | None = None
    cep: str | None = None
    cidade: str | None = None
    estado: str | None = None
