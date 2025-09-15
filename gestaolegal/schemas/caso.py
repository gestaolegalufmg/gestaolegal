from datetime import datetime
from typing import TYPE_CHECKING, Final

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gestaolegal.schemas import associacao_casos_atendidos
from gestaolegal.schemas.base import Base

if TYPE_CHECKING:
    from gestaolegal.schemas.atendido import AtendidoSchema
    from gestaolegal.schemas.usuario import UsuarioSchema


class CasoSchema(Base):
    __tablename__ = "casos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    id_usuario_responsavel: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False
    )
    usuario_responsavel: Mapped["UsuarioSchema"] = relationship(
        "UsuarioSchema", foreign_keys=[id_usuario_responsavel]
    )

    area_direito: Mapped[str] = mapped_column(
        String(50, collation="latin1_general_ci"), nullable=False
    )
    sub_area: Mapped[str | None] = mapped_column(
        String(50, collation="latin1_general_ci")
    )

    clientes: Mapped[list["AtendidoSchema"]] = relationship(
        "AtendidoSchema", secondary=associacao_casos_atendidos, back_populates="casos"
    )

    id_orientador: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("usuarios.id")
    )
    orientador: Mapped["UsuarioSchema | None"] = relationship(
        "UsuarioSchema", foreign_keys=[id_orientador]
    )

    id_estagiario: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("usuarios.id")
    )
    estagiario: Mapped["UsuarioSchema | None"] = relationship(
        "UsuarioSchema", foreign_keys=[id_estagiario]
    )

    id_colaborador: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("usuarios.id")
    )
    colaborador: Mapped["UsuarioSchema | None"] = relationship(
        "UsuarioSchema", foreign_keys=[id_colaborador]
    )

    data_criacao: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    id_criado_por: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False
    )
    criado_por: Mapped["UsuarioSchema"] = relationship(
        "UsuarioSchema", foreign_keys=[id_criado_por]
    )

    data_modificacao: Mapped[datetime | None] = mapped_column(DateTime)
    id_modificado_por: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("usuarios.id")
    )
    modificado_por: Mapped["UsuarioSchema | None"] = relationship(
        "UsuarioSchema", foreign_keys=[id_modificado_por]
    )

    situacao_deferimento: Mapped[str] = mapped_column(
        String(50, collation="latin1_general_ci"),
        nullable=False,
        default="aguardando_deferimento",
    )
    justif_indeferimento: Mapped[str | None] = mapped_column(
        String(280, collation="latin1_general_ci"), nullable=True
    )

    status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text(collation="latin1_general_ci"))

    numero_ultimo_processo: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True
    )
