from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.atendido import Atendido


class FilaPrioridade:
    """Grau de prioridade de um atendido na fila."""

    NORMAL = 0
    PRIORIDADE = 1
    SUPER_PRIORIDADE = 2

    VALORES = (NORMAL, PRIORIDADE, SUPER_PRIORIDADE)


class FilaStatus:
    """Estado de um atendido dentro da fila do dia."""

    NA_FILA = 0
    CHAMADO = 1
    CANCELADO = 2


# Prefixo da senha por grau de prioridade (N01, P01, S01).
SENHA_PREFIXOS = {
    FilaPrioridade.NORMAL: "N",
    FilaPrioridade.PRIORIDADE: "P",
    FilaPrioridade.SUPER_PRIORIDADE: "S",
}


@dataclass
class FilaAtendimento:
    psicologia: int
    prioridade: int
    senha: str
    status: int

    id: int | None = None
    id_atendido: int | None = None
    data_criacao: datetime | None = None
    data_saida: datetime | None = None

    atendido: "Atendido | None" = None


@dataclass
class ListFilaAtendimento:
    """Linha da fila com o nome do atendido já resolvido, para exibição."""

    id: int
    id_atendido: int | None
    nome: str | None
    senha: str
    prioridade: int
    psicologia: int
    status: int
    data_criacao: datetime | None
    data_saida: datetime | None
