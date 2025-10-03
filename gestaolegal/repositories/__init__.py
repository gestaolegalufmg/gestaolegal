from gestaolegal.repositories.assistido_repository import AssistidoRepository
from gestaolegal.repositories.atendido_repository import AtendidoRepository
from gestaolegal.repositories.base_repository import (
    BaseRepository,
    PaginatedResult,
    WhereCondition,
    WhereConditions,
)
from gestaolegal.repositories.endereco_repository import EnderecoRepository
from gestaolegal.repositories.orientacao_juridica_repository import (
    OrientacaoJuridicaRepository,
)
from gestaolegal.repositories.user_repository import UserRepository

__all__ = [
    "BaseRepository",
    "PaginatedResult",
    "WhereCondition",
    "WhereConditions",
    "AssistidoRepository",
    "AtendidoRepository",
    "EnderecoRepository",
    "OrientacaoJuridicaRepository",
    "UserRepository",
]

