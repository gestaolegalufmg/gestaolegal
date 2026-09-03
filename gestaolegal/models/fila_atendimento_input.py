from pydantic import field_validator

from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.fila_atendimento import FilaPrioridade


class FilaAtendimentoCreateInput(BaseModel):
    id_atendido: int
    prioridade: int
    psicologia: bool = False

    @field_validator("prioridade")
    @classmethod
    def validate_prioridade(cls, value: int) -> int:
        if value not in FilaPrioridade.VALORES:
            raise ValueError(
                "prioridade deve ser 0 (normal), 1 (prioridade) ou 2 (super prioridade)"
            )
        return value
