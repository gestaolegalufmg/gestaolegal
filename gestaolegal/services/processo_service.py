import logging

from gestaolegal.common import PageParams
from gestaolegal.models.processo import Processo
from gestaolegal.models.processo_input import ProcessoCreateInput, ProcessoUpdateInput
from gestaolegal.repositories.pagination_result import PaginatedResult
from gestaolegal.repositories.processo_repository import ProcessoRepository
from gestaolegal.repositories.repository import (
    ComplexWhereClause,
    GetParams,
    WhereClause,
)

logger = logging.getLogger(__name__)


class ProcessoService:
    repository: ProcessoRepository

    def __init__(self):
        self.repository = ProcessoRepository()

    def find_by_id(self, id: int) -> Processo | None:
        logger.info(f"Finding processo by id: {id}")
        processo = self.repository.find_by_id(id)
        if processo:
            logger.info(f"Processo found with id: {id}")
        else:
            logger.warning(f"Processo not found with id: {id}")
        return processo

    def find_by_caso_id(self, caso_id: int) -> list[Processo]:
        logger.info(f"Finding processos by caso_id: {caso_id}")
        processos = self.repository.find_by_caso_id(caso_id)
        logger.info(f"Found {len(processos)} processos for caso_id: {caso_id}")
        return processos

    def search(
        self,
        page_params: PageParams,
        search: str = "",
        show_inactive: bool = False,
        caso_id: int | None = None,
    ) -> PaginatedResult[Processo]:
        logger.info(
            f"Searching processos with search: '{search}', caso_id: {caso_id}, show_inactive: {show_inactive}, page: {page_params['page']}, per_page: {page_params['per_page']}"
        )
        clauses: list[WhereClause] = []

        if not show_inactive:
            clauses.append(WhereClause(column="status", operator="==", value=True))

        if caso_id:
            clauses.append(WhereClause(column="id_caso", operator="==", value=caso_id))

        if search:
            clauses.append(
                WhereClause(
                    column="identificacao", operator="ilike", value=f"%{search}%"
                )
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
            f"Returning {len(result.items)} processos of total {result.total} found"
        )
        return result

    def create(
        self, processo_input: ProcessoCreateInput, criado_por_id: int
    ) -> Processo:
        logger.info(
            f"Creating processo with especie: {processo_input.especie}, caso_id: {processo_input.id_caso}, created by: {criado_por_id}"
        )
        processo_data = processo_input.model_dump()

        processo_data["id_criado_por"] = criado_por_id

        processo = Processo.model_validate(processo_data)
        processo_id = self.repository.create(processo)

        created_processo = self.find_by_id(processo_id)
        if not created_processo:
            logger.error("Failed to create processo")
            raise ValueError("Failed to create processo")

        logger.info(f"Processo created successfully with id: {processo_id}")
        return created_processo

    def update(
        self,
        processo_id: int,
        processo_input: ProcessoUpdateInput,
    ) -> Processo | None:
        logger.info(f"Updating processo with id: {processo_id}")
        existing = self.repository.find_by_id(processo_id)
        if not existing:
            logger.error(f"Update failed: processo not found with id: {processo_id}")
            raise ValueError(f"Processo with id {processo_id} not found")

        processo_data = processo_input.model_dump(exclude_none=True)

        updated_data = {**existing.model_dump(), **processo_data}
        processo = Processo.model_validate(updated_data)

        self.repository.update(processo_id, processo)

        logger.info(f"Processo updated successfully with id: {processo_id}")
        return self.repository.find_by_id(processo_id)

    def soft_delete(self, processo_id: int) -> bool:
        logger.info(f"Soft deleting processo with id: {processo_id}")
        result = self.repository.delete(processo_id)
        if result:
            logger.info(f"Processo soft deleted successfully with id: {processo_id}")
        else:
            logger.warning(f"Soft delete failed for processo with id: {processo_id}")
        return result
