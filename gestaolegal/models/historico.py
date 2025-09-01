from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.caso import Caso
    from gestaolegal.models.usuario import Usuario
    from gestaolegal.schemas.historico import HistoricoSchema


@dataclass(frozen=True)
class Historico:
    id: int
    id_usuario: int
    usuario: "Usuario"
    id_caso: int
    caso: "Caso"
    data: datetime

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(historico: "HistoricoSchema") -> "Historico":
        return Historico(
            id=historico.id,
            id_usuario=historico.id_usuario,
            usuario=historico.usuario,
            id_caso=historico.id_caso,
            caso=historico.caso,
            data=historico.data,
        )
