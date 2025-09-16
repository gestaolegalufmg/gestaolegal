from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from gestaolegal.schemas.base import Base


class RoteiroSchema(Base):
    __tablename__ = "documentos_roteiro"

    id: Mapped[int] = mapped_column(primary_key=True)
    area_direito: Mapped[str] = mapped_column(
        String(50, collation="latin1_general_ci"), nullable=False
    )
    link: Mapped[str] = mapped_column(String(1000, collation="latin1_general_ci"))
