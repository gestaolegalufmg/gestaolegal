from dataclasses import dataclass, fields
from datetime import date, datetime
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from gestaolegal.models.endereco import Endereco


@dataclass
class User:
    email: str
    senha: str
    urole: Literal["admin", "colab_proj", "orient", "estag_direito", "colab_ext"]
    nome: str
    sexo: str
    rg: str
    cpf: str
    profissao: str
    estado_civil: str
    nascimento: date
    telefone: str | None
    celular: str
    oab: str | None
    obs: str | None
    data_entrada: date
    data_saida: date | None
    criadopor: int
    matricula: str | None
    modificadopor: int | None
    bolsista: bool
    tipo_bolsa: str | None
    horario_atendimento: str | None
    suplente: str | None
    ferias: str | None
    cert_atuacao_DAJ: str
    inicio_bolsa: datetime | None
    fim_bolsa: datetime | None
    endereco_id: int
    status: bool
    criado: datetime

    id: int | None = None
    modificado: datetime | None = None
    chave_recuperacao: bool | None = None
    endereco: "Endereco | None" = None

    def to_info(self) -> "UserInfo":
        user_info_fields = fields(UserInfo)
        data = {field.name: getattr(self, field.name) for field in user_info_fields}
        return UserInfo(**data)

    @staticmethod
    def to_info_optional(user: "User | None") -> "UserInfo | None":
        return user.to_info() if user else None


@dataclass
class UserInfo:
    email: str
    urole: Literal["admin", "colab_proj", "orient", "estag_direito", "colab_ext"]
    nome: str
    sexo: str
    rg: str
    cpf: str
    profissao: str
    estado_civil: str
    nascimento: date
    telefone: str | None
    celular: str
    oab: str | None
    obs: str | None
    data_entrada: date
    data_saida: date | None
    criadopor: int
    matricula: str | None
    modificadopor: int | None
    bolsista: bool
    tipo_bolsa: str | None
    horario_atendimento: str | None
    suplente: str | None
    ferias: str | None
    cert_atuacao_DAJ: str
    inicio_bolsa: datetime | None
    fim_bolsa: datetime | None
    endereco_id: int
    status: bool
    criado: datetime

    id: int | None = None
    modificado: datetime | None = None
    chave_recuperacao: bool | None = None
    endereco: "Endereco | None" = None
