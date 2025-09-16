import logging
from typing import Optional

from gestaolegal.common.constants.user_roles import UserRole
from gestaolegal.models.processo import Processo
from gestaolegal.repositories.base_repository import BaseRepository
from gestaolegal.repositories.caso_repository import CasoRepository
from gestaolegal.schemas.processo import ProcessoSchema

logger = logging.getLogger(__name__)


class ProcessoService:
    repository: BaseRepository[ProcessoSchema, Processo]
    caso_repository: CasoRepository

    def __init__(self):
        self.repository = BaseRepository(ProcessoSchema, Processo)
        self.caso_repository = CasoRepository()

    def create(self, processo_data: dict) -> Processo:
        existing_processo = self.repository.find(
            where_conditions=[("numero", "eq", processo_data["numero"])]
        )
        if existing_processo:
            raise ValueError("O número deste processo já está cadastrado no sistema")

        processo = self.repository.create(processo_data)
        logger.info(
            f"Processo associado com sucesso ao caso {processo_data.get('id_caso', 'N/A')}"
        )
        return processo

    def find_by_id(self, processo_id: int) -> Optional[Processo]:
        return self.repository.find_by_id(processo_id)

    def get_processo_by_numero(self, numero_processo: int) -> Optional[Processo]:
        return self.repository.find(
            where_conditions=[("numero", "eq", numero_processo)]
        )

    def get_processos_by_caso(self, caso_id: int) -> list[Processo]:
        result = self.repository.get(where_conditions=[("id_caso", "eq", caso_id)])
        return result.items

    def update_processo(
        self,
        processo_id: int,
        processo_data: dict,
    ) -> Processo:
        processo = self.repository.find_by_id(processo_id)
        if not processo:
            raise ValueError("Processo não encontrado")

        return self.repository.update(processo_id, processo_data)

    def delete_processo(self, processo_id: int) -> None:
        processo = self.repository.find_by_id(processo_id)
        if not processo:
            raise ValueError("Processo não encontrado")

        self.repository.delete(processo_id)

    def get_ultimo_processo_numero(self, caso_id: int) -> int | None:
        result = self.repository.get(where_conditions=[("id_caso", "eq", caso_id)])
        if result.items:
            return result.items[-1].numero
        return None

    def validate_processo_permission(
        self, processo_id: int, user_id: int, user_role: str
    ) -> bool:
        processo = self.find_by_id(processo_id)

        if not processo:
            return False

        if user_role == UserRole.ADMINISTRADOR:
            return True

        if user_id == processo.id_criado_por:
            return True

        return False

    def update_ultimo_processo_dos_casos(self) -> None:
        casos = self.caso_repository.get()

        for caso in casos.items:
            processos = self.get_processos_by_caso(caso.id)
            if processos:
                ultimo_processo = (
                    processos[-1]
                    if isinstance(processos, list)
                    else processos.items[-1]
                    if hasattr(processos, "items")
                    else processos
                )
                caso_data = caso.to_dict()
                caso_data["numero_ultimo_processo"] = ultimo_processo.numero
                self.caso_repository.update(caso.id, caso_data)
