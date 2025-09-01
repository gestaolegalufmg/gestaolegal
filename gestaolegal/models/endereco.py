from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.schemas.endereco import EnderecoSchema


@dataclass(frozen=True)
class Endereco:
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

    @staticmethod
    def from_sqlalchemy(endereco: "EnderecoSchema") -> "Endereco":
        return Endereco(
            id=endereco.id,
            logradouro=endereco.logradouro,
            numero=endereco.numero,
            complemento=endereco.complemento,
            bairro=endereco.bairro,
            cep=endereco.cep,
            cidade=endereco.cidade,
            estado=endereco.estado,
        )
