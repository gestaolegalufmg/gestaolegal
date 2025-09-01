from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gestaolegal.schemas.base import Base

if TYPE_CHECKING:
    from gestaolegal.schemas.endereco import EnderecoSchema
    from gestaolegal.schemas.orientacao_juridica import OrientacaoJuridicaSchema


class AssistenciaJudiciariaSchema(Base):
    __tablename__ = "assistencias_judiciarias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(
        String(150, collation="latin1_general_ci"), nullable=False
    )
    regiao: Mapped[str] = mapped_column(
        String(80, collation="latin1_general_ci"), nullable=False
    )
    areas_atendidas: Mapped[str] = mapped_column(
        String(1000, collation="latin1_general_ci"), nullable=False
    )
    endereco_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("enderecos.id"))
    endereco: Mapped["EnderecoSchema | None"] = relationship(
        "EnderecoSchema", lazy="joined", back_populates="assistencias_judiciarias"
    )
    telefone: Mapped[str] = mapped_column(
        String(18, collation="latin1_general_ci"), nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(80, collation="latin1_general_ci"), unique=True, nullable=False
    )
    status: Mapped[int] = mapped_column(Integer, nullable=False)

    orientacoesJuridicas: Mapped[list["OrientacaoJuridicaSchema"]] = relationship(
        "OrientacaoJuridicaSchema",
        secondary="assistenciasJudiciarias_xOrientacao_juridica",
        back_populates="assistenciasJudiciarias",
    )

    def setAreas_atendidas(self, opcoes):
        self.areas_atendidas = ",".join(opcoes)

    def getAreas_atendidas(self):
        return self.areas_atendidas.split(",")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
