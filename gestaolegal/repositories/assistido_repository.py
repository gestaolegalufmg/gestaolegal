import logging

from gestaolegal.models.assistido import Assistido
from gestaolegal.repositories.base_repository import BaseRepository
from gestaolegal.repositories.table_definitions import assistidos

logger = logging.getLogger(__name__)


class AssistidoRepository(BaseRepository[Assistido]):
    def __init__(self):
        super().__init__(assistidos, Assistido)

