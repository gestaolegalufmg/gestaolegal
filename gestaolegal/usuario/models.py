from datetime import date, datetime

import click
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from sqlalchemy import false

from gestaolegal import app, db, login_manager
from gestaolegal.models.base import Base
from gestaolegal.models.endereco import Endereco

##############################################################
################## CONSTANTES/ENUMS ##########################
##############################################################

usuario_urole_roles = {
    "USER": "user",  # DEFAULT PARA NAO DAR ERRO, DEPOIS TIRA
    "ADMINISTRADOR": ("admin", "Administrador"),
    "ORIENTADOR": ("orient", "Orientador"),
    "COLAB_PROJETO": ("colab_proj", "Colaborador de projeto"),
    "ESTAGIARIO_DIREITO": ("estag_direito", "Estagiário de Direito"),
    "COLAB_EXTERNO": ("colab_ext", "Colaborador externo"),
    "PROFESSOR": ("prof", "Professor"),
}

usuario_urole_inverso = {
    "admin": "Administrador",
    "orient": "Orientador",
    "colab_proj": "Colaborador de projeto",
    "estag_direito": "Estagiário de Direito",
    "colab_ext": "Colaborador externo",
    "prof": "Professor",
}

sexo_usuario = {
    "MASCULINO": ("M", "Masculino"),
    "FEMININO": ("F", "Feminino"),
    "OUTROS": ("O", "Outro"),
}

estado_civilUsuario = {
    "SOLTEIRO": ("solteiro", "Solteiro"),
    "CASADO": ("casado", "Casado"),
    "DIVORCIADO": ("divorciado", "Divorciado"),
    "SEPARADO": ("separado", "Separado"),
    "UNIAO": ("uniao", "União estável"),
    "VIUVO": ("viuvo", "Viúvo"),
}

tipo_bolsaUsuario = {
    "FUMP": ("fump", "FUMP"),
    "VALE": ("vale", "Valle Ferreira"),
    "PROEX": ("proex", "Projeto de extensão"),
    "OUTRA": ("outra", "Outra"),
}


#####################################################
################## MODELOS ##########################
#####################################################


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, user_id)


class Usuario(Base, UserMixin):
    bcrypt = Bcrypt()

    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(
        db.String(80, collation="latin1_general_ci"), unique=True, nullable=False
    )
    senha = db.Column(db.String(60, collation="latin1_general_ci"), nullable=False)
    urole = db.Column(db.String(50, collation="latin1_general_ci"), nullable=False)
    nome = db.Column(db.String(60, collation="latin1_general_ci"), nullable=False)
    sexo = db.Column(db.String(60, collation="latin1_general_ci"), nullable=False)
    rg = db.Column(db.String(18, collation="latin1_general_ci"), nullable=False)
    cpf = db.Column(db.String(14, collation="latin1_general_ci"), nullable=False)
    profissao = db.Column(db.String(45, collation="latin1_general_ci"), nullable=False)
    estado_civil = db.Column(
        db.String(45, collation="latin1_general_ci"), nullable=False
    )
    nascimento = db.Column(db.Date, nullable=False)
    telefone = db.Column(db.String(18, collation="latin1_general_ci"))
    celular = db.Column(db.String(18, collation="latin1_general_ci"), nullable=False)
    oab = db.Column(db.String(30, collation="latin1_general_ci"))
    obs = db.Column(db.Text(collation="latin1_general_ci"))
    data_entrada = db.Column(db.Date, nullable=False)
    data_saida = db.Column(db.Date, nullable=True)
    criado = db.Column(db.DateTime, nullable=False)
    modificado = db.Column(db.DateTime)
    criadopor = db.Column(db.Integer, nullable=False)
    matricula = db.Column(db.String(45, collation="latin1_general_ci"))
    modificadopor = db.Column(db.Integer)
    bolsista = db.Column(db.Boolean, nullable=False)
    tipo_bolsa = db.Column(db.String(50, collation="latin1_general_ci"))
    horario_atendimento = db.Column(db.String(30, collation="latin1_general_ci"))  # !!!
    suplente = db.Column(db.String(30, collation="latin1_general_ci"))
    # TODO: Ver qual é o Input de Ferias se é data ou só um status
    ferias = db.Column(db.String(150, collation="latin1_general_ci"))
    status = db.Column(db.Boolean, nullable=False)

    cert_atuacao_DAJ = db.Column(
        db.String(3, collation="latin1_general_ci"), nullable=False, default="nao"
    )
    inicio_bolsa = db.Column(db.DateTime)
    fim_bolsa = db.Column(db.DateTime)
    endereco_id = db.Column(db.Integer, db.ForeignKey("enderecos.id"))
    endereco = db.relationship(Endereco, lazy="joined")
    chave_recuperacao = db.Column(db.Boolean, server_default=false())

    def setSenha(self, senha):
        self.senha = self.bcrypt.generate_password_hash(senha).decode("utf-8")

    def checa_senha(self, senha):
        return self.bcrypt.check_password_hash(self.senha, senha)

    def atualizaCamposModificao(self, modificadoPor):
        self.modificado = datetime.now()
        self.modificadopor = modificadoPor

    def setCamposBolsista(self, bolsista, tipo_bolsa, inicio_bolsa, fim_bolsa):
        self.bolsista = bolsista
        if self.bolsista == True:
            self.inicio_bolsa = inicio_bolsa
            self.fim_bolsa = fim_bolsa
            self.tipo_bolsa = tipo_bolsa
        else:
            self.inicio_bolsa = None
            self.fim_bolsa = None
            self.tipo_bolsa = None

    def tokenRecuperacao(self, expires_sec=2200):
        s = Serializer(app.config["SECRET_KEY"], expires_sec)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @staticmethod
    def verificaToken(token):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return db.session.get(Usuario, user_id)


@app.cli.command("create-admin")
@click.argument("nome")
@click.argument("email")
@click.argument("senha")
def create_user(nome, email, senha):
    """
    Este comando cria um usuário com permissões de administrador.
    Deve ser usado na primeira instalação para criar o usuário que irá acessar o sistema pelo primeira vez.
    Os demais usuários devem ser criados a partir da interface web.
    """

    entidade_endereco = Endereco(
        logradouro="Administrador",
        numero="0",
        complemento="0",
        bairro="Administrador",
        cep="000000000",
        cidade="Administrador",
        estado="AD",
    )

    entidade_usuario = Usuario(
        senha=senha,
        urole=usuario_urole_roles["ADMINISTRADOR"][0],
        nome=nome,
        email=email,
        sexo="M",
        rg="123",
        cpf="12345678901",
        profissao="admin",
        estado_civil="solteiro",
        nascimento=date.today(),
        data_entrada=date.today(),
        criado=datetime.now(),
        celular="123",
        criadopor=1,
        bolsista=False,
        endereco_id=entidade_endereco.id,
        endereco=entidade_endereco,
        status=True,
    )
    entidade_usuario.setSenha(senha)

    db.session.add(entidade_usuario)
    db.session.commit()
