from gestaolegal.models.roteiro import Roteiro
from gestaolegal.repositories.base_repository import BaseRepository
from gestaolegal.schemas.roteiro import RoteiroSchema


class RoteiroRepository(BaseRepository):
    def __init__(self):
        super().__init__(RoteiroSchema, Roteiro)

    def find_by_area_direito(self, area_direito: str):
        """Find roteiro by area_direito"""
        return self.find(where_conditions=[("area_direito", "eq", area_direito)])

    def create_or_update(self, area_direito: str, link: str):
        """Create or update roteiro"""
        roteiro = self.find_by_area_direito(area_direito)

        if roteiro:
            return self.update(roteiro.id, {"link": link})
        else:
            return self.create({"area_direito": area_direito, "link": link})
