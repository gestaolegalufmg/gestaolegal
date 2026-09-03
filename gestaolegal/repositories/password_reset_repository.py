from datetime import datetime

from sqlalchemy import func, insert, select
from sqlalchemy import update as sql_update
from sqlalchemy.orm import Session

from gestaolegal.database.tables import password_reset_tokens
from gestaolegal.models.password_reset import PasswordResetToken
from gestaolegal.repositories.repository import BaseRepository
from gestaolegal.utils.dataclass_utils import from_dict


class PasswordResetRepository(BaseRepository):
    session: Session

    def __init__(self):
        super().__init__()

    def create(self, usuario_id: int, token_hash: str, expira_em: datetime) -> int:
        result = self.session.execute(
            insert(password_reset_tokens).values(
                usuario_id=usuario_id,
                token_hash=token_hash,
                expira_em=expira_em,
                criado_em=datetime.now(),
            )
        )
        self.session.flush()
        return result.lastrowid

    def find_valid_by_hash(self, token_hash: str) -> PasswordResetToken | None:
        """Token que existe, não foi usado e ainda não expirou."""
        stmt = (
            select(password_reset_tokens)
            .where(password_reset_tokens.c.token_hash == token_hash)
            .where(password_reset_tokens.c.usado_em.is_(None))
            .where(password_reset_tokens.c.expira_em > datetime.now())
        )
        row = self.session.execute(stmt).one_or_none()
        return from_dict(PasswordResetToken, dict(row._mapping)) if row else None

    def mark_used(self, id: int) -> None:
        self.session.execute(
            sql_update(password_reset_tokens)
            .where(password_reset_tokens.c.id == id)
            .values(usado_em=datetime.now())
        )

    def invalidate_for_user(self, usuario_id: int) -> int:
        """Consome os pedidos anteriores do usuário, deixando um link válido só."""
        stmt = (
            sql_update(password_reset_tokens)
            .where(password_reset_tokens.c.usuario_id == usuario_id)
            .where(password_reset_tokens.c.usado_em.is_(None))
            .values(usado_em=datetime.now())
        )
        return self.session.execute(stmt).rowcount

    def contar_desde(self, usuario_id: int, desde: datetime) -> int:
        stmt = (
            select(func.count())
            .select_from(password_reset_tokens)
            .where(password_reset_tokens.c.usuario_id == usuario_id)
            .where(password_reset_tokens.c.criado_em >= desde)
        )
        return self.session.execute(stmt).scalar() or 0
