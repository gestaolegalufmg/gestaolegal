from dataclasses import dataclass
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class Endereco(BaseModel):
    logradouro: str
    numero: str
    complemento: str | None
    bairro: str
    cep: str
    cidade: str
    estado: str

    id: int | None = None

    def __post_init__(self):
        return

    def to_dict(self, *args, **kwargs):
        data = super().to_dict(*args, **kwargs)
        data.pop("id")
        return data
