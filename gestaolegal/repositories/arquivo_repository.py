from gestaolegal.models.arquivo import Arquivo
from gestaolegal.models.arquivo_caso import ArquivoCaso
from gestaolegal.models.arquivos_evento import ArquivosEvento
from gestaolegal.repositories.base_repository import BaseRepository
from gestaolegal.schemas.arquivo import ArquivoSchema
from gestaolegal.schemas.arquivo_caso import ArquivoCasoSchema
from gestaolegal.schemas.arquivos_evento import ArquivosEventoSchema


class ArquivoRepository(BaseRepository):
    def __init__(self):
        super().__init__(ArquivoSchema, Arquivo)

        self.arquivo_caso_repo = BaseRepository(ArquivoCasoSchema, ArquivoCaso)
        self.arquivos_evento_repo = BaseRepository(ArquivosEventoSchema, ArquivosEvento)

    def create_arquivo_caso(self, data: dict):
        return self.arquivo_caso_repo.create(data)

    def find_arquivo_caso_by_id(self, arquivo_id: int) -> ArquivoCaso | None:
        return self.arquivo_caso_repo.find_by_id(arquivo_id)

    def get_arquivos_by_caso(self, caso_id: int) -> list[ArquivoCaso]:
        result = self.arquivo_caso_repo.get(
            where_conditions=[("id_caso", "eq", caso_id)]
        )
        return result.items

    def update_arquivo_caso(self, arquivo_id: int, data: dict) -> ArquivoCaso | None:
        return self.arquivo_caso_repo.update(arquivo_id, data)

    def delete_arquivo_caso(self, arquivo_id: int) -> bool:
        return self.arquivo_caso_repo.delete(arquivo_id, hard_delete=True)

    def create_arquivo_evento(self, data: dict) -> ArquivosEvento:
        return self.arquivos_evento_repo.create(data)

    def find_arquivo_evento_by_id(self, arquivo_id: int) -> ArquivosEvento | None:
        return self.arquivos_evento_repo.find_by_id(arquivo_id)

    def get_arquivos_by_evento(self, evento_id: int) -> list[ArquivosEvento]:
        result = self.arquivos_evento_repo.get(
            where_conditions=[("id_evento", "eq", evento_id)]
        )
        return result.items

    def update_arquivo_evento(
        self, arquivo_id: int, data: dict
    ) -> ArquivosEvento | None:
        return self.arquivos_evento_repo.update(arquivo_id, data)

    def delete_arquivo_evento(self, arquivo_id: int) -> bool:
        return self.arquivos_evento_repo.delete(arquivo_id, hard_delete=True)
