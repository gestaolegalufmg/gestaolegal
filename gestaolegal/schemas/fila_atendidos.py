from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gestaolegal.schemas.base import Base

if TYPE_CHECKING:
    from gestaolegal.schemas.atendido import AtendidoSchema


class FilaAtendidosSchema(Base):
    __tablename__ = "fila_atendimentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    psicologia: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    prioridade: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    data_criacao: Mapped[datetime | None] = mapped_column(DateTime)
    senha: Mapped[str] = mapped_column(
        String(10, collation="latin1_general_ci"), nullable=False
    )
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    id_atendido: Mapped[int | None] = mapped_column(Integer, ForeignKey("atendidos.id"))

    atendido: Mapped["AtendidoSchema | None"] = relationship(
        "AtendidoSchema", backref="atendidos"
    )
