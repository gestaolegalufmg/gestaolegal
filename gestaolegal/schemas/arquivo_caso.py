from typing import TYPE_CHECKING, Final

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from gestaolegal.schemas.base import Base

if TYPE_CHECKING:
    pass


class ArquivoCasoSchema(Base):
    __tablename__ = "arquivosCaso"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    link_arquivo: Mapped[str | None] = mapped_column(
        String(300, collation="latin1_general_ci")
    )
    id_caso: Mapped[int] = mapped_column(
        Integer, ForeignKey("casos.id", ondelete="CASCADE")
    )
