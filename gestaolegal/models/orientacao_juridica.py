from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gestaolegal.common.constants import area_do_direito
from gestaolegal.schemas.base import Base

if TYPE_CHECKING:
    from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
    from gestaolegal.schemas.atendido import AtendidoSchema
    from gestaolegal.usuario.models import Usuario


class OrientacaoJuridica(Base):
    __tablename__ = "orientacao_juridica"

    id: Mapped[int] = mapped_column(primary_key=True)
    area_direito: Mapped[str] = mapped_column(
        String(50, collation="latin1_general_ci"), nullable=False
    )
    sub_area: Mapped[str | None] = mapped_column(
        String(50, collation="latin1_general_ci")
    )
    descricao: Mapped[str] = mapped_column(
        Text(collation="latin1_general_ci"), nullable=False
    )
    data_criacao: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[int] = mapped_column(Integer, nullable=False)

    assistenciasJudiciarias: Mapped[list["AssistenciaJudiciaria"]] = relationship(
        "AssistenciaJudiciaria",
        secondary="assistenciasJudiciarias_xOrientacao_juridica",
        backref="AssistenciaJudiciaria",
    )
    atendidos: Mapped[list["AtendidoSchema"]] = relationship(
        "AtendidoSchema", secondary="atendido_xOrientacaoJuridica"
    )
    id_usuario: Mapped[int | None] = mapped_column(Integer, ForeignKey("usuarios.id"))
    usuario: Mapped["Usuario | None"] = relationship("Usuario", backref="usuarios")

    def setSubAreas(self, area_direito, sub_area, sub_areaAdmin):
        if area_direito == area_do_direito["CIVEL"][0]:
            self.sub_area = sub_area
        elif area_direito == area_do_direito["ADMINISTRATIVO"][0]:
            self.sub_area = sub_areaAdmin
        else:
            self.sub_area = None

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
