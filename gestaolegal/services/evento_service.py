import logging
import os
from datetime import datetime
from typing import Final, cast

from flask import current_app
from werkzeug.datastructures import FileStorage

from gestaolegal.common import PageParams, PaginatedResult
from gestaolegal.database.session import transaction
from gestaolegal.exceptions import (
    DatabaseException,
    FileOperationException,
    ForbiddenException,
    GestaoLegalException,
    NotFoundException,
    ValidationException,
)
from gestaolegal.models.caso import Caso
from gestaolegal.models.evento import Evento, ListEvento
from gestaolegal.models.evento_input import EventoCreateInput, EventoUpdateInput
from gestaolegal.models.user import UserInfo
from gestaolegal.services import private_file_storage
from gestaolegal.services.notificacao_service import NotificacaoService
from gestaolegal.repositories.caso_repository import CasoRepository
from gestaolegal.repositories.evento_repository import EventoRepository
from gestaolegal.repositories.user_repository import UserRepository
from gestaolegal.utils.request_context import RequestContext

logger = logging.getLogger(__name__)

EVENTO_CATEGORIA = "eventos"

EXTENSOES_ANEXO_EVENTO: Final[frozenset[str]] = frozenset(
    {".pdf", ".png", ".jpg", ".jpeg", ".doc", ".docx", ".odt", ".rtf", ".txt"}
)
"""Extensões aceitas como anexo de evento.

Mais larga que a de anexo de caso (só PDF) de propósito: o anexo de evento
nunca teve restrição nenhuma — nem na API, nem no `input type="file"` do
`evento-dialog.svelte` —, e apertar para PDF aqui derrubaria a foto de
documento e o .docx que já se anexa hoje. O que a lista barra é o que não tem
por que virar anexo de um prazo ou de uma audiência: executável, script,
arquivo sem extensão.
"""


def _max_arquivo_bytes() -> int:
    return int(current_app.config["MAX_CONTENT_LENGTH"])


class EventoService:
    repository: EventoRepository
    user_repository: UserRepository
    caso_repository: CasoRepository

    def __init__(self):
        self.repository = EventoRepository()
        self.user_repository = UserRepository()
        self.caso_repository = CasoRepository()

    def _caso_da_unidade_ativa(self, caso_id: int) -> Caso | None:
        """O evento pertence à unidade do caso, não à do header.

        Quem tem as duas unidades enxerga o caso de uma delas por vez; a agenda
        e os eventos do caso seguem a unidade em que o caso foi aberto.
        """
        return self.caso_repository.find_by_id(
            caso_id, unidade_id=RequestContext.get_unidade_ativa()
        )

    def find_by_id(self, id: int) -> Evento | None:
        logger.info(f"Finding evento by id: {id}")
        evento = self.repository.find_by_id(
            id, unidade_id=RequestContext.get_unidade_ativa()
        )
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
        self, caso_id: int, page_params: PageParams, tipo: str | None = None
    ) -> PaginatedResult[ListEvento]:
        logger.info(f"Finding eventos for caso id: {caso_id}, tipo: {tipo}")
        if not self._caso_da_unidade_ativa(caso_id):
            logger.warning(f"Caso {caso_id} is not in the active unidade")
            raise NotFoundException(resource="Caso", resource_id=caso_id)

        result = self.repository.find_by_caso_id_paginated(
            caso_id,
            page_params,
            tipo,
            unidade_id=RequestContext.get_unidade_ativa(),
        )

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
                    id_criado_por=evento.id_criado_por,
                    descricao=evento.descricao,
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
        if not self._caso_da_unidade_ativa(caso_id):
            logger.warning(f"Caso {caso_id} is not in the active unidade")
            return None

        evento = self.repository.find_by_id(
            evento_id, unidade_id=RequestContext.get_unidade_ativa()
        )

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
        self,
        caso_id: int,
        evento_input: EventoCreateInput,
        criado_por_id: int,
        arquivo: FileStorage | None = None,
    ) -> Evento:
        """Cria o evento e, se houver anexo, grava-o na raiz privada.

        O caso, a unidade e o próprio arquivo são validados **antes** de
        qualquer gravação: o controller gravava primeiro e só depois descobria
        que o acesso era negado, deixando órfão no volume.
        """
        logger.info(
            f"Creating evento for caso {caso_id} with tipo: {evento_input.tipo}, created by: {criado_por_id}"
        )
        caso = self._caso_da_unidade_ativa(caso_id)
        if not caso:
            logger.warning(f"Caso {caso_id} is not in the active unidade")
            raise NotFoundException(resource="Caso", resource_id=caso_id)

        self._validar_anexo(arquivo)

        evento_data = evento_input.model_dump()
        evento_data["id_caso"] = caso_id
        evento_data["unidade_id"] = caso.unidade_id
        evento_data["data_criacao"] = datetime.now()
        evento_data["id_criado_por"] = criado_por_id
        evento_data["num_evento"] = self.repository.count_by_caso_id(caso_id) + 1

        ref = None
        try:
            if arquivo:
                ref = private_file_storage.save(EVENTO_CATEGORIA, arquivo)
            evento_data["arquivo"] = ref

            evento_id = self.repository.create(evento_data)

            created_evento = self.find_by_id(evento_id)
            if not created_evento:
                logger.error("Failed to create evento")
                raise DatabaseException("Falha ao criar evento")
        except Exception as e:
            # O evento não existe: o anexo recém-gravado não é referenciado
            # por ninguém e não pode ficar no volume.
            if ref:
                private_file_storage.remove(EVENTO_CATEGORIA, ref)
            if isinstance(e, GestaoLegalException):
                raise
            logger.error(f"Error creating evento for caso {caso_id}: {e}", exc_info=True)
            raise FileOperationException(
                f"Erro ao anexar o arquivo do evento: {e}", operation="upload"
            )

        with transaction():
            NotificacaoService().evento_criado(created_evento, criado_por_id)

        logger.info(f"Evento created successfully with id: {evento_id}")
        return created_evento

    def update(
        self,
        evento_id: int,
        evento_input: EventoUpdateInput,
        arquivo: FileStorage | None = None,
    ) -> Evento | None:
        """Atualiza o evento e, se vier anexo novo, substitui o anterior.

        O anexo substituído sai do volume **depois** de o banco confirmar a
        nova referência: até esta story ele simplesmente vazava.
        """
        logger.info(f"Updating evento with id: {evento_id}")
        existing = self.repository.find_by_id(
            evento_id, unidade_id=RequestContext.get_unidade_ativa()
        )
        if not existing:
            logger.error(f"Update failed: evento not found with id: {evento_id}")
            raise NotFoundException(resource="Evento", resource_id=evento_id)

        self._validar_anexo(arquivo)

        evento_data = evento_input.model_dump(exclude_none=True)

        nova_ref = None
        try:
            if arquivo:
                nova_ref = private_file_storage.save(EVENTO_CATEGORIA, arquivo)
                evento_data["arquivo"] = nova_ref

            self.repository.update(evento_id, evento_data)
        except Exception as e:
            # Nada confirmado: some com o novo e o anexo anterior segue de pé.
            if nova_ref:
                private_file_storage.remove(EVENTO_CATEGORIA, nova_ref)
            if isinstance(e, GestaoLegalException):
                raise
            logger.error(f"Error updating evento {evento_id}: {e}", exc_info=True)
            raise FileOperationException(
                f"Erro ao anexar o arquivo do evento: {e}", operation="upload"
            )

        anterior = existing.arquivo
        if nova_ref and anterior and anterior != nova_ref:
            self._remover_do_volume(
                anterior, contexto=f"anexo do evento {evento_id} substituído"
            )

        logger.info(f"Evento updated successfully with id: {evento_id}")
        return self.repository.find_by_id(
            evento_id, unidade_id=RequestContext.get_unidade_ativa()
        )

    def delete(self, evento_id: int, caso_id: int, user: UserInfo) -> None:
        """Exclui (soft delete) um evento e apaga o arquivo anexo.

        Regra herdada da v2: só o admin ou quem criou o evento pode excluí-lo.
        """
        logger.info(f"Deleting evento {evento_id} from caso {caso_id} by user {user.id}")
        evento = self.validate_evento_for_caso(evento_id, caso_id)
        if not evento or not evento.status:
            raise NotFoundException(resource="Evento", resource_id=evento_id)

        if user.urole != "admin" and evento.id_criado_por != user.id:
            logger.warning(
                f"User {user.id} tried to delete evento {evento_id} created by {evento.id_criado_por}"
            )
            raise ForbiddenException(
                "Apenas o administrador ou quem criou o evento pode excluí-lo"
            )

        # O banco manda: o registro perde a referência primeiro, e só depois o
        # anexo deixa o volume. Apagar antes deixaria o evento apontando para
        # o nada se a atualização falhasse.
        anexo = evento.arquivo
        self.repository.update(evento_id, {"status": False, "arquivo": None})

        self._remover_do_volume(anexo, contexto=f"evento {evento_id} excluído")
        logger.info(f"Evento {evento_id} deleted successfully")

    def get_evento_file_for_download(
        self, evento_id: int, caso_id: int
    ) -> tuple[str, str]:
        """Devolve `(caminho absoluto no volume privado, nome original)`.

        O caminho nunca sai daqui para o banco nem para a resposta da API —
        quem o recebe é o `send_file`. Evento excluído (status falso) não é
        baixável: o `delete` já limpa a referência, mas registro herdado da
        2.0 pode ter as duas coisas.
        """
        logger.info(f"Getting evento {evento_id} file for download from caso {caso_id}")

        evento = self.validate_evento_for_caso(evento_id, caso_id)
        if not evento or not evento.status:
            raise NotFoundException(resource="Evento", resource_id=evento_id)

        if not evento.arquivo:
            logger.warning(f"Evento {evento_id} has no file")
            raise FileOperationException(
                "Evento não possui arquivo", operation="download"
            )

        if not private_file_storage.exists(EVENTO_CATEGORIA, evento.arquivo):
            logger.error(f"Anexo ausente no volume privado: {evento.arquivo}")
            raise FileOperationException(
                "Arquivo não encontrado no servidor", operation="download"
            )

        logger.info(f"Evento {evento_id} file ready for download: {evento.arquivo}")
        return (
            private_file_storage.resolve(EVENTO_CATEGORIA, evento.arquivo),
            private_file_storage.nome_original(evento.arquivo),
        )

    @staticmethod
    def _validar_anexo(file: FileStorage | None) -> None:
        """Tipo e tamanho do anexo de evento — nenhum dos dois era checado."""
        if file is None:
            return

        if not file.filename:
            logger.warning("Invalid file provided for evento upload")
            raise ValidationException("Arquivo inválido", field="arquivo")

        extensao = os.path.splitext(file.filename)[1].lower()
        if extensao not in EXTENSOES_ANEXO_EVENTO:
            logger.warning(f"Rejected evento upload of type {extensao!r}")
            permitidas = ", ".join(sorted(EXTENSOES_ANEXO_EVENTO))
            raise ValidationException(
                f"Tipo de arquivo não permitido. Aceitos: {permitidas}",
                field="arquivo",
            )

        file.stream.seek(0, os.SEEK_END)
        size = file.stream.tell()
        file.stream.seek(0)
        limite = _max_arquivo_bytes()
        if size > limite:
            logger.warning(f"Rejected oversized upload ({size} bytes): {file.filename}")
            raise ValidationException(
                f"O arquivo excede o tamanho máximo de {limite // (1024 * 1024)} MB",
                field="arquivo",
            )

    @staticmethod
    def _remover_do_volume(ref: str | None, contexto: str) -> None:
        """Limpeza **pós-commit**: falha aqui vira log de reconciliação.

        O banco já confirmou. Levantar exceção agora simularia um rollback que
        não existe — o que sobra é um órfão no volume, e órfão é problema de
        faxina, não de requisição.
        """
        if not ref:
            return
        try:
            private_file_storage.remove(EVENTO_CATEGORIA, ref)
        except Exception as e:
            logger.error(
                f"Reconciliação pendente: {contexto}, mas {EVENTO_CATEGORIA}/{ref} "
                f"continua no volume ({e})"
            )

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
