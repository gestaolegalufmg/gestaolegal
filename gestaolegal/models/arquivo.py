from dataclasses import dataclass
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class Arquivo(BaseModel):
    id: int
    titulo: str
    descricao: str | None
    nome: str

    blob: bytes | None = None

    def __post_init__(self):
        return
