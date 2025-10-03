import logging
from typing import Any

from gestaolegal.models.endereco import Endereco
from gestaolegal.repositories.endereco_repository import EnderecoRepository

logger = logging.getLogger(__name__)


class EnderecoService:
    repository: EnderecoRepository

    def __init__(self):
        self.repository = EnderecoRepository()

    def create_or_update_from_data(
        self, data: dict[str, Any], endereco_id: int | None = None
    ) -> Endereco:
        if endereco_id:
            logger.info(f"Updating existing endereco with ID: {endereco_id}")
            return self.repository.update(endereco_id, data)
        else:
            logger.info("Creating new endereco")
            return self.repository.create(data)
