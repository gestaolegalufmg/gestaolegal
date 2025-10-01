import logging
from typing import Any

from gestaolegal.common import PageParams
from gestaolegal.common.constants.atendido import TipoBusca
from gestaolegal.models.assistido import Assistido
from gestaolegal.models.atendido import Atendido
from gestaolegal.models.endereco import Endereco
from gestaolegal.repositories.atendido_repository import AtendidoRepository
from gestaolegal.repositories.base_repository import BaseRepository, WhereConditions
from gestaolegal.schemas.assistido import AssistidoSchema
from gestaolegal.schemas.endereco import EnderecoSchema
from gestaolegal.services.endereco_service import EnderecoService

logger = logging.getLogger(__name__)


class AtendidoService:
    repository: AtendidoRepository
    assistido_repository: BaseRepository[AssistidoSchema, Assistido]
    endereco_repository: BaseRepository[EnderecoSchema, Endereco]
    endereco_service: EnderecoService

    def __init__(self):
        self.repository = AtendidoRepository()
        self.assistido_repository = BaseRepository(AssistidoSchema, Assistido)
        self.endereco_repository = BaseRepository(EnderecoSchema, Endereco)
        self.endereco_service = EnderecoService()

    def find_by_id(self, atendido_id: int) -> Atendido | None:
        return self.repository.find_by_id(atendido_id)

    def search(self, search: str = "", page_params: PageParams | None = None, tipo_busca: str = "todos", show_inactive: bool = False):
        search_type = tipo_busca if tipo_busca != "todos" else None
        return self.repository.search(
            search_term=search, 
            search_type=search_type, 
            page_params=page_params, 
            show_inactive=show_inactive
        )

    def get(
        self,
        valor_busca: str = "",
        tipo_busca: TipoBusca = TipoBusca.TODOS,
        page_params: PageParams | None = None,
        show_inactive: bool = False,
    ):
        search_type = tipo_busca.value if tipo_busca != TipoBusca.TODOS else None
        return self.repository.search(valor_busca, search_type, page_params, show_inactive)

    def get_by_ids(self, atendido_ids: list[int]) -> list[Atendido]:
        if not atendido_ids:
            return []
        where_clauses: WhereConditions = [("id", "in", atendido_ids)]
        result = self.repository.get(where_conditions=where_clauses)
        return result.items

    def create(self, atendido_data: dict[str, Any]) -> Atendido:
        endereco_data = self.__extract_endereco_data(atendido_data)
        endereco = self.endereco_repository.create(endereco_data)

        atendido_data["endereco_id"] = endereco.id

        return self.repository.create(Atendido(**atendido_data))

    def update(
        self, 
        atendido_id: int, 
        atendido_data: dict[str, Any],
        modificado_por: int | None = None
    ) -> Atendido:
        atendido = self.repository.find_by_id(atendido_id)
        if not atendido:
            raise ValueError(f"Atendido with id {atendido_id} not found")

        endereco_data = self.__extract_endereco_data(atendido_data)
        endereco = atendido.endereco
        if not endereco or atendido.endereco_id is None:
            raise ValueError(f"Atendido with id {atendido_id} does not have an endereco")

        _ = self.endereco_repository.update(atendido.endereco_id, Endereco(**endereco_data))

        logger.info(f"Existing data: {atendido.to_dict()}")
        existing_data = atendido.to_dict(with_endereco=False)
        existing_data.update(atendido_data)

        logger.info(f"Updated data to be saved: {existing_data}")
        return self.repository.update(atendido_id, Atendido(**existing_data))

    def create_assistido(self, atendido_id: int, assistido_data: dict) -> Assistido:
        if not self.repository.find_by_id(atendido_id):
            raise ValueError(f"Atendido with id {atendido_id} not found")

        if self.assistido_repository.find(
            where_conditions=[("id_atendido", "eq", atendido_id)]
        ):
            raise ValueError(f"Assistido with id {atendido_id} already exists")

        assistido_data["id_atendido"] = atendido_id
        return self.assistido_repository.create(assistido_data)

    def update_assistido(
        self,
        id_atendido: int,
        atendido_data: dict[str, Any],
        assistido_data: dict[str, Any],
    ) -> Assistido:
        atendido = self.repository.find_by_id(id_atendido)
        if not atendido:
            raise ValueError(f"Atendido with id {id_atendido} not found")

        assistido = self.assistido_repository.find(
            where_conditions=[("id_atendido", "eq", id_atendido)]
        )
        if not assistido:
            raise ValueError(
                f"No assistido found for this atendido with id {id_atendido}"
            )

        if atendido_data:
            endereco_data = self.__extract_endereco_data(atendido_data)
            if atendido.endereco_id:
                self.endereco_repository.update(atendido.endereco_id, Endereco(**endereco_data))
            
            if atendido_data:
                existing_atendido_data = atendido.to_dict(with_endereco=False)
                existing_atendido_data.update(atendido_data)
                self.repository.update(atendido.id, Atendido(**existing_atendido_data))

        if assistido_data:
            existing_assistido_data = assistido.to_dict()
            existing_assistido_data.update(assistido_data)
            updated_assistido = self.assistido_repository.update(assistido.id, Assistido(**existing_assistido_data))
            return updated_assistido
        
        return assistido

    def soft_delete(self, atendido_id: int) -> bool:
        return self.repository.soft_delete(atendido_id)

    def __extract_endereco_data(self, atendido_data: dict[str, Any]) -> dict[str, Any]:
        atendido_data.pop("endereco_id", None)
        atendido_data.pop("csrf_token", None)
        return {
            "logradouro": atendido_data.pop("logradouro"),
            "numero": atendido_data.pop("numero"),
            "cidade": atendido_data.pop("cidade"),
            "estado": atendido_data.pop("estado"),
            "complemento": atendido_data.pop("complemento"),
            "bairro": atendido_data.pop("bairro"),
            "cep": atendido_data.pop("cep"),
        }
