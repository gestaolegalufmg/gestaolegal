from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gestaolegal.schemas.base import Base

if TYPE_CHECKING:
    from gestaolegal.schemas.endereco import EnderecoSchema


class UserSchema(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(80, collation="latin1_general_ci"), unique=True, nullable=False
    )
    senha: Mapped[str] = mapped_column(
        String(60, collation="latin1_general_ci"), nullable=False
    )
    urole: Mapped[str] = mapped_column(
        String(50, collation="latin1_general_ci"), nullable=False
    )
    nome: Mapped[str] = mapped_column(
        String(60, collation="latin1_general_ci"), nullable=False
    )
    sexo: Mapped[str] = mapped_column(
        String(60, collation="latin1_general_ci"), nullable=False
    )
    rg: Mapped[str] = mapped_column(
        String(18, collation="latin1_general_ci"), nullable=False
    )
    cpf: Mapped[str] = mapped_column(
        String(14, collation="latin1_general_ci"), nullable=False
    )
    profissao: Mapped[str] = mapped_column(
        String(45, collation="latin1_general_ci"), nullable=False
    )
    estado_civil: Mapped[str] = mapped_column(
        String(45, collation="latin1_general_ci"), nullable=False
    )
    nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    telefone: Mapped[str] = mapped_column(String(18, collation="latin1_general_ci"))
    celular: Mapped[str] = mapped_column(
        String(18, collation="latin1_general_ci"), nullable=False
    )
    oab: Mapped[str] = mapped_column(String(30, collation="latin1_general_ci"))
    obs: Mapped[str] = mapped_column(Text(collation="latin1_general_ci"))
    data_entrada: Mapped[date] = mapped_column(Date, nullable=False)
    data_saida: Mapped[date | None] = mapped_column(Date, nullable=True)
    criado: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    modificado: Mapped[datetime | None] = mapped_column(DateTime)
    criadopor: Mapped[int] = mapped_column(Integer, nullable=False)
    matricula: Mapped[str] = mapped_column(String(45, collation="latin1_general_ci"))
    modificadopor: Mapped[int | None] = mapped_column(Integer)
    bolsista: Mapped[bool] = mapped_column(Boolean, nullable=False)
    tipo_bolsa: Mapped[str] = mapped_column(String(50, collation="latin1_general_ci"))
    horario_atendimento: Mapped[str] = mapped_column(
        String(30, collation="latin1_general_ci")
    )
    suplente: Mapped[str] = mapped_column(String(30, collation="latin1_general_ci"))
    ferias: Mapped[str] = mapped_column(String(150, collation="latin1_general_ci"))
    status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    cert_atuacao_DAJ: Mapped[str] = mapped_column(
        String(3, collation="latin1_general_ci"), nullable=False, default="nao"
    )
    inicio_bolsa: Mapped[datetime | None] = mapped_column(DateTime)
    fim_bolsa: Mapped[datetime | None] = mapped_column(DateTime)
    endereco_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("enderecos.id"))
    endereco: Mapped["EnderecoSchema"] = relationship(
        "EnderecoSchema", back_populates="usuarios"
    )
    chave_recuperacao: Mapped[bool] = mapped_column(
        Boolean, server_default=false(), nullable=True
    )
