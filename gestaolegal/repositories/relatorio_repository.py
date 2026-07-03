from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from gestaolegal.database.tables import casos, orientacao_juridica
from gestaolegal.repositories.repository import BaseRepository


class RelatorioRepository(BaseRepository):
    session: Session

    def __init__(self):
        super().__init__()

    def casos_cadastrados_por_area(
        self, inicio: datetime, fim: datetime, areas: list[str] | None
    ) -> list[dict]:
        stmt = (
            select(
                casos.c.area_direito.label("area_direito"),
                func.count().label("quantidade"),
            )
            .where(casos.c.status == True)  # noqa: E712
            .where(casos.c.data_criacao >= inicio)
            .where(casos.c.data_criacao < fim)
        )
        if areas:
            stmt = stmt.where(casos.c.area_direito.in_(areas))
        stmt = stmt.group_by(casos.c.area_direito).order_by(casos.c.area_direito.asc())

        results = self.session.execute(stmt).all()
        return [
            {"area_direito": row.area_direito, "quantidade": row.quantidade}
            for row in results
        ]

    def casos_por_status(
        self, inicio: datetime, fim: datetime, areas: list[str] | None
    ) -> list[dict]:
        stmt = (
            select(
                casos.c.situacao_deferimento.label("situacao_deferimento"),
                func.count().label("quantidade"),
            )
            .where(casos.c.status == True)  # noqa: E712
            .where(casos.c.data_criacao >= inicio)
            .where(casos.c.data_criacao < fim)
        )
        if areas:
            stmt = stmt.where(casos.c.area_direito.in_(areas))
        stmt = stmt.group_by(casos.c.situacao_deferimento).order_by(
            casos.c.situacao_deferimento.asc()
        )

        results = self.session.execute(stmt).all()
        return [
            {
                "situacao_deferimento": row.situacao_deferimento,
                "quantidade": row.quantidade,
            }
            for row in results
        ]

    def orientacoes_por_area(
        self, inicio: datetime, fim: datetime, areas: list[str] | None
    ) -> list[dict]:
        stmt = (
            select(
                orientacao_juridica.c.area_direito.label("area_direito"),
                func.count().label("quantidade"),
            )
            .where(orientacao_juridica.c.status == 1)
            .where(orientacao_juridica.c.data_criacao >= inicio)
            .where(orientacao_juridica.c.data_criacao < fim)
        )
        if areas:
            stmt = stmt.where(orientacao_juridica.c.area_direito.in_(areas))
        stmt = stmt.group_by(orientacao_juridica.c.area_direito).order_by(
            orientacao_juridica.c.area_direito.asc()
        )

        results = self.session.execute(stmt).all()
        return [
            {"area_direito": row.area_direito, "quantidade": row.quantidade}
            for row in results
        ]
