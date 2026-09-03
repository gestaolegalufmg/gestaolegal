"""Helpers de data/hora no fuso de Brasília.

O servidor roda em UTC, mas o sistema é operado presencialmente na DAJ: dia de
plantão, senha da fila e registro de ponto são todos em horário de parede de
Brasília. Gravamos os timestamps já convertidos (naive) para que a filtragem por
dia seja consistente com o que é exibido.
"""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

FUSO_BRASILIA = ZoneInfo("America/Sao_Paulo")


def agora_brasilia() -> datetime:
    """Data/hora atual em Brasília, como datetime "naive" (sem tzinfo)."""
    return datetime.now(FUSO_BRASILIA).replace(tzinfo=None)


def hoje_brasilia() -> date:
    return agora_brasilia().date()


def dia_util_anterior(referencia: date | None = None) -> date:
    """Último dia útil antes da referência (padrão: hoje em Brasília).

    Segunda-feira volta para a sexta anterior e domingo para a sexta; nos demais
    dias é simplesmente a véspera.
    """
    referencia = referencia or hoje_brasilia()
    # date.weekday(): segunda = 0 ... domingo = 6
    dias_atras = {0: 3, 6: 2}.get(referencia.weekday(), 1)
    return referencia - timedelta(days=dias_atras)
