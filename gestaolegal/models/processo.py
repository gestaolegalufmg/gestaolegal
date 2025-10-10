from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.caso import Caso
    from gestaolegal.models.user import User


@dataclass
class Processo:
    especie: str
    id_caso: int
    status: bool
    id_criado_por: int

    id: int | None = None
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
    caso: "Caso | None" = None
    criado_por: "User | None" = None
