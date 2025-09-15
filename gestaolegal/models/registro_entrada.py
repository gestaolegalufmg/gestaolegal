from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.usuario import Usuario

if TYPE_CHECKING:
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
    def from_sqlalchemy(
        registro_entrada_schema: "RegistroEntradaSchema",
    ) -> "RegistroEntrada":
        registro_entrada_items = registro_entrada_schema.to_dict()
        registro_entrada_items["usuario"] = (
            Usuario.from_sqlalchemy(registro_entrada_schema.usuario)
            if registro_entrada_schema.usuario
            else None
        )
        return RegistroEntrada(**registro_entrada_items)
