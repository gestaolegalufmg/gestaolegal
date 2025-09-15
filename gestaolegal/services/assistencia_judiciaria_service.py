import logging
from typing import Any, TypeVar

from gestaolegal.forms.plantao.assistencia_juridica_form import AssistenciaJudiciariaForm
from gestaolegal.models.assistencia_judiciaria import AssistenciaJudiciaria
from gestaolegal.repositories.assistencia_judiciaria_repository import (
    AssistenciaJudiciariaRepository,
)
from gestaolegal.repositories.base_repository import PageParams
from gestaolegal.schemas.assistencia_judiciaria import AssistenciaJudiciariaSchema
from gestaolegal.schemas.assistido import AssistidoSchema as Assistido
from gestaolegal.services.endereco_service import EnderecoService

T = TypeVar("T")

logger = logging.getLogger(__name__)


class AssistenciaJudiciariaService:
    def __init__(self):
        self.repository = AssistenciaJudiciariaRepository()
        self.endereco_service = EnderecoService()

    def _prepare_assistencia_data(
        self, assistencia_judiciaria_data: dict, endereco_id: int | None = None
    ) -> dict:
        prepared_data = assistencia_judiciaria_data.copy()

        if endereco_id is not None:
            prepared_data["endereco_id"] = endereco_id

        prepared_data["status"] = 1
        prepared_data["areas_atendidas"] = ",".join(prepared_data["areas_atendidas"])

        return prepared_data

    def create(self, assistencia_judiciaria_data: dict) -> AssistenciaJudiciaria:
        assistencia_judiciaria_data = assistencia_judiciaria_data.pop("csrf_token")
        endereco_data = {
            "logradouro": assistencia_judiciaria_data.pop("logradouro"),
            "numero": assistencia_judiciaria_data.pop("numero"),
            "complemento": assistencia_judiciaria_data.pop("complemento"),
            "bairro": assistencia_judiciaria_data.pop("bairro"),
            "cep": assistencia_judiciaria_data.pop("cep"),
            "cidade": assistencia_judiciaria_data.pop("cidade"),
            "estado": assistencia_judiciaria_data.pop("estado"),
        }

        endereco = self.endereco_service.create_or_update_from_data(endereco_data)
        prepared_data = self._prepare_assistencia_data(
            assistencia_judiciaria_data, endereco.id
        )
        return self.repository.create(prepared_data)

    def update(
        self,
        id_assistencia_judiciaria: int,
        assistencia_judiciaria_data: dict,
    ) -> AssistenciaJudiciaria:
        assistencia_judiciaria = self.repository.find_by_id(id_assistencia_judiciaria)
        if not assistencia_judiciaria:
            raise ValueError(
                f"Assistência judiciária com id {id_assistencia_judiciaria} não encontrada"
            )

        endereco_data = {
            "logradouro": assistencia_judiciaria_data.pop("logradouro"),
            "numero": assistencia_judiciaria_data.pop("numero"),
            "complemento": assistencia_judiciaria_data.pop("complemento"),
            "bairro": assistencia_judiciaria_data.pop("bairro"),
            "cep": assistencia_judiciaria_data.pop("cep"),
            "cidade": assistencia_judiciaria_data.pop("cidade"),
            "estado": assistencia_judiciaria_data.pop("estado"),
        }

        endereco = self.endereco_service.create_or_update_from_data(endereco_data)

        prepared_data = self._prepare_assistencia_data(
            assistencia_judiciaria_data, endereco.id
        )
        return self.repository.update(id_assistencia_judiciaria, prepared_data)

    def soft_delete(self, id_assistencia_judiciaria: int) -> AssistenciaJudiciaria:
        return self.repository.soft_delete(id_assistencia_judiciaria)

    def find_by_id(self, id: int) -> AssistenciaJudiciariaSchema | None:
        return self.repository.find_by_id(id)

    def get_by_area_do_direito(
        self, area_do_direito: str
    ) -> AssistenciaJudiciariaSchema | None:
        return self.repository.find_by_field("area_direito", area_do_direito)

    def get_by_areas_atendida(
        self,
        area_atendida: str,
        nome: str | None = None,
        page_params: PageParams | None = None,
    ):
        return self.repository.get_by_areas_atendida(area_atendida, nome, page_params)

    def get_by_name(self, name: str, page_params: PageParams | None = None):
        return self.repository.get_by_nome(name)

    def find_atendido_assistido_by_id(
        self, id_atendido: int
    ) -> tuple[AssistenciaJudiciariaSchema, Assistido] | None:
        return self.repository.find_atendido_assistido_by_id(id_atendido)

    def get_all(self, page_params: PageParams | None = None):
        return self.repository.get_all_with_pagination(page_params)

    def get_encaminhar_assistencia_data(self, id_orientacao: int) -> dict[str, Any]:
        
        try:
            form = AssistenciaJudiciariaForm()
            return {"success": True, "form": form}
        except Exception:
            return {"success": False, "form": None}
