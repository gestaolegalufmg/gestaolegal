import logging
from datetime import date, datetime, time
from typing import Any

from sqlalchemy import insert, select
from sqlalchemy import update as sql_update

from gestaolegal.database.tables import registro_entrada, usuarios
from gestaolegal.models.presenca import RegistroEntrada
from gestaolegal.repositories.repository import BaseRepository
from gestaolegal.utils.dataclass_utils import from_dict

logger = logging.getLogger(__name__)


class PresencaRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def find_by_id(self, id: int) -> RegistroEntrada | None:
        stmt = select(registro_entrada).where(registro_entrada.c.id == id)
        row = self.session.execute(stmt).first()
        return from_dict(RegistroEntrada, dict(row._mapping)) if row else None

    def find_aberto_do_usuario(self, id_usuario: int) -> RegistroEntrada | None:
        """Registro em curso (entrada sem saída) da pessoa, se houver."""
        stmt = (
            select(registro_entrada)
            .where(
                registro_entrada.c.id_usuario == id_usuario,
                registro_entrada.c.status.is_(True),
            )
            .order_by(registro_entrada.c.data_entrada.desc())
        )
        row = self.session.execute(stmt).first()
        return from_dict(RegistroEntrada, dict(row._mapping)) if row else None

    def create(self, data: dict[str, Any]) -> int:
        result = self.session.execute(insert(registro_entrada).values(**data))
        self.session.flush()
        return result.lastrowid

    def update(self, id: int, data: dict[str, Any]) -> None:
        self.session.execute(
            sql_update(registro_entrada)
            .where(registro_entrada.c.id == id)
            .values(**data)
        )

    def list_para_confirmacao(self, dia: date) -> list[dict[str, Any]]:
        """Registros fechados do dia que ainda não passaram pela conferência."""
        inicio = datetime.combine(dia, time.min)
        fim = datetime.combine(dia, time.max)
        stmt = (
            select(
                registro_entrada.c.id,
                registro_entrada.c.data_entrada,
                registro_entrada.c.data_saida,
                registro_entrada.c.confirmacao,
                registro_entrada.c.id_usuario,
                usuarios.c.nome,
                usuarios.c.urole,
            )
            .join(usuarios, usuarios.c.id == registro_entrada.c.id_usuario)
            .where(
                registro_entrada.c.status.is_(False),
                registro_entrada.c.confirmacao == "aberto",
                registro_entrada.c.data_entrada >= inicio,
                registro_entrada.c.data_entrada <= fim,
                usuarios.c.status.is_(True),
            )
            .order_by(usuarios.c.nome)
        )
        return [dict(row) for row in self.session.execute(stmt).mappings().all()]

    def update_confirmacao(self, id: int, confirmacao: str) -> None:
        self.session.execute(
            sql_update(registro_entrada)
            .where(registro_entrada.c.id == id)
            .values(confirmacao=confirmacao)
        )
