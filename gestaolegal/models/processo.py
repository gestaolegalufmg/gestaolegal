from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.user import User

if TYPE_CHECKING:
    from gestaolegal.models.caso import Caso
    from gestaolegal.schemas.processo import ProcessoSchema


@dataclass(frozen=True)
class Processo(BaseModel):
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
    criado_por: "User"

    def __post_init__(self):
        return

    @classmethod
    def from_sqlalchemy(
        cls, schema: "ProcessoSchema", shallow: bool = False
    ) -> "Processo":
        processo_items = schema.to_dict()

        if not shallow:
            from gestaolegal.models.caso import Caso

            processo_items["caso"] = Caso.from_sqlalchemy(schema.caso, shallow=True)
            processo_items["criado_por"] = User.from_sqlalchemy(schema.criado_por)
        else:
            processo_items["caso"] = None
            processo_items["criado_por"] = None

        return Processo(**processo_items)
