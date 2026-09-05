from typing import Any

from sqlalchemy import delete as sql_delete
from sqlalchemy import insert, or_, select
from sqlalchemy import update as sql_update
from sqlalchemy.orm import Session

from gestaolegal.database.tables import unidades, usuarios_unidades
from gestaolegal.models.unidade import Unidade
from gestaolegal.repositories.repository import BaseRepository
from gestaolegal.utils.dataclass_utils import from_dict


class UnidadeRepository(BaseRepository):
    session: Session

    def __init__(self):
        super().__init__()

    def find_by_id(self, id: int) -> Unidade | None:
        stmt = select(unidades).where(unidades.c.id == id)
        result = self.session.execute(stmt).one_or_none()
        return from_dict(Unidade, dict(result._mapping)) if result else None

    def list_ativas(self) -> list[Unidade]:
        stmt = select(unidades).where(unidades.c.ativa).order_by(unidades.c.nome)
        results = self.session.execute(stmt).all()
        return [from_dict(Unidade, dict(row._mapping)) for row in results]

    def create(self, data: dict[str, Any]) -> int:
        stmt = insert(unidades).values(**data)
        result = self.session.execute(stmt)
        self.session.flush()
        return result.lastrowid

    def update(self, id: int, data: dict[str, Any]) -> None:
        stmt = sql_update(unidades).where(unidades.c.id == id).values(**data)
        self.session.execute(stmt)

    def existe_com_nome_ou_sigla(
        self, nome: str, sigla: str, ignorar_id: int | None = None
    ) -> bool:
        """`nome` e `sigla` são UNIQUE; checar antes evita IntegrityError (500)."""
        stmt = select(unidades.c.id).where(
            or_(unidades.c.nome == nome, unidades.c.sigla == sigla)
        )
        if ignorar_id is not None:
            stmt = stmt.where(unidades.c.id != ignorar_id)
        return self.session.execute(stmt).first() is not None

    def unidades_do_usuario(self, usuario_id: int) -> list[Unidade]:
        """Unidades do usuário em uma única consulta.

        O `JWTAuth` recarrega o usuário a cada requisição; resolver o vínculo
        com JOIN evita uma query por unidade.
        """
        stmt = (
            select(unidades)
            .join(
                usuarios_unidades,
                usuarios_unidades.c.unidade_id == unidades.c.id,
            )
            .where(usuarios_unidades.c.usuario_id == usuario_id)
            .order_by(unidades.c.nome)
        )
        results = self.session.execute(stmt).all()
        return [from_dict(Unidade, dict(row._mapping)) for row in results]

    def vincular(self, usuario_id: int, unidade_ids: list[int]) -> None:
        """Substitui os vínculos do usuário pelos informados."""
        stmt = sql_delete(usuarios_unidades).where(
            usuarios_unidades.c.usuario_id == usuario_id
        )
        self.session.execute(stmt)

        for unidade_id in unidade_ids:
            stmt = insert(usuarios_unidades).values(
                usuario_id=usuario_id, unidade_id=unidade_id
            )
            self.session.execute(stmt)

    def usuario_pertence(self, usuario_id: int, unidade_id: int) -> bool:
        stmt = select(usuarios_unidades.c.usuario_id).where(
            usuarios_unidades.c.usuario_id == usuario_id,
            usuarios_unidades.c.unidade_id == unidade_id,
        )
        return self.session.execute(stmt).one_or_none() is not None
