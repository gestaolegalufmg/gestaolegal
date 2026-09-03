from typing import Any

from sqlalchemy import func, insert, or_, select
from sqlalchemy import update as sql_update
from sqlalchemy.orm import Session

from gestaolegal.common import PageParams, PaginatedResult
from gestaolegal.database.tables import notificacao, usuarios
from gestaolegal.models.notificacao import Notificacao, NotificacaoListItem
from gestaolegal.repositories.repository import BaseRepository
from gestaolegal.utils.dataclass_utils import from_dict


class NotificacaoRepository(BaseRepository):
    session: Session

    def __init__(self):
        super().__init__()

    def _visiveis_para(self, user_id: int, inclui_gerais: bool):
        cond = notificacao.c.id_usu_notificar == user_id
        if inclui_gerais:
            cond = or_(cond, notificacao.c.id_usu_notificar.is_(None))
        return cond

    def find_by_id(self, id: int) -> Notificacao | None:
        row = self.session.execute(
            select(notificacao).where(notificacao.c.id == id)
        ).one_or_none()
        return from_dict(Notificacao, dict(row._mapping)) if row else None

    def listar(
        self, user_id: int, inclui_gerais: bool, page_params: PageParams
    ) -> PaginatedResult[NotificacaoListItem]:
        stmt = (
            select(
                notificacao,
                usuarios.c.nome.label("executor"),
                func.count().over().label("total_count"),
            )
            .select_from(
                notificacao.outerjoin(
                    usuarios, usuarios.c.id == notificacao.c.id_executor_acao
                )
            )
            .where(self._visiveis_para(user_id, inclui_gerais))
            .order_by(notificacao.c.id.desc())
        )
        stmt = self._apply_pagination(stmt, page_params)
        rows = self.session.execute(stmt).mappings().all()
        total = rows[0]["total_count"] if rows else 0
        items = [
            from_dict(
                NotificacaoListItem,
                {k: v for k, v in dict(row).items() if k != "total_count"},
            )
            for row in rows
        ]
        return PaginatedResult(
            items=items,
            total=total,
            page=page_params["page"],
            per_page=page_params["per_page"],
        )

    def contar_nao_lidas(self, user_id: int, inclui_gerais: bool) -> int:
        stmt = (
            select(func.count())
            .select_from(notificacao)
            .where(self._visiveis_para(user_id, inclui_gerais))
            .where(notificacao.c.lida.is_(False))
        )
        return self.session.execute(stmt).scalar() or 0

    def create(self, data: dict[str, Any]) -> int:
        result = self.session.execute(insert(notificacao).values(**data))
        self.session.flush()
        return result.lastrowid

    def create_many(self, rows: list[dict[str, Any]]) -> None:
        if rows:
            self.session.execute(insert(notificacao), rows)
            self.session.flush()

    def marcar_lida(self, id: int, user_id: int, inclui_gerais: bool) -> bool:
        stmt = (
            sql_update(notificacao)
            .where(notificacao.c.id == id)
            .where(self._visiveis_para(user_id, inclui_gerais))
            .values(lida=True)
        )
        return self.session.execute(stmt).rowcount > 0

    def marcar_todas_lidas(self, user_id: int, inclui_gerais: bool) -> int:
        stmt = (
            sql_update(notificacao)
            .where(self._visiveis_para(user_id, inclui_gerais))
            .where(notificacao.c.lida.is_(False))
            .values(lida=True)
        )
        return self.session.execute(stmt).rowcount
