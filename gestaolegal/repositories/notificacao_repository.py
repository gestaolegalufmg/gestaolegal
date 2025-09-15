from gestaolegal.common.constants import UserRole
from gestaolegal.models.notificacao import Notificacao
from gestaolegal.repositories.base_repository import (
    BaseRepository,
    PageParams,
    WhereConditions,
)
from gestaolegal.schemas.notificacao import NotificacaoSchema


class NotificacaoRepository(BaseRepository):
    def __init__(self):
        super().__init__(NotificacaoSchema, Notificacao)

    def get_notificacoes_for_user(
        self,
        user_id: int,
        user_role: UserRole,
        page_params: PageParams | None = None,
    ):
        where_conditions: WhereConditions = []

        if user_role in [UserRole.ORIENTADOR, UserRole.ESTAGIARIO_DIREITO]:
            where_conditions.append(
                ("id_usu_notificar", "eq", user_id),
            )
        else:
            where_conditions.append(("id_usu_notificar", "eq", user_id))

        return self.get(
            where_conditions=where_conditions,
            order_by=["data"],
            order_desc=True,
            page_params=page_params,
        )
