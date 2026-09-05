import logging
import os
from datetime import datetime
from typing import Any, cast

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from gestaolegal.common import PageParams, PaginatedResult
from gestaolegal.database.session import transaction
from gestaolegal.exceptions import NotFoundException, ValidationException
from gestaolegal.models.arquivo import Arquivo
from gestaolegal.repositories.arquivo_repository import ArquivoRepository

logger = logging.getLogger(__name__)

ARQUIVOS_CATEGORIA = "arquivos"


def _arquivos_dir() -> str:
    """Resolvida a cada chamada: a raiz vem da config do app, não do import."""
    return os.path.join(current_app.config["PRIVATE_FILES_ROOT"], ARQUIVOS_CATEGORIA)


def _max_arquivo_bytes() -> int:
    return int(current_app.config["MAX_CONTENT_LENGTH"])

TITULO_MAX = 150
DESCRICAO_MAX = 8000


class ArquivoService:
    """Arquivos gerais da organização (módulo "Arquivos" da v2).

    Qualquer tipo de arquivo é aceito, até 10 MB. O arquivo fica em
    raiz privada (categoria "arquivos") com prefixo de data/hora para evitar colisão de nomes; o
    nome original é guardado em `nome` para o download.
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

        caminho = self._salvar(file)
        try:
            with transaction():
                arquivo_id = self.repository.create(
                    {
                        "titulo": titulo,
                        "descricao": descricao,
                        "nome": cast(str, file.filename),
                        "caminho": caminho,
                        "data_criacao": datetime.now(),
                        "id_criado_por": criado_por,
                    }
                )
        except Exception:
            self._remover_do_disco(caminho)
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

        novo_caminho: str | None = None
        if file is not None and file.filename:
            self._validar_arquivo(file)
            novo_caminho = self._salvar(file)
            data["nome"] = file.filename
            data["caminho"] = novo_caminho

        try:
            with transaction():
                self.repository.update(id, data)
        except Exception:
            if novo_caminho:
                self._remover_do_disco(novo_caminho)
            raise

        if novo_caminho and self._caminho_de(atual) != novo_caminho:
            self._remover_do_disco(self._caminho_de(atual))
        logger.info(f"Arquivo {id} atualizado")
        return self.find_by_id(id)

    def delete(self, id: int) -> None:
        arquivo = self.find_by_id(id)
        with transaction():
            self.repository.delete(id)
        self._remover_do_disco(self._caminho_de(arquivo))
        logger.info(f"Arquivo {id} excluído")

    def get_for_download(self, id: int) -> tuple[str, str]:
        """Caminho no disco e nome original para o download."""
        arquivo = self.find_by_id(id)
        caminho = self._caminho_de(arquivo)
        if not os.path.exists(caminho):
            logger.error(f"Arquivo {id} não encontrado no disco: {caminho}")
            raise NotFoundException(resource="Arquivo no disco", resource_id=id)
        return caminho, arquivo.nome

    @staticmethod
    def _caminho_de(arquivo: Arquivo) -> str:
        """Registros da v2 não têm `caminho`: o arquivo ficava na raiz/nome."""
        return arquivo.caminho or os.path.join(_arquivos_dir(), arquivo.nome)

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

    @staticmethod
    def _salvar(file: FileStorage) -> str:
        filename = secure_filename(cast(str, file.filename)) or "arquivo"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        arquivos_dir = _arquivos_dir()
        os.makedirs(arquivos_dir, exist_ok=True)
        caminho = os.path.join(arquivos_dir, f"{timestamp}_{filename}")
        file.save(caminho)
        logger.info(f"Arquivo gravado em {caminho}")
        return caminho

    @staticmethod
    def _remover_do_disco(caminho: str | None) -> None:
        if caminho and os.path.exists(caminho):
            try:
                os.remove(caminho)
            except OSError as e:
                logger.warning(f"Não foi possível remover {caminho}: {e}")
