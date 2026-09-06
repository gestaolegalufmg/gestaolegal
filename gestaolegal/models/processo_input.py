from datetime import date
from typing import TYPE_CHECKING

from pydantic import Field, field_validator

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    pass


class ProcessoNumeroInput(BaseModel):
    numero: str | None = Field(default=None, max_length=25)

    @field_validator("numero", mode="before")
    @classmethod
    def normalizar_numero(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip() or None
        return value


class ProcessoCreateInput(ProcessoNumeroInput):
    especie: str
    identificacao: str | None = None
    vara: str | None = None
    link: str | None = None
    probabilidade: str | None = None
    posicao_assistido: str | None = None
    valor_causa_inicial: int | None = None
    valor_causa_atual: int | None = None
    data_distribuicao: date | None = None
    data_transito_em_julgado: date | None = None
    obs: str | None = None
    id_caso: int | None = None
    status: bool = True


class ProcessoUpdateInput(ProcessoNumeroInput):
    especie: str | None = None
    identificacao: str | None = None
    vara: str | None = None
    link: str | None = None
    probabilidade: str | None = None
    posicao_assistido: str | None = None
    valor_causa_inicial: int | None = None
    valor_causa_atual: int | None = None
    data_distribuicao: date | None = None
    data_transito_em_julgado: date | None = None
    obs: str | None = None
    id_caso: int | None = None
    status: bool | None = None
