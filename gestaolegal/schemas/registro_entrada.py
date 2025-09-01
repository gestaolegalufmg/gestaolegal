from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gestaolegal.schemas.base import Base

if TYPE_CHECKING:
    from gestaolegal.schemas.usuario import UsuarioSchema


class RegistroEntradaSchema(Base):
    __tablename__ = "registro_entrada"

    id: Mapped[int] = mapped_column(primary_key=True)
    data_entrada: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    data_saida: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    confirmacao: Mapped[str] = mapped_column(
        String(15, collation="latin1_general_ci"), nullable=False, default="aberto"
    )
    id_usuario: Mapped[int | None] = mapped_column(Integer, ForeignKey("usuarios.id"))
    usuario: Mapped["UsuarioSchema | None"] = relationship(
        "UsuarioSchema", backref="registro_entrada"
    )
