from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.usuario import Usuario
    from gestaolegal.schemas.registro_entrada import RegistroEntradaSchema


@dataclass(frozen=True)
class RegistroEntrada:
    id: int
    data_entrada: datetime
    data_saida: datetime
    status: bool
    confirmacao: str
    id_usuario: int | None
    usuario: "Usuario | None"

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(registro_entrada: "RegistroEntradaSchema") -> "RegistroEntrada":
        return RegistroEntrada(
            id=registro_entrada.id,
            data_entrada=registro_entrada.data_entrada,
            data_saida=registro_entrada.data_saida,
            status=registro_entrada.status,
            confirmacao=registro_entrada.confirmacao,
            id_usuario=registro_entrada.id_usuario,
            usuario=registro_entrada.usuario,
        )
