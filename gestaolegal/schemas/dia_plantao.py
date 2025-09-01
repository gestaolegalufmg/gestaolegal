from datetime import date

from sqlalchemy import Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column

from gestaolegal.schemas.base import Base


class DiaPlantaoSchema(Base):
    __tablename__ = "dias_plantao"

    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[date | None] = mapped_column(Date)
    status: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
