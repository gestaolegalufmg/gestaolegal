from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.usuario import Usuario

if TYPE_CHECKING:
    from gestaolegal.schemas.registro_entrada import RegistroEntradaSchema


@dataclass(frozen=True)
class RegistroEntrada(BaseModel):
    id: int
    data_entrada: datetime
    data_saida: datetime
    status: bool
    confirmacao: str
    id_usuario: int | None
    usuario: "Usuario | None"

    def __post_init__(self):
        return

    @classmethod
    def from_sqlalchemy(
        cls, schema: "RegistroEntradaSchema", shallow: bool = False
    ) -> "RegistroEntrada":
        registro_entrada_items = schema.to_dict()

        if not shallow:
            registro_entrada_items["usuario"] = (
                Usuario.from_sqlalchemy(schema.usuario) if schema.usuario else None
            )
        else:
            registro_entrada_items["usuario"] = None

        return RegistroEntrada(**registro_entrada_items)
