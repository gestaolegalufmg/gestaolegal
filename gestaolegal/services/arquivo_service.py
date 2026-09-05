import logging
import os
from datetime import datetime
from typing import Any, cast

from flask import current_app
from werkzeug.datastructures import FileStorage

from gestaolegal.common import PageParams, PaginatedResult
from gestaolegal.database.session import transaction
from gestaolegal.exceptions import NotFoundException, ValidationException
from gestaolegal.models.arquivo import Arquivo
from gestaolegal.repositories.arquivo_repository import ArquivoRepository
from gestaolegal.services import private_file_storage

logger = logging.getLogger(__name__)

ARQUIVOS_CATEGORIA = "arquivos"


def _max_arquivo_bytes() -> int:
    return int(current_app.config["MAX_CONTENT_LENGTH"])


TITULO_MAX = 150
DESCRICAO_MAX = 8000


class ArquivoService:
    """Arquivos gerais da organização (módulo "Arquivos" da v2).

    Qualquer tipo de arquivo é aceito, até 10 MB. O arquivo mora na raiz
    privada (categoria "arquivos") e `caminho` guarda a **referência relativa**
    à categoria, nunca um caminho absoluto; o nome original fica em `nome`,
    para o download.
    """

    repository: ArquivoRepository

    def __init__(self):
        self.repository = ArquivoRepository()

    def find_by_id(self, id: int) -> Arquivo:
        arquivo = self.repository.find_by_id(id)
        if not arquivo:
            raise NotFoundException(resource="Arquivo", resource_id=id)
        return arquivo

    def search(self, page_params: PageParams, search: str = "") -> PaginatedResult[dict]:
        return self.repository.search(page_params, search.strip())

    def create(
        self, titulo: str, descricao: str | None, file: FileStorage, criado_por: int
    ) -> Arquivo:
        titulo, descricao = self._validar_campos(titulo, descricao)
        self._validar_arquivo(file)

        ref = private_file_storage.save(ARQUIVOS_CATEGORIA, file)
        try:
            with transaction():
                arquivo_id = self.repository.create(
                    {
                        "titulo": titulo,
                        "descricao": descricao,
                        "nome": cast(str, file.filename),
                        "caminho": ref,
                        "data_criacao": datetime.now(),
                        "id_criado_por": criado_por,
                    }
                )
        except Exception:
            private_file_storage.remove(ARQUIVOS_CATEGORIA, ref)
            raise
        logger.info(f"Arquivo {arquivo_id} criado por usuário {criado_por}")
        return self.find_by_id(arquivo_id)

    def update(
        self,
        id: int,
        titulo: str,
        descricao: str | None,
        file: FileStorage | None,
    ) -> Arquivo:
        """Edita título/descrição e, se enviado, substitui o arquivo.

        O arquivo antigo só é apagado depois que o novo foi gravado e o banco
        atualizado, como no "editar arquivo" da v2.
        """
        atual = self.find_by_id(id)
        titulo, descricao = self._validar_campos(titulo, descricao)
        data: dict[str, Any] = {"titulo": titulo, "descricao": descricao}

        nova_ref: str | None = None
        if file is not None and file.filename:
            self._validar_arquivo(file)
            nova_ref = private_file_storage.save(ARQUIVOS_CATEGORIA, file)
            data["nome"] = file.filename
            data["caminho"] = nova_ref

        try:
            with transaction():
                self.repository.update(id, data)
        except Exception:
            if nova_ref:
                private_file_storage.remove(ARQUIVOS_CATEGORIA, nova_ref)
            raise

        if nova_ref and atual.caminho and atual.caminho != nova_ref:
            self._remover_do_volume(atual.caminho, contexto=f"arquivo {id} substituído")
        logger.info(f"Arquivo {id} atualizado")
        return self.find_by_id(id)

    def delete(self, id: int) -> None:
        arquivo = self.find_by_id(id)
        with transaction():
            self.repository.delete(id)
        self._remover_do_volume(arquivo.caminho, contexto=f"arquivo {id} excluído")
        logger.info(f"Arquivo {id} excluído")

    def get_for_download(self, id: int) -> tuple[str, str]:
        """Caminho absoluto no volume e nome original para o download."""
        arquivo = self.find_by_id(id)
        if not arquivo.caminho:
            logger.error(f"Arquivo {id} sem referência de anexo (registro herdado da 2.0)")
            raise NotFoundException(resource="Arquivo no disco", resource_id=id)
        caminho = private_file_storage.resolve(ARQUIVOS_CATEGORIA, arquivo.caminho)
        if not os.path.isfile(caminho):
            logger.error(f"Arquivo {id} não encontrado no volume: {arquivo.caminho}")
            raise NotFoundException(resource="Arquivo no disco", resource_id=id)
        return caminho, arquivo.nome

    @staticmethod
    def _remover_do_volume(ref: str | None, contexto: str) -> None:
        """Limpeza **pós-commit**: falha aqui vira log de reconciliação.

        O banco já confirmou; levantar agora simularia um rollback que não
        existe. O que sobra é um órfão no volume — problema de faxina.
        """
        if not ref:
            return
        try:
            private_file_storage.remove(ARQUIVOS_CATEGORIA, ref)
        except Exception as e:
            logger.error(
                f"Reconciliação pendente: {contexto}, mas {ARQUIVOS_CATEGORIA}/{ref} "
                f"continua no volume ({e})"
            )

    # ------------------------------------------------------------------ util

    @staticmethod
    def _validar_campos(titulo: str | None, descricao: str | None) -> tuple[str, str | None]:
        titulo = (titulo or "").strip()
        if not titulo:
            raise ValidationException("Informe o título do arquivo", field="titulo")
        if len(titulo) > TITULO_MAX:
            raise ValidationException(
                f"O título deve ter no máximo {TITULO_MAX} caracteres", field="titulo"
            )
        descricao = (descricao or "").strip() or None
        if descricao and len(descricao) > DESCRICAO_MAX:
            raise ValidationException(
                f"A descrição deve ter no máximo {DESCRICAO_MAX} caracteres",
                field="descricao",
            )
        return titulo, descricao

    @staticmethod
    def _validar_arquivo(file: FileStorage | None) -> None:
        if file is None or not file.filename:
            raise ValidationException("Você precisa adicionar um arquivo", field="arquivo")
        file.stream.seek(0, os.SEEK_END)
        size = file.stream.tell()
        file.stream.seek(0)
        if size == 0:
            raise ValidationException("O arquivo está vazio", field="arquivo")
        limite = _max_arquivo_bytes()
        if size > limite:
            raise ValidationException(
                f"O arquivo excede o tamanho máximo de {limite // (1024 * 1024)} MB",
                field="arquivo",
            )

