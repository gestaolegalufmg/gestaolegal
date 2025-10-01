from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.user import User

if TYPE_CHECKING:
    from gestaolegal.models.caso import Caso
    from gestaolegal.schemas.lembrete import LembreteSchema


@dataclass(frozen=True)
class Lembrete(BaseModel):
    id: int
    num_lembrete: int
    id_do_criador: int
    criador: "User"
    id_caso: int
    caso: "Caso"
    id_usuario: int
    usuario: "User"
    data_criacao: datetime
    data_lembrete: datetime
    descricao: str
    status: bool

    def __post_init__(self):
        return

    @classmethod
    def from_sqlalchemy(
        cls, schema: "LembreteSchema", shallow: bool = False
    ) -> "Lembrete":
        lembrete_items = schema.to_dict()

        if not shallow:
            from gestaolegal.models.caso import Caso

            lembrete_items["criador"] = User.from_sqlalchemy(schema.criador)
            lembrete_items["caso"] = Caso.from_sqlalchemy(schema.caso, shallow=True)
            lembrete_items["usuario"] = User.from_sqlalchemy(schema.usuario)
        else:
            lembrete_items["criador"] = None
            lembrete_items["caso"] = None
            lembrete_items["usuario"] = None

        return Lembrete(**lembrete_items)
