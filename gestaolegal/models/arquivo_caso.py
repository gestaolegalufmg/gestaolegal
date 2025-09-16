from dataclasses import dataclass
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    from gestaolegal.schemas.arquivo_caso import ArquivoCasoSchema


@dataclass(frozen=True)
class ArquivoCaso(BaseModel):
    id: int
    link_arquivo: str | None
    id_caso: int

    def __post_init__(self):
        return

    @classmethod
    def from_sqlalchemy(
        cls, schema: "ArquivoCasoSchema", shallow: bool = False
    ) -> "ArquivoCaso":
        arquivo_caso_items = schema.to_dict()
        return ArquivoCaso(**arquivo_caso_items)
