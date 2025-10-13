import logging
import os
from datetime import datetime

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from gestaolegal.common import PageParams, PaginatedResult
from gestaolegal.config import Config
from gestaolegal.models.arquivo_caso import ArquivoCaso
from gestaolegal.models.caso import Caso
from gestaolegal.models.caso_input import CasoCreateInput, CasoUpdateInput
from gestaolegal.models.evento import Evento
from gestaolegal.models.evento_input import EventoCreateInput, EventoUpdateInput
from gestaolegal.models.processo import Processo
from gestaolegal.models.processo_input import ProcessoCreateInput, ProcessoUpdateInput
from gestaolegal.repositories.arquivo_caso_repository import ArquivoCasoRepository
from gestaolegal.repositories.atendido_repository import AtendidoRepository
from gestaolegal.repositories.caso_repository import CasoRepository
from gestaolegal.repositories.evento_repository import EventoRepository
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
EVENTO_FILES_DIR = os.path.join(Config.STATIC_ROOT_DIR, "eventos")


class CasoService:
    repository: CasoRepository
    user_repository: UserRepository
    atendido_repository: AtendidoRepository
    processo_repository: ProcessoRepository
    evento_repository: EventoRepository
    arquivo_repository: ArquivoCasoRepository

    def __init__(self):
        self.repository = CasoRepository()
        self.user_repository = UserRepository()
        self.atendido_repository = AtendidoRepository()
        self.processo_repository = ProcessoRepository()
        self.evento_repository = EventoRepository()
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
    ) -> PaginatedResult[Caso]:
        logger.info(
            f"Searching casos with search: '{search}', situacao_deferimento: {situacao_deferimento}, show_inactive: {show_inactive}, page: {page_params['page']}, per_page: {page_params['per_page']}"
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
            raise ValueError("Failed to create caso")

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
            raise ValueError(f"Caso with id {caso_id} not found")

        caso_data = caso_input.model_dump(exclude_none=True, exclude={"ids_clientes"})

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
            raise ValueError(f"Caso with id {caso_id} not found")

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
            raise ValueError(f"Caso with id {caso_id} not found")

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
        logger.info(
            f"Validating arquivo {arquivo_id} for caso {caso_id}"
        )
        arquivo = self.arquivo_repository.find_by_id(arquivo_id)

        if not arquivo:
            logger.warning(f"Arquivo not found with id: {arquivo_id}")
            return None

        if arquivo.id_caso != caso_id:
            logger.warning(
                f"Arquivo {arquivo_id} does not belong to caso {caso_id}"
            )
            return None

        return arquivo

    def get_arquivo_for_download(
        self, arquivo_id: int, caso_id: int
    ) -> tuple[str | None, str]:
        logger.info(f"Getting arquivo {arquivo_id} for download from caso {caso_id}")
        
        arquivo = self.validate_arquivo_for_caso(arquivo_id, caso_id)
        if not arquivo:
            return None, "Arquivo não encontrado ou não pertence ao caso"

        if not arquivo.link_arquivo:
            logger.warning(f"Arquivo {arquivo_id} has no file path")
            return None, "Arquivo não possui link"

        if not os.path.exists(arquivo.link_arquivo):
            logger.error(f"File not found in filesystem: {arquivo.link_arquivo}")
            return None, "Arquivo não encontrado no servidor"

        logger.info(f"Arquivo {arquivo_id} ready for download: {arquivo.link_arquivo}")
        return arquivo.link_arquivo, "OK"

    def upload_arquivo(
        self, caso_id: int, file: FileStorage
    ) -> tuple[ArquivoCaso | None, str]:
        logger.info(f"Uploading arquivo for caso id: {caso_id}")
        
        caso = self.repository.find_by_id(caso_id)
        if not caso:
            logger.error(f"Caso not found with id: {caso_id}")
            return None, "Caso não encontrado"

        if not file or not file.filename:
            logger.warning("Invalid file provided for upload")
            return None, "Arquivo inválido"

        try:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"

            os.makedirs(CASO_FILES_DIR, exist_ok=True)

            filepath = os.path.join(CASO_FILES_DIR, filename)
            file.save(filepath)
            logger.info(f"File saved to filesystem: {filepath}")

            arquivo_id = self.arquivo_repository.create({
                "id_caso": caso_id,
                "link_arquivo": filepath,
            })
            arquivo = self.arquivo_repository.find_by_id(arquivo_id)
            logger.info(f"Arquivo created successfully with id: {arquivo_id}")
            return arquivo, "Arquivo criado com sucesso"
        except Exception as e:
            logger.error(
                f"Error uploading arquivo for caso {caso_id}: {str(e)}", exc_info=True
            )
            return None, f"Erro ao fazer upload do arquivo: {str(e)}"

    def delete_arquivo(self, arquivo_id: int, caso_id: int) -> tuple[bool, str]:
        logger.info(f"Deleting arquivo with id: {arquivo_id}")
        
        arquivo = self.validate_arquivo_for_caso(arquivo_id, caso_id)
        if not arquivo:
            return False, "Arquivo não encontrado ou não pertence ao caso"

        if arquivo.link_arquivo and os.path.exists(arquivo.link_arquivo):
            try:
                os.remove(arquivo.link_arquivo)
                logger.info(f"File deleted from filesystem: {arquivo.link_arquivo}")
            except Exception as e:
                logger.error(
                    f"Error deleting file {arquivo.link_arquivo}: {str(e)}",
                    exc_info=True,
                )
                return False, f"Erro ao deletar arquivo do sistema: {str(e)}"

        result = self.arquivo_repository.delete(arquivo_id)
        if result:
            logger.info(f"Arquivo deleted successfully with id: {arquivo_id}")
            return True, "Arquivo deletado com sucesso"
        else:
            logger.warning(f"Failed to delete arquivo with id: {arquivo_id}")
            return False, "Erro ao deletar arquivo do banco de dados"

    def _load_caso_dependencies(self, caso: Caso) -> None:
        caso.usuario_responsavel = self.user_repository.find_by_id(
            caso.id_usuario_responsavel
        )

        if caso.id_criado_por:
            caso.criado_por = self.user_repository.find_by_id(caso.id_criado_por)

        if caso.id_orientador:
            caso.orientador = self.user_repository.find_by_id(caso.id_orientador)

        if caso.id_estagiario:
            caso.estagiario = self.user_repository.find_by_id(caso.id_estagiario)

        if caso.id_colaborador:
            caso.colaborador = self.user_repository.find_by_id(caso.id_colaborador)

        if caso.id_modificado_por:
            caso.modificado_por = self.user_repository.find_by_id(
                caso.id_modificado_por
            )

        if caso.id:
            atendido_ids = self.repository.get_atendido_ids_by_caso_id(caso.id)
            caso.clientes = self.atendido_repository.get_by_ids(atendido_ids)

            processos = self.processo_repository.find_by_caso_id(caso.id)
            for processo in processos:
                if processo.id_criado_por:
                    processo.criado_por = self.user_repository.find_by_id(
                        processo.id_criado_por
                    )
            caso.processos = processos

            caso.arquivos = self.arquivo_repository.find_by_caso_id(caso.id)

    # Processo management methods
    def search_processos(
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

        where = ComplexWhereClause(clauses=clauses, operator="and") if len(clauses) > 1 else clauses[0]

        params = SearchParams(page_params=page_params, where=where)
        result = self.processo_repository.search(params=params)

        for processo in result.items:
            if processo.id_criado_por:
                processo.criado_por = self.user_repository.find_by_id(
                    processo.id_criado_por
                )

        logger.info(
            f"Returning {len(result.items)} processos of total {result.total} found for caso {caso_id}"
        )
        return result

    def find_processo_by_id(self, processo_id: int) -> Processo | None:
        logger.info(f"Finding processo by id: {processo_id}")
        processo = self.processo_repository.find_by_id(processo_id)
        if not processo:
            logger.warning(f"Processo not found with id: {processo_id}")
            return None

        if processo.id_criado_por:
            processo.criado_por = self.user_repository.find_by_id(
                processo.id_criado_por
            )

        logger.info(f"Processo found with id: {processo_id}")
        return processo

    def validate_processo_for_caso(
        self, processo_id: int, caso_id: int
    ) -> Processo | None:
        logger.info(f"Validating processo {processo_id} for caso {caso_id}")
        processo = self.processo_repository.find_by_id(processo_id)

        if not processo:
            logger.warning(f"Processo not found with id: {processo_id}")
            return None

        if processo.id_caso != caso_id:
            logger.warning(
                f"Processo {processo_id} does not belong to caso {caso_id}"
            )
            return None

        # Load dependencies
        if processo.id_criado_por:
            processo.criado_por = self.user_repository.find_by_id(
                processo.id_criado_por
            )

        return processo

    def create_processo(
        self, caso_id: int, processo_input: ProcessoCreateInput, criado_por_id: int
    ) -> Processo:
        logger.info(
            f"Creating processo for caso {caso_id} with especie: {processo_input.especie}, created by: {criado_por_id}"
        )
        processo_data = processo_input.model_dump()
        processo_data["id_caso"] = caso_id
        processo_data["id_criado_por"] = criado_por_id

        processo_id = self.processo_repository.create(processo_data)

        created_processo = self.find_processo_by_id(processo_id)
        if not created_processo:
            logger.error("Failed to create processo")
            raise ValueError("Failed to create processo")

        logger.info(f"Processo created successfully with id: {processo_id}")
        return created_processo

    def update_processo(
        self, processo_id: int, processo_input: ProcessoUpdateInput
    ) -> Processo | None:
        logger.info(f"Updating processo with id: {processo_id}")
        existing = self.processo_repository.find_by_id(processo_id)
        if not existing:
            logger.error(f"Update failed: processo not found with id: {processo_id}")
            raise ValueError(f"Processo with id {processo_id} not found")

        processo_data = processo_input.model_dump(exclude_none=True)
        self.processo_repository.update(processo_id, processo_data)

        logger.info(f"Processo updated successfully with id: {processo_id}")
        return self.find_processo_by_id(processo_id)

    def delete_processo(self, processo_id: int) -> bool:
        logger.info(f"Soft deleting processo with id: {processo_id}")
        result = self.processo_repository.delete(processo_id)
        if result:
            logger.info(f"Processo soft deleted successfully with id: {processo_id}")
        else:
            logger.warning(f"Soft delete failed for processo with id: {processo_id}")
        return result

    # Evento management methods
    def find_eventos_by_caso_id(self, caso_id: int) -> PaginatedResult[Evento]:
        logger.info(f"Finding eventos for caso id: {caso_id}")
        eventos = self.evento_repository.find_by_caso_id(caso_id)
        logger.info(f"Found {eventos.total} eventos for caso id: {caso_id}")
        return eventos

    def find_evento_by_id(self, evento_id: int) -> Evento | None:
        logger.info(f"Finding evento by id: {evento_id}")
        evento = self.evento_repository.find_by_id(evento_id)
        if not evento:
            logger.warning(f"Evento not found with id: {evento_id}")
        return evento

    def validate_evento_for_caso(
        self, evento_id: int, caso_id: int
    ) -> Evento | None:
        logger.info(f"Validating evento {evento_id} for caso {caso_id}")
        evento = self.evento_repository.find_by_id(evento_id)

        if not evento:
            logger.warning(f"Evento not found with id: {evento_id}")
            return None

        if evento.id_caso != caso_id:
            logger.warning(f"Evento {evento_id} does not belong to caso {caso_id}")
            return None

        return evento

    def create_evento(
        self, caso_id: int, evento_input: EventoCreateInput, criado_por_id: int
    ) -> Evento:
        logger.info(
            f"Creating evento for caso {caso_id} with tipo: {evento_input.tipo}, created by: {criado_por_id}"
        )
        evento_data = evento_input.model_dump()
        evento_data["id_caso"] = caso_id
        evento_data["data_criacao"] = datetime.now()
        evento_data["id_criado_por"] = criado_por_id
        evento_data["num_evento"] = (
            self.evento_repository.count_by_caso_id(caso_id) + 1
        )

        evento_id = self.evento_repository.create(evento_data)

        created_evento = self.find_evento_by_id(evento_id)
        if not created_evento:
            logger.error("Failed to create evento")
            raise ValueError("Failed to create evento")

        logger.info(f"Evento created successfully with id: {evento_id}")
        return created_evento

    def update_evento(
        self, evento_id: int, evento_input: EventoUpdateInput
    ) -> Evento | None:
        logger.info(f"Updating evento with id: {evento_id}")
        existing = self.evento_repository.find_by_id(evento_id)
        if not existing:
            logger.error(f"Update failed: evento not found with id: {evento_id}")
            raise ValueError(f"Evento with id {evento_id} not found")

        evento_data = evento_input.model_dump(exclude_none=True)
        self.evento_repository.update(evento_id, evento_data)

        logger.info(f"Evento updated successfully with id: {evento_id}")
        return self.evento_repository.find_by_id(evento_id)

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
