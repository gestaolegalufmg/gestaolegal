from dataclasses import dataclass
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.endereco import Endereco
from gestaolegal.models.orientacao_juridica import OrientacaoJuridica
from gestaolegal.schemas.assistencia_judiciaria import AssistenciaJudiciariaSchema

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class AssistenciaJudiciaria(BaseModel):
    id: int
    nome: str
    regiao: str
    areas_atendidas: str
    endereco_id: int | None
    endereco: "Endereco | None"
    telefone: str
    email: str
    status: int
    orientacoes_juridicas: list["OrientacaoJuridica"]

    def __post_init__(self):
        return

    @classmethod
    def from_sqlalchemy(
        cls, schema: "AssistenciaJudiciariaSchema", shallow: bool = False
    ) -> "AssistenciaJudiciaria":
        assistencia_judiciaria_items = schema.to_dict()

        if not shallow:
            assistencia_judiciaria_items["endereco"] = (
                Endereco.from_sqlalchemy(schema.endereco) if schema.endereco else None
            )
            assistencia_judiciaria_items["orientacoes_juridicas"] = [
                OrientacaoJuridica.from_sqlalchemy(orientacao, shallow=True)
                for orientacao in schema.orientacoesJuridicas
                if orientacao is not None
            ]
        else:
            assistencia_judiciaria_items["endereco"] = None
            assistencia_judiciaria_items["orientacoes_juridicas"] = []

        return AssistenciaJudiciaria(**assistencia_judiciaria_items)
