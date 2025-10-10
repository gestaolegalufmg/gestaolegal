import logging

from sqlalchemy import func, insert, select
from sqlalchemy import update as sql_update

from gestaolegal.common import PaginatedResult
from gestaolegal.database.tables import (
    assistidos,
    atendido_xOrientacaoJuridica,
    atendidos,
)
from gestaolegal.models.assistido import Assistido
from gestaolegal.models.atendido import Atendido
from gestaolegal.repositories.repository import (
    BaseRepository,
    CountParams,
    GetParams,
    SearchParams,
)
from gestaolegal.utils.dataclass_utils import from_dict, to_dict

logger = logging.getLogger(__name__)


class AtendidoRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def find_by_id(self, id: int) -> Atendido | None:
        stmt = select(atendidos).where(atendidos.c.id == id)
        result = self.session.execute(stmt).one_or_none()
        return from_dict(Atendido, dict(result._mapping)) if result else None

    def find_by_email(self, email: str) -> Atendido | None:
        stmt = select(atendidos).where(atendidos.c.email == email)
        result = self.session.execute(stmt).one_or_none()
        return from_dict(Atendido, dict(result._mapping)) if result else None

    def get(self, params: GetParams) -> list[Atendido]:
        stmt = select(atendidos)
        stmt = self._apply_where_clause(stmt, params.get("where"), atendidos)
        result = self.session.execute(stmt).all()
        return [from_dict(Atendido, dict(row._mapping)) for row in result]

    def get_by_ids(self, ids: list[int]) -> list[Atendido]:
        if not ids:
            return []
        stmt = select(atendidos).where(atendidos.c.id.in_(ids))
        results = self.session.execute(stmt).all()
        return [from_dict(Atendido, dict(row._mapping)) for row in results]

    # TODO: Avaliar se existe uma forma melhor de modelar este método (e o comportamento como um todo).
    #
    # Explicação:
    # Como as dependências (entidades relacionadas) neste caso são obtidas por meio de uma tabela auxiliar,
    # não é possível implementar a lógica de carregamento das dependências no service, como normalmente fazemos.
    # Por isso, este método retorna não apenas as entidades, mas também um mapa para relacionar cada orientação jurídica com seus atendidos.
    #
    # Observação:
    # Recebemos uma lista de IDs de orientação jurídica, em vez de um único ID, para evitar o problema de "N+1 queries".
    def get_related_with_orientacao_juridica(
        self, orientacao_juridica_ids: list[int]
    ) -> tuple[list[Atendido], dict[int, list[int]]]:
        stmt = select(
            atendidos, atendido_xOrientacaoJuridica.c.id_orientacaoJuridica
        ).join(
            atendido_xOrientacaoJuridica,
            atendido_xOrientacaoJuridica.c.id_atendido == atendidos.c.id,
        )
        stmt = stmt.where(
            atendido_xOrientacaoJuridica.c.id_orientacaoJuridica.in_(
                orientacao_juridica_ids
            )
        )

        result = self.session.execute(stmt).mappings().all()

        orientacao_juridica_map: dict[int, list[int]] = {}
        atendidos_list = []

        for row in result:
            orientacao_id = row["id_orientacaoJuridica"]
            atendido_id = row["id"]

            if orientacao_id not in orientacao_juridica_map:
                orientacao_juridica_map[orientacao_id] = []
            orientacao_juridica_map[orientacao_id].append(atendido_id)

            atendidos_list.append(from_dict(Atendido, dict(row)))

        return atendidos_list, orientacao_juridica_map

    def search(
        self, params: SearchParams, tipo_busca: str = "todos"
    ) -> PaginatedResult[dict]:
        stmt = select(
            atendidos.c.id,
            atendidos.c.nome,
            atendidos.c.cpf,
            atendidos.c.telefone,
            atendidos.c.celular,
            atendidos.c.email,
            atendidos.c.status,
            atendidos.c.data_nascimento,
            atendidos.c.endereco_id,
            func.count().over().label("total_count"),
            (assistidos.c.id_atendido.is_not(None)).label("is_assistido"),
        ).outerjoin(assistidos, assistidos.c.id_atendido == atendidos.c.id)

        stmt = self._apply_where_clause(stmt, params.get("where"), atendidos)

        if tipo_busca == "atendidos":
            stmt = stmt.where(assistidos.c.id_atendido.is_(None))
        elif tipo_busca == "assistidos":
            stmt = stmt.where(assistidos.c.id_atendido.is_not(None))

        stmt = stmt.order_by(atendidos.c.nome)
        stmt = self._apply_pagination(stmt, params.get("page_params"))

        results = self.session.execute(stmt).mappings().all()
        total = results[0].total_count if results else 0

        items = [dict(row) for row in results]

        page_params = params.get("page_params")
        return PaginatedResult(
            items=items,
            total=total,
            page=page_params["page"] if page_params else 1,
            per_page=page_params["per_page"] if page_params else total,
        )

    def find_one(self, params: SearchParams) -> Atendido | None:
        stmt = select(atendidos)
        stmt = self._apply_where_clause(stmt, params.get("where"), atendidos)
        result = self.session.execute(stmt).one_or_none()
        return from_dict(Atendido, dict(result._mapping)) if result else None

    def count(self, params: CountParams) -> int:
        stmt = select(func.count()).select_from(atendidos)
        stmt = self._apply_where_clause(stmt, params.get("where"), atendidos)

        result = self.session.execute(stmt).scalar()
        return result or 0

    def create(self, data: Atendido) -> int:
        atendido_dict = to_dict(
            data,
            exclude={"id", "endereco", "assistido", "orientacoes_juridicas", "casos"},
        )
        stmt = insert(atendidos).values(**atendido_dict)
        result = self.session.execute(stmt)
        return result.lastrowid

    def update(self, id: int, data: Atendido) -> None:
        check_stmt = select(atendidos).where(atendidos.c.id == id)
        existing = self.session.execute(check_stmt).first()

        if not existing:
            raise ValueError(f"Atendido with id {id} not found")

        atendido_dict = to_dict(
            data,
            exclude={"id", "endereco", "assistido", "orientacoes_juridicas", "casos"},
        )
        stmt = sql_update(atendidos).where(atendidos.c.id == id).values(**atendido_dict)
        self.session.execute(stmt)

    def delete(self, id: int) -> bool:
        stmt = sql_update(atendidos).where(atendidos.c.id == id).values(status=0)
        result = self.session.execute(stmt)
        return result.rowcount > 0

    def find_assistido_by_atendido_id(self, atendido_id: int) -> Assistido | None:
        stmt = select(assistidos).where(assistidos.c.id_atendido == atendido_id)
        result = self.session.execute(stmt).one_or_none()
        return from_dict(Assistido, dict(result._mapping)) if result else None

    def get_assistidos_by_atendido_ids(
        self, atendido_ids: list[int]
    ) -> list[Assistido]:
        if not atendido_ids:
            return []
        stmt = select(assistidos).where(assistidos.c.id_atendido.in_(atendido_ids))
        results = self.session.execute(stmt).all()
        return [from_dict(Assistido, dict(row._mapping)) for row in results]

    def create_assistido(self, assistido: Assistido) -> int:
        assistido_dict = to_dict(assistido, exclude={"id", "assistido_pessoa_juridica"})
        stmt = insert(assistidos).values(**assistido_dict)
        result = self.session.execute(stmt)
        return result.lastrowid

    def update_assistido(self, id_atendido: int, assistido: Assistido) -> None:
        check_stmt = select(assistidos).where(assistidos.c.id_atendido == id_atendido)
        existing = self.session.execute(check_stmt).first()

        if not existing:
            raise ValueError(f"Assistido for atendido {id_atendido} not found")

        assistido_dict = to_dict(assistido, exclude={"id", "assistido_pessoa_juridica"})
        stmt = (
            sql_update(assistidos)
            .where(assistidos.c.id_atendido == id_atendido)
            .values(**assistido_dict)
        )
        self.session.execute(stmt)
