from typing import Any, Callable, TypeVar

from gestaolegal.common.constants import UserRole
from gestaolegal.models.notificacao import Notificacao
from gestaolegal.schemas.notificacao import NotificacaoSchema
from gestaolegal.services.base_service import BaseService

T = TypeVar("T")


class NotificacaoService(BaseService[NotificacaoSchema, Notificacao]):
    def __init__(self):
        super().__init__(NotificacaoSchema)

    def get_notificacoes_for_user(
        self,
        user_id: int,
        user_role: UserRole,
        paginator: Callable[..., Any] | None = None,
    ):
        """
        Get notifications for a specific user based on their role.
        For ORIENTADOR and ESTAGIARIO_DIREITO, they can see notifications for themselves or general notifications (id_usu_notificar is None).
        For other roles, they only see notifications specifically for them.
        """

        query = self.session.query(NotificacaoSchema)

        if user_role in [UserRole.ORIENTADOR, UserRole.ESTAGIARIO_DIREITO]:
            query = query.filter(
                (NotificacaoSchema.id_usu_notificar == user_id)
                | (NotificacaoSchema.id_usu_notificar == None)
            )
        else:
            query = query.filter(NotificacaoSchema.id_usu_notificar == user_id)

        query = query.order_by(NotificacaoSchema.data.desc())

        if paginator:
            result = paginator(query)
            if hasattr(result, "items"):
                result.items = [
                    Notificacao.from_sqlalchemy(item) for item in result.items
                ]
                return result
            else:
                return [Notificacao.from_sqlalchemy(item) for item in result]

        notificacoes_schema = query.all()
        return [
            Notificacao.from_sqlalchemy(notificacao)
            for notificacao in notificacoes_schema
        ]

    def find_by_id(self, id: int) -> Notificacao | None:
        notificacao_schema = (
            self.session.query(NotificacaoSchema)
            .filter(NotificacaoSchema.id == id)
            .first()
        )
        return (
            Notificacao.from_sqlalchemy(notificacao_schema)
            if notificacao_schema
            else None
        )
