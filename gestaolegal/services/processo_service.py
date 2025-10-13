import logging

from gestaolegal.common import PageParams, PaginatedResult
from gestaolegal.models.processo import Processo
from gestaolegal.models.processo_input import ProcessoCreateInput, ProcessoUpdateInput
from gestaolegal.repositories.processo_repository import ProcessoRepository
from gestaolegal.repositories.repository import (
    ComplexWhereClause,
    SearchParams,
    WhereClause,
)
from gestaolegal.repositories.user_repository import UserRepository
from gestaolegal.models.user import User

logger = logging.getLogger(__name__)


class ProcessoService:
    repository: ProcessoRepository
    user_repository: UserRepository

    def __init__(self):
        self.repository = ProcessoRepository()
        self.user_repository = UserRepository()

    def find_by_id(self, processo_id: int) -> Processo | None:
        logger.info(f"Finding processo by id: {processo_id}")
        processo = self.repository.find_by_id(processo_id)
        if not processo:
            logger.warning(f"Processo not found with id: {processo_id}")
            return None

        if processo.id_criado_por:
            processo.criado_por = User.to_info_optional(
                self.user_repository.find_by_id(processo.id_criado_por)
            )

        logger.info(f"Processo found with id: {processo_id}")
        return processo

    def search_by_caso(
        self,
        page_params: PageParams,
        caso_id: int,
        search: str = "",
        show_inactive: bool = False,
    ) -> PaginatedResult[Processo]:
        logger.info(
            f"Searching processos for caso {caso_id} with search: '{search}', show_inactive: {show_inactive}"
        )
        clauses: list[WhereClause] = [
            WhereClause(column="id_caso", operator="==", value=caso_id)
        ]

        if not show_inactive:
            clauses.append(WhereClause(column="status", operator="==", value=True))

        if search:
            clauses.append(
                WhereClause(
                    column="identificacao", operator="ilike", value=f"%{search}%"
                )
            )

        where = (
            ComplexWhereClause(clauses=clauses, operator="and")
            if len(clauses) > 1
            else clauses[0]
        )

        params = SearchParams(page_params=page_params, where=where)
        result = self.repository.search(params=params)

        for processo in result.items:
            if processo.id_criado_por:
                processo.criado_por = User.to_info_optional(
                    self.user_repository.find_by_id(processo.id_criado_por)
                )

        logger.info(
            f"Returning {len(result.items)} processos of total {result.total} found for caso {caso_id}"
        )
        return result

    def validate_processo_for_caso(
        self, processo_id: int, caso_id: int
    ) -> Processo | None:
        logger.info(f"Validating processo {processo_id} for caso {caso_id}")
        processo = self.repository.find_by_id(processo_id)

        if not processo:
            logger.warning(f"Processo not found with id: {processo_id}")
            return None

        if processo.id_caso != caso_id:
            logger.warning(f"Processo {processo_id} does not belong to caso {caso_id}")
            return None

        if processo.id_criado_por:
            processo.criado_por = User.to_info_optional(
                self.user_repository.find_by_id(processo.id_criado_por)
            )

        return processo

    def create(
        self, caso_id: int, processo_input: ProcessoCreateInput, criado_por_id: int
    ) -> Processo:
        logger.info(
            f"Creating processo for caso {caso_id} with especie: {processo_input.especie}, created by: {criado_por_id}"
        )
        processo_data = processo_input.model_dump()
        processo_data["id_caso"] = caso_id
        processo_data["id_criado_por"] = criado_por_id

        processo_id = self.repository.create(processo_data)

        created_processo = self.find_by_id(processo_id)
        if not created_processo:
            logger.error("Failed to create processo")
            raise ValueError("Failed to create processo")

        logger.info(f"Processo created successfully with id: {processo_id}")
        return created_processo

    def update(
        self, processo_id: int, processo_input: ProcessoUpdateInput
    ) -> Processo | None:
        logger.info(f"Updating processo with id: {processo_id}")
        existing = self.repository.find_by_id(processo_id)
        if not existing:
            logger.error(f"Update failed: processo not found with id: {processo_id}")
            raise ValueError(f"Processo with id {processo_id} not found")

        processo_data = processo_input.model_dump(exclude_none=True)
        self.repository.update(processo_id, processo_data)

        logger.info(f"Processo updated successfully with id: {processo_id}")
        return self.find_by_id(processo_id)

    def soft_delete(self, processo_id: int) -> bool:
        logger.info(f"Soft deleting processo with id: {processo_id}")
        result = self.repository.delete(processo_id)
        if result:
            logger.info(f"Processo soft deleted successfully with id: {processo_id}")
        else:
            logger.warning(f"Soft delete failed for processo with id: {processo_id}")
        return result
