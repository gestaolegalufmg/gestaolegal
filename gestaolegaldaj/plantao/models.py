import enum
from datetime import datetime
from enum import Enum

from flask import session
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from sqlalchemy import null
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import expression

from gestaolegaldaj import db
from gestaolegaldaj.casos.models import associacao_casos_atendidos

##############################################################
################## CONSTANTES/ENUMS ##########################
##############################################################

area_do_direito = {
    'CIVEL'                : ('civel','Cível'),
    'TRABALHISTA'          : ('trabalhista', 'Trabalhista'),
    'ADMINISTRATIVO'       : ('administrativo', 'Administrativo'),
    'PENAL'                : ('penal', 'Penal'),
    'EMPRESARIAL'          : ('empresarial', 'Empresarial'),
    'AMBIENTAL'            : ('ambiental', 'Ambiental')
}

se_civel = {
    'CONSUMIDOR'                   : ('Consumidor','Consumidor'),
    'CONTRATOS'                    : ('contratos', 'Contratos'),
    'RESPONSABILIDADE_CIVIL'       : ('resp_civil', 'Responsabilidade Civil'),
    'REAIS'                        : ('reais', 'Reais'),
    'FAMILIA'                      : ('familia', 'Família'),
    'SUCESSOES'                    : ('sucessoes', 'Sucessões')
}

se_administrativo = {
    'PREVIDENCIARIO'                : ('previdenciario','Previdenciário'),
    'TRIBUTARIO'                    : ('tributario', 'Tributário')
}

como_conheceu_daj = {
    'ASSISTIDOS'           : ('assist','Assistidos/ex-assistidos'),
    'INTEGRANTES'          : ('integ', 'Integrantes/ex-integrantes da UFMG'),
    'ORGAOSPUBLICOS'       : ('orgaos_pub', 'Órgãos públicos'),
    'MEIOSCOMUNICACAO'     : ('meios_com', 'Meios de comunicação (televisão, jornal, rádio, etc)'),
    'NUCLEOS'              : ('nucleos', 'Núcleos de prática jurídica de outras faculdades'),
    'CONHECIDOS'           : ('conhec', 'Amigos, familiares ou conhecidos'),
    'OUTROS'               : ('outros', 'Outros')
}

raca_cor = {

    'INDIGENA'      :       ('indigena','Indígena'),
    'PRETA'         :       ('preta','Preta'),
    'PARDA'         :       ('parda','Parda'),
    'AMARELA'       :       ('amarela','Amarela'),
    'BRANCA'        :       ('branca','Branca'),
    'NAO_DECLARADO' :       ('nao_declarado','Prefere não declarar')
}

escolaridade = {
        'NAO_FREQUENTOU'     :     ('nao_frequentou','Não frequentou a escola'),
        'INFANTIL_INC'       :     ('infantil_inc','Educação infantil incompleta'),
        'INFANTIL_COMP'      :     ('infantil_comp','Educação infantil completa'),
        'FUNDAMENTAL1_INC'   :     ('fundamental1_inc','Ensino fundamental - 1° ao 5° ano incompletos'),#TODO: Verificar pq esse símbolo "º" não aparece no html
        'FUNDAMENTAL1_COMP'  :     ('fundamental1_comp','Ensino fundamental - 1° ao 5° ano completos'),
        'FUNDAMENTAL2_INC'   :     ('fundamental2_inc','Ensino fundamental - 6° ao 9° ano incompletos'),
        'FUNDAMENTAL2_COMP'  :     ('fundamental2_comp','Ensino fundamental - 6° ao 9° ano completos'),
        'MEDIO_INC'          :     ('medio_inc','Ensino médio incompleto'),
        'MEDIO_COMP'         :     ('medio_comp','Ensino médio completo'),
        'TECNICO_INC'        :     ('tecnico_inc','Curso técnico incompleto'),
        'TECNICO_COMP'       :     ('tecnico_comp','Curso técnico completo'),
        'SUPERIOR_INC'       :     ('superior_inc','Ensino superior incompleto'),
        'SUPERIOR_COMP'      :     ('superior_comp','Ensino superior completo'),
        'NAO_INFORMADO'      :     ('nao_info','Não informou')

}


beneficio = {

        "BENEFICIO_PRESTACAO_CONT"          :   ("ben_prestacao_continuada", "Benefício de prestação continuada"),
        "BOLSA_FAMILIA"                     :   ("bolsa_familia","Bolsa família"),
        "BOLSA_ESCOLA"                      :   ("bolsa_escola","Bolsa escola"),
        "BOLSA_MORADIA"                     :   ("bolsa_moradia","Bolsa moradia"),
        "CESTA_BASICA"                      :   ("cesta_basica","Cesta básica"),
        "VALEGAS"                           :   ("valegas","Valegás"),
        "NAO"                               :   ("nao","Não"),
        "NAO_INFORMOU"                      :   ("outro","Outro"),
        "OUTRO"                             :   ("nao_info","Não informou")
}

contribuicao_inss = {

    "SIM"               :       ("sim","Sim"),
    "ENQ_TRABALHAVA"    :       ("enq_trabalhava","Enquanto trabalhava"),
    "NAO"               :       ("nao","Não"),
    "NAO_INFO"          :       ("nao_info","Não informou")

}



participacao_renda = {

    "PRINCIPAL_RESPONSAVEL"     :      ("principal", "Principal responsável"),
    "CONTRIBUINTE"              :      ("contribuinte", "Contribuinte"),
    "DEPENDENTE"                :      ("dependente","Dependente"),
    "NAO_CONTRIBUINTE"          :      ("nao_contribuinte", "Não contribuinte")

}


moradia = {

    "PROPRIA_QUITADA"           :   ("propria_quitada","Moradia Própria quitada"),
    "PROPRIA_FINANCIADA"        :   ("propria_financiada","Moradia Própria financiada"),
    "MORADIA_CEDIDA"            :   ("moradia_cedida","Moradia Cedida"),
    "OCUPADA_IRREGULAR"         :   ("ocupada_irregular","Moradia Ocupada/Irregular"),
    "EM_CONSTRUCAO"             :   ("em_construcao","Moradia Em construção"),
    "ALUGADA"                   :   ("alugada","Moradia Alugada"),
    "PARENTES_OU_AMIGOS"        :   ("parentes_amigos","Mora na casa de Parentes ou Amigos"),
    "SITUACAO_DE_RUA"           :   ("situacao_rua","Pessoa em Situação de Rua")


}



qual_pessoa_doente = {

    "PROPRIA_PESSOA"                        : ("propria_pessoa","Própria pessoa"),
    "CONJUGE_OU_COMPANHEIRA_COMPANHEIRO"    : ("companheira_companheiro","Cônjuge ou Companheira(o)"),
    "FILHOS"                                : ("filhos","Filhos"),
    "PAIS"                                  : ("pais","Pais"),
    "AVOS"                                  : ("avos","Avós"),
    "SOGROS"                                : ("sogros","Sogros"),
    "NAO_SE_APLICA"                         : ("nao_aplica","Não se aplica"),
    "OUTROS"                                : ("outros","Outros")
}



enquadramento = {

    "MICROEMPREENDEDOR_INDIVIDUAL"  : ("mei","Microempreendedor Individual"),
    "MICROEMPRESA"		            : ("microempresa","Microempresa"),
    "EMPRESA_PEQUENO_PORTE"	        : ("pequeno_porte","Empresa de pequeno porte"),
    "NAO_SE_APLICA"		            : ("nao_aplica","Não se aplica")

}


regiao_bh = {

    "BARREIRO"	    : ("barreiro","Barreiro"),
    "PAMPULHA"	    : ("pampulha","Pampulha"),
    "VENDA_NOVA"	: ("venda nova","Venda Nova"),
    "NORTE"		    : ("norte","Norte"),
    "NORDESTE"	    : ("nordeste","Nordeste"),
    "NOROESTE"	    : ("noroeste","Noroeste"),
    "LESTE"		    : ("leste","Leste"),
    "OESTE"		    : ("oeste","Oeste"),
    "SUL"		    : ("sul","Sul"),
    "CENTRO_SUL"	: ("centro_sul","Centro-Sul")

}


area_atuacao = {

    "PRODUCAO_CIRCULACAO_BENS"  : ("producao_circ_bens","Produção e/ou circulação de bens"),
    "PRESTACAO_SERVICOS"	    : ("prestacao_serviços","Prestação de serviços"),
    "ATIVIDADE_RURAL"	        : ("atividade_rural","Atividade rural"),
    "OUTROS"		            : ("outros","Outros")

}

orgao_reg = {

    "JUCEMG"            : ("jucemg","JUNTA COMERCIAL DO ESTADO DE MINAS GERAIS"),
    "CARTORIO_PJ"       : ("cartorio_pj","CARTÓRIO DE REGISTRO CIVIL DAS PESSOAS JURÍDICAS")

}

assistencia_jud_areas_atendidas = {
    "CIVEL"                  :(area_do_direito['CIVEL'][0],area_do_direito['CIVEL'][1]),
    "TRABALHISTA"            :(area_do_direito['TRABALHISTA'][0],area_do_direito['TRABALHISTA'][1]),
    "ADMINISTRATIVO"         :(area_do_direito['ADMINISTRATIVO'][0],area_do_direito['ADMINISTRATIVO'][1]),
    "PENAL"                  :(area_do_direito['PENAL'][0],area_do_direito['PENAL'][1]),
    "EMPRESARIAL"            :(area_do_direito['EMPRESARIAL'][0],area_do_direito['EMPRESARIAL'][1]),
    "AMBIENTAL"              :(area_do_direito['AMBIENTAL'][0],area_do_direito['AMBIENTAL'][1]),
    "CONSUMIDOR"             :('consumidor','Consumidor'),
    "CONTRATOS"              :('contratos','Contratos'),
    "RESPONSABILIDADE_CIVIL" :('responsabilidade_civil','Responsabilidade Civil'),
    "REAIS"                  :('reais','Reais'),
    "FAMILIA"                :('familia','Família'),
    "SUCESSOES"              :('sucessoes','Sucessões'),
    "PREVIDENCIARIO"         :('previdenciario','Previdenciário'),
    "TRIBUTARIO"             :('tributario','Tributário')
}

assistencia_jud_regioes={
    "NORTE"      :('norte','Norte'),
    "SUL"        :('sul','Sul'),
    "LESTE"      :('leste','Leste'),
    "OESTE"      :('oeste','Oeste'),
    "NOROESTE"   :('noroeste','Noroeste'),
    "CENTRO_SUL" :('centro_sul','Centro-Sul'),
    "NORDESTE"   :('nordeste','Nordeste'),
    "PAMPULHA"   :('pampulha','Pampulha'),
    "BARREIRO"   :('barreiro','Barreiro'),
    "VENDA_NOVA" :('venda_nova','Venda Nova'),
    "CONTAGEM"   :('contagem','Contagem'),
    "BETIM"      :('betim','Betim')
}



class Atendido(db.Model):

    __tablename__ = 'atendidos'

    id                    = db.Column(db.Integer, primary_key = True)
    orientacoesJuridicas  = db.relationship("OrientacaoJuridica", secondary="atendido_xOrientacaoJuridica")
    casos                 = db.relationship("Caso", secondary=associacao_casos_atendidos, back_populates='clientes')



    #Dados básicos
    nome                = db.Column(db.String(80,  collation = 'latin1_general_ci'),  nullable=False)
    data_nascimento     = db.Column(db.Date,       nullable = False)
    cpf                 = db.Column(db.String(14,  collation = 'latin1_general_ci'), nullable=False)
    cnpj                = db.Column(db.String(18,  collation = 'latin1_general_ci'))
    endereco_id         = db.Column(db.Integer,    db.ForeignKey("enderecos.id"))
    endereco            = db.relationship("Endereco", lazy="joined")
    telefone            = db.Column(db.String(18,  collation = 'latin1_general_ci'))
    celular             = db.Column(db.String(18,  collation = 'latin1_general_ci'), nullable=False)
    email               = db.Column(db.String(80,  collation = 'latin1_general_ci'), unique=True, nullable=False)
    estado_civil        = db.Column(db.String(80,  collation = 'latin1_general_ci'), nullable = False)



    #antiga Área_demanda
    area_juridica          = db.Column(db.String(80, collation = 'latin1_general_ci'), nullable=False)
    como_conheceu          = db.Column(db.String(80, collation = 'latin1_general_ci'), nullable=False)
    indicacao_orgao        = db.Column(db.String(80, collation = 'latin1_general_ci'))
    procurou_outro_local   = db.Column(db.String(80, collation = 'latin1_general_ci'), nullable=False)
    procurou_qual_local    = db.Column(db.String(80, collation = 'latin1_general_ci'))
    obs                    = db.Column(db.Text(      collation = 'latin1_general_ci'))
    pj_constituida         = db.Column(db.String(80, collation = 'latin1_general_ci'), nullable=False)
    repres_legal           = db.Column(db.Boolean)
    nome_repres_legal      = db.Column(db.String(80, collation = 'latin1_general_ci'))
    cpf_repres_legal       = db.Column(db.String(14, collation = 'latin1_general_ci'))
    contato_repres_legal   = db.Column(db.String(18, collation = 'latin1_general_ci'))
    rg_repres_legal        = db.Column(db.String(50, collation = 'latin1_general_ci'))
    nascimento_repres_legal = db.Column(db.Date)
    pretende_constituir_pj = db.Column(db.String(80, collation = 'latin1_general_ci'))
    status                 = db.Column(db.Integer, nullable = False)

    def setIndicacao_orgao(self, indicacao_orgao, como_conheceu):
        if como_conheceu == como_conheceu_daj['ORGAOSPUBLICOS'][0]:
            self.indicacao_orgao = indicacao_orgao
        else:
            self.indicacao_orgao = null()

    def setCnpj(self, pj_constituida, cnpj, repres_legal):
        if pj_constituida:
            self.cnpj = cnpj
            self.repres_legal = repres_legal
        else:
            self.cnpj = null()
            self.repres_legal = null()

    def setRepres_legal(self, repres_legal, pj_constituida,nome_repres_legal, cpf_repres_legal,
                        contato_repres_legal, rg_repres_legal, nascimento_repres_legal):
        if (repres_legal  == False) and pj_constituida:
            self.nome_repres_legal = nome_repres_legal
            self.cpf_repres_legal = cpf_repres_legal
            self.contato_repres_legal = contato_repres_legal
            self.rg_repres_legal = rg_repres_legal
            self.nascimento_repres_legal = nascimento_repres_legal
        else:
            self.nome_repres_legal = null()
            self.cpf_repres_legal = null()
            self.contato_repres_legal = null()
            self.rg_repres_legal = null()
            self.nascimento_repres_legal = null()

    def setProcurou_qual_local(self, procurou_outro_local, procurou_qual_local):
        if procurou_outro_local:
            self.procurou_qual_local = procurou_qual_local
        else:
            self.procurou_qual_local = null()

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"Nome:{self.nome}"

class Assistido(db.Model):

    __tablename__       = "assistidos"

    id                  = db.Column(db.Integer, primary_key=True)
    id_atendido         = db.Column(db.Integer, db.ForeignKey("atendidos.id"))
    atendido            = db.relationship("Atendido", lazy="joined")

    #Dados pessoais
    sexo                = db.Column(db.String(1, collation  = 'latin1_general_ci'), nullable=False)
    profissao           = db.Column(db.String(80, collation = 'latin1_general_ci'), nullable=False)
    raca                = db.Column(db.String(20, collation = 'latin1_general_ci'), nullable=False)
    rg                  = db.Column(db.String(50, collation = 'latin1_general_ci'), nullable=False)

    #Dados sociais
    grau_instrucao      = db.Column(db.String(100, collation = 'latin1_general_ci'), nullable=False)

    #Renda e patrimônio
    salario                = db.Column(db.Numeric(10,2), nullable=False)
    beneficio              = db.Column(db.String(30, collation = 'latin1_general_ci'), nullable=False)
    contribui_inss         = db.Column(db.String(20, collation = 'latin1_general_ci'),nullable=False)
    qtd_pessoas_moradia    = db.Column(db.Integer, nullable=False)
    renda_familiar         = db.Column(db.Numeric(10,2), nullable=False)
    participacao_renda     = db.Column(db.String(100, collation = 'latin1_general_ci'), nullable=False)
    tipo_moradia           = db.Column(db.String(100, collation = 'latin1_general_ci'), nullable=False)
    possui_outros_imoveis  = db.Column(db.Boolean, nullable=False)
    possui_veiculos        = db.Column(db.Boolean, nullable=False)
    possui_veiculos_obs    = db.Column(db.String(100, collation = 'latin1_general_ci'))
    quantos_veiculos       = db.Column(db.Integer)
    ano_veiculo            = db.Column(db.String(5, collation = 'latin1_general_ci'))
    doenca_grave_familia   = db.Column(db.String(20, collation = 'latin1_general_ci'),nullable=False)
    pessoa_doente          = db.Column(db.String(50, collation = 'latin1_general_ci'))
    pessoa_doente_obs      = db.Column(db.String(100, collation = 'latin1_general_ci'))
    gastos_medicacao       = db.Column(db.Numeric(10,2))
    obs                    = db.Column(db.String(1000, collation = 'latin1_general_ci'))

    def setCamposVeiculo(self, possui_veiculos, possui_veiculos_obs, quantos_veiculos, ano_veiculo):
        if possui_veiculos:
            self.possui_veiculos_obs = possui_veiculos_obs
            self.quantos_veiculos    = quantos_veiculos
            self.ano_veiculo         = ano_veiculo
        else:
            self.possui_veiculos_obs = null()
            self.quantos_veiculos    = null()
            self.ano_veiculo         = null()

    def setCamposDoenca(self, doenca_grave_familia, pessoa_doente, pessoa_doente_obs, gastos_medicacao):
        if doenca_grave_familia == 'sim':
            self.pessoa_doente     = pessoa_doente
            self.gastos_medicacao  = gastos_medicacao
            if pessoa_doente == 'sim':
                self.pessoa_doente_obs = pessoa_doente_obs
            else:
                self.pessoa_doente_obs = null()
        else:
            self.pessoa_doente     = null()
            self.pessoa_doente_obs = null()
            self.gastos_medicacao  = null()

    def __repr__(self):
        return f"RG:{self.rg}"

class AssistidoPessoaJuridica(db.Model):
    __tablename__       = "assistidos_pessoa_juridica"

    id                  = db.Column(db.Integer, primary_key=True)
    id_assistido        = db.Column(db.Integer, db.ForeignKey("assistidos.id"))
    assistido           = db.relationship("Assistido", lazy="joined")

    #Dados específicos
    socios              = db.Column(db.String(1000, collation = 'latin1_general_ci'))
    situacao_receita    = db.Column(db.String(100, collation = 'latin1_general_ci'), nullable=False)
    enquadramento       = db.Column(db.String(100, collation = 'latin1_general_ci'), nullable=False)
    sede_bh             = db.Column(db.Boolean, nullable=False)
    regiao_sede_bh      = db.Column(db.String(50, collation = 'latin1_general_ci'))
    regiao_sede_outros  = db.Column(db.String(100, collation = 'latin1_general_ci'))
    area_atuacao        = db.Column(db.String(50, collation = 'latin1_general_ci'), nullable=False)
    negocio_nascente    = db.Column(db.Boolean, nullable=False)
    orgao_registro      = db.Column(db.String(100, collation = 'latin1_general_ci'), nullable=False)
    faturamento_anual   = db.Column(db.Numeric(10,2), nullable=False)
    ultimo_balanco_neg  = db.Column(db.String(50, collation = 'latin1_general_ci'))
    resultado_econ_neg  = db.Column(db.String(50, collation = 'latin1_general_ci'))
    tem_funcionarios    = db.Column(db.String(20, collation = 'latin1_general_ci'), nullable=False)
    qtd_funcionarios    = db.Column(db.String(7, collation = 'latin1_general_ci'))

    def setCamposRegiao_sede(self, sede_bh, regiao_sede_bh, regiao_sede_outros):
        if sede_bh:
            self.regiao_sede_bh = regiao_sede_bh
            self.regiao_sede_outros = null()
        else:
            self.regiao_sede_bh = null()
            self.regiao_sede_outros = regiao_sede_outros

    def setQtd_funcionarios(self, tem_funcionarios, qtd_funcionarios):
        if tem_funcionarios:
            self.qtd_funcionarios = qtd_funcionarios
        else:
            self.qtd_funcionarios = null()

    def __repr__(self):
        return f"RG:{self.enquadramento}"


class OrientacaoJuridica(db.Model):
    __tablename__       = "orientacao_juridica"

    id                  = db.Column(db.Integer, primary_key=True)
    area_direito        = db.Column(db.String(50, collation = 'latin1_general_ci'), nullable = False)
    sub_area            = db.Column(db.String(50, collation = 'latin1_general_ci'))
    descricao           = db.Column(db.String(1000, collation = 'latin1_general_ci'), nullable = False)
    status              = db.Column(db.Integer, nullable = False)

    assistenciasJudiciarias = db.relationship("AssistenciaJudiciaria", secondary="assistenciasJudiciarias_xOrientacao_juridica", backref='AssistenciaJudiciaria')
    atendidos               = db.relationship("Atendido", secondary="atendido_xOrientacaoJuridica")

    def setSubAreas(self, area_direito, sub_area, sub_areaAdmin):
        if area_direito == area_do_direito['CIVEL'][0]:
            self.sub_area = sub_area
        elif area_direito == area_do_direito['ADMINISTRATIVO'][0]:
            self.sub_area = sub_areaAdmin
        else:
            self.sub_area = null()

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Atendido_xOrientacaoJuridica(db.Model):
    __tablename__= "atendido_xOrientacaoJuridica"

    id                       = db.Column(db.Integer, primary_key=True)
    id_orientacaoJuridica    = db.Column(db.Integer, db.ForeignKey('orientacao_juridica.id'))
    id_atendido              = db.Column(db.Integer, db.ForeignKey('atendidos.id'))

    atendido                 = db.relationship(Atendido, backref=db.backref("atendido_xOrientacaoJuridica"))
    orientacaoJuridica       = db.relationship(OrientacaoJuridica, backref=db.backref("atendido_xOrientacaoJuridica"))

# ASSISTÊNCIA JUDICIÁRIA
class AssistenciaJudiciaria(db.Model):
    __tablename__= "assistencias_judiciarias"

    id                  = db.Column(db.Integer, primary_key=True)
    nome                = db.Column(db.String(150, collation = 'latin1_general_ci'), nullable=False)
    regiao              = db.Column(db.String(80, collation = 'latin1_general_ci'), nullable=False)
    areas_atendidas     = db.Column(db.String(1000, collation = 'latin1_general_ci'), nullable = False)
    endereco_id         = db.Column(db.Integer, db.ForeignKey("enderecos.id"))
    endereco            = db.relationship("Endereco", lazy="joined")
    telefone            = db.Column(db.String(18, collation = 'latin1_general_ci'), nullable=False)
    email               = db.Column(db.String(80, collation = 'latin1_general_ci'), unique=True, nullable=False)
    status              = db.Column(db.Integer, nullable = False)

    orientacoesJuridicas = db.relationship("OrientacaoJuridica", secondary="assistenciasJudiciarias_xOrientacao_juridica")

    def setAreas_atendidas(self, opcoes):
        self.areas_atendidas = ",".join(opcoes)

    def getAreas_atendidas(self):
        return self.areas_atendidas.split(",")

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class AssistenciaJudiciaria_xOrientacaoJuridica(db.Model):
    __tablename__= "assistenciasJudiciarias_xOrientacao_juridica"

    id                       = db.Column(db.Integer, primary_key=True)
    id_orientacaoJuridica    = db.Column(db.Integer, db.ForeignKey('orientacao_juridica.id'))
    id_assistenciaJudiciaria = db.Column(db.Integer, db.ForeignKey('assistencias_judiciarias.id'))

    assistenciaJudiciaria    = db.relationship(AssistenciaJudiciaria, backref=db.backref("assistenciasJudiciarias_xOrientacao_juridica"))
    orientacaoJuridica     = db.relationship(OrientacaoJuridica, backref=db.backref("assistenciasJudiciarias_xOrientacao_juridica"))
