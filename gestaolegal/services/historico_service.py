import logging
from datetime import datetime
from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from gestaolegal.common import PageParams
from gestaolegal.models.historico import Historico
from gestaolegal.repositories.base_repository import BaseRepository
from gestaolegal.schemas.historico import HistoricoSchema
from gestaolegal.schemas.user import UserSchema

logger = logging.getLogger(__name__)


class HistoricoService:
    repository: BaseRepository[HistoricoSchema, Historico]

    def __init__(self):
        self.repository = BaseRepository(HistoricoSchema, Historico)

    def create_historico(self, id_usuario: int, id_caso: int) -> bool:
        try:
            self.repository.create(
                {
                    "id_usuario": id_usuario,
                    "id_caso": id_caso,
                    "data": datetime.now(),
                }
            )
            return True
        except SQLAlchemyError as e:
            erro = str(e.__dict__["orig"])
            logger.error(f"Database error in historico creation: {erro}", exc_info=True)
            return False

    def get_historico_by_caso(
        self, caso_id: int, page_params: PageParams | None = None
    ) -> Any:
        return self.repository.get(
            where_conditions=[
                ("id_caso", "eq", caso_id),
                ("id_usuario", "eq", UserSchema.id),
            ],
            page_params=page_params,
            order_by="data",
            order_desc=True,
        )
