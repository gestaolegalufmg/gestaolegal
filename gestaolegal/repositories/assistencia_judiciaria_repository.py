from typing import Any

from sqlalchemy import delete as sql_delete
from sqlalchemy import func, insert, select
from sqlalchemy import update as sql_update
from sqlalchemy.orm import Session

from gestaolegal.common import PaginatedResult
from gestaolegal.database.tables import (
    assistencias_judiciarias,
    assistenciasJudiciarias_xOrientacao_juridica,
    orientacao_juridica,
)
from gestaolegal.models.assistencia_judiciaria import (
    AssistenciaJudiciaria,
    OrientacaoJuridicaResumo,
)
from gestaolegal.repositories.repository import (
    BaseRepository,
    CountParams,
    SearchParams,
)
from gestaolegal.utils.dataclass_utils import from_dict


class AssistenciaJudiciariaRepository(BaseRepository):
    session: Session

    def __init__(self):
        super().__init__()

    def find_by_id(self, id: int) -> AssistenciaJudiciaria | None:
        stmt = select(assistencias_judiciarias).where(
            assistencias_judiciarias.c.id == id
        )
        result = self.session.execute(stmt).one_or_none()
        return (
            from_dict(AssistenciaJudiciaria, dict(result._mapping)) if result else None
        )

    def search(self, params: SearchParams) -> PaginatedResult[AssistenciaJudiciaria]:
        stmt = select(
            assistencias_judiciarias, func.count().over().label("total_count")
        )
        stmt = self._apply_where_clause(
            stmt, params.get("where"), assistencias_judiciarias
        )
        stmt = stmt.order_by(assistencias_judiciarias.c.nome.asc())
        stmt = self._apply_pagination(stmt, params.get("page_params"))

        results = self.session.execute(stmt).all()
        total = results[0].total_count if results else 0

        items = [
            from_dict(AssistenciaJudiciaria, dict(row._mapping)) for row in results
        ]

        page_params = params.get("page_params")
        return PaginatedResult(
            items=items,
            total=total,
            page=page_params["page"] if page_params else 1,
            per_page=page_params["per_page"] if page_params else total,
        )

    def count(self, params: CountParams) -> int:
        stmt = select(func.count()).select_from(assistencias_judiciarias)
        stmt = self._apply_where_clause(
            stmt, params.get("where"), assistencias_judiciarias
        )
        result = self.session.execute(stmt).scalar()
        return result or 0

    def create(self, data: dict[str, Any]) -> int:
        stmt = insert(assistencias_judiciarias).values(**data)
        result = self.session.execute(stmt)
        self.session.flush()
        return result.lastrowid

    def update(self, id: int, data: dict[str, Any]) -> None:
        stmt = (
            sql_update(assistencias_judiciarias)
            .where(assistencias_judiciarias.c.id == id)
            .values(**data)
        )
        self.session.execute(stmt)

    def delete(self, id: int) -> None:
        stmt = (
            sql_update(assistencias_judiciarias)
            .where(assistencias_judiciarias.c.id == id)
            .values(status=0)
        )
        self.session.execute(stmt)

    def get_orientacoes(self, assistencia_id: int) -> list[OrientacaoJuridicaResumo]:
        join_table = assistenciasJudiciarias_xOrientacao_juridica
        stmt = (
            select(
                orientacao_juridica.c.id,
                orientacao_juridica.c.area_direito,
                orientacao_juridica.c.sub_area,
                orientacao_juridica.c.descricao,
            )
            .select_from(
                join_table.join(
                    orientacao_juridica,
                    join_table.c.id_orientacaoJuridica == orientacao_juridica.c.id,
                )
            )
            .where(join_table.c.id_assistenciaJudiciaria == assistencia_id)
        )
        results = self.session.execute(stmt).all()
        return [
            OrientacaoJuridicaResumo(
                id=row.id,
                area_direito=row.area_direito,
                sub_area=row.sub_area,
                descricao=row.descricao,
            )
            for row in results
        ]

    def get_assistencias_by_orientacao(
        self, id_orientacao: int
    ) -> list[AssistenciaJudiciaria]:
        join_table = assistenciasJudiciarias_xOrientacao_juridica
        stmt = (
            select(assistencias_judiciarias)
            .select_from(
                join_table.join(
                    assistencias_judiciarias,
                    join_table.c.id_assistenciaJudiciaria
                    == assistencias_judiciarias.c.id,
                )
            )
            .where(join_table.c.id_orientacaoJuridica == id_orientacao)
            .order_by(assistencias_judiciarias.c.nome.asc())
        )
        results = self.session.execute(stmt).all()
        return [
            from_dict(AssistenciaJudiciaria, dict(row._mapping)) for row in results
        ]

    def link_orientacao(self, assistencia_id: int, id_orientacao: int) -> None:
        join_table = assistenciasJudiciarias_xOrientacao_juridica
        existing = self.session.execute(
            select(join_table.c.id).where(
                join_table.c.id_assistenciaJudiciaria == assistencia_id,
                join_table.c.id_orientacaoJuridica == id_orientacao,
            )
        ).one_or_none()
        if existing:
            return
        self.session.execute(
            insert(join_table).values(
                id_assistenciaJudiciaria=assistencia_id,
                id_orientacaoJuridica=id_orientacao,
            )
        )

    def unlink_orientacao(self, assistencia_id: int, id_orientacao: int) -> None:
        join_table = assistenciasJudiciarias_xOrientacao_juridica
        self.session.execute(
            sql_delete(join_table).where(
                join_table.c.id_assistenciaJudiciaria == assistencia_id,
                join_table.c.id_orientacaoJuridica == id_orientacao,
            )
        )
