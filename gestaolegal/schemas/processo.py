from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gestaolegal.schemas.base import Base

if TYPE_CHECKING:
    from gestaolegal.schemas.caso import CasoSchema
    from gestaolegal.schemas.usuario import UsuarioSchema


class ProcessoSchema(Base):
    __tablename__ = "processos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    especie: Mapped[str] = mapped_column(
        String(25, collation="latin1_general_ci"), nullable=False
    )
    numero: Mapped[int | None] = mapped_column(BigInteger, unique=True)
    identificacao: Mapped[str | None] = mapped_column(
        Text(collation="latin1_general_ci")
    )
    vara: Mapped[str | None] = mapped_column(String(200, collation="latin1_general_ci"))
    link: Mapped[str | None] = mapped_column(
        String(1000, collation="latin1_general_ci")
    )
    probabilidade: Mapped[str | None] = mapped_column(
        String(25, collation="latin1_general_ci")
    )
    posicao_assistido: Mapped[str | None] = mapped_column(
        String(25, collation="latin1_general_ci")
    )
    valor_causa_inicial: Mapped[int | None] = mapped_column(Integer)
    valor_causa_atual: Mapped[int | None] = mapped_column(Integer)
    data_distribuicao: Mapped[date | None] = mapped_column(Date)
    data_transito_em_julgado: Mapped[date | None] = mapped_column(Date)
    obs: Mapped[str | None] = mapped_column(Text(collation="latin1_general_ci"))
    id_caso: Mapped[int] = mapped_column(
        Integer, ForeignKey("casos.id"), nullable=False
    )
    caso: Mapped["CasoSchema"] = relationship("CasoSchema", lazy="joined")
    status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    id_criado_por: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False, default=1
    )
    criado_por: Mapped["UsuarioSchema"] = relationship(
        "UsuarioSchema", foreign_keys=[id_criado_por]
    )
