from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.usuario import Usuario

if TYPE_CHECKING:
    from gestaolegal.models.caso import Caso
    from gestaolegal.schemas.lembrete import LembreteSchema


@dataclass(frozen=True)
class Lembrete:
    id: int
    num_lembrete: int
    id_do_criador: int
    criador: "Usuario"
    id_caso: int
    caso: "Caso"
    id_usuario: int
    usuario: "Usuario"
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

            lembrete_items["criador"] = Usuario.from_sqlalchemy(schema.criador)
            lembrete_items["caso"] = Caso.from_sqlalchemy(schema.caso, shallow=True)
            lembrete_items["usuario"] = Usuario.from_sqlalchemy(schema.usuario)
        else:
            lembrete_items["criador"] = None
            lembrete_items["caso"] = None
            lembrete_items["usuario"] = None

        return Lembrete(**lembrete_items)
