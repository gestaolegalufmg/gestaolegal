from datetime import datetime
from typing import TYPE_CHECKING, Final

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gestaolegal.schemas.base import Base

if TYPE_CHECKING:
    from gestaolegal.schemas.caso import CasoSchema
    from gestaolegal.schemas.usuario import UsuarioSchema


class LembreteSchema(Base):
    __tablename__: Final = "lembretes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    num_lembrete: Mapped[int] = mapped_column(Integer, default=0)
    id_do_criador: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False
    )
    criador: Mapped["UsuarioSchema"] = relationship(
        "UsuarioSchema", foreign_keys=[id_do_criador]
    )
    id_caso: Mapped[int] = mapped_column(
        Integer, ForeignKey("casos.id"), nullable=False
    )
    caso: Mapped["CasoSchema"] = relationship("CasoSchema", foreign_keys=[id_caso])
    id_usuario: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False
    )
    usuario: Mapped["UsuarioSchema"] = relationship(
        "UsuarioSchema", foreign_keys=[id_usuario]
    )
    data_criacao: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    data_lembrete: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    descricao: Mapped[str] = mapped_column(
        Text(collation="latin1_general_ci"), nullable=False
    )
    status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
