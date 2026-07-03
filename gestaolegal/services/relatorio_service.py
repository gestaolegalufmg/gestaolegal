import logging
from datetime import datetime, timedelta

from gestaolegal.exceptions import ValidationException
from gestaolegal.repositories.relatorio_repository import RelatorioRepository

logger = logging.getLogger(__name__)


class RelatorioService:
    repository: RelatorioRepository

    def __init__(self):
        self.repository = RelatorioRepository()

    @staticmethod
    def _parse_range(data_inicio: str, data_final: str) -> tuple[datetime, datetime]:
        try:
            inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
            # Exclusive upper bound = final date + 1 day, so the whole final day is included.
            fim = datetime.strptime(data_final, "%Y-%m-%d") + timedelta(days=1)
        except (ValueError, TypeError):
            raise ValidationException(
                "Datas inválidas. Use o formato AAAA-MM-DD.", field="data_inicio"
            )
        if fim <= inicio:
            raise ValidationException(
                "A data final deve ser maior ou igual à data inicial.",
                field="data_final",
            )
        return inicio, fim

    @staticmethod
    def _parse_areas(areas: str | None) -> list[str] | None:
        if not areas:
            return None
        parsed = [a for a in areas.split(",") if a and a != "todas"]
        return parsed or None

    def casos_cadastrados(
        self, data_inicio: str, data_final: str, areas: str | None
    ) -> dict:
        inicio, fim = self._parse_range(data_inicio, data_final)
        rows = self.repository.casos_cadastrados_por_area(
            inicio, fim, self._parse_areas(areas)
        )
        return {"items": rows, "total": sum(r["quantidade"] for r in rows)}

    def casos_por_status(
        self, data_inicio: str, data_final: str, areas: str | None
    ) -> dict:
        inicio, fim = self._parse_range(data_inicio, data_final)
        rows = self.repository.casos_por_status(inicio, fim, self._parse_areas(areas))
        return {"items": rows, "total": sum(r["quantidade"] for r in rows)}

    def casos_por_orientacao(
        self, data_inicio: str, data_final: str, areas: str | None
    ) -> dict:
        inicio, fim = self._parse_range(data_inicio, data_final)
        rows = self.repository.orientacoes_por_area(
            inicio, fim, self._parse_areas(areas)
        )
        return {"items": rows, "total": sum(r["quantidade"] for r in rows)}
