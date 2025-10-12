import logging
from datetime import datetime

from gestaolegal.common import PageParams, PaginatedResult
from gestaolegal.models.evento import Evento
from gestaolegal.models.evento_input import EventoCreateInput, EventoUpdateInput
from gestaolegal.repositories.evento_repository import EventoRepository
from gestaolegal.repositories.repository import (
    ComplexWhereClause,
    SearchParams,
    WhereClause,
)

logger = logging.getLogger(__name__)


class EventoService:
    repository: EventoRepository

    def __init__(self):
        self.repository = EventoRepository()

    def find_by_id(self, id: int) -> Evento | None:
        logger.info(f"Finding evento by id: {id}")
        evento = self.repository.find_by_id(id)
        if evento:
            logger.info(f"Evento found with id: {id}")
        else:
            logger.warning(f"Evento not found with id: {id}")
        return evento

    def find_by_caso_id(self, caso_id: int) -> PaginatedResult[Evento]:
        logger.info(f"Finding eventos by caso_id: {caso_id}")
        eventos = self.repository.find_by_caso_id(caso_id)
        logger.info(f"Found {eventos.total} eventos for caso_id: {caso_id}")
        return eventos

    def search(
        self,
        page_params: PageParams,
        search: str = "",
        show_inactive: bool = False,
        caso_id: int | None = None,
        tipo: str | None = None,
    ) -> PaginatedResult[Evento]:
        logger.info(
            f"Searching eventos with search: '{search}', caso_id: {caso_id}, tipo: {tipo}, show_inactive: {show_inactive}, page: {page_params['page']}, per_page: {page_params['per_page']}"
        )
        clauses: list[WhereClause] = []

        if not show_inactive:
            clauses.append(WhereClause(column="status", operator="==", value=True))

        if caso_id:
            clauses.append(WhereClause(column="id_caso", operator="==", value=caso_id))

        if tipo:
            clauses.append(WhereClause(column="tipo", operator="==", value=tipo))

        if search:
            clauses.append(
                WhereClause(column="descricao", operator="ilike", value=f"%{search}%")
            )

        where = None
        if len(clauses) > 1:
            where = ComplexWhereClause(clauses=clauses, operator="and")
        elif len(clauses) == 1:
            where = clauses[0]

        params = SearchParams(
            page_params=page_params,
            where=where,
        )

        result = self.repository.search(params=params)
        logger.info(
            f"Returning {len(result.items)} eventos of total {result.total} found"
        )
        return result

    def create(self, evento_input: EventoCreateInput, criado_por_id: int) -> Evento:
        logger.info(
            f"Creating evento with tipo: {evento_input.tipo}, caso_id: {evento_input.id_caso}, created by: {criado_por_id}"
        )
        evento_data = evento_input.model_dump()

        evento_data["data_criacao"] = datetime.now()
        evento_data["id_criado_por"] = criado_por_id
        evento_data["num_evento"] = (
            self.repository.count_by_caso_id(evento_input.id_caso) + 1
        )

        evento_id = self.repository.create(evento_data)

        created_evento = self.find_by_id(evento_id)
        if not created_evento:
            logger.error("Failed to create evento")
            raise ValueError("Failed to create evento")

        logger.info(f"Evento created successfully with id: {evento_id}")
        return created_evento

    def update(
        self,
        evento_id: int,
        evento_input: EventoUpdateInput,
    ) -> Evento | None:
        logger.info(f"Updating evento with id: {evento_id}")
        existing = self.repository.find_by_id(evento_id)
        if not existing:
            logger.error(f"Update failed: evento not found with id: {evento_id}")
            raise ValueError(f"Evento with id {evento_id} not found")

        evento_data = evento_input.model_dump(exclude_none=True)

        self.repository.update(evento_id, evento_data)

        logger.info(f"Evento updated successfully with id: {evento_id}")
        return self.repository.find_by_id(evento_id)

    def soft_delete(self, evento_id: int) -> bool:
        logger.info(f"Soft deleting evento with id: {evento_id}")
        result = self.repository.delete(evento_id)
        if result:
            logger.info(f"Evento soft deleted successfully with id: {evento_id}")
        else:
            logger.warning(f"Soft delete failed for evento with id: {evento_id}")
        return result
