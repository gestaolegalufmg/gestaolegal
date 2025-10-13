from datetime import date
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    pass


class ProcessoCreateInput(BaseModel):
    especie: str
    numero: int | None = None
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


class ProcessoUpdateInput(BaseModel):
    especie: str | None = None
    numero: int | None = None
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
