import logging
from datetime import datetime
from typing import cast

from gestaolegal.database.session import transaction
from gestaolegal.exceptions import NotFoundException
from gestaolegal.models.lembrete import LembreteListItem
from gestaolegal.models.lembrete_input import (
    LembreteCreateInput,
    LembreteUpdateInput,
)
from gestaolegal.repositories.lembrete_repository import LembreteRepository
from gestaolegal.repositories.repository import GetParams, WhereClause
from gestaolegal.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class LembreteService:
    repository: LembreteRepository
    user_repository: UserRepository

    def __init__(self):
        self.repository = LembreteRepository()
        self.user_repository = UserRepository()

    def _to_list_item(self, lembrete) -> LembreteListItem:
        user_ids = [
            uid
            for uid in {lembrete.id_do_criador, lembrete.id_usuario}
            if uid is not None
        ]
        users = self.user_repository.get(
            params=GetParams(
                where=WhereClause(column="id", operator="in", value=user_ids)
            )
        )
        user_map = {
            cast(int, u.id): u.to_info() for u in users if u.id is not None
        }
        return LembreteListItem(
            id=cast(int, lembrete.id),
            num_lembrete=lembrete.num_lembrete,
            id_caso=lembrete.id_caso,
            data_criacao=lembrete.data_criacao,
            data_lembrete=lembrete.data_lembrete,
            descricao=lembrete.descricao,
            status=bool(lembrete.status),
            criador=user_map.get(lembrete.id_do_criador),
            usuario=user_map.get(lembrete.id_usuario),
        )

    def get_by_caso(self, caso_id: int) -> list[LembreteListItem]:
        logger.info(f"Fetching lembretes for caso {caso_id}")
        lembretes = self.repository.get_by_caso(caso_id)
        return [self._to_list_item(lembrete) for lembrete in lembretes]

    def find_by_id(self, id: int) -> LembreteListItem | None:
        lembrete = self.repository.find_by_id(id)
        if not lembrete:
            return None
        return self._to_list_item(lembrete)

    def validate_lembrete_for_caso(self, lembrete_id: int, caso_id: int):
        lembrete = self.repository.find_by_id(lembrete_id)
        if not lembrete or lembrete.id_caso != caso_id:
            return None
        return lembrete

    def create(
        self, caso_id: int, criador_id: int, data: LembreteCreateInput
    ) -> LembreteListItem:
        logger.info(f"Creating lembrete for caso {caso_id} by user {criador_id}")
        with transaction():
            num_lembrete = self.repository.count_by_caso(caso_id) + 1
            lembrete_id = self.repository.create(
                {
                    "num_lembrete": num_lembrete,
                    "id_do_criador": criador_id,
                    "id_caso": caso_id,
                    "id_usuario": data.id_usuario,
                    "data_criacao": datetime.now(),
                    "data_lembrete": data.data_lembrete,
                    "descricao": data.descricao,
                    "status": True,
                }
            )
        created = self.find_by_id(lembrete_id)
        assert created is not None
        return created

    def update(
        self, lembrete_id: int, data: LembreteUpdateInput
    ) -> LembreteListItem:
        existing = self.repository.find_by_id(lembrete_id)
        if not existing:
            raise NotFoundException(resource="Lembrete", resource_id=lembrete_id)
        with transaction():
            update_data = data.model_dump(exclude_none=True)
            if update_data:
                self.repository.update(lembrete_id, update_data)
        updated = self.find_by_id(lembrete_id)
        assert updated is not None
        return updated

    def delete(self, lembrete_id: int) -> bool:
        existing = self.repository.find_by_id(lembrete_id)
        if not existing:
            raise NotFoundException(resource="Lembrete", resource_id=lembrete_id)
        with transaction():
            self.repository.delete(lembrete_id)
        return True
