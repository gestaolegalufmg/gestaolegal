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

    @staticmethod
    def from_sqlalchemy(lembrete_schema: "LembreteSchema") -> "Lembrete":
        from gestaolegal.models.caso import Caso

        lembrete_items = lembrete_schema.to_dict()
        lembrete_items["criador"] = Usuario.from_sqlalchemy(lembrete_schema.criador)
        lembrete_items["caso"] = Caso.from_sqlalchemy(lembrete_schema.caso)
        lembrete_items["usuario"] = Usuario.from_sqlalchemy(lembrete_schema.usuario)
        return Lembrete(**lembrete_items)
