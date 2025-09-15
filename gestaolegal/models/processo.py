from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from gestaolegal.models.usuario import Usuario

if TYPE_CHECKING:
    from gestaolegal.models.caso import Caso
    from gestaolegal.schemas.processo import ProcessoSchema


@dataclass(frozen=True)
class Processo:
    id: int
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
    caso: "Caso"
    status: bool
    id_criado_por: int
    criado_por: "Usuario"

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(processo_schema: "ProcessoSchema") -> "Processo":
        from gestaolegal.models.caso import Caso

        processo_items = processo_schema.to_dict()
        processo_items["caso"] = Caso.from_sqlalchemy(processo_schema.caso)
        processo_items["criado_por"] = Usuario.from_sqlalchemy(
            processo_schema.criado_por
        )
        return Processo(**processo_items)
