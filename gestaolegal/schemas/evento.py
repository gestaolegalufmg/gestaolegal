from datetime import date, datetime
from typing import TYPE_CHECKING, Final

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gestaolegal.schemas.base import Base

if TYPE_CHECKING:
    from gestaolegal.schemas.caso import CasoSchema
    from gestaolegal.schemas.usuario import UsuarioSchema


class EventoSchema(Base):
    __tablename__: Final = "eventos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_caso: Mapped[int] = mapped_column(
        Integer, ForeignKey("casos.id"), nullable=False
    )
    caso: Mapped["CasoSchema"] = relationship("CasoSchema")

    num_evento: Mapped[int] = mapped_column(Integer, default=0)
    tipo: Mapped[str] = mapped_column(
        String(50, collation="latin1_general_ci"), nullable=False
    )
    descricao: Mapped[str | None] = mapped_column(Text(collation="latin1_general_ci"))
    arquivo: Mapped[str | None] = mapped_column(
        String(100, collation="latin1_general_ci")
    )
    data_evento: Mapped[date] = mapped_column(Date, nullable=False)

    data_criacao: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    id_criado_por: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False
    )

    id_usuario_responsavel: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=True
    )
    usuario_responsavel: Mapped["UsuarioSchema | None"] = relationship(
        "UsuarioSchema", foreign_keys=[id_usuario_responsavel]
    )

    criado_por: Mapped["UsuarioSchema"] = relationship(
        "UsuarioSchema", foreign_keys=[id_criado_por]
    )
    status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
