from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from gestaolegal.database.tables import (
    casos,
    dias_marcados_plantao,
    orientacao_juridica,
    registro_entrada,
    usuarios,
)
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

    # --- horários de chegada e saída -----------------------------------------

    def usuarios_ativos(self) -> list[dict]:
        """Usuários ativos para o seletor do relatório de horários."""
        stmt = (
            select(usuarios.c.id, usuarios.c.nome, usuarios.c.urole)
            .where(usuarios.c.status.is_(True))
            .order_by(usuarios.c.nome.asc())
        )
        return [dict(row) for row in self.session.execute(stmt).mappings().all()]

    def presencas_no_periodo(
        self, inicio: datetime, fim: datetime, usuarios_ids: list[int] | None
    ) -> list[dict]:
        """Registros de ponto fechados cuja saída caiu no período."""
        stmt = (
            select(
                registro_entrada.c.id,
                registro_entrada.c.id_usuario,
                usuarios.c.nome,
                usuarios.c.urole,
                registro_entrada.c.data_entrada,
                registro_entrada.c.data_saida,
                registro_entrada.c.confirmacao,
            )
            .join(usuarios, usuarios.c.id == registro_entrada.c.id_usuario)
            .where(registro_entrada.c.status.is_(False))
            .where(registro_entrada.c.data_saida >= inicio)
            .where(registro_entrada.c.data_saida < fim)
        )
        if usuarios_ids:
            stmt = stmt.where(registro_entrada.c.id_usuario.in_(usuarios_ids))
        stmt = stmt.order_by(registro_entrada.c.data_entrada.asc(), usuarios.c.nome.asc())
        return [dict(row) for row in self.session.execute(stmt).mappings().all()]

    def plantoes_no_periodo(
        self, inicio: datetime, fim: datetime, usuarios_ids: list[int] | None
    ) -> list[dict]:
        """Dias de plantão marcados (ativos) no período."""
        stmt = (
            select(
                dias_marcados_plantao.c.id,
                dias_marcados_plantao.c.id_usuario,
                usuarios.c.nome,
                usuarios.c.urole,
                dias_marcados_plantao.c.data_marcada,
                dias_marcados_plantao.c.confirmacao,
            )
            .join(usuarios, usuarios.c.id == dias_marcados_plantao.c.id_usuario)
            .where(dias_marcados_plantao.c.status.is_(True))
            .where(dias_marcados_plantao.c.data_marcada >= inicio.date())
            .where(dias_marcados_plantao.c.data_marcada < fim.date())
        )
        if usuarios_ids:
            stmt = stmt.where(dias_marcados_plantao.c.id_usuario.in_(usuarios_ids))
        stmt = stmt.order_by(
            dias_marcados_plantao.c.data_marcada.asc(), usuarios.c.nome.asc()
        )
        return [dict(row) for row in self.session.execute(stmt).mappings().all()]
