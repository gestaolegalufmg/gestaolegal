from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gestaolegal.schemas.base import Base

if TYPE_CHECKING:
    from gestaolegal.schemas.assistencia_judiciaria import AssistenciaJudiciariaSchema
    from gestaolegal.schemas.atendido import AtendidoSchema
    from gestaolegal.schemas.usuario import UsuarioSchema


class EnderecoSchema(Base):
    __tablename__ = "enderecos"

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

    # Relationships
    usuarios: Mapped[list["UsuarioSchema"]] = relationship(
        "UsuarioSchema", back_populates="endereco"
    )
    atendidos: Mapped[list["AtendidoSchema"]] = relationship(
        "AtendidoSchema", back_populates="endereco"
    )
    assistencias_judiciarias: Mapped[list["AssistenciaJudiciariaSchema"]] = (
        relationship("AssistenciaJudiciariaSchema", back_populates="endereco")
    )
