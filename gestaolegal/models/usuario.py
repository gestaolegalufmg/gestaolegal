from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING

from flask import current_app
from flask_login import UserMixin
from itsdangerous import Serializer

from gestaolegal import bcrypt, login_manager
from gestaolegal.database import get_db
from gestaolegal.schemas.usuario import UsuarioSchema

if TYPE_CHECKING:
    from gestaolegal.schemas.endereco import EnderecoSchema


@login_manager.user_loader
def load_user(user_id):
    db = get_db()

    db_user = db.session.get(UsuarioSchema, user_id)
    return Usuario.from_sqlalchemy(db_user)


@dataclass(frozen=True)
class Usuario(UserMixin):
    id: int
    email: str
    senha: str
    urole: str
    nome: str
    sexo: str
    rg: str
    cpf: str
    profissao: str
    estado_civil: str
    nascimento: date
    telefone: str
    celular: str
    oab: str
    obs: str
    data_entrada: date
    data_saida: date | None
    criado: datetime
    modificado: datetime | None
    criadopor: int
    matricula: str
    modificadopor: int | None
    bolsista: bool
    tipo_bolsa: str
    horario_atendimento: str
    suplente: str
    ferias: str
    status: bool
    cert_atuacao_DAJ: str
    inicio_bolsa: datetime | None
    fim_bolsa: datetime | None
    endereco_id: int | None
    endereco: "EnderecoSchema"
    chave_recuperacao: bool

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(usuario: "UsuarioSchema") -> "Usuario":
        return Usuario(
            id=usuario.id,
            email=usuario.email,
            senha=usuario.senha,
            urole=usuario.urole,
            nome=usuario.nome,
            sexo=usuario.sexo,
            rg=usuario.rg,
            cpf=usuario.cpf,
            profissao=usuario.profissao,
            estado_civil=usuario.estado_civil,
            nascimento=usuario.nascimento,
            telefone=usuario.telefone,
            celular=usuario.celular,
            oab=usuario.oab,
            obs=usuario.obs,
            data_entrada=usuario.data_entrada,
            data_saida=usuario.data_saida,
            criado=usuario.criado,
            modificado=usuario.modificado,
            criadopor=usuario.criadopor,
            matricula=usuario.matricula,
            modificadopor=usuario.modificadopor,
            bolsista=usuario.bolsista,
            tipo_bolsa=usuario.tipo_bolsa,
            horario_atendimento=usuario.horario_atendimento,
            suplente=usuario.suplente,
            ferias=usuario.ferias,
            status=usuario.status,
            cert_atuacao_DAJ=usuario.cert_atuacao_DAJ,
            inicio_bolsa=usuario.inicio_bolsa,
            fim_bolsa=usuario.fim_bolsa,
            endereco_id=usuario.endereco_id,
            endereco=usuario.endereco,
            chave_recuperacao=usuario.chave_recuperacao,
        )

    def setSenha(self, senha):
        self.senha = bcrypt.generate_password_hash(senha).decode("utf-8")

    def checa_senha(self, senha):
        return bcrypt.check_password_hash(self.senha, senha)

    def atualizaCamposModificao(self, modificadoPor):
        self.modificado = datetime.now()
        self.modificadopor = modificadoPor

    def setCamposBolsista(self, bolsista, tipo_bolsa, inicio_bolsa, fim_bolsa):
        self.bolsista = bolsista
        if self.bolsista:
            self.inicio_bolsa = inicio_bolsa
            self.fim_bolsa = fim_bolsa
            self.tipo_bolsa = tipo_bolsa
        else:
            self.inicio_bolsa = None
            self.fim_bolsa = None
            self.tipo_bolsa = None

    def tokenRecuperacao(self, expires_sec=2200):
        s = Serializer(current_app.config["SECRET_KEY"], expires_sec)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    def as_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "urole": self.urole,
            "nome": self.nome,
            "sexo": self.sexo,
            "rg": self.rg,
            "cpf": self.cpf,
            "profissao": self.profissao,
            "estado_civil": self.estado_civil,
            "nascimento": str(self.nascimento) if self.nascimento else None,
            "telefone": self.telefone,
            "celular": self.celular,
            "oab": self.oab,
            "obs": self.obs,
            "data_entrada": str(self.data_entrada) if self.data_entrada else None,
            "data_saida": str(self.data_saida) if self.data_saida else None,
            "criado": str(self.criado) if self.criado else None,
            "modificado": str(self.modificado) if self.modificado else None,
            "criadopor": self.criadopor,
            "matricula": self.matricula,
            "modificadopor": self.modificadopor,
            "bolsista": self.bolsista,
            "tipo_bolsa": self.tipo_bolsa,
            "horario_atendimento": self.horario_atendimento,
            "suplente": self.suplente,
            "ferias": self.ferias,
            "status": self.status,
            "cert_atuacao_DAJ": self.cert_atuacao_DAJ,
            "inicio_bolsa": str(self.inicio_bolsa) if self.inicio_bolsa else None,
            "fim_bolsa": str(self.fim_bolsa) if self.fim_bolsa else None,
            "endereco_id": self.endereco_id,
            "chave_recuperacao": self.chave_recuperacao,
        }

    @staticmethod
    def verificaToken(token):
        db = get_db()

        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return db.session.get(UsuarioSchema, user_id)
