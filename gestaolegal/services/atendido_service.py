import logging

from gestaolegal.common import PageParams
from gestaolegal.common.constants.atendido import TipoBusca
from gestaolegal.models.assistido import Assistido
from gestaolegal.models.atendido import Atendido
from gestaolegal.repositories.atendido_repository import AtendidoRepository
from gestaolegal.repositories.base_repository import BaseRepository, WhereConditions
from gestaolegal.schemas.assistido import AssistidoSchema
from gestaolegal.services.endereco_service import EnderecoService

logger = logging.getLogger(__name__)


class AtendidoService:
    repository: AtendidoRepository
    assistido_repository: BaseRepository[AssistidoSchema, Assistido]
    endereco_service: EnderecoService

    def __init__(self):
        self.repository = AtendidoRepository()
        self.assistido_repository = BaseRepository(AssistidoSchema, Assistido)
        self.endereco_service = EnderecoService()

    def get(
        self,
        valor_busca: str = "",
        tipo_busca: TipoBusca = TipoBusca.TODOS,
        page_params: PageParams | None = None,
        show_inactive: bool = False,
    ):
        search_type = tipo_busca.value if tipo_busca != TipoBusca.TODOS else None
        return self.repository.search(valor_busca, search_type, page_params, show_inactive)

    def find_by_email(self, email: str) -> Atendido | None:
        return self.repository.find(where_conditions=[("email", "eq", email)])

    def find_by_id(self, atendido_id: int) -> Atendido | None:
        return self.repository.find_by_id(atendido_id)

    def get_by_ids(self, atendido_ids: list[int]) -> list[Atendido]:
        if not atendido_ids:
            return []
        where_clauses: WhereConditions = [("id", "in", atendido_ids)]
        result = self.repository.get(where_conditions=where_clauses)
        return result.items

    def create(self, atendido_data: dict) -> Atendido:
        if self.find_by_email(atendido_data["email"]):
            raise ValueError("Email já cadastrado no sistema")

        endereco_data = atendido_data.pop("csrf_token")

        endereco_data = {
            "logradouro": atendido_data.pop("logradouro"),
            "numero": atendido_data.pop("numero"),
            "complemento": atendido_data.pop("complemento"),
            "bairro": atendido_data.pop("bairro"),
            "cep": atendido_data.pop("cep"),
            "cidade": atendido_data.pop("cidade"),
            "estado": atendido_data.pop("estado"),
        }

        endereco = self.endereco_service.create_or_update_from_data(endereco_data)

        atendido_data["endereco_id"] = endereco.id
        atendido_data["status"] = 1

        return self.repository.create(atendido_data)

    def update(self, atendido_id: int, atendido_data: dict) -> Atendido:
        atendido = self.repository.find_by_id(atendido_id)
        if not atendido:
            raise ValueError(f"Atendido with id {atendido_id} not found")

        atendido_data.pop("csrf_token")
        endereco_data = {
            "logradouro": atendido_data.pop("logradouro"),
            "numero": atendido_data.pop("numero"),
            "complemento": atendido_data.pop("complemento"),
            "bairro": atendido_data.pop("bairro"),
            "cep": atendido_data.pop("cep"),
            "cidade": atendido_data.pop("cidade"),
            "estado": atendido_data.pop("estado"),
        }

        endereco = self.endereco_service.create_or_update_from_data(
            endereco_data, atendido.endereco_id
        )
        atendido_data["endereco_id"] = endereco.id

        return self.repository.update(atendido_id, atendido_data)

    def create_atendido_from_json(self, data: dict) -> dict:
        try:
            logger.info(
                f"Starting create_atendido_from_json with data keys: {list(data.keys())}"
            )

            atendido_data = data.copy()

            boolean_fields = [
                "procurou_outro_local",
                "pj_constituida",
                "repres_legal",
                "pretende_constituir_pj",
            ]
            for field in boolean_fields:
                if field in atendido_data:
                    old_value = atendido_data[field]
                    atendido_data[field] = "1" if atendido_data[field] else "0"
                    logger.debug(
                        f"Converted boolean field {field}: {old_value} -> {atendido_data[field]}"
                    )

            if "obs_atendido" in atendido_data:
                obs_value = atendido_data.pop("obs_atendido")
                atendido_data["obs"] = obs_value

            endereco_data = {
                "logradouro": atendido_data.pop("logradouro", ""),
                "numero": atendido_data.pop("numero", ""),
                "complemento": atendido_data.pop("complemento", ""),
                "bairro": atendido_data.pop("bairro", ""),
                "cep": atendido_data.pop("cep", ""),
                "cidade": atendido_data.pop("cidade", ""),
                "estado": atendido_data.pop("estado", ""),
            }
            logger.info(f"Extracted endereco_data: {endereco_data}")

            address_fields_to_remove = ["sem_numero"]
            removed_fields = {}
            for field in address_fields_to_remove:
                if field in atendido_data:
                    removed_fields[field] = atendido_data.pop(field)
                    logger.warning(
                        f"Removed address field {field}: {removed_fields[field]}"
                    )

            logger.info(
                f"Final atendido_data keys before creating atendido: {list(atendido_data.keys())}"
            )
            logger.info("Creating endereco...")
            endereco = self.endereco_service.create_or_update_from_data(endereco_data)
            logger.info(f"Created endereco with ID: {endereco.id}")

            atendido_data["endereco_id"] = endereco.id
            atendido_data["status"] = 1

            logger.info("Creating atendido...")
            atendido = self.repository.create(atendido_data)
            logger.info(f"Successfully created atendido with ID: {atendido.id}")
            return {"id": atendido.id, "message": "success"}

        except Exception as e:
            logger.error(f"Error in create_atendido_from_json: {str(e)}", exc_info=True)
            logger.error(f"Data that caused error: {data}")
            return {"message": f"error: {str(e)}"}

    def create_assistido(self, atendido_id: int, assistido_data: dict) -> Assistido:
        if self.repository.find_by_id(atendido_id):
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
        atendido_data: dict,
        assistido_data: dict,
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

        endereco_data = atendido_data.pop("csrf_token")
        endereco_data = {
            "logradouro": atendido_data.pop("logradouro"),
            "numero": atendido_data.pop("numero"),
            "complemento": atendido_data.pop("complemento"),
            "bairro": atendido_data.pop("bairro"),
            "cep": atendido_data.pop("cep"),
            "cidade": atendido_data.pop("cidade"),
            "estado": atendido_data.pop("estado"),
        }

        self.endereco_service.create_or_update_from_data(
            endereco_data, atendido.endereco_id
        )

        self.repository.update(atendido.id, atendido_data)
        updated_assistido = self.assistido_repository.update(
            assistido.id, assistido_data
        )
        return updated_assistido

    def soft_delete(self, atendido_id: int) -> bool:
        return self.repository.soft_delete(atendido_id)
