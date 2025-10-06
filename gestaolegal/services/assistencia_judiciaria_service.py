import logging
from typing import Any

from gestaolegal.common import PageParams
from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
from gestaolegal.models.assistencia_judiciaria_input import (
    AssistenciaJudiciariaCreateInput,
    AssistenciaJudiciariaUpdateInput,
)
from gestaolegal.repositories.assistencia_judiciaria_repository import (
    AssistenciaJudiciariaRepository,
)
from gestaolegal.repositories.endereco_repository import EnderecoRepository
from gestaolegal.repositories.pagination_result import PaginatedResult
from gestaolegal.repositories.repository import (
    ComplexWhereClause,
    GetParams,
    WhereClause,
)

logger = logging.getLogger(__name__)


class AssistenciaJudiciariaService:
    repository: AssistenciaJudiciariaRepository
    endereco_repository: EnderecoRepository

    def __init__(self):
        self.repository = AssistenciaJudiciariaRepository()
        self.endereco_repository = EnderecoRepository()

    def find_by_id(self, id: int) -> AssistenciaJudiciaria | None:
        logger.info(f"Finding assistencia judiciaria by id: {id}")
        assistencia = self.repository.find_by_id(id)
        if assistencia:
            if assistencia.endereco_id:
                assistencia.endereco = self.endereco_repository.find_by_id(
                    assistencia.endereco_id
                )
            logger.info(f"Assistencia judiciaria found with id: {id}")
        else:
            logger.warning(f"Assistencia judiciaria not found with id: {id}")
        return assistencia

    def search(
        self,
        page_params: PageParams,
        search: str = "",
        show_inactive: bool = False,
    ) -> PaginatedResult[AssistenciaJudiciaria]:
        logger.info(
            f"Searching assistencias judiciarias with search: '{search}', show_inactive: {show_inactive}, page: {page_params['page']}, per_page: {page_params['per_page']}"
        )
        status = 0 if show_inactive else 1

        clauses: list[WhereClause] = [
            WhereClause(column="status", operator="==", value=status),
        ]

        if search:
            clauses.append(
                WhereClause(column="nome", operator="ilike", value=f"%{search}%")
            )

        where = (
            ComplexWhereClause(
                clauses=clauses,
                operator="and",
            )
            if len(clauses) > 1
            else clauses[0]
        )

        params = GetParams(
            page_params=page_params,
            where=where,
        )

        result = self.repository.search(params=params)

        endereco_ids = [a.endereco_id for a in result.items if a.endereco_id]
        if endereco_ids:
            enderecos = self.endereco_repository.get_by_ids(endereco_ids)
            endereco_map = {e.id: e for e in enderecos}
            for assistencia in result.items:
                if assistencia.endereco_id:
                    assistencia.endereco = endereco_map.get(assistencia.endereco_id)

        logger.info(
            f"Returning {len(result.items)} assistencias judiciarias of total {result.total} found"
        )
        return result

    def create(
        self, assistencia_input: AssistenciaJudiciariaCreateInput
    ) -> AssistenciaJudiciaria:
        logger.info(
            f"Creating assistencia judiciaria with nome: {assistencia_input.nome}"
        )
        assistencia_data = assistencia_input.model_dump()

        endereco_data = self.__extract_endereco_data(assistencia_data)
        endereco_id = self.endereco_repository.create(endereco_data)

        assistencia_data["endereco_id"] = endereco_id
        assistencia_data["status"] = 1

        assistencia_id = self.repository.create(
            AssistenciaJudiciaria.model_validate(assistencia_data)
        )

        assistencia = self.find_by_id(assistencia_id)
        if not assistencia:
            logger.error("Failed to create assistencia judiciaria")
            raise ValueError("Failed to create assistencia judiciaria")

        logger.info(
            f"Assistencia judiciaria created successfully with id: {assistencia_id}"
        )
        return assistencia

    def update(
        self,
        assistencia_id: int,
        assistencia_input: AssistenciaJudiciariaUpdateInput,
    ) -> AssistenciaJudiciaria | None:
        logger.info(f"Updating assistencia judiciaria with id: {assistencia_id}")
        existing = self.repository.find_by_id(assistencia_id)
        if not existing:
            logger.error(
                f"Update failed: assistencia judiciaria not found with id: {assistencia_id}"
            )
            raise ValueError(
                f"Assistência judiciária with id {assistencia_id} not found"
            )

        assistencia_data = assistencia_input.model_dump(exclude_none=True)

        if any(
            key in assistencia_data
            for key in [
                "logradouro",
                "numero",
                "complemento",
                "bairro",
                "cep",
                "cidade",
                "estado",
            ]
        ):
            endereco_data = self.__extract_endereco_data(assistencia_data)
            if existing.endereco_id:
                self.endereco_repository.update(existing.endereco_id, endereco_data)
            else:
                endereco_id = self.endereco_repository.create(endereco_data)
                assistencia_data["endereco_id"] = endereco_id

        updated_data = {**existing.model_dump(), **assistencia_data}
        assistencia = AssistenciaJudiciaria.model_construct(values=updated_data)

        self.repository.update(assistencia_id, assistencia)

        assistencia = self.repository.find_by_id(assistencia_id)
        if assistencia and assistencia.endereco_id:
            assistencia.endereco = self.endereco_repository.find_by_id(
                assistencia.endereco_id
            )

        logger.info(
            f"Assistencia judiciaria updated successfully with id: {assistencia_id}"
        )
        return assistencia

    def soft_delete(self, assistencia_id: int) -> bool:
        logger.info(f"Soft deleting assistencia judiciaria with id: {assistencia_id}")
        result = self.repository.delete(assistencia_id)
        if result:
            logger.info(
                f"Assistencia judiciaria soft deleted successfully with id: {assistencia_id}"
            )
        else:
            logger.warning(
                f"Soft delete failed for assistencia judiciaria with id: {assistencia_id}"
            )
        return result

    def __extract_endereco_data(self, assistencia_data: dict[str, Any]):
        return {
            "logradouro": assistencia_data.pop("logradouro", None),
            "numero": assistencia_data.pop("numero", None),
            "cidade": assistencia_data.pop("cidade", None),
            "estado": assistencia_data.pop("estado", None),
            "complemento": assistencia_data.pop("complemento", None),
            "bairro": assistencia_data.pop("bairro", None),
            "cep": assistencia_data.pop("cep", None),
        }
