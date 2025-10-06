import logging
from datetime import datetime

from gestaolegal.common import PageParams
from gestaolegal.models.caso import Caso
from gestaolegal.models.caso_input import CasoCreateInput, CasoUpdateInput
from gestaolegal.repositories.caso_repository import CasoRepository
from gestaolegal.repositories.pagination_result import PaginatedResult
from gestaolegal.repositories.repository import (
    ComplexWhereClause,
    GetParams,
    WhereClause,
)

logger = logging.getLogger(__name__)


class CasoService:
    repository: CasoRepository

    def __init__(self):
        self.repository = CasoRepository()

    def find_by_id(self, id: int) -> Caso | None:
        logger.info(f"Finding caso by id: {id}")
        caso = self.repository.find_by_id(id)
        if caso:
            logger.info(f"Caso found with id: {id}")
        else:
            logger.warning(f"Caso not found with id: {id}")
        return caso

    def search(
        self,
        page_params: PageParams,
        search: str = "",
        show_inactive: bool = False,
        situacao_deferimento: str | None = None,
    ) -> PaginatedResult[Caso]:
        logger.info(
            f"Searching casos with search: '{search}', situacao_deferimento: {situacao_deferimento}, show_inactive: {show_inactive}, page: {page_params['page']}, per_page: {page_params['per_page']}"
        )
        clauses: list[WhereClause] = []

        if not show_inactive:
            clauses.append(WhereClause(column="status", operator="==", value=True))

        if situacao_deferimento and situacao_deferimento != "todos":
            clauses.append(
                WhereClause(
                    column="situacao_deferimento",
                    operator="==",
                    value=situacao_deferimento,
                )
            )

        if search:
            clauses.append(
                WhereClause(column="descricao", operator="ilike", value=f"%{search}%")
            )

        where = None
        if len(clauses) > 1:
            where = ComplexWhereClause(clauses=clauses, operator="and")
        elif len(clauses) == 1:
            where = clauses[0]

        params = GetParams(
            page_params=page_params,
            where=where,
        )

        result = self.repository.search(params=params)
        logger.info(
            f"Returning {len(result.items)} casos of total {result.total} found"
        )
        return result

    def create(self, caso_input: CasoCreateInput, criado_por_id: int) -> Caso:
        logger.info(
            f"Creating caso with area_direito: {caso_input.area_direito}, created by: {criado_por_id}, clients count: {len(caso_input.ids_clientes) if caso_input.ids_clientes else 0}"
        )
        caso_data = caso_input.model_dump(exclude={"ids_clientes"})

        caso_data["data_criacao"] = datetime.now()
        caso_data["id_criado_por"] = criado_por_id
        caso_data["status"] = True

        caso = Caso.from_dict(caso_data)
        caso_id = self.repository.create(caso)

        if caso_input.ids_clientes:
            self.repository.link_atendidos(caso_id, caso_input.ids_clientes)
            logger.info(
                f"Linked {len(caso_input.ids_clientes)} atendidos to caso: {caso_id}"
            )

        created_caso = self.find_by_id(caso_id)
        if not created_caso:
            logger.error("Failed to create caso")
            raise ValueError("Failed to create caso")

        logger.info(f"Caso created successfully with id: {caso_id}")
        return created_caso

    def update(
        self,
        caso_id: int,
        caso_input: CasoUpdateInput,
        modificado_por_id: int,
    ) -> Caso | None:
        logger.info(
            f"Updating caso with id: {caso_id}, modified by: {modificado_por_id}"
        )
        existing = self.repository.find_by_id(caso_id)
        if not existing:
            logger.error(f"Update failed: caso not found with id: {caso_id}")
            raise ValueError(f"Caso with id {caso_id} not found")

        caso_data = caso_input.model_dump(exclude_none=True, exclude={"ids_clientes"})

        caso_data["data_modificacao"] = datetime.now()
        caso_data["id_modificado_por"] = modificado_por_id

        updated_data = {**existing.model_dump(), **caso_data}
        caso = Caso.from_dict(updated_data)

        self.repository.update(caso_id, caso)

        if caso_input.ids_clientes is not None:
            self.repository.link_atendidos(caso_id, caso_input.ids_clientes)
            logger.info(
                f"Updated caso {caso_id} with {len(caso_input.ids_clientes)} linked atendidos"
            )

        logger.info(f"Caso updated successfully with id: {caso_id}")
        return self.repository.find_by_id(caso_id)

    def soft_delete(self, caso_id: int) -> bool:
        logger.info(f"Soft deleting caso with id: {caso_id}")
        result = self.repository.delete(caso_id)
        if result:
            logger.info(f"Caso soft deleted successfully with id: {caso_id}")
        else:
            logger.warning(f"Soft delete failed for caso with id: {caso_id}")
        return result
