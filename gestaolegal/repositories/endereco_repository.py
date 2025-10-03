import logging

from gestaolegal.models.endereco import Endereco
from gestaolegal.repositories.base_repository import BaseRepository
from gestaolegal.repositories.table_definitions import enderecos

logger = logging.getLogger(__name__)


class EnderecoRepository(BaseRepository[Endereco]):
    def __init__(self):
        super().__init__(enderecos, Endereco)

