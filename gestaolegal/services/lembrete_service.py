import logging
from datetime import datetime

from gestaolegal.models.lembrete import Lembrete
from gestaolegal.repositories.base_repository import BaseRepository
from gestaolegal.schemas.lembrete import LembreteSchema

logger = logging.getLogger(__name__)


class LembreteService:
    repository: BaseRepository[LembreteSchema, Lembrete]

    def __init__(self):
        self.repository = BaseRepository(LembreteSchema, Lembrete)

    def get_num_lembretes_atual(self, caso_id):
        num_lembretes_criados = self.repository.count(
            {"id_caso": caso_id},
            order_by=LembreteSchema.num_lembrete,
            order_desc=True,
        )
        return num_lembretes_criados + 1 if num_lembretes_criados else 1

    def create_lembrete(
        self,
        caso_id: int,
        id_usuario: int,
        data_lembrete: datetime,
        descricao: str,
        id_do_criador: int,
    ) -> Lembrete:
        lembrete_data = {
            "id_caso": caso_id,
            "num_lembrete": self.get_num_lembretes_atual(caso_id),
            "id_usuario": id_usuario,
            "data_lembrete": data_lembrete,
            "descricao": descricao,
            "id_do_criador": id_do_criador,
            "data_criacao": datetime.now(),
        }

        return self.repository.create(lembrete_data)

    def get_lembretes_by_caso(self, caso_id: int) -> list[Lembrete]:
        result = self.repository.get(
            where_conditions=[
                ("id_caso", "eq", caso_id),
            ],
            order_by="data_criacao",
            order_desc=True,
        )
        return result.items

    def get_lembrete_by_id(self, lembrete_id: int) -> Lembrete | None:
        return self.repository.find_by_id(lembrete_id)

    def get_lembrete_by_numero(
        self, caso_id: int, num_lembrete: int
    ) -> Lembrete | None:
        return self.repository.find(
            where_conditions=[
                ("num_lembrete", "eq", num_lembrete),
                ("id_caso", "eq", caso_id),
            ]
        )

    def update_lembrete(
        self,
        lembrete_id: int,
        id_usuario: int,
        data_lembrete: datetime,
        descricao: str,
    ) -> Lembrete:
        lembrete = self.repository.find_by_id(lembrete_id)
        if not lembrete:
            raise ValueError("Lembrete não encontrado")

        lembrete_data = lembrete.to_dict()
        lembrete_data["id_usuario"] = id_usuario
        lembrete_data["data_lembrete"] = data_lembrete
        lembrete_data["descricao"] = descricao

        return self.repository.update(lembrete_id, lembrete_data)

    def delete_lembrete(self, lembrete_id: int) -> None:
        lembrete = self.repository.find_by_id(lembrete_id)
        if not lembrete:
            raise ValueError("Lembrete não encontrado")

        self.repository.delete(lembrete_id)
