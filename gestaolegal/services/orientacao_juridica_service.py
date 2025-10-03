import logging

from gestaolegal.common import PageParams
from gestaolegal.models.orientacao_juridica import OrientacaoJuridica
from gestaolegal.repositories.orientacao_juridica_repository import (
    OrientacaoJuridicaRepository,
)

logger = logging.getLogger(__name__)


class OrientacaoJuridicaService:
    repository: OrientacaoJuridicaRepository

    def __init__(self):
        self.repository = OrientacaoJuridicaRepository()

    def find_by_id(self, id: int) -> OrientacaoJuridica | None:
        return self.repository.find_by_id(id)

    def search(self, search: str = "", page_params: PageParams | None = None):
        return self.repository.search(search=search, page_params=page_params)

    def delete(self, id: int):
        return self.repository.delete(id)

    def create(self, orientacao_data: OrientacaoJuridica) -> OrientacaoJuridica:
        return self.repository.create(orientacao_data.to_dict())

    def update(
        self, id: int, orientacao_data: OrientacaoJuridica
    ) -> OrientacaoJuridica:
        return self.repository.update(id, orientacao_data)
