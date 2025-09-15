from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING

from flask_login import UserMixin

from gestaolegal import login_manager
from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.endereco import Endereco

if TYPE_CHECKING:
    from gestaolegal.schemas.usuario import UsuarioSchema


@login_manager.user_loader
def load_user(user_id):
    from gestaolegal.services.usuario_service import UsuarioService

    usuario_service = UsuarioService()
    return usuario_service.find_by_id(user_id)


@dataclass(frozen=True)
class Usuario(UserMixin, BaseModel):
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
    endereco: "Endereco"
    chave_recuperacao: bool

    def __post_init__(self):
        pass

    @staticmethod
    def from_sqlalchemy(usuario_schema: "UsuarioSchema") -> "Usuario":
        usuario_items = usuario_schema.to_dict()
        usuario_items["endereco"] = (
            Endereco.from_sqlalchemy(usuario_schema.endereco)
            if usuario_schema.endereco
            else None
        )
        return Usuario(**usuario_items)
