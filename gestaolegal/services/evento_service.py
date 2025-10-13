import logging
import os
from datetime import datetime
from typing import cast

from gestaolegal.common import PageParams, PaginatedResult
from gestaolegal.models.evento import Evento, ListEvento
from gestaolegal.models.evento_input import EventoCreateInput, EventoUpdateInput
from gestaolegal.models.user import UserInfo
from gestaolegal.repositories.evento_repository import EventoRepository
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
            user_map = self.__get_user_map([evento])
            evento.usuario_responsavel = (
                user_map.get(evento.id_usuario_responsavel)
                if evento.id_usuario_responsavel
                else None
            )
            evento.criado_por = (
                user_map.get(evento.id_criado_por) if evento.id_criado_por else None
            )
            logger.info(f"Evento found with id: {id}")
        else:
            logger.warning(f"Evento not found with id: {id}")
        return evento

    def find_by_caso_id(
        self, caso_id: int, page_params: PageParams
    ) -> PaginatedResult[ListEvento]:
        logger.info(f"Finding eventos for caso id: {caso_id}")
        result = self.repository.find_by_caso_id_paginated(caso_id, page_params)

        user_map = self.__get_user_map(result.items)

        list_eventos: list[ListEvento] = []
        for evento in result.items:
            usuario_responsavel = (
                user_map.get(evento.id_usuario_responsavel)
                if evento.id_usuario_responsavel
                else None
            )
            criado_por = user_map.get(evento.id_criado_por)

            list_eventos.append(
                ListEvento(
                    id=cast(int, evento.id),
                    num_evento=evento.num_evento,
                    tipo=evento.tipo,
                    data_evento=evento.data_evento,
                    data_criacao=evento.data_criacao,
                    status=evento.status,
                    usuario_responsavel=usuario_responsavel.nome
                    if usuario_responsavel
                    else None,
                    criado_por=criado_por.nome if criado_por else None,
                )
            )

        return PaginatedResult(
            items=list_eventos,
            total=result.total,
            page=result.page,
            per_page=result.per_page,
        )

    def validate_evento_for_caso(self, evento_id: int, caso_id: int) -> Evento | None:
        logger.info(f"Validating evento {evento_id} for caso {caso_id}")
        evento = self.repository.find_by_id(evento_id)

        if not evento:
            logger.warning(f"Evento not found with id: {evento_id}")
            return None

        if evento.id_caso != caso_id:
            logger.warning(f"Evento {evento_id} does not belong to caso {caso_id}")
            return None

        user_map = self.__get_user_map([evento])
        if evento.id_usuario_responsavel:
            evento.usuario_responsavel = user_map.get(evento.id_usuario_responsavel)
        evento.criado_por = user_map.get(evento.id_criado_por)

        logger.info(f"Evento validated successfully with id: {evento_id}")
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

    def __get_user_map(self, eventos: list[Evento]) -> dict[int, UserInfo]:
        user_ids: set[int] = set()
        for evento in eventos:
            if evento.id_criado_por is not None:
                user_ids.add(evento.id_criado_por)
            if evento.id_usuario_responsavel:
                user_ids.add(evento.id_usuario_responsavel)

        users = self.user_repository.get_by_ids(list(user_ids))
        user_map: dict[int, UserInfo] = {}
        for user in users:
            if user.id is None:
                continue
            user_map[user.id] = user.to_info()

        return user_map
