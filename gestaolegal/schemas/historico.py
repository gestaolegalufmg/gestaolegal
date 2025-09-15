from datetime import datetime
from typing import TYPE_CHECKING, Final

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gestaolegal.schemas.base import Base

if TYPE_CHECKING:
    from gestaolegal.schemas.caso import CasoSchema
    from gestaolegal.schemas.usuario import UsuarioSchema


class HistoricoSchema(Base):
    __tablename__ = "historicos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_usuario: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False
    )
    usuario: Mapped["UsuarioSchema"] = relationship("UsuarioSchema", lazy="joined")
    id_caso: Mapped[int] = mapped_column(
        Integer, ForeignKey("casos.id"), nullable=False
    )
    caso: Mapped["CasoSchema"] = relationship("CasoSchema", lazy="joined")
    data: Mapped[datetime] = mapped_column(DateTime, nullable=False)
