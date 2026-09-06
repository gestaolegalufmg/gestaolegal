import logging
import os
from datetime import datetime
from typing import Final, cast

from flask import current_app
from werkzeug.datastructures import FileStorage

from gestaolegal.common import PageParams, PaginatedResult
from gestaolegal.exceptions import (
    DatabaseException,
    FileOperationException,
    ForbiddenException,
    GestaoLegalException,
    NotFoundException,
    ValidationException,
)
from gestaolegal.models.caso import Caso
from gestaolegal.models.evento import Evento, ListEvento, ArquivoEvento
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
            self._carregar_arquivos(evento)
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

        self._carregar_arquivos(evento)
        user_map = self.__get_user_map([evento])
        if evento.id_usuario_responsavel:
            evento.usuario_responsavel = user_map.get(evento.id_usuario_responsavel)
        evento.criado_por = user_map.get(evento.id_criado_por)

        logger.info(f"Evento validated successfully with id: {evento_id}")
        return evento

    def _carregar_arquivos(self, evento: Evento) -> None:
        evento.arquivos = [ArquivoEvento(
            id=row["id"], nome=private_file_storage.nome_original(row["link_arquivo"]),
            indisponivel_origem=row["indisponivel_origem"]
        ) for row in self.repository.listar_arquivos(evento.id)]

    def _salvar_arquivos(self, evento_id: int, caso_id: int,
                         arquivos: list[FileStorage], refs: list[str]) -> None:
        for arquivo in arquivos:
            ref = private_file_storage.save(EVENTO_CATEGORIA, arquivo)
            refs.append(ref)
            self.repository.adicionar_arquivo(evento_id, caso_id, ref)

    def create(
        self, caso_id: int, evento_input: EventoCreateInput, criado_por_id: int,
        arquivo: FileStorage | None = None, arquivos: list[FileStorage] | None = None,
    ) -> Evento:
        caso = self._caso_da_unidade_ativa(caso_id)
        if not caso:
            raise NotFoundException(resource="Caso", resource_id=caso_id)
        uploads = list(arquivos or []) + ([arquivo] if arquivo else [])
        for file in uploads:
            self._validar_anexo(file)
        data = evento_input.model_dump()
        data.update(id_caso=caso_id, unidade_id=caso.unidade_id,
                    data_criacao=datetime.now(), id_criado_por=criado_por_id,
                    num_evento=self.repository.count_by_caso_id(caso_id) + 1)
        refs: list[str] = []
        try:
            evento_id = self.repository.create(data)
            self._salvar_arquivos(evento_id, caso_id, uploads, refs)
            created = self.find_by_id(evento_id)
            if not created:
                raise DatabaseException("Falha ao criar evento")
            NotificacaoService().evento_criado(created, criado_por_id)
            # Evento, anexos e notificação são confirmados juntos. Só depois
            # a resposta pode afirmar que os arquivos foram anexados.
            self.repository.session.commit()
            return created
        except Exception as error:
            self.repository.session.rollback()
            for ref in refs:
                self._remover_do_volume(ref, contexto="upload de evento revertido")
            if isinstance(error, GestaoLegalException):
                raise
            raise FileOperationException("Falha ao salvar evento e anexos", operation="upload") from error

    def update(
        self, evento_id: int, evento_input: EventoUpdateInput,
        arquivo: FileStorage | None = None, arquivos: list[FileStorage] | None = None,
    ) -> Evento | None:
        existing = self.repository.find_by_id(
            evento_id, unidade_id=RequestContext.get_unidade_ativa())
        if not existing or not existing.status:
            raise NotFoundException(resource="Evento", resource_id=evento_id)
        uploads = list(arquivos or []) + ([arquivo] if arquivo else [])
        for file in uploads:
            self._validar_anexo(file)
        refs: list[str] = []
        try:
            data = evento_input.model_dump(exclude_none=True)
            if data:
                self.repository.update(evento_id, data)
            # Adicionar arquivos nunca substitui os anexos já existentes.
            self._salvar_arquivos(evento_id, existing.id_caso, uploads, refs)
            updated = self.find_by_id(evento_id)
            self.repository.session.commit()
            return updated
        except Exception as error:
            self.repository.session.rollback()
            for ref in refs:
                self._remover_do_volume(ref, contexto="upload de evento revertido")
            if isinstance(error, GestaoLegalException):
                raise
            raise FileOperationException("Falha ao salvar evento e anexos", operation="upload") from error

    def _autorizar_exclusao(self, evento_id: int, caso_id: int, user: UserInfo) -> Evento:
        evento = self.validate_evento_for_caso(evento_id, caso_id)
        if not evento or not evento.status:
            raise NotFoundException(resource="Evento", resource_id=evento_id)
        if user.urole != "admin" and evento.id_criado_por != user.id:
            raise ForbiddenException("Apenas o administrador ou quem criou o evento pode excluí-lo ou remover anexos")
        return evento

    def _limpar_sem_referencia(self, rows: list[dict]) -> None:
        for row in rows:
            ref = row["link_arquivo"]
            if ref and not self.repository.referencia_em_uso(ref):
                self._remover_do_volume(ref, contexto="anexo de evento excluído")

    def delete(self, evento_id: int, caso_id: int, user: UserInfo) -> None:
        self._autorizar_exclusao(evento_id, caso_id, user)
        rows = self.repository.listar_arquivos(evento_id)
        try:
            for row in rows:
                self.repository.remover_arquivo(row["id"], evento_id)
            self.repository.update(evento_id, {"status": False})
            self.repository.session.commit()
        except Exception:
            self.repository.session.rollback()
            raise
        self._limpar_sem_referencia(rows)

    def delete_arquivo(self, evento_id: int, caso_id: int, arquivo_id: int, user: UserInfo) -> None:
        self._autorizar_exclusao(evento_id, caso_id, user)
        row = next((r for r in self.repository.listar_arquivos(evento_id) if r["id"] == arquivo_id), None)
        if row is None:
            raise NotFoundException(resource="Anexo", resource_id=arquivo_id)
        try:
            self.repository.remover_arquivo(arquivo_id, evento_id)
            self.repository.session.commit()
        except Exception:
            self.repository.session.rollback()
            raise
        self._limpar_sem_referencia([row])

    def get_evento_file_for_download(
        self, evento_id: int, caso_id: int, arquivo_id: int | None = None
    ) -> tuple[str, str]:
        evento = self.validate_evento_for_caso(evento_id, caso_id)
        if not evento or not evento.status:
            raise NotFoundException(resource="Evento", resource_id=evento_id)
        rows = self.repository.listar_arquivos(evento_id)
        if arquivo_id is None:
            # Compatibilidade com links antigos apenas quando não há ambiguidade.
            if len(rows) != 1:
                raise ValidationException("Selecione um anexo do evento", field="arquivo")
            row = rows[0]
        else:
            row = next((r for r in rows if r["id"] == arquivo_id), None)
        if row is None:
            raise NotFoundException(resource="Anexo", resource_id=arquivo_id)
        if row["indisponivel_origem"]:
            raise FileOperationException("Arquivo indisponível no acervo original", operation="download")
        ref = row["link_arquivo"]
        if not ref or not private_file_storage.exists(EVENTO_CATEGORIA, ref):
            raise FileOperationException("Arquivo não encontrado no servidor", operation="download")
        return (private_file_storage.resolve(EVENTO_CATEGORIA, ref),
                private_file_storage.nome_original(ref))

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
