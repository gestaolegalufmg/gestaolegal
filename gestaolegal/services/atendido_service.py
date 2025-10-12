import logging

from gestaolegal.common import PageParams, PaginatedResult
from gestaolegal.models.assistido import Assistido
from gestaolegal.models.assistido_input import (
    AssistidoCreateInput,
    AssistidoUpdateInput,
)
from gestaolegal.models.atendido import Atendido
from gestaolegal.models.atendido_input import (
    AtendidoCreateInput,
    AtendidoUpdateInput,
    ListAtendido,
)
from gestaolegal.repositories.atendido_repository import AtendidoRepository
from gestaolegal.repositories.endereco_repository import EnderecoRepository
from gestaolegal.repositories.repository import (
    ComplexWhereClause,
    SearchParams,
    WhereClause,
)

logger = logging.getLogger(__name__)


class AtendidoService:
    repository: AtendidoRepository
    endereco_repository: EnderecoRepository

    def __init__(self):
        self.repository = AtendidoRepository()
        self.endereco_repository = EnderecoRepository()

    def find_by_id(self, atendido_id: int) -> Atendido | None:
        logger.info(f"Finding atendido by id: {atendido_id}")
        atendido = self.repository.find_by_id(atendido_id)
        if atendido:
            if atendido.endereco_id:
                atendido.endereco = self.endereco_repository.find_by_id(
                    atendido.endereco_id
                )
            atendido.assistido = self.repository.find_assistido_by_atendido_id(
                atendido_id
            )
            logger.info(
                f"Atendido found with id: {atendido_id}, has assistido: {atendido.assistido is not None}"
            )
        else:
            logger.warning(f"Atendido not found with id: {atendido_id}")
        return atendido

    def search(
        self,
        search: str,
        page_params: PageParams,
        tipo_busca: str = "todos",
        show_inactive: bool = False,
    ) -> PaginatedResult[ListAtendido]:
        logger.info(
            f"AtendidoService.search called with search_term: '{search}', tipo_busca: {tipo_busca}, "
            + f"page_params: {page_params}, show_inactive: {show_inactive}"
        )

        clauses: list[WhereClause] = []

        if not show_inactive:
            clauses.append(WhereClause(column="status", operator="==", value=1))

        if search:
            clauses.append(
                WhereClause(column="nome", operator="ilike", value=f"%{search}%")
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

        result = self.repository.search(params=params, tipo_busca=tipo_busca)

        endereco_ids = [a["endereco_id"] for a in result.items if a["endereco_id"]]
        endereco_map = {}
        if endereco_ids:
            enderecos = self.endereco_repository.get_by_ids(endereco_ids)
            endereco_map = {e.id: e for e in enderecos}

        for atendido in result.items:
            atendido["endereco"] = (
                endereco_map.get(atendido["endereco_id"])
                if atendido["endereco_id"]
                else None
            )
            del atendido["endereco_id"]
            if "total_count" in atendido:
                del atendido["total_count"]

        converted_result = PaginatedResult(
            items=[
                ListAtendido(**a) if isinstance(a, dict) else a for a in result.items
            ],
            total=result.total,
            page=result.page,
            per_page=result.per_page,
        )

        logger.info(
            f"AtendidoService.search returning {result.total} total results, {len(result.items)} items on this page"
        )

        return converted_result

    def create(self, atendido_input: AtendidoCreateInput) -> Atendido:
        logger.info(
            f"Creating atendido with nome: {atendido_input.nome}, cpf: {atendido_input.cpf}"
        )
        atendido_data = atendido_input.model_dump()
        atendido_data["status"] = 1
        atendido_id = self.repository.create(atendido_data)
        logger.info(f"Atendido created successfully with id: {atendido_id}")
        return self.find_by_id(atendido_id)

    def update(
        self,
        atendido_id: int,
        atendido_input: AtendidoUpdateInput,
    ) -> Atendido | None:
        logger.info(f"Updating atendido with id: {atendido_id}")
        existing = self.repository.find_by_id(atendido_id)
        if not existing:
            logger.error(f"Update failed: atendido not found with id: {atendido_id}")
            raise ValueError(f"Atendido with id {atendido_id} not found")

        update_data = atendido_input.model_dump(exclude_none=True)
        self.repository.update(atendido_id, update_data)
        logger.info(f"Atendido updated successfully with id: {atendido_id}")
        return self.find_by_id(atendido_id)

    def create_assistido(
        self, id_atendido: int, assistido_input: AssistidoCreateInput
    ) -> Assistido:
        logger.info(f"Creating assistido for atendido id: {id_atendido}")
        atendido = self.repository.find_by_id(id_atendido)
        if not atendido:
            logger.error(
                f"Create assistido failed: atendido not found with id: {id_atendido}"
            )
            raise ValueError(f"Atendido with id {id_atendido} not found")

        assistido_data = assistido_input.model_dump()
        assistido_data["id_atendido"] = id_atendido

        assistido_id = self.repository.create_assistido(assistido_data)
        logger.info(
            f"Assistido created successfully with id: {assistido_id} for atendido: {id_atendido}"
        )
        return self.repository.find_assistido_by_atendido_id(id_atendido)

    def update_assistido(
        self,
        id_atendido: int,
        atendido_input: AtendidoUpdateInput | None,
        assistido_input: AssistidoUpdateInput,
    ) -> Assistido:
        logger.info(f"Updating assistido for atendido id: {id_atendido}")
        atendido = self.repository.find_by_id(id_atendido)
        if not atendido:
            logger.error(
                f"Update assistido failed: atendido not found with id: {id_atendido}"
            )
            raise ValueError(f"Atendido with id {id_atendido} not found")

        if atendido_input:
            update_data = atendido_input.model_dump(exclude_none=True)
            self.repository.update(id_atendido, update_data)
            logger.info(f"Updated atendido data for id: {id_atendido}")

        assistido = self.repository.find_assistido_by_atendido_id(id_atendido)
        if not assistido:
            logger.error(
                f"Update assistido failed: atendido {id_atendido} does not have an assistido record"
            )
            raise ValueError(
                f"Atendido {id_atendido} does not have an assistido record"
            )

        assistido_update_data = assistido_input.model_dump(exclude_none=True)
        self.repository.update_assistido(id_atendido, assistido_update_data)
        logger.info(f"Assistido updated successfully for atendido id: {id_atendido}")
        return self.repository.find_assistido_by_atendido_id(id_atendido)

    def soft_delete(self, atendido_id: int):
        logger.info(f"Soft deleting atendido with id: {atendido_id}")
        self.repository.delete(atendido_id)
        logger.info(f"Atendido soft deleted successfully with id: {atendido_id}")
