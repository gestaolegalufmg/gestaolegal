from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship

from gestaolegal.schemas.base import Base

if TYPE_CHECKING:
    from gestaolegal.schemas.assistencia_judiciaria import AssistenciaJudiciariaSchema
    from gestaolegal.schemas.orientacao_juridica import OrientacaoJuridicaSchema


class AssistenciaJudiciaria_xOrientacaoJuridicaSchema(Base):
    __tablename__ = "assistenciasJudiciarias_xOrientacao_juridica"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_orientacaoJuridica: Mapped[int] = mapped_column(
        Integer, ForeignKey("orientacao_juridica.id")
    )
    id_assistenciaJudiciaria: Mapped[int] = mapped_column(
        Integer, ForeignKey("assistencias_judiciarias.id")
    )

    assistenciaJudiciaria: Mapped["AssistenciaJudiciariaSchema"] = relationship(
        "AssistenciaJudiciariaSchema",
        backref="assistenciasJudiciarias_xOrientacao_juridica",
    )
    orientacaoJuridica: Mapped["OrientacaoJuridicaSchema"] = relationship(
        "OrientacaoJuridicaSchema",
        backref="assistenciasJudiciarias_xOrientacao_juridica",
    )
