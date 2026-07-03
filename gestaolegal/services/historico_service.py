import logging
from datetime import datetime
from typing import cast

from gestaolegal.common import PageParams, PaginatedResult
from gestaolegal.database.session import transaction
from gestaolegal.models.historico import HistoricoListItem
from gestaolegal.models.user import User
from gestaolegal.repositories.historico_repository import HistoricoRepository
from gestaolegal.repositories.repository import (
    GetParams,
    SearchParams,
    WhereClause,
)
from gestaolegal.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class HistoricoService:
    repository: HistoricoRepository
    user_repository: UserRepository

    def __init__(self):
        self.repository = HistoricoRepository()
        self.user_repository = UserRepository()

    def registrar(
        self,
        id_caso: int,
        id_usuario: int,
        acao: str,
        descricao: str | None = None,
    ) -> None:
        """Record an audit-log entry for a caso. Runs inside the caller's transaction
        when there is one; otherwise opens its own."""
        logger.info(
            f"Recording historico for caso {id_caso} by user {id_usuario}: {acao}"
        )
        self.repository.create(
            {
                "id_caso": id_caso,
                "id_usuario": id_usuario,
                "data": datetime.now(),
                "acao": acao,
                "descricao": descricao,
            }
        )

    def get_by_caso(
        self, caso_id: int, page_params: PageParams | None = None
    ) -> PaginatedResult[HistoricoListItem]:
        logger.info(f"Fetching historico for caso {caso_id}")
        result = self.repository.get_by_caso(
            caso_id, SearchParams(page_params=page_params, where=None)
        )

        user_ids = [item.id_usuario for item in result.items if item.id_usuario]
        users = self.user_repository.get(
            params=GetParams(
                where=WhereClause(column="id", operator="in", value=user_ids)
            )
        )
        user_map = {
            cast(int, user.id): user.to_info() for user in users if user.id is not None
        }

        items = [
            HistoricoListItem(
                id=cast(int, item.id),
                data=item.data,
                acao=item.acao,
                descricao=item.descricao,
                usuario=user_map.get(item.id_usuario),
            )
            for item in result.items
            if item.id is not None
        ]

        return PaginatedResult(
            items=items,
            total=result.total,
            page=result.page,
            per_page=result.per_page,
        )
