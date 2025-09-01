from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.schemas.arquivo import ArquivoSchema


@dataclass(frozen=True)
class Arquivo:
    id: int
    titulo: str
    descricao: str | None
    nome: str

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(arquivo: "ArquivoSchema") -> "Arquivo":
        return Arquivo(
            id=arquivo.id,
            titulo=arquivo.titulo,
            descricao=arquivo.descricao,
            nome=arquivo.nome,
        )
