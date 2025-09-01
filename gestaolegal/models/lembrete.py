from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.caso import Caso
    from gestaolegal.models.usuario import Usuario
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
    def from_sqlalchemy(lembrete: "LembreteSchema") -> "Lembrete":
        return Lembrete(
            id=lembrete.id,
            num_lembrete=lembrete.num_lembrete,
            id_do_criador=lembrete.id_do_criador,
            criador=lembrete.criador,
            id_caso=lembrete.id_caso,
            caso=lembrete.caso,
            id_usuario=lembrete.id_usuario,
            usuario=lembrete.usuario,
            data_criacao=lembrete.data_criacao,
            data_lembrete=lembrete.data_lembrete,
            descricao=lembrete.descricao,
            status=lembrete.status,
        )
