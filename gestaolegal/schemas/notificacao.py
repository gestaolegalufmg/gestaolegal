from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gestaolegal.schemas.base import Base

if TYPE_CHECKING:
    from gestaolegal.schemas.user import UserSchema


class NotificacaoSchema(Base):
    __tablename__ = "notificacao"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_executor_acao: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("usuarios.id")
    )
    id_usu_notificar: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("usuarios.id")
    )
    acao: Mapped[str] = mapped_column(
        String(200, collation="latin1_general_ci"), nullable=False
    )
    data: Mapped[datetime] = mapped_column(Date, nullable=False)

    executor_acao: Mapped["UserSchema | None"] = relationship(
        "UserSchema", foreign_keys=[id_executor_acao]
    )
    usu_notificar: Mapped["UserSchema | None"] = relationship(
        "UserSchema", foreign_keys=[id_usu_notificar]
    )
