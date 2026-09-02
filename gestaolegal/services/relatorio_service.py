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

    # --- horários de chegada e saída -----------------------------------------

    @staticmethod
    def _parse_usuarios(usuarios: str | None) -> list[int] | None:
        """Lista de ids separada por vírgula; vazio ou "todos" = sem filtro."""
        if not usuarios or usuarios == "todos":
            return None
        try:
            ids = [int(u) for u in usuarios.split(",") if u.strip()]
        except ValueError:
            raise ValidationException(
                "Usuários inválidos. Informe ids separados por vírgula.",
                field="usuarios",
            )
        return ids or None

    def usuarios_disponiveis(self) -> list[dict]:
        return self.repository.usuarios_ativos()

    def horarios(self, data_inicio: str, data_final: str, usuarios: str | None) -> dict:
        """Relatório "Horário de chegada e saída dos usuários" da v2.

        Junta o ponto diário (registro_entrada) e os dias de plantão marcados no
        período, com a situação da conferência de cada linha.
        """
        inicio, fim = self._parse_range(data_inicio, data_final)
        ids = self._parse_usuarios(usuarios)

        presencas = [
            {
                "id": p["id"],
                "id_usuario": p["id_usuario"],
                "nome": p["nome"],
                "urole": p["urole"],
                "data": p["data_entrada"].date().isoformat(),
                "entrada": p["data_entrada"].strftime("%H:%M"),
                "saida": p["data_saida"].strftime("%H:%M"),
                "confirmacao": p["confirmacao"],
            }
            for p in self.repository.presencas_no_periodo(inicio, fim, ids)
        ]
        plantoes = [
            {
                "id": m["id"],
                "id_usuario": m["id_usuario"],
                "nome": m["nome"],
                "urole": m["urole"],
                "data": m["data_marcada"].isoformat(),
                "confirmacao": m["confirmacao"],
            }
            for m in self.repository.plantoes_no_periodo(inicio, fim, ids)
        ]
        return {
            "presencas": presencas,
            "plantoes": plantoes,
            "total_presencas": len(presencas),
            "total_plantoes": len(plantoes),
        }
