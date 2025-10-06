from gestaolegal.repositories.atendido_repository import AtendidoRepository
from gestaolegal.repositories.endereco_repository import EnderecoRepository
from gestaolegal.repositories.orientacao_juridica_repository import (
    OrientacaoJuridicaRepository,
)
from gestaolegal.repositories.pagination_result import PaginatedResult
from gestaolegal.repositories.repository import (
    BaseRepository,
    ComplexWhereClause,
    CountParams,
    GetParams,
    Repository,
    WhereClause,
)
from gestaolegal.repositories.user_repository import UserRepository

__all__ = [
    "AtendidoRepository",
    "EnderecoRepository",
    "OrientacaoJuridicaRepository",
    "UserRepository",
    "PaginatedResult",
    "BaseRepository",
    "GetParams",
    "CountParams",
    "WhereClause",
    "ComplexWhereClause",
    "Repository",
]
