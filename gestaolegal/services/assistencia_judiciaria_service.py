import logging
from typing import Any

from gestaolegal.common import PageParams, PaginatedResult
from gestaolegal.database.session import transaction
from gestaolegal.exceptions import DatabaseException, NotFoundException
from gestaolegal.models.assistencia_judiciaria import (
    AssistenciaJudiciaria,
    AssistenciaJudiciariaDetail,
    AssistenciaJudiciariaListItem,
)
from gestaolegal.models.assistencia_judiciaria_input import (
    AssistenciaJudiciariaCreateInput,
    AssistenciaJudiciariaUpdateInput,
)
from gestaolegal.repositories.assistencia_judiciaria_repository import (
    AssistenciaJudiciariaRepository,
)
from gestaolegal.repositories.endereco_repository import EnderecoRepository
from gestaolegal.repositories.orientacao_juridica_repository import (
    OrientacaoJuridicaRepository,
)
from gestaolegal.repositories.repository import (
    ComplexWhereClause,
    SearchParams,
    WhereClause,
)

logger = logging.getLogger(__name__)

ENDERECO_FIELDS = [
    "logradouro",
    "numero",
    "complemento",
    "bairro",
    "cep",
    "cidade",
    "estado",
]


class AssistenciaJudiciariaService:
    repository: AssistenciaJudiciariaRepository
    endereco_repository: EnderecoRepository
    orientacao_repository: OrientacaoJuridicaRepository

    def __init__(self):
        self.repository = AssistenciaJudiciariaRepository()
        self.endereco_repository = EnderecoRepository()
        self.orientacao_repository = OrientacaoJuridicaRepository()

    @staticmethod
    def _split_areas(areas: str | None) -> list[str]:
        if not areas:
            return []
        return [a for a in areas.split(",") if a]

    def find_by_id(self, id: int) -> AssistenciaJudiciariaDetail | None:
        logger.info(f"Finding assistencia judiciaria by id: {id}")
        assistencia = self.repository.find_by_id(id)
        if not assistencia:
            logger.warning(f"Assistencia judiciaria with id: {id} not found")
            return None

        assert assistencia.id is not None

        endereco = (
            self.endereco_repository.find_by_id(assistencia.endereco_id)
            if assistencia.endereco_id
            else None
        )
        orientacoes = self.repository.get_orientacoes(assistencia.id)

        return AssistenciaJudiciariaDetail(
            id=assistencia.id,
            nome=assistencia.nome,
            regiao=assistencia.regiao,
            areas_atendidas=self._split_areas(assistencia.areas_atendidas),
            telefone=assistencia.telefone,
            email=assistencia.email,
            status=assistencia.status == 1,
            endereco=endereco,
            orientacoes=orientacoes,
        )

    def search(
        self,
        search: str = "",
        page_params: PageParams | None = None,
        show_inactive: bool = False,
        area: str = "",
        regiao: str = "",
    ) -> PaginatedResult[AssistenciaJudiciariaListItem]:
        logger.info(
            f"Searching assistencias judiciarias with search: '{search}', area: {area}, regiao: {regiao}, show_inactive: {show_inactive}"
        )
        clauses = []

        if not show_inactive:
            clauses.append(WhereClause(column="status", operator="==", value=1))

        if search:
            clauses.append(
                WhereClause(column="nome", operator="ilike", value=f"%{search}%")
            )

        if area and area != "todas":
            clauses.append(
                WhereClause(
                    column="areas_atendidas", operator="like", value=f"%{area}%"
                )
            )

        if regiao and regiao != "todas":
            clauses.append(WhereClause(column="regiao", operator="==", value=regiao))

        where = None
        if len(clauses) > 1:
            where = ComplexWhereClause(clauses=clauses, operator="and")
        elif len(clauses) == 1:
            where = clauses[0]

        result = self.repository.search(
            params=SearchParams(page_params=page_params, where=where)
        )

        endereco_ids = [
            item.endereco_id for item in result.items if item.endereco_id is not None
        ]
        enderecos = self.endereco_repository.get_by_ids(endereco_ids)
        endereco_map = {e.id: e for e in enderecos}

        filled_items = [
            AssistenciaJudiciariaListItem(
                id=item.id,
                nome=item.nome,
                regiao=item.regiao,
                areas_atendidas=self._split_areas(item.areas_atendidas),
                telefone=item.telefone,
                email=item.email,
                status=item.status == 1,
                cidade=(
                    endereco_map[item.endereco_id].cidade
                    if item.endereco_id and item.endereco_id in endereco_map
                    else None
                ),
            )
            for item in result.items
            if item.id is not None
        ]

        logger.info(
            f"Returning {len(filled_items)} assistencias judiciarias of total {result.total} found"
        )

        return PaginatedResult(
            items=filled_items,
            total=result.total,
            page=result.page,
            per_page=result.per_page,
        )

    def create(
        self, data: AssistenciaJudiciariaCreateInput
    ) -> AssistenciaJudiciariaDetail:
        logger.info(f"Creating assistencia judiciaria with nome: {data.nome}")
        with transaction():
            payload = data.model_dump()
            orientacao_ids = payload.pop("orientacao_ids", []) or []

            endereco_data = {field: payload.pop(field) for field in ENDERECO_FIELDS}
            endereco_id = self.endereco_repository.create(endereco_data)

            payload["endereco_id"] = endereco_id
            payload["areas_atendidas"] = ",".join(data.areas_atendidas)
            payload["status"] = 1

            assistencia_id = self.repository.create(payload)

            for id_orientacao in orientacao_ids:
                self.repository.link_orientacao(assistencia_id, id_orientacao)

            created = self.find_by_id(assistencia_id)
            if not created:
                raise DatabaseException("Falha ao criar assistência judiciária")
            logger.info(
                f"Assistencia judiciaria created successfully with id: {assistencia_id}"
            )
            return created

    def update(
        self, id: int, data: AssistenciaJudiciariaUpdateInput
    ) -> AssistenciaJudiciariaDetail:
        logger.info(f"Updating assistencia judiciaria with id: {id}")
        existing = self.repository.find_by_id(id)
        if not existing:
            raise NotFoundException(resource="Assistencia Judiciaria", resource_id=id)

        with transaction():
            payload: dict[str, Any] = data.model_dump(exclude_none=True)

            endereco_data = {
                field: payload.pop(field)
                for field in ENDERECO_FIELDS
                if field in payload
            }
            if endereco_data:
                if existing.endereco_id:
                    self.endereco_repository.update(existing.endereco_id, endereco_data)
                else:
                    payload["endereco_id"] = self.endereco_repository.create(
                        endereco_data
                    )

            if "areas_atendidas" in payload and payload["areas_atendidas"] is not None:
                payload["areas_atendidas"] = ",".join(payload["areas_atendidas"])

            if payload:
                self.repository.update(id, payload)

            updated = self.find_by_id(id)
            assert updated is not None
            logger.info(f"Assistencia judiciaria updated successfully with id: {id}")
            return updated

    def delete(self, id: int) -> bool:
        logger.info(f"Deleting assistencia judiciaria with id: {id}")
        existing = self.repository.find_by_id(id)
        if not existing:
            raise NotFoundException(resource="Assistencia Judiciaria", resource_id=id)

        with transaction():
            self.repository.delete(id)
        logger.info(f"Assistencia judiciaria deleted successfully with id: {id}")
        return True

    def encaminhar(
        self, assistencia_id: int, id_orientacao: int
    ) -> AssistenciaJudiciariaDetail:
        logger.info(
            f"Linking assistencia judiciaria {assistencia_id} to orientacao {id_orientacao}"
        )
        assistencia = self.repository.find_by_id(assistencia_id)
        if not assistencia:
            raise NotFoundException(
                resource="Assistencia Judiciaria", resource_id=assistencia_id
            )
        orientacao = self.orientacao_repository.find_by_id(id_orientacao)
        if not orientacao:
            raise NotFoundException(
                resource="Orientacao Juridica", resource_id=id_orientacao
            )

        with transaction():
            self.repository.link_orientacao(assistencia_id, id_orientacao)

        result = self.find_by_id(assistencia_id)
        assert result is not None
        return result

    def desvincular(self, assistencia_id: int, id_orientacao: int) -> None:
        logger.info(
            f"Unlinking assistencia judiciaria {assistencia_id} from orientacao {id_orientacao}"
        )
        with transaction():
            self.repository.unlink_orientacao(assistencia_id, id_orientacao)

    def get_by_orientacao(
        self, id_orientacao: int
    ) -> list[AssistenciaJudiciariaListItem]:
        assistencias = self.repository.get_assistencias_by_orientacao(id_orientacao)
        endereco_ids = [a.endereco_id for a in assistencias if a.endereco_id]
        enderecos = self.endereco_repository.get_by_ids(endereco_ids)
        endereco_map = {e.id: e for e in enderecos}
        return [
            AssistenciaJudiciariaListItem(
                id=a.id,
                nome=a.nome,
                regiao=a.regiao,
                areas_atendidas=self._split_areas(a.areas_atendidas),
                telefone=a.telefone,
                email=a.email,
                status=a.status == 1,
                cidade=(
                    endereco_map[a.endereco_id].cidade
                    if a.endereco_id and a.endereco_id in endereco_map
                    else None
                ),
            )
            for a in assistencias
            if a.id is not None
        ]
