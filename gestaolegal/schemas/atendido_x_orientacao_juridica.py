from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gestaolegal.schemas.base import Base

if TYPE_CHECKING:
    from gestaolegal.schemas.atendido import AtendidoSchema
    from gestaolegal.schemas.orientacao_juridica import OrientacaoJuridicaSchema


class Atendido_xOrientacaoJuridicaSchema(Base):
    __tablename__ = "atendido_xOrientacaoJuridica"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_orientacaoJuridica: Mapped[int] = mapped_column(
        Integer, ForeignKey("orientacao_juridica.id")
    )
    id_atendido: Mapped[int] = mapped_column(Integer, ForeignKey("atendidos.id"))

    atendido: Mapped["AtendidoSchema"] = relationship(
        "AtendidoSchema", backref="atendido_xOrientacaoJuridica"
    )
    orientacaoJuridica: Mapped["OrientacaoJuridicaSchema"] = relationship(
        "OrientacaoJuridicaSchema", backref="atendido_xOrientacaoJuridica"
    )
