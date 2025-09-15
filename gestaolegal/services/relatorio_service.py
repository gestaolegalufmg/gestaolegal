import logging
from typing import Any

from gestaolegal.common.constants import assistencia_jud_areas_atendidas
from gestaolegal.repositories.caso_repository import CasoRepository
from gestaolegal.repositories.dias_marcados_repository import DiasMarcadosRepository
from gestaolegal.repositories.orientacao_juridica_repository import (
    OrientacaoJuridicaRepository,
)
from gestaolegal.repositories.registro_entrada_repository import (
    RegistroEntradaRepository,
)
from gestaolegal.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class RelatorioService:
    def __init__(self):
        self.orientacao_repo = OrientacaoJuridicaRepository()
        self.caso_repo = CasoRepository()
        self.usuario_repo = UserRepository()
        self.registro_entrada_repo = RegistroEntradaRepository()
        self.dias_marcados_repo = DiasMarcadosRepository()

    def get_orientacoes_juridicas_por_area(
        self, inicio: str, final: str, areas: list[str] | None = None
    ) -> list[tuple]:
        return self.orientacao_repo.get_orientacoes_count_by_area(inicio, final, areas)

    def get_casos_cadastrados_por_area(
        self, inicio: str, final: str, areas: list[str] | None = None
    ) -> list[tuple]:
        return self.caso_repo.get_casos_count_by_area(inicio, final, areas)

    def get_relatorio_horarios(
        self, inicio: str, final: str, usuarios: list[str] | str | None = None
    ) -> dict[str, Any]:
        if usuarios == "all":
            usuarios_list = self.usuario_repo.get_all(order_by="nome")
            usuarios_ids = [usuario.id for usuario in usuarios_list]
            horarios = self.registro_entrada_repo.get_registros_with_join_by_date_range_and_users(
                inicio, final, usuarios_ids
            )
        else:
            if isinstance(usuarios, str):
                usuarios_list = usuarios.split(",")
            else:
                usuarios_list = usuarios or []
            horarios = self.registro_entrada_repo.get_registros_by_date_range_and_users(
                inicio, final, usuarios_list
            )

        horarios_plantao = (
            self.dias_marcados_repo.get_dias_marcados_by_date_range_and_users(
                inicio, final, usuarios_ids if usuarios == "all" else usuarios_list
            )
        )

        return {
            "usuarios": usuarios_list,
            "horarios": horarios,
            "horarios_plantao": horarios_plantao,
        }

    def get_casos_por_status(
        self,
        inicio: str,
        final: str,
        areas: list[str] | None = None,
        situacoes: list[str] | None = None,
    ):
        return self.caso_repo.get_casos_by_status_and_area(
            inicio, final, areas, situacoes
        )

    def buscar_usuarios(self, termo: str | None = None):
        if termo:
            result = self.usuario_repo.search_by_name(termo)
            return result.items
        else:
            return self.usuario_repo.get_all(order_by="nome")

    def buscar_area_direito(self, termo: str | None = None) -> list[dict[str, str]]:
        if not termo:
            return [
                {
                    "id": assistencia_jud_areas_atendidas[area][0],
                    "text": assistencia_jud_areas_atendidas[area][1],
                }
                for area in assistencia_jud_areas_atendidas
            ]
        else:
            area_direito_front = {}
            for area in assistencia_jud_areas_atendidas:
                if (termo in assistencia_jud_areas_atendidas[area][1]) or (
                    termo in area
                ):
                    area_direito_front[area] = assistencia_jud_areas_atendidas[area][1]

            return [
                {
                    "id": assistencia_jud_areas_atendidas[area][0],
                    "text": area_direito_front[area],
                }
                for area in area_direito_front
            ]

    def get_relatorio_plantao(self, data_inicio: str, data_fim: str):
        return self.dias_marcados_repo.get_dias_marcados_by_date_range(
            data_inicio, data_fim
        )

    def get_relatorio_casos(self, data_inicio: str, data_fim: str):
        return self.caso_repo.get_casos_by_date_range(data_inicio, data_fim)

    def get_relatorio_usuarios(self):
        return self.usuario_repo.get_all(order_by="nome")
