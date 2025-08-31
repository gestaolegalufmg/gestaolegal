from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gestaolegal.schemas.base import Base
from gestaolegal.usuario.models import Usuario

acoes = {
    "CAD_NOVO_CASO": "Cadastrado no caso {}",
    "ABERTURA_PLANTAO": "Abertura do plantão",  # notificar orientadores e estagiarios
    "EVENTO": "Cadastrado no evento {} do caso {}",
    "LEMBRETE": "Cadastrado no lembrete {} do caso {}",
}


class Notificacao(Base):
    __tablename__ = "notificacao"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_executor_acao: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id")
    )
    id_usu_notificar: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id")
    )
    acao: Mapped[str] = mapped_column(
        String(200, collation="latin1_general_ci"), nullable=False
    )
    data: Mapped[date] = mapped_column(Date, nullable=False)

    executor_acao: Mapped[Optional[Usuario]] = relationship(
        "Usuario", foreign_keys=[id_executor_acao]
    )
    usu_notificar: Mapped[Optional[Usuario]] = relationship(
        "Usuario", foreign_keys=[id_usu_notificar]
    )
