import logging
from datetime import datetime
from typing import Any

from sqlalchemy import func, insert, select
from sqlalchemy import update as sql_update

from gestaolegal.database.tables import atendidos, fila_atendimentos
from gestaolegal.models.fila_atendimento import FilaAtendimento
from gestaolegal.repositories.repository import BaseRepository
from gestaolegal.utils.dataclass_utils import from_dict

logger = logging.getLogger(__name__)


class FilaAtendimentoRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def find_by_id(self, id: int) -> FilaAtendimento | None:
        stmt = select(fila_atendimentos).where(fila_atendimentos.c.id == id)
        result = self.session.execute(stmt).one_or_none()
        return from_dict(FilaAtendimento, dict(result._mapping)) if result else None

    def count_by_prioridade_no_periodo(
        self, prioridade: int, inicio: datetime, fim: datetime
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(fila_atendimentos)
            .where(
                fila_atendimentos.c.prioridade == prioridade,
                fila_atendimentos.c.data_criacao >= inicio,
                fila_atendimentos.c.data_criacao <= fim,
            )
        )
        return self.session.execute(stmt).scalar() or 0

    def list_no_periodo(self, inicio: datetime, fim: datetime) -> list[dict[str, Any]]:
        stmt = (
            select(
                fila_atendimentos.c.id,
                fila_atendimentos.c.id_atendido,
                fila_atendimentos.c.senha,
                fila_atendimentos.c.prioridade,
                fila_atendimentos.c.psicologia,
                fila_atendimentos.c.status,
                fila_atendimentos.c.data_criacao,
                fila_atendimentos.c.data_saida,
                atendidos.c.nome,
            )
            .outerjoin(atendidos, atendidos.c.id == fila_atendimentos.c.id_atendido)
            .where(
                fila_atendimentos.c.data_criacao >= inicio,
                fila_atendimentos.c.data_criacao <= fim,
            )
        )
        results = self.session.execute(stmt).mappings().all()
        return [dict(row) for row in results]

    def create(self, data: dict[str, Any]) -> int:
        stmt = insert(fila_atendimentos).values(**data)
        result = self.session.execute(stmt)
        self.session.flush()
        return result.lastrowid

    def update(self, id: int, data: dict[str, Any]) -> None:
        stmt = (
            sql_update(fila_atendimentos)
            .where(fila_atendimentos.c.id == id)
            .values(**data)
        )
        self.session.execute(stmt)
