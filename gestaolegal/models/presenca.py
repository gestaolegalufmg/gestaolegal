from dataclasses import dataclass
from datetime import datetime

from gestaolegal.models.plantao import Confirmacao


class StatusPresenca:
    """Próxima ação disponível no relógio de ponto."""

    ENTRADA = "entrada"
    SAIDA = "saida"


@dataclass
class RegistroEntrada:
    """Ponto de um dia. `status=True` = em curso (entrada sem saída registrada)."""

    data_entrada: datetime
    # Enquanto o registro está em curso guarda o provisório 23:59:59 do dia da
    # entrada: a coluna é NOT NULL no schema legado.
    data_saida: datetime
    id_usuario: int
    confirmacao: str = Confirmacao.ABERTO
    status: bool = True
    id: int | None = None
