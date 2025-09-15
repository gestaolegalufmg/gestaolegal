from dataclasses import dataclass
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    from gestaolegal.schemas.arquivo import ArquivoSchema


@dataclass(frozen=True)
class Arquivo(BaseModel):
    id: int
    titulo: str
    descricao: str | None
    nome: str

    blob: bytes | None = None

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(self, arquivo_schema: "ArquivoSchema") -> "Arquivo":
        arquivo_items = arquivo_schema.to_dict()
        return Arquivo(**arquivo_items)
