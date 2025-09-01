from typing import Final

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from gestaolegal.schemas.base import Base


class ArquivosEventoSchema(Base):
    __tablename__: Final = "arquivosEvento"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_evento: Mapped[int] = mapped_column(
        Integer, ForeignKey("eventos.id", ondelete="CASCADE")
    )
    id_caso: Mapped[int] = mapped_column(
        Integer, ForeignKey("casos.id", ondelete="CASCADE")
    )
    link_arquivo: Mapped[str | None] = mapped_column(
        String(300, collation="latin1_general_ci")
    )
