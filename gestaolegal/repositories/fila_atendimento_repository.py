from typing import Any

from sqlalchemy import delete as sql_delete
from sqlalchemy import func, insert, select
from sqlalchemy import update as sql_update

from gestaolegal.database.tables import fila_atendimentos
from gestaolegal.models.fila_atendimento import FilaAtendimento
from gestaolegal.repositories.repository import BaseRepository
from gestaolegal.utils.dataclass_utils import from_dict


class FilaAtendimentoRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def get_active(self) -> list[FilaAtendimento]:
        """Entradas em atendimento (1) e aguardando (0), na ordem de exibição."""
        stmt = (
            select(fila_atendimentos)
            .where(fila_atendimentos.c.status.in_([0, 1]))
            .order_by(
                fila_atendimentos.c.status.desc(),
                fila_atendimentos.c.prioridade.desc(),
                fila_atendimentos.c.data_criacao.asc(),
            )
        )
        results = self.session.execute(stmt).all()
        return [from_dict(FilaAtendimento, dict(row._mapping)) for row in results]

    def find_by_id(self, id: int) -> FilaAtendimento | None:
        stmt = select(fila_atendimentos).where(fila_atendimentos.c.id == id)
        result = self.session.execute(stmt).one_or_none()
        return from_dict(FilaAtendimento, dict(result._mapping)) if result else None

    def find_em_atendimento(self) -> list[FilaAtendimento]:
        stmt = select(fila_atendimentos).where(fila_atendimentos.c.status == 1)
        results = self.session.execute(stmt).all()
        return [from_dict(FilaAtendimento, dict(row._mapping)) for row in results]

    def find_proximo_aguardando(self) -> FilaAtendimento | None:
        stmt = (
            select(fila_atendimentos)
            .where(fila_atendimentos.c.status == 0)
            .order_by(
                fila_atendimentos.c.prioridade.desc(),
                fila_atendimentos.c.data_criacao.asc(),
            )
            .limit(1)
        )
        result = self.session.execute(stmt).first()
        return from_dict(FilaAtendimento, dict(result._mapping)) if result else None

    def count_all(self) -> int:
        stmt = select(func.count()).select_from(fila_atendimentos)
        return self.session.execute(stmt).scalar() or 0

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

    def delete(self, id: int) -> None:
        stmt = sql_delete(fila_atendimentos).where(fila_atendimentos.c.id == id)
        self.session.execute(stmt)
