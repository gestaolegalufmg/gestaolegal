import logging
from datetime import datetime

from gestaolegal.common.constants import UserRole
from gestaolegal.models.notificacao import Notificacao
from gestaolegal.common import PageParams
from gestaolegal.repositories.notificacao_repository import NotificacaoRepository

logger = logging.getLogger(__name__)


class NotificacaoService:
    def __init__(self):
        self.repository = NotificacaoRepository()

    def create_notificacao(
        self, acao: str, id_executor_acao: int, id_usu_notificar: int
    ) -> Notificacao:
        notificacao_data = {
            "acao": acao,
            "data": datetime.now(),
            "id_executor_acao": id_executor_acao,
            "id_usu_notificar": id_usu_notificar,
        }

        return self.repository.create(notificacao_data)

    def get_notificacoes_for_user(
        self,
        user_id: int,
        user_role: UserRole,
        page_params: PageParams | None = None,
    ):
        return self.repository.get_notificacoes_for_user(
            user_id, user_role, page_params
        )
