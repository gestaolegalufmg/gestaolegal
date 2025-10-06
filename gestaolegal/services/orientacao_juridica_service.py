import logging

from gestaolegal.common import PageParams
from gestaolegal.models.orientacao_juridica import OrientacaoJuridica
from gestaolegal.models.orientacao_juridica_input import (
    OrientacaoJuridicaCreateInput,
    OrientacaoJuridicaUpdateInput,
)
from gestaolegal.repositories.orientacao_juridica_repository import (
    OrientacaoJuridicaRepository,
)
from gestaolegal.repositories.pagination_result import PaginatedResult
from gestaolegal.repositories.repository import (
    ComplexWhereClause,
    GetParams,
    WhereClause,
)

logger = logging.getLogger(__name__)


class OrientacaoJuridicaService:
    repository: OrientacaoJuridicaRepository

    def __init__(self):
        self.repository = OrientacaoJuridicaRepository()

    def find_by_id(self, id: int) -> OrientacaoJuridica | None:
        logger.info(f"Finding orientacao juridica by id: {id}")
        orientacao = self.repository.find_by_id(id)
        if orientacao:
            logger.info(f"Orientacao juridica found with id: {id}")
        else:
            logger.warning(f"Orientacao juridica not found with id: {id}")
        return orientacao

    def search(
        self,
        search: str = "",
        page_params: PageParams | None = None,
        show_inactive: bool = False,
        area: str = "",
    ) -> PaginatedResult[OrientacaoJuridica]:
        logger.info(
            f"Searching orientacoes juridicas with search: '{search}', area: {area}, show_inactive: {show_inactive}"
        )
        clauses = [
            WhereClause(
                column="status", operator="==", value=0 if show_inactive else 1
            ),
        ]

        if search:
            clauses.append(
                WhereClause(column="descricao", operator="ilike", value=f"%{search}%")
            )

        if area and area != "todas":
            clauses.append(
                WhereClause(column="area_direito", operator="==", value=area)
            )

        where = (
            ComplexWhereClause(clauses=clauses, operator="and")
            if len(clauses) > 1
            else clauses[0]
        )

        params = GetParams(
            page_params=page_params,
            where=where,
        )

        result = self.repository.search(params=params)
        logger.info(
            f"Returning {len(result.items)} orientacoes juridicas of total {result.total} found"
        )
        return result

    def delete(self, id: int):
        logger.info(f"Deleting orientacao juridica with id: {id}")
        result = self.repository.delete(id)
        logger.info(f"Orientacao juridica deleted successfully with id: {id}")
        return result

    def create(
        self, orientacao_input: OrientacaoJuridicaCreateInput, id_usuario: int
    ) -> OrientacaoJuridica:
        logger.info(
            f"Creating orientacao juridica with area_direito: {orientacao_input.area_direito}, created by user: {id_usuario}"
        )

        orientacao_data = orientacao_input.model_dump(exclude={"atendidos_ids"})
        orientacao = OrientacaoJuridica.model_construct(
            id=None, id_usuario=id_usuario, status=1, values=orientacao_data
        )

        orientacao_id = self.repository.create(orientacao)
        created_orientacao = self.repository.find_by_id(orientacao_id)
        if not created_orientacao:
            logger.error(
                f"Could not find created orientacao juridica with id: {orientacao_id}"
            )
            raise ValueError("Something went wrong while creating orientacao juridica")

        logger.info(
            f"Orientacao juridica created successfully with id: {orientacao_id}"
        )
        return created_orientacao

    def update(
        self, id: int, orientacao_input: OrientacaoJuridicaUpdateInput
    ) -> OrientacaoJuridica | None:
        logger.info(f"Updating orientacao juridica with id: {id}")
        existing = self.repository.find_by_id(id)
        if not existing:
            logger.error(f"Update failed: orientacao juridica not found with id: {id}")
            raise ValueError(f"Orientacao juridica with id {id} not found")

        update_data = orientacao_input.model_dump(
            exclude_none=True, exclude={"atendidos_ids"}
        )
        updated_data = {**existing.model_dump(), **update_data}
        orientacao = OrientacaoJuridica.model_construct(values=updated_data)

        self.repository.update(id, orientacao)
        logger.info(f"Orientacao juridica updated successfully with id: {id}")
        return self.repository.find_by_id(id)
