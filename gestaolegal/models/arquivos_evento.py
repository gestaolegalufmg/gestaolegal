from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.schemas.arquivos_evento import ArquivosEventoSchema


@dataclass(frozen=True)
class ArquivosEvento:
    id: int
    id_evento: int
    id_caso: int
    link_arquivo: str | None

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(arquivos_evento: "ArquivosEventoSchema") -> "ArquivosEvento":
        return ArquivosEvento(
            id=arquivos_evento.id,
            id_evento=arquivos_evento.id_evento,
            id_caso=arquivos_evento.id_caso,
            link_arquivo=arquivos_evento.link_arquivo,
        )
