from dateutil.parser import parse as parse_date
from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING, Any
from typing_extensions import override

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.endereco import Endereco

if TYPE_CHECKING:
    from gestaolegal.schemas.user import UserSchema


@dataclass(frozen=True)
class User(BaseModel):
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
    
    id: int | None = None

    chave_recuperacao: bool | None = None
    endereco: "Endereco | None" = None
    status: bool = True

    modificado: datetime = datetime.now()
    criado: datetime = datetime.now()

    def __post_init__(self):
        if isinstance(self.nascimento, str):
            object.__setattr__(self, 'nascimento', self._parse_date_string(self.nascimento))
        
        if isinstance(self.data_entrada, str):
            object.__setattr__(self, 'data_entrada', self._parse_date_string(self.data_entrada))
        
        if self.data_saida and isinstance(self.data_saida, str):
            object.__setattr__(self, 'data_saida', self._parse_date_string(self.data_saida))
        
        if self.inicio_bolsa and isinstance(self.inicio_bolsa, str):
            object.__setattr__(self, 'inicio_bolsa', self._parse_date_string(self.inicio_bolsa))
        
        if self.fim_bolsa and isinstance(self.fim_bolsa, str):
            object.__setattr__(self, 'fim_bolsa', self._parse_date_string(self.fim_bolsa))

        if not self.bolsista:
            object.__setattr__(self, 'inicio_bolsa', None)
            object.__setattr__(self, 'fim_bolsa', None)
            object.__setattr__(self, 'tipo_bolsa', None)

    @staticmethod
    def _parse_date_string(date_value: str | date | None) -> date | None:
        if date_value is None:
            return None
        if isinstance(date_value, date):
            return date_value

        return parse_date(date_value)

    @classmethod
    def from_sqlalchemy(
        cls, schema: "UserSchema", shallow: bool = False
    ) -> "User":
        user_items = schema.to_dict()

        if not shallow:
            user_items["endereco"] = (
                Endereco.from_sqlalchemy(schema.endereco) if schema.endereco else None
            )
        else:
            user_items["endereco"] = None

        return User(**user_items)



    @override
    def to_dict(self, with_endereco: bool = True, *args: Any, **kwargs: Any) -> dict[str, Any]:
        data = super().to_dict(*args, **kwargs)
        
        endereco: Endereco | None = data.pop("endereco")
        if endereco and with_endereco:
            data["logradouro"] = endereco.logradouro
            data["numero"] = endereco.numero
            data["complemento"] = endereco.complemento
            data["bairro"] = endereco.bairro
            data["cep"] = endereco.cep
            data["cidade"] = endereco.cidade
            data["estado"] = endereco.estado

        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"returning dict: {data}")

        return data