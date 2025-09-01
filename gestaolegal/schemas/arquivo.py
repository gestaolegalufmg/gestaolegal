from typing import Final, Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from gestaolegal.schemas.base import Base


class ArquivoSchema(Base):
    __tablename__: Final = "arquivos"

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
