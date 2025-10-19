import logging
import os
from datetime import datetime

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from gestaolegal.common import PageParams, PaginatedResult
from gestaolegal.config import Config
from gestaolegal.database.session import transaction
from gestaolegal.exceptions import (
    DatabaseException,
    FileOperationException,
    NotFoundException,
    ValidationException,
)
from gestaolegal.models.arquivo_caso import ArquivoCaso
from gestaolegal.models.caso import Caso
from gestaolegal.models.caso_input import CasoCreateInput, CasoUpdateInput
from gestaolegal.models.user import User
from gestaolegal.repositories.arquivo_caso_repository import ArquivoCasoRepository
from gestaolegal.repositories.atendido_repository import AtendidoRepository
from gestaolegal.repositories.caso_repository import CasoRepository
from gestaolegal.repositories.processo_repository import ProcessoRepository
from gestaolegal.repositories.repository import (
    ComplexWhereClause,
    SearchParams,
    WhereClause,
    and_clauses,
    or_clauses,
)
from gestaolegal.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

CASO_FILES_DIR = Config.UPLOADS


class CasoService:
    repository: CasoRepository
    user_repository: UserRepository
    atendido_repository: AtendidoRepository
    processo_repository: ProcessoRepository
    arquivo_repository: ArquivoCasoRepository

    def __init__(self):
        self.repository = CasoRepository()
        self.user_repository = UserRepository()
        self.atendido_repository = AtendidoRepository()
        self.processo_repository = ProcessoRepository()
        self.arquivo_repository = ArquivoCasoRepository()

    def find_by_id(self, id: int) -> Caso | None:
        logger.info(f"Finding caso by id: {id}")
        caso = self.repository.find_by_id(id)
        if not caso:
            logger.warning(f"Caso not found with id: {id}")
            return None

        self._load_caso_dependencies(caso)
        logger.info(f"Caso found with id: {id}")
        return caso

    def search(
        self,
        page_params: PageParams,
        search: str = "",
        show_inactive: bool = False,
        situacao_deferimento: str | None = None,
        id_usuario_responsavel: int | None = None,
    ) -> PaginatedResult[Caso]:
        logger.info(
            f"Searching casos with search: '{search}', situacao_deferimento: {situacao_deferimento}, id_usuario_responsavel: {id_usuario_responsavel}, show_inactive: {show_inactive}, page: {page_params['page']}, per_page: {page_params['per_page']}"
        )
        clauses: list[WhereClause | ComplexWhereClause] = []

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

        if id_usuario_responsavel is not None:
            clauses.append(
                WhereClause(
                    column="id_usuario_responsavel",
                    operator="==",
                    value=id_usuario_responsavel,
                )
            )

        if search:
            search_clauses: list[WhereClause] = [
                WhereClause(column="descricao", operator="ilike", value=f"%{search}%")
            ]

            if search.isdigit():
                search_clauses.append(
                    WhereClause(column="id", operator="==", value=int(search))
                )

            clauses.append(or_clauses(*search_clauses))

        where = None
        if len(clauses) > 1:
            where = and_clauses(*clauses)
        elif len(clauses) == 1:
            where = clauses[0]

        params = SearchParams(
            page_params=page_params,
            where=where,
        )

        logger.info(f"Performing search with processed params: {params}")

        result = self.repository.search(params=params)

        for caso in result.items:
            self._load_caso_dependencies(caso)

        logger.info(
            f"Returning {len(result.items)} casos of total {result.total} found"
        )
        return result

    def create(self, caso_input: CasoCreateInput, criado_por_id: int) -> Caso:
        logger.info(
            f"Creating caso with area_direito: {caso_input.area_direito}, created by: {criado_por_id}, clients count: {len(caso_input.ids_clientes) if caso_input.ids_clientes else 0}"
        )

        with transaction():
            caso_data = caso_input.model_dump(exclude={"ids_clientes"})

            caso_data["data_criacao"] = datetime.now()
            caso_data["data_modificacao"] = datetime.now()
            caso_data["id_criado_por"] = criado_por_id
            caso_data["id_modificado_por"] = criado_por_id
            caso_data["numero_ultimo_processo"] = None
            caso_data["status"] = True

            caso_id = self.repository.create(caso_data)

            if caso_input.ids_clientes:
                self.repository.link_atendidos(caso_id, caso_input.ids_clientes)
                logger.info(
                    f"Linked {len(caso_input.ids_clientes)} atendidos to caso: {caso_id}"
                )

            created_caso = self.find_by_id(caso_id)
            if not created_caso:
                logger.error("Failed to create caso")
                raise DatabaseException("Falha ao criar caso")

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
            raise NotFoundException(resource="Caso", resource_id=caso_id)

        with transaction():
            caso_data = caso_input.model_dump(
                exclude_none=True, exclude={"ids_clientes"}
            )

            caso_data["data_modificacao"] = datetime.now()
            caso_data["id_modificado_por"] = modificado_por_id

            self.repository.update(caso_id, caso_data)

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

    def deferir(self, caso_id: int, modificado_por_id: int) -> Caso | None:
        logger.info(
            f"Deferring caso with id: {caso_id}, modified by: {modificado_por_id}"
        )
        existing = self.repository.find_by_id(caso_id)
        if not existing:
            logger.error(f"Defer failed: caso not found with id: {caso_id}")
            raise NotFoundException(resource="Caso", resource_id=caso_id)

        caso_data = {
            "situacao_deferimento": "deferido",
            "justif_indeferimento": None,
            "data_modificacao": datetime.now(),
            "id_modificado_por": modificado_por_id,
        }

        self.repository.update(caso_id, caso_data)

        logger.info(f"Caso deferred successfully with id: {caso_id}")
        return self.find_by_id(caso_id)

    def indeferir(
        self, caso_id: int, justificativa: str, modificado_por_id: int
    ) -> Caso | None:
        logger.info(
            f"Indeferring caso with id: {caso_id}, modified by: {modificado_por_id}"
        )
        existing = self.repository.find_by_id(caso_id)
        if not existing:
            logger.error(f"Indefer failed: caso not found with id: {caso_id}")
            raise NotFoundException(resource="Caso", resource_id=caso_id)

        caso_data = {
            "situacao_deferimento": "indeferido",
            "justif_indeferimento": justificativa,
            "data_modificacao": datetime.now(),
            "id_modificado_por": modificado_por_id,
        }

        self.repository.update(caso_id, caso_data)

        logger.info(f"Caso indeferred successfully with id: {caso_id}")
        return self.find_by_id(caso_id)

    def find_arquivos_by_caso_id(self, caso_id: int) -> list[ArquivoCaso]:
        logger.info(f"Finding arquivos for caso id: {caso_id}")
        arquivos = self.arquivo_repository.find_by_caso_id(caso_id)
        logger.info(f"Found {len(arquivos)} arquivos for caso id: {caso_id}")
        return arquivos

    def find_arquivo_by_id(self, arquivo_id: int) -> ArquivoCaso | None:
        logger.info(f"Finding arquivo by id: {arquivo_id}")
        arquivo = self.arquivo_repository.find_by_id(arquivo_id)
        if not arquivo:
            logger.warning(f"Arquivo not found with id: {arquivo_id}")
        return arquivo

    def validate_arquivo_for_caso(
        self, arquivo_id: int, caso_id: int
    ) -> ArquivoCaso | None:
        logger.info(f"Validating arquivo {arquivo_id} for caso {caso_id}")
        arquivo = self.arquivo_repository.find_by_id(arquivo_id)

        if not arquivo:
            logger.warning(f"Arquivo not found with id: {arquivo_id}")
            return None

        if arquivo.id_caso != caso_id:
            logger.warning(f"Arquivo {arquivo_id} does not belong to caso {caso_id}")
            return None

        return arquivo

    def get_arquivo_for_download(self, arquivo_id: int, caso_id: int) -> str:
        """
        Get the file path for downloading an arquivo.

        Args:
            arquivo_id: ID of the arquivo
            caso_id: ID of the caso (for validation)

        Returns:
            File path for download

        Raises:
            NotFoundException: If arquivo is not found or doesn't belong to caso
            FileOperationException: If file doesn't exist in filesystem
        """
        logger.info(f"Getting arquivo {arquivo_id} for download from caso {caso_id}")

        arquivo = self.validate_arquivo_for_caso(arquivo_id, caso_id)
        if not arquivo:
            raise NotFoundException(resource="Arquivo", resource_id=arquivo_id)

        if not arquivo.link_arquivo:
            logger.warning(f"Arquivo {arquivo_id} has no file path")
            raise FileOperationException(
                "Arquivo não possui link no sistema", operation="download"
            )

        if not os.path.exists(arquivo.link_arquivo):
            logger.error(f"File not found in filesystem: {arquivo.link_arquivo}")
            raise FileOperationException(
                "Arquivo não encontrado no servidor", operation="download"
            )

        logger.info(f"Arquivo {arquivo_id} ready for download: {arquivo.link_arquivo}")
        return arquivo.link_arquivo

    def upload_arquivo(self, caso_id: int, file: FileStorage) -> ArquivoCaso:
        """
        Upload a file for a caso.

        Args:
            caso_id: ID of the caso
            file: File to upload

        Returns:
            Created ArquivoCaso instance

        Raises:
            NotFoundException: If caso is not found
            ValidationException: If file is invalid
            FileOperationException: If file upload fails
        """
        logger.info(f"Uploading arquivo for caso id: {caso_id}")

        caso = self.repository.find_by_id(caso_id)
        if not caso:
            logger.error(f"Caso not found with id: {caso_id}")
            raise NotFoundException(resource="Caso", resource_id=caso_id)

        if not file or not file.filename:
            logger.warning("Invalid file provided for upload")
            raise ValidationException("Arquivo inválido", field="arquivo")

        filepath = None
        try:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"

            os.makedirs(CASO_FILES_DIR, exist_ok=True)

            filepath = os.path.join(CASO_FILES_DIR, filename)
            file.save(filepath)
            logger.info(f"File saved to filesystem: {filepath}")

            with transaction():
                arquivo_id = self.arquivo_repository.create(
                    {
                        "id_caso": caso_id,
                        "link_arquivo": filepath,
                    }
                )
                arquivo = self.arquivo_repository.find_by_id(arquivo_id)
                if not arquivo:
                    raise DatabaseException("Falha ao criar arquivo no banco de dados")
                logger.info(f"Arquivo created successfully with id: {arquivo_id}")
                return arquivo
        except (NotFoundException, ValidationException, DatabaseException):
            # Re-raise our custom exceptions
            if filepath and os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    logger.info(f"Cleaned up file after error: {filepath}")
                except Exception:
                    pass
            raise
        except Exception as e:
            logger.error(
                f"Error uploading arquivo for caso {caso_id}: {str(e)}", exc_info=True
            )
            if filepath and os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    logger.info(f"Cleaned up file after error: {filepath}")
                except Exception:
                    pass
            raise FileOperationException(
                f"Erro ao fazer upload do arquivo: {str(e)}", operation="upload"
            )

    def delete_arquivo(self, arquivo_id: int, caso_id: int) -> None:
        """
        Delete an arquivo from a caso.

        Args:
            arquivo_id: ID of the arquivo to delete
            caso_id: ID of the caso (for validation)

        Raises:
            NotFoundException: If arquivo is not found or doesn't belong to caso
            FileOperationException: If file deletion fails
            DatabaseException: If database deletion fails
        """
        logger.info(f"Deleting arquivo with id: {arquivo_id}")

        arquivo = self.validate_arquivo_for_caso(arquivo_id, caso_id)
        if not arquivo:
            raise NotFoundException(resource="Arquivo", resource_id=arquivo_id)

        # Delete file from filesystem if it exists
        if arquivo.link_arquivo and os.path.exists(arquivo.link_arquivo):
            try:
                os.remove(arquivo.link_arquivo)
                logger.info(f"File deleted from filesystem: {arquivo.link_arquivo}")
            except Exception as e:
                logger.error(
                    f"Error deleting file {arquivo.link_arquivo}: {str(e)}",
                    exc_info=True,
                )
                raise FileOperationException(
                    f"Erro ao deletar arquivo do sistema de arquivos: {str(e)}",
                    operation="delete",
                )

        # Delete from database
        try:
            with transaction():
                result = self.arquivo_repository.delete(arquivo_id)
                if not result:
                    logger.warning(f"Failed to delete arquivo with id: {arquivo_id}")
                    raise DatabaseException("Erro ao deletar arquivo do banco de dados")
                logger.info(f"Arquivo deleted successfully with id: {arquivo_id}")
        except DatabaseException:
            raise
        except Exception as e:
            logger.error(
                f"Error deleting arquivo from database: {str(e)}", exc_info=True
            )
            raise DatabaseException(
                f"Erro ao deletar arquivo do banco de dados: {str(e)}"
            )

    def _load_caso_dependencies(self, caso: Caso) -> None:
        caso.usuario_responsavel = User.to_info_optional(
            self.user_repository.find_by_id(caso.id_usuario_responsavel)
        )

        if caso.id_criado_por:
            caso.criado_por = User.to_info_optional(
                self.user_repository.find_by_id(caso.id_criado_por)
            )

        if caso.id_orientador:
            caso.orientador = User.to_info_optional(
                self.user_repository.find_by_id(caso.id_orientador)
            )

        if caso.id_estagiario:
            caso.estagiario = User.to_info_optional(
                self.user_repository.find_by_id(caso.id_estagiario)
            )

        if caso.id_colaborador:
            caso.colaborador = User.to_info_optional(
                self.user_repository.find_by_id(caso.id_colaborador)
            )

        if caso.id_modificado_por:
            caso.modificado_por = User.to_info_optional(
                self.user_repository.find_by_id(caso.id_modificado_por)
            )

        if caso.id:
            atendido_ids = self.repository.get_atendido_ids_by_caso_id(caso.id)
            caso.clientes = self.atendido_repository.get_by_ids(atendido_ids)

            processos = self.processo_repository.find_by_caso_id(caso.id)
            for processo in processos:
                if processo.id_criado_por:
                    processo.criado_por = User.to_info_optional(
                        self.user_repository.find_by_id(processo.id_criado_por)
                    )
            caso.processos = processos

            caso.arquivos = self.arquivo_repository.find_by_caso_id(caso.id)
