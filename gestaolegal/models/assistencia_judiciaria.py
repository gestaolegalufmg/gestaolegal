from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.orientacao_juridica import OrientacaoJuridica
    from gestaolegal.schemas.assistencia_judiciaria import AssistenciaJudiciariaSchema
    from gestaolegal.schemas.endereco import EnderecoSchema


@dataclass(frozen=True)
class AssistenciaJudiciaria:
    id: int
    nome: str
    regiao: str
    areas_atendidas: str
    endereco_id: int | None
    endereco: "EnderecoSchema | None"
    telefone: str
    email: str
    status: int
    orientacoes_juridicas: list["OrientacaoJuridica"]

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(
        assistencia_judiciaria: "AssistenciaJudiciariaSchema",
    ) -> "AssistenciaJudiciaria":
        return AssistenciaJudiciaria(
            id=assistencia_judiciaria.id,
            nome=assistencia_judiciaria.nome,
            regiao=assistencia_judiciaria.regiao,
            areas_atendidas=assistencia_judiciaria.areas_atendidas,
            endereco_id=assistencia_judiciaria.endereco_id,
            endereco=assistencia_judiciaria.endereco,
            telefone=assistencia_judiciaria.telefone,
            email=assistencia_judiciaria.email,
            status=assistencia_judiciaria.status,
            orientacoes_juridicas=assistencia_judiciaria.orientacoesJuridicas,
        )
