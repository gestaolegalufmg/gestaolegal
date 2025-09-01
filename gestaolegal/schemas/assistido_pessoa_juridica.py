from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gestaolegal.schemas.base import Base

if TYPE_CHECKING:
    from gestaolegal.schemas.assistido import AssistidoSchema


class AssistidoPessoaJuridicaSchema(Base):
    __tablename__ = "assistidos_pessoa_juridica"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_assistido: Mapped[int] = mapped_column(
        Integer, ForeignKey("assistidos.id", ondelete="CASCADE")
    )
    assistido: Mapped["AssistidoSchema"] = relationship(
        "AssistidoSchema", lazy="joined"
    )

    # Dados específicos
    socios: Mapped[str | None] = mapped_column(
        String(1000, collation="latin1_general_ci")
    )
    situacao_receita: Mapped[str] = mapped_column(
        String(100, collation="latin1_general_ci"), nullable=False
    )
    enquadramento: Mapped[str] = mapped_column(
        String(100, collation="latin1_general_ci"), nullable=False
    )
    sede_bh: Mapped[bool] = mapped_column(Boolean, nullable=False)
    regiao_sede_bh: Mapped[str | None] = mapped_column(
        String(50, collation="latin1_general_ci")
    )
    regiao_sede_outros: Mapped[str | None] = mapped_column(
        String(100, collation="latin1_general_ci")
    )
    area_atuacao: Mapped[str] = mapped_column(
        String(50, collation="latin1_general_ci"), nullable=False
    )
    negocio_nascente: Mapped[bool] = mapped_column(Boolean, nullable=False)
    orgao_registro: Mapped[str] = mapped_column(
        String(100, collation="latin1_general_ci"), nullable=False
    )
    faturamento_anual: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    ultimo_balanco_neg: Mapped[str | None] = mapped_column(
        String(50, collation="latin1_general_ci")
    )
    resultado_econ_neg: Mapped[str | None] = mapped_column(
        String(50, collation="latin1_general_ci")
    )
    tem_funcionarios: Mapped[str] = mapped_column(
        String(20, collation="latin1_general_ci"), nullable=False
    )
    qtd_funcionarios: Mapped[str | None] = mapped_column(
        String(7, collation="latin1_general_ci")
    )
