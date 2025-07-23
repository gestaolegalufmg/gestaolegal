from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gestaolegal.common.constants import area_do_direito
from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
from gestaolegal.models.base import Base

if TYPE_CHECKING:
    from gestaolegal.models.atendido import Atendido
    from gestaolegal.models.orientacao_juridica import OrientacaoJuridica
    from gestaolegal.usuario.models import Usuario


##############################################################
################## CONSTANTES/ENUMS ##########################
##############################################################

se_civel = {
    "CONSUMIDOR": ("consumidor", "Consumidor"),
    "CONTRATOS": ("contratos", "Contratos"),
    "FAMILIA": ("familia", "Família"),
    "REAIS": ("reais", "Reais"),
    "RESPONSABILIDADE_CIVIL": ("resp_civil", "Responsabilidade Civil"),
    "SUCESSOES": ("sucessoes", "Sucessões"),
}

se_administrativo = {
    "ADMINISTRATIVO": ("administrativo", "Administrativo"),
    "PREVIDENCIARIO": ("previdenciario", "Previdenciário"),
    "TRIBUTARIO": ("tributario", "Tributário"),
}

como_conheceu_daj = {
    "ASSISTIDOS": ("assist", "Assistidos/ex-assistidos"),
    "INTEGRANTES": ("integ", "Integrantes/ex-integrantes da UFMG"),
    "ORGAOSPUBLICOS": ("orgaos_pub", "Órgãos públicos"),
    "MEIOSCOMUNICACAO": (
        "meios_com",
        "Meios de comunicação (televisão, jornal, rádio, etc)",
    ),
    "NUCLEOS": ("nucleos", "Núcleos de prática jurídica de outras faculdades"),
    "CONHECIDOS": ("conhec", "Amigos, familiares ou conhecidos"),
    "OUTROS": ("outros", "Outros"),
}

raca_cor = {
    "INDIGENA": ("indigena", "Indígena"),
    "PRETA": ("preta", "Preta"),
    "PARDA": ("parda", "Parda"),
    "AMARELA": ("amarela", "Amarela"),
    "BRANCA": ("branca", "Branca"),
    "NAO_DECLARADO": ("nao_declarado", "Prefere não declarar"),
}

escolaridade = {
    "NAO_FREQUENTOU": ("nao_frequentou", "Não frequentou a escola"),
    "INFANTIL_INC": ("infantil_inc", "Educação infantil incompleta"),
    "INFANTIL_COMP": ("infantil_comp", "Educação infantil completa"),
    "FUNDAMENTAL1_INC": (
        "fundamental1_inc",
        "Ensino fundamental - 1° ao 5° ano incompletos",
    ),  # TODO: Verificar pq esse símbolo "º" não aparece no html
    "FUNDAMENTAL1_COMP": (
        "fundamental1_comp",
        "Ensino fundamental - 1° ao 5° ano completos",
    ),
    "FUNDAMENTAL2_INC": (
        "fundamental2_inc",
        "Ensino fundamental - 6° ao 9° ano incompletos",
    ),
    "FUNDAMENTAL2_COMP": (
        "fundamental2_comp",
        "Ensino fundamental - 6° ao 9° ano completos",
    ),
    "MEDIO_INC": ("medio_inc", "Ensino médio incompleto"),
    "MEDIO_COMP": ("medio_comp", "Ensino médio completo"),
    "TECNICO_INC": ("tecnico_inc", "Curso técnico incompleto"),
    "TECNICO_COMP": ("tecnico_comp", "Curso técnico completo"),
    "SUPERIOR_INC": ("superior_inc", "Ensino superior incompleto"),
    "SUPERIOR_COMP": ("superior_comp", "Ensino superior completo"),
    "NAO_INFORMADO": ("nao_info", "Não informou"),
}


beneficio = {
    "BENEFICIO_PRESTACAO_CONT": (
        "ben_prestacao_continuada",
        "Benefício de prestação continuada",
    ),
    "RENDA_BASICA": ("renda_basica", "Renda Básica"),
    "BOLSA_ESCOLA": ("bolsa_escola", "Bolsa escola"),
    "BOLSA_MORADIA": ("bolsa_moradia", "Bolsa moradia"),
    "CESTA_BASICA": ("cesta_basica", "Cesta básica"),
    "VALEGAS": ("valegas", "Vale Gás"),
    "NAO": ("nao", "Não"),
    "NAO_INFORMOU": ("outro", "Outro"),
    "OUTRO": ("nao_info", "Não informou"),
}

contribuicao_inss = {
    "SIM": ("sim", "Sim"),
    "ENQ_TRABALHAVA": ("enq_trabalhava", "Enquanto trabalhava"),
    "NAO": ("nao", "Não"),
    "NAO_INFO": ("nao_info", "Não informou"),
}


participacao_renda = {
    "PRINCIPAL_RESPONSAVEL": ("principal", "Principal responsável"),
    "CONTRIBUINTE": ("contribuinte", "Contribuinte"),
    "DEPENDENTE": ("dependente", "Dependente"),
}


moradia = {
    "PROPRIA_QUITADA": ("propria_quitada", "Moradia Própria quitada"),
    "PROPRIA_FINANCIADA": ("propria_financiada", "Moradia Própria financiada"),
    "MORADIA_CEDIDA": ("moradia_cedida", "Moradia Cedida"),
    "OCUPADA_IRREGULAR": ("ocupada_irregular", "Moradia Ocupada/Irregular"),
    "EM_CONSTRUCAO": ("em_construcao", "Moradia Em construção"),
    "ALUGADA": ("alugada", "Moradia Alugada"),
    "PARENTES_OU_AMIGOS": ("parentes_amigos", "Mora na casa de Parentes ou Amigos"),
    "SITUACAO_DE_RUA": ("situacao_rua", "Pessoa em Situação de Rua"),
}


qual_pessoa_doente = {
    "PROPRIA_PESSOA": ("propria_pessoa", "Própria pessoa"),
    "CONJUGE_OU_COMPANHEIRA_COMPANHEIRO": (
        "companheira_companheiro",
        "Cônjuge ou Companheira(o)",
    ),
    "FILHOS": ("filhos", "Filhos"),
    "PAIS": ("pais", "Pais"),
    "AVOS": ("avos", "Avós"),
    "SOGROS": ("sogros", "Sogros"),
    "OUTROS": ("outros", "Outros"),
}


enquadramento = {
    "MICROEMPREENDEDOR_INDIVIDUAL": ("mei", "Microempreendedor Individual"),
    "MICROEMPRESA": ("microempresa", "Microempresa"),
    "EMPRESA_PEQUENO_PORTE": ("pequeno_porte", "Empresa de pequeno porte"),
    "OUTROS": ("outros", "Outros"),
}


regiao_bh = {
    "BARREIRO": ("barreiro", "Barreiro"),
    "PAMPULHA": ("pampulha", "Pampulha"),
    "VENDA_NOVA": ("venda nova", "Venda Nova"),
    "NORTE": ("norte", "Norte"),
    "NORDESTE": ("nordeste", "Nordeste"),
    "NOROESTE": ("noroeste", "Noroeste"),
    "LESTE": ("leste", "Leste"),
    "OESTE": ("oeste", "Oeste"),
    "SUL": ("sul", "Sul"),
    "CENTRO_SUL": ("centro_sul", "Centro-Sul"),
}


area_atuacao = {
    "PRODUCAO_CIRCULACAO_BENS": (
        "producao_circ_bens",
        "Produção e/ou circulação de bens",
    ),
    "PRESTACAO_SERVICOS": ("prestacao_serviços", "Prestação de serviços"),
    "ATIVIDADE_RURAL": ("atividade_rural", "Atividade rural"),
    "OUTROS": ("outros", "Outros"),
}

orgao_reg = {
    "JUCEMG": ("jucemg", "JUNTA COMERCIAL DO ESTADO DE MINAS GERAIS"),
    "CARTORIO_PJ": ("cartorio_pj", "CARTÓRIO DE REGISTRO CIVIL DAS PESSOAS JURÍDICAS"),
}

assistencia_jud_areas_atendidas = {
    "ADMINISTRATIVO": (
        area_do_direito["ADMINISTRATIVO"][0],
        area_do_direito["ADMINISTRATIVO"][1],
    ),
    "AMBIENTAL": (area_do_direito["AMBIENTAL"][0], area_do_direito["AMBIENTAL"][1]),
    "CIVEL": (area_do_direito["CIVEL"][0], area_do_direito["CIVEL"][1]),
    "EMPRESARIAL": (
        area_do_direito["EMPRESARIAL"][0],
        area_do_direito["EMPRESARIAL"][1],
    ),
    "PENAL": (area_do_direito["PENAL"][0], area_do_direito["PENAL"][1]),
    "TRABALHISTA": (
        area_do_direito["TRABALHISTA"][0],
        area_do_direito["TRABALHISTA"][1],
    ),
}

assistencia_jud_regioes = {
    "NORTE": ("norte", "Norte"),
    "SUL": ("sul", "Sul"),
    "LESTE": ("leste", "Leste"),
    "OESTE": ("oeste", "Oeste"),
    "NOROESTE": ("noroeste", "Noroeste"),
    "CENTRO_SUL": ("centro_sul", "Centro-Sul"),
    "NORDESTE": ("nordeste", "Nordeste"),
    "PAMPULHA": ("pampulha", "Pampulha"),
    "BARREIRO": ("barreiro", "Barreiro"),
    "VENDA_NOVA": ("venda_nova", "Venda Nova"),
    "CONTAGEM": ("contagem", "Contagem"),
    "BETIM": ("betim", "Betim"),
}

meses = {
    "Jan": 1,
    "Fev": 2,
    "Mar": 3,
    "Abr": 4,
    "Mai": 5,
    "Jun": 6,
    "Jul": 7,
    "Ago": 8,
    "Set": 9,
    "Out": 10,
    "Nov": 11,
    "Dez": 12,
}


class Assistido(Base):
    __tablename__ = "assistidos"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_atendido: Mapped[int] = mapped_column(
        Integer, ForeignKey("atendidos.id", ondelete="CASCADE")
    )
    atendido: Mapped["Atendido"] = relationship("Atendido", lazy="joined")

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

    # Dados sociais
    grau_instrucao: Mapped[str] = mapped_column(
        String(100, collation="latin1_general_ci"), nullable=False
    )

    # Renda e patrimônio
    salario: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    beneficio: Mapped[str] = mapped_column(
        String(30, collation="latin1_general_ci"), nullable=False
    )
    qual_beneficio: Mapped[Optional[str]] = mapped_column(
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
    quantos_imoveis: Mapped[Optional[int]] = mapped_column(Integer)
    possui_veiculos: Mapped[bool] = mapped_column(Boolean, nullable=False)
    possui_veiculos_obs: Mapped[Optional[str]] = mapped_column(
        String(100, collation="latin1_general_ci")
    )
    quantos_veiculos: Mapped[Optional[int]] = mapped_column(Integer)
    ano_veiculo: Mapped[Optional[str]] = mapped_column(
        String(5, collation="latin1_general_ci")
    )
    doenca_grave_familia: Mapped[str] = mapped_column(
        String(20, collation="latin1_general_ci"), nullable=False
    )
    pessoa_doente: Mapped[Optional[str]] = mapped_column(
        String(50, collation="latin1_general_ci")
    )
    pessoa_doente_obs: Mapped[Optional[str]] = mapped_column(
        String(100, collation="latin1_general_ci")
    )
    gastos_medicacao: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    obs: Mapped[Optional[str]] = mapped_column(
        String(1000, collation="latin1_general_ci")
    )

    def setCamposVeiculo(
        self, possui_veiculos, possui_veiculos_obs, quantos_veiculos, ano_veiculo
    ):
        if possui_veiculos:
            self.possui_veiculos_obs = possui_veiculos_obs
            self.quantos_veiculos = quantos_veiculos
            self.ano_veiculo = ano_veiculo
        else:
            self.possui_veiculos_obs = None
            self.quantos_veiculos = None
            self.ano_veiculo = None

    def setCamposDoenca(
        self, doenca_grave_familia, pessoa_doente, pessoa_doente_obs, gastos_medicacao
    ):
        if doenca_grave_familia == "sim":
            self.pessoa_doente = pessoa_doente
            self.gastos_medicacao = gastos_medicacao
            if pessoa_doente == "sim":
                self.pessoa_doente_obs = pessoa_doente_obs
            else:
                self.pessoa_doente_obs = None
        else:
            self.pessoa_doente = None
            self.pessoa_doente_obs = None
            self.gastos_medicacao = None

    def __repr__(self):
        return f"RG:{self.rg}"


class AssistidoPessoaJuridica(Base):
    __tablename__ = "assistidos_pessoa_juridica"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_assistido: Mapped[int] = mapped_column(
        Integer, ForeignKey("assistidos.id", ondelete="CASCADE")
    )
    assistido: Mapped["Assistido"] = relationship("Assistido", lazy="joined")

    # Dados específicos
    socios: Mapped[Optional[str]] = mapped_column(
        String(1000, collation="latin1_general_ci")
    )
    situacao_receita: Mapped[str] = mapped_column(
        String(100, collation="latin1_general_ci"), nullable=False
    )
    enquadramento: Mapped[str] = mapped_column(
        String(100, collation="latin1_general_ci"), nullable=False
    )
    sede_bh: Mapped[bool] = mapped_column(Boolean, nullable=False)
    regiao_sede_bh: Mapped[Optional[str]] = mapped_column(
        String(50, collation="latin1_general_ci")
    )
    regiao_sede_outros: Mapped[Optional[str]] = mapped_column(
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
    ultimo_balanco_neg: Mapped[Optional[str]] = mapped_column(
        String(50, collation="latin1_general_ci")
    )
    resultado_econ_neg: Mapped[Optional[str]] = mapped_column(
        String(50, collation="latin1_general_ci")
    )
    tem_funcionarios: Mapped[str] = mapped_column(
        String(20, collation="latin1_general_ci"), nullable=False
    )
    qtd_funcionarios: Mapped[Optional[str]] = mapped_column(
        String(7, collation="latin1_general_ci")
    )

    def setCamposRegiao_sede(self, sede_bh, regiao_sede_bh, regiao_sede_outros):
        if sede_bh:
            self.regiao_sede_bh = regiao_sede_bh
            self.regiao_sede_outros = None
        else:
            self.regiao_sede_bh = None
            self.regiao_sede_outros = regiao_sede_outros

    def setQtd_funcionarios(self, tem_funcionarios, qtd_funcionarios):
        if tem_funcionarios:
            self.qtd_funcionarios = qtd_funcionarios
        else:
            self.qtd_funcionarios = None

    def __repr__(self):
        return f"RG:{self.enquadramento}"


class Atendido_xOrientacaoJuridica(Base):
    __tablename__ = "atendido_xOrientacaoJuridica"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_orientacaoJuridica: Mapped[int] = mapped_column(
        Integer, ForeignKey("orientacao_juridica.id")
    )
    id_atendido: Mapped[int] = mapped_column(Integer, ForeignKey("atendidos.id"))

    atendido: Mapped["Atendido"] = relationship(
        "Atendido", backref="atendido_xOrientacaoJuridica"
    )
    orientacaoJuridica: Mapped["OrientacaoJuridica"] = relationship(
        "OrientacaoJuridica", backref="atendido_xOrientacaoJuridica"
    )


class AssistenciaJudiciaria_xOrientacaoJuridica(Base):
    __tablename__ = "assistenciasJudiciarias_xOrientacao_juridica"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_orientacaoJuridica: Mapped[int] = mapped_column(
        Integer, ForeignKey("orientacao_juridica.id")
    )
    id_assistenciaJudiciaria: Mapped[int] = mapped_column(
        Integer, ForeignKey("assistencias_judiciarias.id")
    )

    assistenciaJudiciaria: Mapped["AssistenciaJudiciaria"] = relationship(
        AssistenciaJudiciaria,
        backref="assistenciasJudiciarias_xOrientacao_juridica",
    )
    orientacaoJuridica: Mapped["OrientacaoJuridica"] = relationship(
        "OrientacaoJuridica",
        backref="assistenciasJudiciarias_xOrientacao_juridica",
    )


class DiaPlantao(Base):
    __tablename__ = "dias_plantao"

    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)


class Plantao(Base):
    __tablename__ = "plantao"

    id: Mapped[int] = mapped_column(primary_key=True)
    data_abertura: Mapped[Optional[datetime]] = mapped_column(DateTime)
    data_fechamento: Mapped[Optional[datetime]] = mapped_column(DateTime)


class DiasMarcadosPlantao(Base):
    __tablename__ = "dias_marcados_plantao"

    id: Mapped[int] = mapped_column(primary_key=True)
    data_marcada: Mapped[date | None] = mapped_column(Date)
    confirmacao: Mapped[str] = mapped_column(
        String(15, collation="latin1_general_ci"), nullable=False, default="aberto"
    )
    status: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)

    id_usuario: Mapped[int | None] = mapped_column(Integer, ForeignKey("usuarios.id"))
    usuario: Mapped["Usuario | None"] = relationship(
        "Usuario", backref="dias_marcados_plantao"
    )


class RegistroEntrada(Base):
    __tablename__ = "registro_entrada"

    id: Mapped[int] = mapped_column(primary_key=True)
    data_entrada: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    data_saida: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    confirmacao: Mapped[str] = mapped_column(
        String(15, collation="latin1_general_ci"), nullable=False, default="aberto"
    )
    id_usuario: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id")
    )
    usuario: Mapped[Optional["Usuario"]] = relationship(
        "Usuario", backref="registro_entrada"
    )


# MELHORIAS SOLICITADAS - SETTER


class FilaAtendidos(Base):
    __tablename__ = "fila_atendimentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    psicologia: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    prioridade: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    data_criacao: Mapped[Optional[datetime]] = mapped_column(DateTime)
    senha: Mapped[str] = mapped_column(
        String(10, collation="latin1_general_ci"), nullable=False
    )
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    id_atendido: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("atendidos.id")
    )

    atendido: Mapped["Atendido | None"] = relationship("Atendido", backref="atendidos")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
