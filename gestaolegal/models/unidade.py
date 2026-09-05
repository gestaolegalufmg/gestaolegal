from dataclasses import dataclass
from datetime import datetime


@dataclass
class Unidade:
    nome: str
    sigla: str
    ativa: bool
    criado: datetime
    id: int | None = None
