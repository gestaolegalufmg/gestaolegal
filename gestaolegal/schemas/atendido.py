from datetime import date
from typing import TYPE_CHECKING, Final

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gestaolegal.casos.models import associacao_casos_atendidos
from gestaolegal.schemas.base import Base

if TYPE_CHECKING:
    from gestaolegal.casos.models import Caso
    from gestaolegal.models.endereco import Endereco
    from gestaolegal.models.orientacao_juridica import OrientacaoJuridica


class AtendidoSchema(Base):
    __tablename__: Final = "atendidos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    orientacoesJuridicas: Mapped[list["OrientacaoJuridica"]] = relationship(
        "OrientacaoJuridica", secondary="atendido_xOrientacaoJuridica"
    )
    casos: Mapped[list["Caso"]] = relationship(
        "Caso", secondary=associacao_casos_atendidos, back_populates="clientes"
    )
    endereco: Mapped["Endereco | None"] = relationship("Endereco", lazy="joined")

    # Dados básicos
    nome: Mapped[str] = mapped_column(String(80, collation="latin1_general_ci"))
    data_nascimento: Mapped[date] = mapped_column(Date)
    cpf: Mapped[str] = mapped_column(String(14, collation="latin1_general_ci"))
    cnpj: Mapped[str | None] = mapped_column(String(18, collation="latin1_general_ci"))
    endereco_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("enderecos.id"))
    telefone: Mapped[str | None] = mapped_column(
        String(18, collation="latin1_general_ci")
    )
    celular: Mapped[str] = mapped_column(String(18, collation="latin1_general_ci"))
    email: Mapped[str] = mapped_column(String(80, collation="latin1_general_ci"))
    estado_civil: Mapped[str] = mapped_column(String(80, collation="latin1_general_ci"))

    # antiga Área_demanda
    como_conheceu: Mapped[str] = mapped_column(
        String(80, collation="latin1_general_ci")
    )
    indicacao_orgao: Mapped[str | None] = mapped_column(
        String(80, collation="latin1_general_ci")
    )
    procurou_outro_local: Mapped[str] = mapped_column(
        String(80, collation="latin1_general_ci")
    )
    procurou_qual_local: Mapped[str | None] = mapped_column(
        String(80, collation="latin1_general_ci")
    )
    obs: Mapped[str | None] = mapped_column(Text(collation="latin1_general_ci"))
    pj_constituida: Mapped[str] = mapped_column(
        String(80, collation="latin1_general_ci")
    )
    repres_legal: Mapped[str | None] = mapped_column(
        String(1, collation="latin1_general_ci")
    )
    nome_repres_legal: Mapped[str | None] = mapped_column(
        String(80, collation="latin1_general_ci")
    )
    cpf_repres_legal: Mapped[str | None] = mapped_column(
        String(14, collation="latin1_general_ci")
    )
    contato_repres_legal: Mapped[str | None] = mapped_column(
        String(18, collation="latin1_general_ci")
    )
    rg_repres_legal: Mapped[str | None] = mapped_column(
        String(50, collation="latin1_general_ci")
    )
    nascimento_repres_legal: Mapped[date | None] = mapped_column(Date)
    pretende_constituir_pj: Mapped[str | None] = mapped_column(
        String(80, collation="latin1_general_ci")
    )
    status: Mapped[int] = mapped_column(Integer)
