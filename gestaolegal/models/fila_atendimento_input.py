from gestaolegal.models.base_model import BaseModel

TIPOS_FILA = [
    "Atendimento Jurídico",
    "Assistência Judiciária",
    "Orientação Jurídica",
    "Atendimento Psicológico",
]


class AdicionarFilaInput(BaseModel):
    id_atendido: int
    tipo: str
    prioridade: int = 0
