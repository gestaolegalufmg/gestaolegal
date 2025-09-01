from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from gestaolegal.schemas.base import Base


class PlantaoSchema(Base):
    __tablename__ = "plantao"

    id: Mapped[int] = mapped_column(primary_key=True)
    data_abertura: Mapped[datetime | None] = mapped_column(DateTime)
    data_fechamento: Mapped[datetime | None] = mapped_column(DateTime)
