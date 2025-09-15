from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from gestaolegal.models.usuario import Usuario

if TYPE_CHECKING:
    from gestaolegal.models.atendido import Atendido
    from gestaolegal.schemas.caso import CasoSchema


@dataclass(frozen=True)
class Caso:
    id: int

    id_usuario_responsavel: int
    usuario_responsavel: "Usuario"
    area_direito: str
    sub_area: str | None
    clientes: list["Atendido"]

    id_orientador: int | None
    orientador: "Usuario | None"
    id_estagiario: int | None
    estagiario: "Usuario | None"
    id_colaborador: int | None
    colaborador: "Usuario | None"

    data_criacao: datetime
    id_criado_por: int
    criado_por: "Usuario"

    data_modificacao: datetime | None
    id_modificado_por: int | None
    modificado_por: "Usuario | None"

    situacao_deferimento: str
    justif_indeferimento: str | None
    status: bool
    descricao: str | None
    numero_ultimo_processo: int | None

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(
        caso_schema: "CasoSchema", load_clientes: bool = True
    ) -> "Caso":
        caso_items = caso_schema.to_dict()

        if load_clientes and caso_schema.clientes:
            from gestaolegal.models.atendido import Atendido

            caso_items["clientes"] = [
                Atendido.from_sqlalchemy(cliente, load_casos=False)
                for cliente in caso_schema.clientes
            ]
        else:
            caso_items["clientes"] = []

        caso_items["usuario_responsavel"] = (
            Usuario.from_sqlalchemy(caso_schema.usuario_responsavel)
            if caso_schema.usuario_responsavel
            else None
        )
        caso_items["orientador"] = (
            Usuario.from_sqlalchemy(caso_schema.orientador)
            if caso_schema.orientador
            else None
        )
        caso_items["estagiario"] = (
            Usuario.from_sqlalchemy(caso_schema.estagiario)
            if caso_schema.estagiario
            else None
        )
        caso_items["colaborador"] = (
            Usuario.from_sqlalchemy(caso_schema.colaborador)
            if caso_schema.colaborador
            else None
        )
        caso_items["criado_por"] = (
            Usuario.from_sqlalchemy(caso_schema.criado_por)
            if caso_schema.criado_por
            else None
        )
        caso_items["modificado_por"] = (
            Usuario.from_sqlalchemy(caso_schema.modificado_por)
            if caso_schema.modificado_por
            else None
        )

        return Caso(**caso_items)
