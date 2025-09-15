from dataclasses import dataclass
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    from gestaolegal.schemas.endereco import EnderecoSchema


@dataclass(frozen=True)
class Endereco(BaseModel):
    id: int
    logradouro: str
    numero: str
    complemento: str | None
    bairro: str
    cep: str
    cidade: str
    estado: str

    def __post_init__(self):
        return

    @classmethod
    def from_sqlalchemy(
        cls, schema: "EnderecoSchema", shallow: bool = False
    ) -> "Endereco":
        endereco_items = schema.to_dict()
        return Endereco(**endereco_items)

    def to_dict(self, *args, **kwargs):
        data = super().to_dict(*args, **kwargs)
        data["endereco_id"] = data.pop("id")
        return data
