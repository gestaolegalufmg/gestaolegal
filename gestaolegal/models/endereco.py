from typing import Final

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from gestaolegal.schemas.base import Base


class Endereco(Base):
    __tablename__: Final = "enderecos"

    id: Mapped[int] = mapped_column(primary_key=True)
    logradouro: Mapped[str] = mapped_column(String(100, collation="latin1_general_ci"))
    numero: Mapped[str] = mapped_column(String(8, collation="latin1_general_ci"))
    complemento: Mapped[str | None] = mapped_column(
        String(100, collation="latin1_general_ci")
    )
    bairro: Mapped[str] = mapped_column(String(100, collation="latin1_general_ci"))
    cep: Mapped[str] = mapped_column(String(9, collation="latin1_general_ci"))
    cidade: Mapped[str] = mapped_column(String(100, collation="latin1_general_ci"))
    estado: Mapped[str] = mapped_column(String(100, collation="latin1_general_ci"))
