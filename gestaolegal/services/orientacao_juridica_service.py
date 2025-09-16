import json
import logging

from gestaolegal.common import PageParams
from gestaolegal.forms.plantao.orientacao_juridica_form import (
    OrientacaoJuridicaForm,
)
from gestaolegal.models.orientacao_juridica import OrientacaoJuridica
from gestaolegal.repositories.base_repository import WhereConditions
from gestaolegal.repositories.orientacao_juridica_repository import (
    OrientacaoJuridicaRepository,
)
from gestaolegal.services import PaginatedResult
from gestaolegal.services.atendido_service import AtendidoService

logger = logging.getLogger(__name__)


class OrientacaoJuridicaService:
    repository: OrientacaoJuridicaRepository

    def __init__(self):
        self.repository = OrientacaoJuridicaRepository()

    def find_by_id(self, id: int) -> OrientacaoJuridica | None:
        return self.repository.find_by_id(id)

    def get_by_area_do_direito(
        self, area_do_direito: str, page_params: PageParams | None = None
    ) -> PaginatedResult[OrientacaoJuridica]:
        where_clauses: WhereConditions = [
            ("area_direito", "ilike", f"%{area_do_direito}%"),
        ]

        return self.repository.get(
            where_conditions=where_clauses,
            order_by="data_criacao",
            order_desc=True,
            page_params=page_params,
        )

    def get_all(self, page_params: PageParams | None = None):
        return self.repository.get(page_params=page_params)

    def soft_delete(self, id: int):
        return self.repository.soft_delete(id)

    def create(self, orientacao_data: dict) -> OrientacaoJuridica:
        return self.repository.create(orientacao_data)

    def create_orientacao_with_atendidos(self, form, request) -> OrientacaoJuridica:
        orientacao_data = OrientacaoJuridicaForm.to_dict(form)

        lista_atendidos = request.form.get("lista_atendidos")
        if lista_atendidos:
            atendidos_data = json.loads(lista_atendidos)
            atendidos_ids = atendidos_data.get("id", [])

            atendido_service = AtendidoService()
            atendidos = atendido_service.get_by_ids(atendidos_ids)
            orientacao_data["atendidos"] = atendidos

        orientacao = self.create(orientacao_data)

        if form.encaminhar_outras_aj.data and orientacao.id:
            assistencia_id = request.form.get("assistencia_judiciaria")
            if assistencia_id:
                success = self.associate_assistencia_judiciaria(
                    orientacao.id, int(assistencia_id)
                )
                if not success:
                    logger.warning(
                        f"Failed to associate assistência judiciária {assistencia_id} with orientação {orientacao.id}"
                    )

        return orientacao

    def associate_atendido(self, orientacao_id: int, atendido_id: int) -> bool:
        return self.repository.associate_atendido(orientacao_id, atendido_id)

    def disassociate_atendido(self, orientacao_id: int, atendido_id: int) -> bool:
        return self.repository.disassociate_atendido(orientacao_id, atendido_id)

    def associate_assistencia_judiciaria(
        self, orientacao_id: int, assistencia_id: int
    ) -> bool:
        return self.repository.associate_assistencia_judiciaria(
            orientacao_id, assistencia_id
        )

    def get_perfil_data(self, orientacao_id: int):
        return self.repository.get_perfil_data(orientacao_id)

    def buscar_atendidos(self, termo: str, orientacao_id: str | None = None):
        return self.repository.buscar_atendidos(termo, orientacao_id)

    def buscar_orientacoes_por_atendido(self, busca: str, page: int, per_page: int):
        return self.repository.buscar_orientacoes_por_atendido(
            busca, PageParams(page=page, per_page=per_page)
        )

    def update_orientacao_juridica(self, id_oj: int, form) -> OrientacaoJuridica:
        orientacao_data = OrientacaoJuridicaForm.to_dict(form)
        orientacao_data["id"] = id_oj
        orientacao = self.repository.update(id_oj, orientacao_data)
        if not orientacao:
            raise ValueError("Orientação jurídica não encontrada.")
        return orientacao

    def get_editar_orientacao_data(self, id_oj: int) -> dict:
        orientacao = self.find_by_id(id_oj)
        if not orientacao:
            return {}

        return {
            "id": orientacao.id,
            "area_direito": orientacao.area_direito,
            "sub_area": orientacao.sub_area,
            "descricao": orientacao.descricao,
        }

    def validate_orientacao_exists(self, orientacao_id: int) -> bool:
        orientacao = self.find_by_id(orientacao_id)
        return orientacao is not None

    def associate_atendido_to_orientacao(
        self, orientacao_id: int, atendido_id: int
    ) -> bool:
        return self.associate_atendido(orientacao_id, atendido_id)

    def get_associacao_page_data(self, orientacao_id: int) -> dict:
        orientacao = self.find_by_id(orientacao_id)
        if not orientacao:
            return {}

        perfil_data = self.get_perfil_data(orientacao_id)
        return {
            "orientacao": orientacao,
            "atendidos": perfil_data.get("atendidos", []),
        }

    def get_paginated_orientacoes(self, page: int, per_page: int):
        return self.get_all(page_params=PageParams(page=page, per_page=per_page))

    def buscar_orientacoes_por_atendido_or_all(
        self, busca: str, page: int, per_page: int
    ):
        if busca and busca.strip():
            return self.buscar_orientacoes_por_atendido(busca, page, per_page)
        return self.get_paginated_orientacoes(page, per_page)
