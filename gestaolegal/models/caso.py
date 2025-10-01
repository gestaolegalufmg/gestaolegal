from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.user import User

if TYPE_CHECKING:
    from gestaolegal.models.atendido import Atendido
    from gestaolegal.schemas.caso import CasoSchema


@dataclass(frozen=True)
class Caso(BaseModel):
    id: int

    id_usuario_responsavel: int
    usuario_responsavel: "User"
    area_direito: str
    sub_area: str | None
    clientes: list["Atendido"]

    id_orientador: int | None
    orientador: "User | None"
    id_estagiario: int | None
    estagiario: "User | None"
    id_colaborador: int | None
    colaborador: "User | None"

    data_criacao: datetime
    id_criado_por: int
    criado_por: "User"

    data_modificacao: datetime | None
    id_modificado_por: int | None
    modificado_por: "User | None"

    situacao_deferimento: str
    justif_indeferimento: str | None
    status: bool
    descricao: str | None
    numero_ultimo_processo: int | None

    def __post_init__(self):
        return

    @classmethod
    def from_sqlalchemy(cls, schema: "CasoSchema", shallow: bool = False) -> "Caso":
        caso_items = schema.to_dict()

        if not shallow:
            from gestaolegal.models.atendido import Atendido

            caso_items["clientes"] = [
                Atendido.from_sqlalchemy(cliente, shallow=True)
                for cliente in schema.clientes
            ]
            caso_items["usuario_responsavel"] = (
                User.from_sqlalchemy(schema.usuario_responsavel)
                if schema.usuario_responsavel
                else None
            )
            caso_items["orientador"] = (
                User.from_sqlalchemy(schema.orientador)
                if schema.orientador
                else None
            )
            caso_items["estagiario"] = (
                User.from_sqlalchemy(schema.estagiario)
                if schema.estagiario
                else None
            )
            caso_items["colaborador"] = (
                User.from_sqlalchemy(schema.colaborador)
                if schema.colaborador
                else None
            )
            caso_items["criado_por"] = (
                User.from_sqlalchemy(schema.criado_por)
                if schema.criado_por
                else None
            )
            caso_items["modificado_por"] = (
                User.from_sqlalchemy(schema.modificado_por)
                if schema.modificado_por
                else None
            )
        else:
            caso_items["clientes"] = []
            caso_items["usuario_responsavel"] = None
            caso_items["orientador"] = None
            caso_items["estagiario"] = None
            caso_items["colaborador"] = None
            caso_items["criado_por"] = None
            caso_items["modificado_por"] = None

        return Caso(**caso_items)
