from datetime import datetime

from gestaolegal.models.plantao import Plantao
from gestaolegal.repositories.base_repository import BaseRepository
from gestaolegal.schemas.plantao import PlantaoSchema


class PlantaoRepository(BaseRepository):
    def __init__(self):
        super().__init__(PlantaoSchema, Plantao)

    def get_active_plantao(self) -> Plantao | None:
        result = self.get(
            where_conditions=[("status", "eq", True)],
            page_params={"page": 1, "per_page": 1},
        )
        return result.items[0] if result.items else None

    def create_plantao(
        self,
        data_abertura: datetime | None = None,
        data_fechamento: datetime | None = None,
    ) -> Plantao:
        return self.create(
            {"data_abertura": data_abertura, "data_fechamento": data_fechamento}
        )
