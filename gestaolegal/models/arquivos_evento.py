from dataclasses import dataclass
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    from gestaolegal.schemas.arquivos_evento import ArquivosEventoSchema


@dataclass(frozen=True)
class ArquivosEvento(BaseModel):
    id: int
    id_evento: int
    id_caso: int
    link_arquivo: str | None

    def __post_init__(self):
        return

    @classmethod
    def from_sqlalchemy(
        cls, schema: "ArquivosEventoSchema", shallow: bool = False
    ) -> "ArquivosEvento":
        arquivos_evento_items = schema.to_dict()
        return ArquivosEvento(**arquivos_evento_items)
