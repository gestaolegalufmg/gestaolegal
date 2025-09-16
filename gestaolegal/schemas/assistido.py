from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gestaolegal.schemas.base import Base

if TYPE_CHECKING:
    from gestaolegal.schemas.assistido_pessoa_juridica import (
        AssistidoPessoaJuridicaSchema,
    )
    from gestaolegal.schemas.atendido import AtendidoSchema


class AssistidoSchema(Base):
    __tablename__ = "assistidos"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_atendido: Mapped[int] = mapped_column(
        Integer, ForeignKey("atendidos.id", ondelete="CASCADE")
    )
    atendido: Mapped["AtendidoSchema"] = relationship("AtendidoSchema", lazy="joined")
    assistido_pessoa_juridica: Mapped["AssistidoPessoaJuridicaSchema | None"] = (
        relationship("AssistidoPessoaJuridicaSchema", back_populates="assistido")
    )

    # Dados pessoais
    sexo: Mapped[str] = mapped_column(
        String(1, collation="latin1_general_ci"), nullable=False
    )
    profissao: Mapped[str] = mapped_column(
        String(80, collation="latin1_general_ci"), nullable=False
    )
    raca: Mapped[str] = mapped_column(
        String(20, collation="latin1_general_ci"), nullable=False
    )
    rg: Mapped[str] = mapped_column(
        String(50, collation="latin1_general_ci"), nullable=False
    )

    grau_instrucao: Mapped[str] = mapped_column(
        String(100, collation="latin1_general_ci"), nullable=False
    )

    salario: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    beneficio: Mapped[str] = mapped_column(
        String(30, collation="latin1_general_ci"), nullable=False
    )
    qual_beneficio: Mapped[str | None] = mapped_column(
        String(30, collation="latin1_general_ci")
    )
    contribui_inss: Mapped[str] = mapped_column(
        String(20, collation="latin1_general_ci"), nullable=False
    )
    qtd_pessoas_moradia: Mapped[int] = mapped_column(Integer, nullable=False)
    renda_familiar: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    participacao_renda: Mapped[str] = mapped_column(
        String(100, collation="latin1_general_ci"), nullable=False
    )
    tipo_moradia: Mapped[str] = mapped_column(
        String(100, collation="latin1_general_ci"), nullable=False
    )
    possui_outros_imoveis: Mapped[bool] = mapped_column(Boolean, nullable=False)
    quantos_imoveis: Mapped[int | None] = mapped_column(Integer)
    possui_veiculos: Mapped[bool] = mapped_column(Boolean, nullable=False)
    possui_veiculos_obs: Mapped[str | None] = mapped_column(
        String(100, collation="latin1_general_ci")
    )
    quantos_veiculos: Mapped[int | None] = mapped_column(Integer)
    ano_veiculo: Mapped[str | None] = mapped_column(
        String(5, collation="latin1_general_ci")
    )
    doenca_grave_familia: Mapped[str] = mapped_column(
        String(20, collation="latin1_general_ci"), nullable=False
    )
    pessoa_doente: Mapped[str | None] = mapped_column(
        String(50, collation="latin1_general_ci")
    )
    pessoa_doente_obs: Mapped[str | None] = mapped_column(
        String(100, collation="latin1_general_ci")
    )
    gastos_medicacao: Mapped[float | None] = mapped_column(Numeric(10, 2))
    obs: Mapped[str | None] = mapped_column(String(1000, collation="latin1_general_ci"))
