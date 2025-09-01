from typing import Optional

from gestaolegal.schemas.endereco import EnderecoSchema
from gestaolegal.services.base_service import BaseService


class EnderecoService(BaseService[EnderecoSchema, EnderecoSchema]):
    def __init__(self):
        super().__init__(EnderecoSchema)

    def create_or_update_from_data(
        self, data: dict, endereco_id: Optional[int] = None
    ) -> EnderecoSchema:
        if endereco_id:
            return self.update_from_data(endereco_id, data)
        else:
            return self.create_from_data(data)
