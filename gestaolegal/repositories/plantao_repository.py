import logging
from datetime import date
from typing import Any

from sqlalchemy import insert, select
from sqlalchemy import true as sa_true
from sqlalchemy import update as sql_update

from gestaolegal.database.tables import (
    dias_marcados_plantao,
    dias_plantao,
    plantao,
    usuarios,
)
from gestaolegal.models.plantao import DiaMarcadoPlantao, DiaPlantao, Plantao
from gestaolegal.repositories.repository import BaseRepository
from gestaolegal.utils.dataclass_utils import from_dict

logger = logging.getLogger(__name__)


class PlantaoRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    escala_id: int | None = None
    incluir_inativos: bool = False
    escrita: bool = False

    def _escala(self, stmt, table):
        if self.escala_id is not None:
            stmt = stmt.where(table.c.plantao_id == self.escala_id)
        return stmt.with_for_update() if self.escrita else stmt

    def list_escalas(self, unidade_id):
        rows = self.session.execute(
            select(plantao)
            .where(plantao.c.unidade_id == unidade_id)
            .order_by(plantao.c.id.desc())
        ).mappings()
        return [from_dict(Plantao, dict(row)) for row in rows]

    def get_plantao(self, unidade_id=None, lock=False):
        self.escrita = self.escrita or lock
        stmt = select(plantao).where(plantao.c.unidade_id == unidade_id)
        if self.escala_id is not None:
            stmt = stmt.where(plantao.c.id == self.escala_id)
        stmt = stmt.order_by(plantao.c.id.desc()).limit(1)
        if self.escrita:
            stmt = stmt.with_for_update()
        row = self.session.execute(stmt).mappings().first()
        return from_dict(Plantao, dict(row)) if row else None

    def create_plantao(self, data: dict[str, Any]) -> int:
        result = self.session.execute(insert(plantao).values(**data))
        self.session.flush()
        return result.lastrowid

    def update_plantao(self, id: int, data: dict[str, Any]) -> None:
        self.session.execute(
            sql_update(plantao).where(plantao.c.id == id).values(**data)
        )

    # --- dias abertos para plantão ---------------------------------------

    def list_dias(
        self, somente_ativos: bool = True, unidade_id: int | None = None
    ) -> list[DiaPlantao]:
        stmt = select(dias_plantao).order_by(dias_plantao.c.data)
        if somente_ativos and not self.incluir_inativos:
            stmt = stmt.where(dias_plantao.c.status.is_(True))
        if unidade_id is not None:
            stmt = stmt.where(dias_plantao.c.unidade_id == unidade_id)
        rows = self.session.execute(self._escala(stmt, dias_plantao)).all()
        return [from_dict(DiaPlantao, dict(row._mapping)) for row in rows]

    def find_dia_por_data(
        self, data: date, unidade_id: int | None = None
    ) -> DiaPlantao | None:
        stmt = select(dias_plantao).where(dias_plantao.c.data == data)
        if unidade_id is not None:
            stmt = stmt.where(dias_plantao.c.unidade_id == unidade_id)
        row = self.session.execute(self._escala(stmt, dias_plantao)).first()
        return from_dict(DiaPlantao, dict(row._mapping)) if row else None

    def create_dia(self, data: date, unidade_id: int) -> int:
        result = self.session.execute(
            insert(dias_plantao).values(
                data=data, status=True, unidade_id=unidade_id, plantao_id=self.escala_id
            )
        )
        self.session.flush()
        return result.lastrowid

    def set_status_dia(self, id: int, status: bool) -> None:
        self.session.execute(
            sql_update(dias_plantao)
            .where(dias_plantao.c.id == id)
            .values(status=status)
        )

    # --- dias marcados pelos usuários ------------------------------------

    def list_marcacoes_ativas_do_usuario(
        self, id_usuario: int, unidade_id: int | None = None
    ) -> list[DiaMarcadoPlantao]:
        stmt = (
            select(dias_marcados_plantao)
            .where(
                dias_marcados_plantao.c.id_usuario == id_usuario,
                dias_marcados_plantao.c.plantao_id == self.escala_id,
                (
                    sa_true()
                    if self.incluir_inativos
                    else dias_marcados_plantao.c.status.is_(True)
                ),
            )
            .order_by(dias_marcados_plantao.c.data_marcada)
        )
        if unidade_id is not None:
            stmt = stmt.where(dias_marcados_plantao.c.unidade_id == unidade_id)
        rows = self.session.execute(self._escala(stmt, dias_marcados_plantao)).all()
        return [from_dict(DiaMarcadoPlantao, dict(row._mapping)) for row in rows]

    def list_marcacoes_ativas(
        self, unidade_id: int | None = None, todos_usuarios: bool = False
    ) -> list[dict[str, Any]]:
        """Todas as marcações ativas de usuários ativos, com nome e papel.

        Uma consulta só alimenta a escala e o cálculo de vagas de todos os dias
        (a v2 fazia um SELECT por dia dentro de dois laços aninhados).
        """
        stmt = (
            select(
                dias_marcados_plantao.c.id,
                dias_marcados_plantao.c.data_marcada,
                dias_marcados_plantao.c.confirmacao,
                dias_marcados_plantao.c.status,
                dias_marcados_plantao.c.id_usuario,
                usuarios.c.nome,
                usuarios.c.urole,
            )
            .join(
                usuarios,
                usuarios.c.id == dias_marcados_plantao.c.id_usuario,
                isouter=self.incluir_inativos,
            )
            .where(
                (
                    sa_true()
                    if self.incluir_inativos
                    else dias_marcados_plantao.c.status.is_(True)
                ),
                (
                    sa_true()
                    if self.incluir_inativos or todos_usuarios
                    else usuarios.c.status.is_(True)
                ),
            )
            .order_by(dias_marcados_plantao.c.data_marcada, usuarios.c.nome)
        )
        if unidade_id is not None:
            stmt = stmt.where(dias_marcados_plantao.c.unidade_id == unidade_id)
        return [
            dict(row)
            for row in self.session.execute(self._escala(stmt, dias_marcados_plantao))
            .mappings()
            .all()
        ]

    def create_marcacao(
        self, data_marcada: date, id_usuario: int, unidade_id: int
    ) -> int:
        result = self.session.execute(
            insert(dias_marcados_plantao).values(
                data_marcada=data_marcada,
                id_usuario=id_usuario,
                confirmacao="aberto",
                status=True,
                unidade_id=unidade_id,
                plantao_id=self.escala_id,
            )
        )
        self.session.flush()
        return result.lastrowid

    def desativar_marcacoes_do_usuario(self, id_usuario: int, unidade_id: int) -> int:
        result = self.session.execute(
            sql_update(dias_marcados_plantao)
            .where(
                dias_marcados_plantao.c.id_usuario == id_usuario,
                dias_marcados_plantao.c.plantao_id == self.escala_id,
                (
                    sa_true()
                    if self.incluir_inativos
                    else dias_marcados_plantao.c.status.is_(True)
                ),
                dias_marcados_plantao.c.unidade_id == unidade_id,
            )
            .values(status=False)
        )
        return result.rowcount

    # --- conferência ------------------------------------------------------

    def list_marcacoes_para_confirmacao(
        self, data: date, unidade_id: int | None = None
    ) -> list[dict[str, Any]]:
        """Marcações ativas de um dia ainda pendentes de conferência."""
        stmt = (
            select(
                plantao.c.nome.label("escala_nome"),
                plantao.c.id.label("escala_id"),
                dias_marcados_plantao.c.id,
                dias_marcados_plantao.c.data_marcada,
                dias_marcados_plantao.c.confirmacao,
                dias_marcados_plantao.c.id_usuario,
                usuarios.c.nome,
                usuarios.c.urole,
            )
            .join(usuarios, usuarios.c.id == dias_marcados_plantao.c.id_usuario)
            .join(plantao, plantao.c.id == dias_marcados_plantao.c.plantao_id)
            .where(
                dias_marcados_plantao.c.data_marcada == data,
                dias_marcados_plantao.c.confirmacao == "aberto",
                dias_marcados_plantao.c.plantao_id.in_(
                    select(plantao.c.id).where(plantao.c.cancelado.is_(False))
                ),
                (
                    sa_true()
                    if self.incluir_inativos
                    else dias_marcados_plantao.c.status.is_(True)
                ),
                usuarios.c.status.is_(True),
            )
            .order_by(usuarios.c.nome)
        )
        if unidade_id is not None:
            stmt = stmt.where(dias_marcados_plantao.c.unidade_id == unidade_id)
        return [
            dict(row)
            for row in self.session.execute(self._escala(stmt, dias_marcados_plantao))
            .mappings()
            .all()
        ]

    def find_marcacao_by_id(
        self, id: int, unidade_id: int | None = None
    ) -> DiaMarcadoPlantao | None:
        stmt = select(dias_marcados_plantao).where(
            dias_marcados_plantao.c.id == id,
            dias_marcados_plantao.c.plantao_id.in_(
                select(plantao.c.id).where(plantao.c.cancelado.is_(False))
            ),
        )
        if unidade_id is not None:
            stmt = stmt.where(dias_marcados_plantao.c.unidade_id == unidade_id)
        row = self.session.execute(stmt).first()
        return from_dict(DiaMarcadoPlantao, dict(row._mapping)) if row else None

    def update_confirmacao_marcacao(self, id: int, confirmacao: str) -> None:
        self.session.execute(
            sql_update(dias_marcados_plantao)
            .where(dias_marcados_plantao.c.id == id)
            .values(confirmacao=confirmacao)
        )
