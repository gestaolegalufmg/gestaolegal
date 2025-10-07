from datetime import date
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    from gestaolegal.models.caso import Caso
    from gestaolegal.models.user import User


class Processo(BaseModel):
    id: int | None = None

    especie: str
    numero: int | None
    identificacao: str | None
    vara: str | None
    link: str | None
    probabilidade: str | None
    posicao_assistido: str | None
    valor_causa_inicial: int | None
    valor_causa_atual: int | None
    data_distribuicao: date | None
    data_transito_em_julgado: date | None
    obs: str | None

    id_caso: int
    caso: "Caso | None" = None

    status: bool
    id_criado_por: int
    criado_por: "User | None" = None
