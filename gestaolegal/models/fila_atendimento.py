from dataclasses import dataclass
from datetime import datetime


@dataclass
class FilaAtendimento:
    id_atendido: int
    prioridade: int
    senha: str
    data_criacao: datetime
    status: int
    psicologia: int = 0
    tipo: str | None = None
    id: int | None = None


@dataclass
class FilaAtendimentoItem:
    id: int
    senha: str
    posicao: int | None
    tipo: str | None
    prioridade: int
    status: int
    status_label: str
    data_criacao: datetime
    id_atendido: int
    atendido_nome: str
    atendido_cpf: str
