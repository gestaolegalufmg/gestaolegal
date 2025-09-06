import logging
from typing import Optional

from gestaolegal.schemas.endereco import EnderecoSchema
from gestaolegal.services.base_service import BaseService

logger = logging.getLogger(__name__)


class EnderecoService(BaseService[EnderecoSchema, EnderecoSchema]):
    def __init__(self):
        super().__init__(EnderecoSchema)

    def create_or_update_from_data(
        self, data: dict, endereco_id: Optional[int] = None
    ) -> EnderecoSchema:
        logger.info(
            f"EnderecoService.create_or_update_from_data called with endereco_id: {endereco_id}"
        )
        if endereco_id:
            logger.info(f"Updating existing endereco with ID: {endereco_id}")
            return self.update_from_data(endereco_id, data)
        else:
            logger.info("Creating new endereco")
            return self.create_from_data(data)
