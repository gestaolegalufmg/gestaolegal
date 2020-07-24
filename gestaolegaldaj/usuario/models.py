import enum
from datetime import datetime
from enum import Enum

from flask import session
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from sqlalchemy.sql import expression
from sqlalchemy import null

from gestaolegaldaj import db, login_manager
from datetime import datetime

##############################################################
################## CONSTANTES/ENUMS ##########################
##############################################################

usuario_urole_roles = {
    'USER': 'user', #DEFAULT PARA NAO DAR ERRO, DEPOIS TIRA
    'ADMINISTRADOR' :       ('admin','Administrador'),
    'ORIENTADOR' :          ('orient','Orientador'),
    'COLAB_PROJETO':        ('colab_proj','Colaborador de projeto'),
    'ESTAGIARIO_DIREITO':   ('estag_direito','Estagiário de Direito'),
    'COLAB_EXTERNO':        ('colab_ext','Colaborador externo'),
    'PROFESSOR':            ('prof','Professor')
}

sexo_usuario = {
    'MASCULINO' : ('M','Masculino'),
    'FEMININO'  : ('F', 'Feminino'),
    'OUTROS'     : ('O', 'Outro')
}

estado_civilUsuario = {
    'SOLTEIRO'   : ('solteiro', 'Solteiro'),
    'CASADO'     : ('casado', 'Casado'),
    'DIVORCIADO' : ('divorciado', 'Divorciado'),
    'SEPARADO'   : ('separado', 'Separado'),
    'UNIAO'      : ('uniao', 'União estável'),
    'VIUVO'      : ('viuvo', 'Viúvo')
}

tipo_bolsaUsuario = {
    'FUMP'  : ('fump','FUMP'),
    'VALE'  : ('vale','VALE'),
    'PROEX' : ('proex','Projeto de extensão'),
    'OUTRA' : ('outra', 'Outra')
}

#####################################################
################## MODELOS ##########################
#####################################################

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(user_id)

class Usuario(db.Model, UserMixin):
    bcrypt = Bcrypt()

    __tablename__ = 'usuarios'
    id                  = db.Column(db.Integer, primary_key=True)
    email               = db.Column(db.String(80, collation = 'latin1_general_ci'), unique=True, nullable=False)
    senha               = db.Column(db.String(60, collation = 'latin1_general_ci'), nullable=False)
    urole               = db.Column(db.String(50, collation = 'latin1_general_ci'), nullable=False)
    nome                = db.Column(db.String(60, collation = 'latin1_general_ci'), nullable=False)
    sexo                = db.Column(db.String(60, collation = 'latin1_general_ci'), nullable=False)
    rg                  = db.Column(db.String(18, collation = 'latin1_general_ci'), nullable=False)
    cpf                 = db.Column(db.String(14, collation = 'latin1_general_ci'), nullable=False)
    profissao           = db.Column(db.String(45, collation = 'latin1_general_ci'), nullable=False)
    estado_civil        = db.Column(db.String(45, collation = 'latin1_general_ci'), nullable=False)
    nascimento          = db.Column(db.Date, nullable=False)
    telefone            = db.Column(db.String(18, collation = 'latin1_general_ci'))
    celular             = db.Column(db.String(18, collation = 'latin1_general_ci'), nullable=False)
    oab                 = db.Column(db.String(30, collation = 'latin1_general_ci'))
    obs                 = db.Column(db.Text(collation = 'latin1_general_ci'))
    data_entrada        = db.Column(db.Date, nullable=False)
    data_saida          = db.Column(db.Date, nullable=True)
    criado              = db.Column(db.DateTime, nullable=False)
    modificado          = db.Column(db.DateTime)
    criadopor           = db.Column(db.Integer, nullable=False)
    matricula           = db.Column(db.String(45, collation = 'latin1_general_ci'))
    modificadopor       = db.Column(db.Integer)
    bolsista            = db.Column(db.Boolean, nullable=False)
    tipo_bolsa          = db.Column(db.String(50, collation = 'latin1_general_ci'))
    #TODO: Analisar necessidade de separar dia/horário de atendimento
    #dia_atendimento     = db.Column(db.String(255, collation = 'latin1_general_ci')) #!!!
    horario_atendimento = db.Column(db.String(30, collation = 'latin1_general_ci')) #!!!
    suplente            = db.Column(db.String(30, collation = 'latin1_general_ci'))
    #TODO: Ver qual é o Input de Ferias se é data ou só um status
    ferias              = db.Column(db.String(150, collation = 'latin1_general_ci'))
    status              = db.Column(db.Boolean, nullable=False)

    cert_atuacao_DAJ    = db.Column(db.String(3, collation = 'latin1_general_ci'), nullable=False, default="nao")
    inicio_bolsa        = db.Column(db.DateTime)
    fim_bolsa           = db.Column(db.DateTime)
    endereco_id         = db.Column(db.Integer, db.ForeignKey("enderecos.id"))
    endereco            = db.relationship("Endereco", lazy="joined")

    def setSenha(self, senha):
        self.senha = self.bcrypt.generate_password_hash(senha).decode('utf-8')

    def checa_senha(self, senha):
        return self.bcrypt.check_password_hash(self.senha,senha)

    def atualizaCamposModificao(self, modificadoPor):
        self.modificado= datetime.now()
        self.modificadopor = modificadoPor

    def setCamposBolsista(self, bolsista, tipo_bolsa,inicio_bolsa, fim_bolsa):
        self.bolsista = bolsista
        if self.bolsista == True:
            self.inicio_bolsa = inicio_bolsa
            self.fim_bolsa    = fim_bolsa
            self.tipo_bolsa   = tipo_bolsa
        else:
            self.inicio_bolsa = null()
            self.fim_bolsa    = null()
            self.tipo_bolsa   = null()



class Endereco(db.Model):

    __tablename__ = "enderecos"

    id          = db.Column(db.Integer, primary_key=True)
    logradouro  = db.Column(db.String(100, collation = "latin1_general_ci"), nullable=False)
    numero      = db.Column(db.String(8, collation = "latin1_general_ci"), nullable=False)
    complemento = db.Column(db.String(100, collation = "latin1_general_ci"))
    bairro      = db.Column(db.String(100, collation = "latin1_general_ci"), nullable=False)
    cep         = db.Column(db.String(9, collation = "latin1_general_ci"), nullable=False)

    cidade_id   = db.Column(db.Integer, db.ForeignKey("cidades.id"))
    cidade      = db.relationship("Cidade", lazy='joined')




class Cidade(db.Model):

    __tablename__ = "cidades"

    id        = db.Column(db.Integer, primary_key=True)
    cidade    = db.Column(db.String(60, collation = "latin1_general_ci"), nullable=False)

    estado_id = db.Column(db.Integer, db.ForeignKey("estados.id"))
    estado    = db.relationship("Estado", lazy='joined')

class Estado(db.Model):

    __tablename__ = "estados"

    id        = db.Column(db.Integer, primary_key=True)
    estado    = db.Column(db.String(45, collation = "latin1_general_ci"), nullable=False)
    uf        = db.Column(db.String(2, collation = "latin1_general_ci"), nullable=False)
