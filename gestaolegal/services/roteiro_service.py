import logging
from typing import cast

from gestaolegal.database.session import transaction
from gestaolegal.models.roteiro import Roteiro
from gestaolegal.repositories.roteiro_repository import RoteiroRepository

logger = logging.getLogger(__name__)


class RoteiroService:
    repository: RoteiroRepository

    def __init__(self):
        self.repository = RoteiroRepository()

    def get_all(self) -> list[Roteiro]:
        return self.repository.get_all()

    def upsert(self, area_direito: str, link: str | None) -> Roteiro:
        logger.info(f"Upserting roteiro for area {area_direito}")
        with transaction():
            existing = self.repository.find_by_area(area_direito)
            if existing:
                self.repository.update(cast(int, existing.id), {"link": link})
                roteiro_id = cast(int, existing.id)
            else:
                roteiro_id = self.repository.create(
                    {"area_direito": area_direito, "link": link}
                )
        result = self.repository.find_by_area(area_direito)
        assert result is not None
        _ = roteiro_id
        return result
