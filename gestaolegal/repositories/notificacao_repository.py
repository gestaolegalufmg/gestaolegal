from gestaolegal.common.constants import UserRole
from gestaolegal.models.notificacao import Notificacao
from gestaolegal.repositories.base_repository import BaseRepository, ConditionList, PageParams
from gestaolegal.schemas.notificacao import NotificacaoSchema


class NotificacaoRepository(BaseRepository[NotificacaoSchema, Notificacao]):
    def __init__(self):
        super().__init__(NotificacaoSchema, Notificacao)

    def get_notificacoes_for_user(
        self,
        user_id: int,
        user_role: UserRole,
        page_params: PageParams | None = None,
    ):
        from sqlalchemy import or_
        
        where_conditions: ConditionList = []

        if user_role in [UserRole.ORIENTADOR, UserRole.ESTAGIARIO_DIREITO]:
            where_conditions.append(
                or_(
                    NotificacaoSchema.id_usu_notificar == user_id,
                    NotificacaoSchema.id_usu_notificar.is_(None)
                )
            )
        else:
            where_conditions.append(("id_usu_notificar", "eq", user_id))

        return self.get(
            where_conditions=where_conditions,
            order_by=["data"],
            order_desc=True,
            page_params=page_params,
        )
