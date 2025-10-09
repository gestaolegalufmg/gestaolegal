from sqlalchemy import func, insert, select
from sqlalchemy import update as sql_update
from sqlalchemy.orm import Session

from gestaolegal.database.tables import eventos, usuarios
from gestaolegal.models.evento import Evento
from gestaolegal.models.user import User
from gestaolegal.repositories.pagination_result import PaginatedResult
from gestaolegal.repositories.repository import (
    BaseRepository,
    CountParams,
    SearchParams,
)


class EventoRepository(BaseRepository):
    session: Session

    def __init__(self):
        super().__init__()

    def find_by_id(self, id: int) -> Evento | None:
        stmt = select(eventos).where(eventos.c.id == id)
        result = self.session.execute(stmt).one_or_none()

        if not result:
            return None

        evento = Evento.model_validate(dict(result._mapping))  # type: ignore
        evento.criado_por = self._get_user_by_id(evento.id_criado_por)

        if evento.id_usuario_responsavel:
            evento.usuario_responsavel = self._get_user_by_id(
                evento.id_usuario_responsavel
            )

        return evento

    def find_by_caso_id(self, caso_id: int) -> PaginatedResult[Evento]:
        stmt = select(eventos).where(eventos.c.id_caso == caso_id)
        results = self.session.execute(stmt).all()

        eventos_list = []
        for row in results:
            evento = Evento.model_validate(dict(row._mapping))
            evento.criado_por = self._get_user_by_id(evento.id_criado_por)

            if evento.id_usuario_responsavel:
                evento.usuario_responsavel = self._get_user_by_id(
                    evento.id_usuario_responsavel
                )

            eventos_list.append(evento)

        return PaginatedResult(
            items=eventos_list,
            total=len(eventos_list),
            page=1,
            per_page=len(eventos_list),
        )

    def search(self, params: SearchParams) -> PaginatedResult[Evento]:
        stmt = select(eventos, func.count().over().label("total_count"))

        stmt = self._apply_where_clause(stmt, params.get("where"), eventos)
        stmt = stmt.order_by(eventos.c.data_evento.desc())
        stmt = self._apply_pagination(stmt, params.get("page_params"))

        results = self.session.execute(stmt).all()
        total = results[0].total_count if results else 0

        items: list[Evento] = []
        for row in results:
            evento = Evento.model_validate(dict(row._mapping))  # type: ignore
            evento.criado_por = self._get_user_by_id(evento.id_criado_por)

            if evento.id_usuario_responsavel:
                evento.usuario_responsavel = self._get_user_by_id(
                    evento.id_usuario_responsavel
                )

            items.append(evento)

        page_params = params.get("page_params")
        return PaginatedResult(
            items=items,
            total=total,
            page=page_params["page"] if page_params else 1,
            per_page=page_params["per_page"] if page_params else total,
        )

    def find_one(self, params: SearchParams) -> Evento | None:
        stmt = select(eventos)
        stmt = self._apply_where_clause(stmt, params.get("where"), eventos)
        result = self.session.execute(stmt).one_or_none()

        if not result:
            return None

        evento = Evento.model_validate(dict(result._mapping))  # type: ignore
        evento.criado_por = self._get_user_by_id(evento.id_criado_por)

        if evento.id_usuario_responsavel:
            evento.usuario_responsavel = self._get_user_by_id(
                evento.id_usuario_responsavel
            )

        return evento

    def count(self, params: CountParams) -> int:
        stmt = select(func.count()).select_from(eventos)
        stmt = self._apply_where_clause(stmt, params.get("where"), eventos)

        result = self.session.execute(stmt).scalar()
        return result or 0

    def create(self, data: Evento) -> int:
        evento_dict = data.model_dump(
            exclude={
                "id",
                "caso",
                "criado_por",
                "usuario_responsavel",
            }
        )
        stmt = insert(eventos).values(**evento_dict)
        result = self.session.execute(stmt)
        return result.lastrowid

    def update(self, id: int, data: Evento) -> None:
        evento_dict = data.model_dump(
            exclude={
                "id",
                "caso",
                "criado_por",
                "usuario_responsavel",
            }
        )
        stmt = sql_update(eventos).where(eventos.c.id == id).values(**evento_dict)
        self.session.execute(stmt)

    def delete(self, id: int) -> bool:
        stmt = sql_update(eventos).where(eventos.c.id == id).values(status=False)
        result = self.session.execute(stmt)
        return result.rowcount > 0

    # TODO: Isso deveria ser uma coluna com autoincrement
    def count_by_caso_id(self, caso_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(eventos)
            .where(eventos.c.id_caso == caso_id)
        )
        result = self.session.execute(stmt).scalar()
        return result or 0

    def _get_user_by_id(self, user_id: int) -> User | None:
        stmt = select(usuarios).where(usuarios.c.id == user_id)
        result = self.session.execute(stmt).one_or_none()
        return User.model_validate(result) if result else None
