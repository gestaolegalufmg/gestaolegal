from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.schemas.arquivo_caso import ArquivoCasoSchema


@dataclass(frozen=True)
class ArquivoCaso:
    id: int
    link_arquivo: str | None
    id_caso: int

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(arquivo_caso: "ArquivoCasoSchema") -> "ArquivoCaso":
        return ArquivoCaso(
            id=arquivo_caso.id,
            link_arquivo=arquivo_caso.link_arquivo,
            id_caso=arquivo_caso.id_caso,
        )
