from sqlalchemy import delete as sql_delete
from sqlalchemy import func, insert, select
from sqlalchemy import update as sql_update
from sqlalchemy.orm import Session

from gestaolegal.database.tables import (
    atendidos,
    casos,
    casos_atendidos,
    processos,
    usuarios,
)
from gestaolegal.models.atendido import Atendido
from gestaolegal.models.caso import Caso
from gestaolegal.models.processo import Processo
from gestaolegal.models.user import User
from gestaolegal.common import PaginatedResult
from gestaolegal.repositories.repository import (
    BaseRepository,
    CountParams,
    SearchParams,
)
from gestaolegal.utils.dataclass_utils import from_dict, to_dict


class CasoRepository(BaseRepository):
    session: Session

    def __init__(self):
        super().__init__()

    def find_by_id(self, id: int) -> Caso | None:
        stmt = select(casos).where(casos.c.id == id)
        result = self.session.execute(stmt).one_or_none()

        if not result:
            return None

        caso = from_dict(Caso, dict(result._mapping))

        exclude_fields = {'usuario_responsavel', 'criado_por', 'orientador', 'estagiario', 'colaborador', 'modificado_por', 'clientes', 'processos'}
        caso = Caso(
            **{k: v for k, v in caso.__dict__.items() if k not in exclude_fields},
            usuario_responsavel=self._get_user_by_id(caso.id_usuario_responsavel),
            criado_por=self._get_user_by_id(caso.id_criado_por) if caso.id_criado_por else None,
            orientador=self._get_user_by_id(caso.id_orientador) if caso.id_orientador else None,
            estagiario=self._get_user_by_id(caso.id_estagiario) if caso.id_estagiario else None,
            colaborador=self._get_user_by_id(caso.id_colaborador) if caso.id_colaborador else None,
            modificado_por=self._get_user_by_id(caso.id_modificado_por) if caso.id_modificado_por else None,
            clientes=self._get_atendidos_by_caso_id(id),
            processos=self._get_processos_by_caso_id(id)
        )

        return caso

    def search(self, params: SearchParams) -> PaginatedResult[Caso]:
        stmt = select(casos, func.count().over().label("total_count"))

        stmt = self._apply_where_clause(stmt, params.get("where"), casos)
        stmt = stmt.order_by(casos.c.data_criacao.desc())
        stmt = self._apply_pagination(stmt, params.get("page_params"))

        results = self.session.execute(stmt).all()
        total = results[0].total_count if results else 0

        items = []
        for row in results:
            caso_temp = from_dict(Caso, dict(row._mapping))
            exclude_fields = {'usuario_responsavel', 'criado_por', 'orientador', 'estagiario', 'colaborador', 'modificado_por', 'clientes', 'processos'}
            caso = Caso(
                **{k: v for k, v in caso_temp.__dict__.items() if k not in exclude_fields},
                usuario_responsavel=self._get_user_by_id(caso_temp.id_usuario_responsavel),
                criado_por=self._get_user_by_id(caso_temp.id_criado_por) if caso_temp.id_criado_por else None,
                orientador=self._get_user_by_id(caso_temp.id_orientador) if caso_temp.id_orientador else None,
                estagiario=self._get_user_by_id(caso_temp.id_estagiario) if caso_temp.id_estagiario else None,
                colaborador=self._get_user_by_id(caso_temp.id_colaborador) if caso_temp.id_colaborador else None,
                modificado_por=self._get_user_by_id(caso_temp.id_modificado_por) if caso_temp.id_modificado_por else None,
                clientes=self._get_atendidos_by_caso_id(caso_temp.id) if caso_temp.id else []
            )
            items.append(caso)

        page_params = params.get("page_params")
        return PaginatedResult(
            items=items,
            total=total,
            page=page_params["page"] if page_params else 1,
            per_page=page_params["per_page"] if page_params else total,
        )

    def find_one(self, params: SearchParams) -> Caso | None:
        stmt = select(casos)
        stmt = self._apply_where_clause(stmt, params.get("where"), casos)
        result = self.session.execute(stmt).one_or_none()

        if not result:
            return None

        caso_temp = from_dict(Caso, dict(result._mapping))
        exclude_fields = {'usuario_responsavel', 'criado_por', 'orientador', 'estagiario', 'colaborador', 'modificado_por', 'clientes', 'processos'}
        caso = Caso(
            **{k: v for k, v in caso_temp.__dict__.items() if k not in exclude_fields},
            usuario_responsavel=self._get_user_by_id(caso_temp.id_usuario_responsavel),
            criado_por=self._get_user_by_id(caso_temp.id_criado_por) if caso_temp.id_criado_por else None,
            clientes=self._get_atendidos_by_caso_id(caso_temp.id) if caso_temp.id else []
        )

        return caso

    def count(self, params: CountParams) -> int:
        stmt = select(func.count()).select_from(casos)
        stmt = self._apply_where_clause(stmt, params.get("where"), casos)

        result = self.session.execute(stmt).scalar()
        return result or 0

    def create(self, data: Caso) -> int:
        caso_dict = to_dict(
            data,
            exclude={
                "id",
                "usuario_responsavel",
                "clientes",
                "orientador",
                "estagiario",
                "colaborador",
                "criado_por",
                "modificado_por",
                "processos",
            }
        )
        stmt = insert(casos).values(**caso_dict)
        result = self.session.execute(stmt)
        return result.lastrowid

    def update(self, id: int, data: Caso) -> None:
        caso_dict = to_dict(
            data,
            exclude={
                "id",
                "usuario_responsavel",
                "clientes",
                "orientador",
                "estagiario",
                "colaborador",
                "criado_por",
                "modificado_por",
                "processos",
            }
        )
        stmt = sql_update(casos).where(casos.c.id == id).values(**caso_dict)
        self.session.execute(stmt)

    def delete(self, id: int) -> bool:
        stmt = sql_update(casos).where(casos.c.id == id).values(status=False)
        result = self.session.execute(stmt)
        return result.rowcount > 0

    def link_atendidos(self, caso_id: int, atendido_ids: list[int]) -> None:
        stmt = sql_delete(casos_atendidos).where(casos_atendidos.c.id_caso == caso_id)
        self.session.execute(stmt)

        for atendido_id in atendido_ids:
            stmt = insert(casos_atendidos).values(
                id_caso=caso_id, id_atendido=atendido_id
            )
            self.session.execute(stmt)

    def _get_user_by_id(self, user_id: int) -> User | None:
        stmt = select(usuarios).where(usuarios.c.id == user_id)
        result = self.session.execute(stmt).one_or_none()
        return from_dict(User, dict(result._mapping)) if result else None

    def _get_atendidos_by_caso_id(self, caso_id: int) -> list[Atendido]:
        stmt = (
            select(atendidos)
            .select_from(
                casos_atendidos.join(
                    atendidos, casos_atendidos.c.id_atendido == atendidos.c.id
                )
            )
            .where(casos_atendidos.c.id_caso == caso_id)
        )

        results = self.session.execute(stmt).all()
        return [from_dict(Atendido, dict(row._mapping)) for row in results]

    def _get_processos_by_caso_id(self, caso_id: int) -> list[Processo]:
        stmt = select(processos).where(processos.c.id_caso == caso_id)

        results = self.session.execute(stmt).all()
        processos_list: list[Processo] = []
        for row in results:
            processo_temp = from_dict(Processo, dict(row._mapping))
            processo = Processo(
                **{k: v for k, v in processo_temp.__dict__.items()},
                criado_por=self._get_user_by_id(processo_temp.id_criado_por)
            )
            processos_list.append(processo)

        return processos_list
