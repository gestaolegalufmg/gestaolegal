from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from gestaolegal.models.endereco import Endereco
from gestaolegal.models.orientacao_juridica import OrientacaoJuridica
from gestaolegal.schemas.assistencia_judiciaria import AssistenciaJudiciariaSchema

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class AssistenciaJudiciaria:
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "nome": self.nome,
            "regiao": self.regiao,
            "areas_atendidas": self.areas_atendidas,
            "endereco_id": self.endereco_id,
            "endereco": self.endereco,
            "telefone": self.telefone,
            "email": self.email,
            "status": self.status,
            "orientacoes_juridicas": self.orientacoes_juridicas,
        }

    @staticmethod
    def from_sqlalchemy(
        assistencia_judiciaria_schema: "AssistenciaJudiciariaSchema",
    ) -> "AssistenciaJudiciaria":
        assistencia_judiciaria_items = assistencia_judiciaria_schema.to_dict()
        assistencia_judiciaria_items["endereco"] = (
            Endereco.from_sqlalchemy(assistencia_judiciaria_schema.endereco)
            if assistencia_judiciaria_schema.endereco
            else None
        )
        assistencia_judiciaria_items["orientacoes_juridicas"] = [
            OrientacaoJuridica.from_sqlalchemy(
                orientacao
            ) for orientacao in assistencia_judiciaria_schema.orientacoesJuridicas if orientacao is not None]

        return AssistenciaJudiciaria(**assistencia_judiciaria_items)
