import logging

from gestaolegal.models.endereco import Endereco
from gestaolegal.repositories.base_repository import BaseRepository
from gestaolegal.schemas.endereco import EnderecoSchema

logger = logging.getLogger(__name__)


class EnderecoService:
    repository: BaseRepository[EnderecoSchema, Endereco]

    def __init__(self):
        self.repository = BaseRepository(EnderecoSchema, Endereco)

    def create_or_update_from_data(
        self, data: dict, endereco_id: int | None = None
    ) -> Endereco:
        if endereco_id:
            logger.info(f"Updating existing endereco with ID: {endereco_id}")
            return self.repository.update(endereco_id, data)
        else:
            logger.info("Creating new endereco")
            return self.repository.create(data)
