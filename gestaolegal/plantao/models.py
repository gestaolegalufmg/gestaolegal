from datetime import date, datetime
from typing import TYPE_CHECKING, Final, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gestaolegal.casos.models import Caso, associacao_casos_atendidos
from gestaolegal.models.base import Base
from gestaolegal.usuario.models import Usuario

if TYPE_CHECKING:
    from gestaolegal.models.endereco import Endereco


##############################################################
################## CONSTANTES/ENUMS ##########################
##############################################################

area_do_direito = {
    "ADMINISTRATIVO": ("administrativo", "Administrativo"),
    "AMBIENTAL": ("ambiental", "Ambiental"),
    "CIVEL": ("civel", "Civel"),
    "EMPRESARIAL": ("empresarial", "Empresarial"),
    "PENAL": ("penal", "Penal"),
    "TRABALHISTA": ("trabalhista", "Trabalhista"),
}

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


class Atendido(Base):
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
    cnpj: Mapped[Optional[str]] = mapped_column(
        String(18, collation="latin1_general_ci")
    )
    endereco_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("enderecos.id")
    )
    telefone: Mapped[Optional[str]] = mapped_column(
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
    procurou_qual_local: Mapped[Optional[str]] = mapped_column(
        String(80, collation="latin1_general_ci")
    )
    obs: Mapped[str | None] = mapped_column(Text(collation="latin1_general_ci"))
    pj_constituida: Mapped[str] = mapped_column(
        String(80, collation="latin1_general_ci")
    )
    repres_legal: Mapped[Optional[str]] = mapped_column(
        String(1, collation="latin1_general_ci")
    )
    nome_repres_legal: Mapped[Optional[str]] = mapped_column(
        String(80, collation="latin1_general_ci")
    )
    cpf_repres_legal: Mapped[Optional[str]] = mapped_column(
        String(14, collation="latin1_general_ci")
    )
    contato_repres_legal: Mapped[Optional[str]] = mapped_column(
        String(18, collation="latin1_general_ci")
    )
    rg_repres_legal: Mapped[Optional[str]] = mapped_column(
        String(50, collation="latin1_general_ci")
    )
    nascimento_repres_legal: Mapped[Optional[date]] = mapped_column(Date)
    pretende_constituir_pj: Mapped[Optional[str]] = mapped_column(
        String(80, collation="latin1_general_ci")
    )
    status: Mapped[int] = mapped_column(Integer)

    def setIndicacao_orgao(self, indicacao_orgao, como_conheceu):
        if como_conheceu == como_conheceu_daj["ORGAOSPUBLICOS"][0]:
            self.indicacao_orgao = indicacao_orgao
        else:
            self.indicacao_orgao = None

    def setCnpj(self, pj_constituida, cnpj, repres_legal):
        if pj_constituida:
            self.cnpj = cnpj
            self.repres_legal = repres_legal
        else:
            self.cnpj = None
            self.repres_legal = None

    def setRepres_legal(
        self,
        repres_legal,
        pj_constituida,
        nome_repres_legal,
        cpf_repres_legal,
        contato_repres_legal,
        rg_repres_legal,
        nascimento_repres_legal,
    ):
        if (repres_legal == False) and pj_constituida:
            self.nome_repres_legal = nome_repres_legal
            self.cpf_repres_legal = cpf_repres_legal
            self.contato_repres_legal = contato_repres_legal
            self.rg_repres_legal = rg_repres_legal
            self.nascimento_repres_legal = nascimento_repres_legal
        else:
            self.nome_repres_legal = None
            self.cpf_repres_legal = None
            self.contato_repres_legal = None
            self.rg_repres_legal = None
            self.nascimento_repres_legal = None

    def setProcurou_qual_local(self, procurou_outro_local, procurou_qual_local):
        if procurou_outro_local:
            self.procurou_qual_local = procurou_qual_local
        else:
            self.procurou_qual_local = None

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"Nome:{self.nome}"


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


class OrientacaoJuridica(Base):
    __tablename__ = "orientacao_juridica"

    id: Mapped[int] = mapped_column(primary_key=True)
    area_direito: Mapped[str] = mapped_column(
        String(50, collation="latin1_general_ci"), nullable=False
    )
    sub_area: Mapped[Optional[str]] = mapped_column(
        String(50, collation="latin1_general_ci")
    )
    descricao: Mapped[str] = mapped_column(
        Text(collation="latin1_general_ci"), nullable=False
    )
    data_criacao: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[int] = mapped_column(Integer, nullable=False)

    assistenciasJudiciarias: Mapped[list["AssistenciaJudiciaria"]] = relationship(
        "AssistenciaJudiciaria",
        secondary="assistenciasJudiciarias_xOrientacao_juridica",
        backref="AssistenciaJudiciaria",
    )
    atendidos: Mapped[list["Atendido"]] = relationship(
        "Atendido", secondary="atendido_xOrientacaoJuridica"
    )
    id_usuario: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id")
    )
    usuario: Mapped[Optional["Usuario"]] = relationship(Usuario, backref="usuarios")

    def setSubAreas(self, area_direito, sub_area, sub_areaAdmin):
        if area_direito == area_do_direito["CIVEL"][0]:
            self.sub_area = sub_area
        elif area_direito == area_do_direito["ADMINISTRATIVO"][0]:
            self.sub_area = sub_areaAdmin
        else:
            self.sub_area = None

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Atendido_xOrientacaoJuridica(Base):
    __tablename__ = "atendido_xOrientacaoJuridica"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_orientacaoJuridica: Mapped[int] = mapped_column(
        Integer, ForeignKey("orientacao_juridica.id")
    )
    id_atendido: Mapped[int] = mapped_column(Integer, ForeignKey("atendidos.id"))

    atendido: Mapped["Atendido"] = relationship(
        Atendido, backref="atendido_xOrientacaoJuridica"
    )
    orientacaoJuridica: Mapped["OrientacaoJuridica"] = relationship(
        OrientacaoJuridica, backref="atendido_xOrientacaoJuridica"
    )


# ASSISTÊNCIA JUDICIÁRIA
class AssistenciaJudiciaria(Base):
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
    endereco_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("enderecos.id")
    )
    endereco: Mapped[Optional["Endereco"]] = relationship("Endereco", lazy="joined")
    telefone: Mapped[str] = mapped_column(
        String(18, collation="latin1_general_ci"), nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(80, collation="latin1_general_ci"), unique=True, nullable=False
    )
    status: Mapped[int] = mapped_column(Integer, nullable=False)

    orientacoesJuridicas: Mapped[list["OrientacaoJuridica"]] = relationship(
        "OrientacaoJuridica",
        secondary="assistenciasJudiciarias_xOrientacao_juridica",
        backref="AssistenciaJudiciaria",
    )

    def setAreas_atendidas(self, opcoes):
        self.areas_atendidas = ",".join(opcoes)

    def getAreas_atendidas(self):
        return self.areas_atendidas.split(",")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


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
        OrientacaoJuridica,
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
    data_marcada: Mapped[Optional[date]] = mapped_column(Date)
    confirmacao: Mapped[str] = mapped_column(
        String(15, collation="latin1_general_ci"), nullable=False, default="aberto"
    )
    status: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)

    id_usuario: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id")
    )
    usuario: Mapped[Optional["Usuario"]] = relationship(
        Usuario, backref="dias_marcados_plantao"
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
        Usuario, backref="registro_entrada"
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

    atendido: Mapped[Optional["Atendido"]] = relationship(Atendido, backref="atendidos")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
