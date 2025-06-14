from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from gestaolegal.models.base import Base


class Arquivo(Base):
    __tablename__ = "arquivos"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(
        String(150, collation="latin1_general_ci"), nullable=False
    )
    descricao: Mapped[Optional[str]] = mapped_column(
        Text(collation="latin1_general_ci")
    )
    nome: Mapped[str] = mapped_column(
        Text(collation="latin1_general_ci"), nullable=False
    )
