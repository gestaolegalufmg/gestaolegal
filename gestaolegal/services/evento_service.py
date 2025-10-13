import logging
import os
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
from gestaolegal.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class EventoService:
    repository: EventoRepository
    user_repository: UserRepository

    def __init__(self):
        self.repository = EventoRepository()
        self.user_repository = UserRepository()

    def find_by_id(self, id: int) -> Evento | None:
        logger.info(f"Finding evento by id: {id}")
        evento = self.repository.find_by_id(id)
        if evento:
            self.__fill_user_data([evento])
            logger.info(f"Evento found with id: {id}")
        else:
            logger.warning(f"Evento not found with id: {id}")
        return evento

    def find_by_caso_id(
        self, caso_id: int, page_params: PageParams
    ) -> PaginatedResult[Evento]:
        logger.info(f"Finding eventos for caso id: {caso_id}")
        result = self.repository.find_by_caso_id_paginated(caso_id, page_params)
        self.__fill_user_data(result.items)
        logger.info(f"Found {result.total} eventos for caso id: {caso_id}")
        return result

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
        self.__fill_user_data(result.items)
        logger.info(
            f"Returning {len(result.items)} eventos of total {result.total} found"
        )
        return result

    def validate_evento_for_caso(self, evento_id: int, caso_id: int) -> Evento | None:
        logger.info(f"Validating evento {evento_id} for caso {caso_id}")
        evento = self.repository.find_by_id(evento_id)

        if not evento:
            logger.warning(f"Evento not found with id: {evento_id}")
            return None

        if evento.id_caso != caso_id:
            logger.warning(f"Evento {evento_id} does not belong to caso {caso_id}")
            return None

        self.__fill_user_data([evento])
        return evento

    def create(
        self, caso_id: int, evento_input: EventoCreateInput, criado_por_id: int
    ) -> Evento:
        logger.info(
            f"Creating evento for caso {caso_id} with tipo: {evento_input.tipo}, created by: {criado_por_id}"
        )
        evento_data = evento_input.model_dump()
        evento_data["id_caso"] = caso_id
        evento_data["data_criacao"] = datetime.now()
        evento_data["id_criado_por"] = criado_por_id
        evento_data["num_evento"] = self.repository.count_by_caso_id(caso_id) + 1

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

    def get_evento_file_for_download(
        self, evento_id: int, caso_id: int
    ) -> tuple[str | None, str]:
        logger.info(f"Getting evento {evento_id} file for download from caso {caso_id}")

        evento = self.validate_evento_for_caso(evento_id, caso_id)
        if not evento:
            return None, "Evento não encontrado ou não pertence ao caso"

        if not evento.arquivo:
            logger.warning(f"Evento {evento_id} has no file")
            return None, "Evento não possui arquivo"

        if not os.path.exists(evento.arquivo):
            logger.error(f"File not found in filesystem: {evento.arquivo}")
            return None, "Arquivo não encontrado no servidor"

        logger.info(f"Evento {evento_id} file ready for download: {evento.arquivo}")
        return evento.arquivo, "OK"

    def __fill_user_data(self, eventos: list[Evento]) -> None:
        if not eventos:
            return

        user_ids = set()
        for evento in eventos:
            user_ids.add(evento.id_criado_por)
            if evento.id_usuario_responsavel:
                user_ids.add(evento.id_usuario_responsavel)

        users = self.user_repository.get_by_ids(list(user_ids))
        user_map = {user.id: user for user in users}

        for evento in eventos:
            evento.criado_por = user_map.get(evento.id_criado_por)
            evento.usuario_responsavel = (
                user_map.get(evento.id_usuario_responsavel)
                if evento.id_usuario_responsavel
                else None
            )
