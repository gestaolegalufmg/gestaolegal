from gestaolegal.models.dias_marcados_plantao import DiasMarcadosPlantao
from gestaolegal.repositories.base_repository import BaseRepository, WhereConditions
from gestaolegal.schemas.dias_marcados_plantao import DiasMarcadosPlantaoSchema


class DiasMarcadosRepository(BaseRepository):
    def __init__(self):
        super().__init__(DiasMarcadosPlantaoSchema, DiasMarcadosPlantao)

    def get_dias_marcados_by_date_range_and_users(
        self, data_inicio: str, data_fim: str, usuarios_ids: list[str] | None = None
    ) -> list[DiasMarcadosPlantao]:
        """Get dias marcados within date range and optionally filtered by users"""
        where_conditions: WhereConditions = [
            ("data_marcada", "gte", data_inicio),
            ("data_marcada", "lte", data_fim),
        ]

        if usuarios_ids:
            where_conditions.append(("id_usuario", "in", usuarios_ids))

        result = self.get(
            where_conditions=where_conditions,
            order_by=["data_marcada"],
            order_desc=True,
        )
        return result.items

    def get_dias_marcados_by_date_range(
        self, data_inicio: str, data_fim: str
    ) -> list[DiasMarcadosPlantao]:
        """Get dias marcados within date range for reports"""
        where_conditions: WhereConditions = [
            ("data_marcada", "gte", data_inicio),
            ("data_marcada", "lte", data_fim),
        ]

        result = self.get(
            where_conditions=where_conditions,
            order_by=["data_marcada"],
            order_desc=True,
        )
        return result.items
