from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gestaolegal.schemas.base import Base

if TYPE_CHECKING:
    from gestaolegal.schemas.usuario import UsuarioSchema


class DiasMarcadosPlantaoSchema(Base):
    __tablename__ = "dias_marcados_plantao"

    id: Mapped[int] = mapped_column(primary_key=True)
    data_marcada: Mapped[date | None] = mapped_column(Date)
    confirmacao: Mapped[str] = mapped_column(
        String(15, collation="latin1_general_ci"), nullable=False, default="aberto"
    )
    status: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)

    id_usuario: Mapped[int | None] = mapped_column(Integer, ForeignKey("usuarios.id"))
    usuario: Mapped["UsuarioSchema | None"] = relationship(
        "UsuarioSchema", backref="dias_marcados_plantao"
    )
