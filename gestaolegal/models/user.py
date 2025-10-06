from datetime import date, datetime
from typing import Literal

from dateutil.parser import parse as parse_date
from pydantic import field_validator

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.endereco import Endereco


class User(BaseModel):
    email: str
    senha: str
    urole: Literal["admin", "colab_proj", "orient", "estag_direito", "colab_ext"]
    nome: str
    sexo: str
    rg: str
    cpf: str
    profissao: str
    estado_civil: str
    nascimento: date
    telefone: str | None
    celular: str
    oab: str | None
    obs: str | None
    data_entrada: date
    data_saida: date | None
    criadopor: int
    matricula: str | None
    modificadopor: int | None
    bolsista: bool
    tipo_bolsa: str | None
    horario_atendimento: str | None
    suplente: str | None
    ferias: str | None
    cert_atuacao_DAJ: str
    inicio_bolsa: datetime | None
    fim_bolsa: datetime | None
    endereco_id: int

    id: int | None = None

    chave_recuperacao: bool | None = None
    endereco: "Endereco | None" = None
    status: bool = True

    modificado: datetime = datetime.now()
    criado: datetime = datetime.now()

    @field_validator("nascimento", mode="before")
    def parse_nascimento_rfc(cls, v):
        if isinstance(v, str):
            try:
                return parse_date(v).date()
            except Exception:
                pass
        return v

    @field_validator("data_entrada", mode="before")
    def parse_data_entrada_rfc(cls, v):
        if isinstance(v, str):
            try:
                return parse_date(v).date()
            except Exception:
                pass
        return v

    @field_validator("data_saida", mode="before")
    def parse_data_saida_rfc(cls, v):
        if isinstance(v, str):
            try:
                return parse_date(v).date()
            except Exception:
                pass
        return v
