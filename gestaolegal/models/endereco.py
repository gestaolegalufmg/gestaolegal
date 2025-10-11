from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass
class Endereco:
    logradouro: str
    numero: str
    complemento: str | None
    bairro: str
    cep: str
    cidade: str
    estado: str

    id: int | None = None
