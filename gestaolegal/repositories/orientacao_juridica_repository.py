from sqlalchemy import delete as sql_delete
from sqlalchemy import func, insert, select
from sqlalchemy import update as sql_update
from sqlalchemy.orm import Session

from gestaolegal.database.tables import (
    atendido_xOrientacaoJuridica,
    orientacao_juridica,
)
from gestaolegal.models.orientacao_juridica import OrientacaoJuridica
from gestaolegal.repositories.pagination_result import PaginatedResult
from gestaolegal.repositories.repository import (
    BaseRepository,
    CountParams,
    SearchParams,
)


class OrientacaoJuridicaRepository(BaseRepository):
    session: Session

    def __init__(self):
        super().__init__()

    def find_by_id(self, id: int) -> OrientacaoJuridica | None:
        stmt = select(orientacao_juridica).where(orientacao_juridica.c.id == id)
        result = self.session.execute(stmt).one_or_none()

        orientacao = OrientacaoJuridica.model_validate(result) if result else None
        return orientacao

    def search(self, params: SearchParams) -> PaginatedResult[OrientacaoJuridica]:
        stmt = select(orientacao_juridica, func.count().over().label("total_count"))

        stmt = self._apply_where_clause(stmt, params.get("where"), orientacao_juridica)
        stmt = stmt.order_by(orientacao_juridica.c.data_criacao.desc())
        stmt = self._apply_pagination(stmt, params.get("page_params"))

        results = self.session.execute(stmt).all()
        total = results[0].total_count if results else 0

        items = [OrientacaoJuridica.model_validate(row) for row in results]

        page_params = params.get("page_params")
        return PaginatedResult(
            items=items,
            total=total,
            page=page_params["page"] if page_params else 1,
            per_page=page_params["per_page"] if page_params else total,
        )

    def find_one(self, params: SearchParams) -> OrientacaoJuridica | None:
        stmt = select(orientacao_juridica)
        stmt = self._apply_where_clause(stmt, params.get("where"), orientacao_juridica)
        result = self.session.execute(stmt).one_or_none()
        return OrientacaoJuridica.model_validate(result) if result else None

    def count(self, params: CountParams) -> int:
        stmt = select(func.count()).select_from(orientacao_juridica)
        stmt = self._apply_where_clause(stmt, params.get("where"), orientacao_juridica)

        result = self.session.execute(stmt).scalar()
        return result or 0

    def create(self, data: OrientacaoJuridica) -> int:
        orientacao_dict = data.model_dump(
            exclude={"id", "atendidos", "usuario"}
        )
        stmt = insert(orientacao_juridica).values(**orientacao_dict)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.lastrowid

    def update(self, id: int, data: OrientacaoJuridica) -> None:
        orientacao_dict = data.model_dump(
            exclude={"id", "atendidos", "usuario"}
        )
        stmt = (
            sql_update(orientacao_juridica)
            .where(orientacao_juridica.c.id == id)
            .values(**orientacao_dict)
        )
        self.session.execute(stmt)
        self.session.commit()

    def add_related_atendidos(
        self, orientacao_id: int, atendidos_ids: list[int]
    ) -> None:
        stmt = sql_delete(atendido_xOrientacaoJuridica).where(
            atendido_xOrientacaoJuridica.c.id_orientacaoJuridica == orientacao_id
        )
        self.session.execute(stmt)

        for atendido_id in atendidos_ids:
            stmt = insert(atendido_xOrientacaoJuridica).values(
                id_orientacao_juridica=orientacao_id, id_atendido=atendido_id
            )
            self.session.execute(stmt)

        self.session.commit()

    def delete(self, id: int) -> None:
        stmt = (
            sql_update(orientacao_juridica)
            .where(orientacao_juridica.c.id == id)
            .values(status=0)
        )
        self.session.execute(stmt)
        self.session.commit()
