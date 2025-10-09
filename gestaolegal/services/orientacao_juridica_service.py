import logging
from datetime import datetime

from gestaolegal.common import PageParams
from gestaolegal.models.orientacao_juridica import (
    OrientacaoJuridica,
    OrientacaoJuridicaDetail,
    OrientacaoJuridicaListItem,
)
from gestaolegal.models.orientacao_juridica_input import (
    OrientacaoJuridicaCreate,
    OrientacaoJuridicaUpdate,
)
from gestaolegal.repositories.atendido_repository import AtendidoRepository
from gestaolegal.repositories.orientacao_juridica_repository import (
    OrientacaoJuridicaRepository,
)
from gestaolegal.common import PaginatedResult
from gestaolegal.repositories.repository import (
    ComplexWhereClause,
    GetParams,
    SearchParams,
    WhereClause,
)
from gestaolegal.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class OrientacaoJuridicaService:
    repository: OrientacaoJuridicaRepository
    user_repository: UserRepository
    atendido_repository: AtendidoRepository

    def __init__(self):
        self.repository = OrientacaoJuridicaRepository()
        self.user_repository = UserRepository()
        self.atendido_repository = AtendidoRepository()

    def find_by_id(self, id: int) -> OrientacaoJuridicaDetail | None:
        logger.info(f"Finding orientacao juridica by id: {id}")
        orientacao = self.repository.find_by_id(id)
        if not orientacao:
            logger.warning(f"Orientacao juridica with id: {id} not found")
            return None

        logger.info(f"Orientacao juridica with id: {id} found")

        assert orientacao.id is not None

        # INFO: O caso em que id_usuario é None provavelmente ocorre apenas em dados antigos, onde possivelmente essa relação não existia
        # Por hora vamos retornar None, porem idealmente deveriamos associar um usuario, por exemplo o Admin do sistema
        if not orientacao.id_usuario:
            logger.warning(
                f"There is no associated user for orientacao juridica with id: {id}"
            )

        usuario = (
            self.user_repository.find_by_id(orientacao.id_usuario)
            if orientacao.id_usuario
            else None
        )

        atendidos = self.atendido_repository.get_related_with_orientacao_juridica(
            [orientacao.id]
        )[0]

        if not usuario and orientacao.id_usuario:
            logger.error(
                f"Could not find associated user for orientacao juridica with id: {id}"
            )

        return OrientacaoJuridicaDetail(
            id=orientacao.id,
            area_direito=orientacao.area_direito,
            sub_area=orientacao.sub_area,
            data_criacao=orientacao.data_criacao,
            status=orientacao.status == 1,
            atendidos=atendidos,
            descricao=orientacao.descricao,
            usuario=usuario if usuario else None,
        )

    def search(
        self,
        search: str = "",
        page_params: PageParams | None = None,
        show_inactive: bool = False,
        area: str = "",
    ) -> PaginatedResult[OrientacaoJuridicaListItem]:
        logger.info(
            f"Searching orientacoes juridicas with search: '{search}', area: {area}, show_inactive: {show_inactive}"
        )
        clauses = [
            WhereClause(
                column="status", operator="==", value=0 if show_inactive else 1
            ),
        ]

        if search:
            clauses.append(
                WhereClause(column="descricao", operator="ilike", value=f"%{search}%")
            )

        if area and area != "todas":
            clauses.append(
                WhereClause(column="area_direito", operator="==", value=area)
            )

        where = (
            ComplexWhereClause(clauses=clauses, operator="and")
            if len(clauses) > 1
            else clauses[0]
        )

        params = SearchParams(
            page_params=page_params,
            where=where,
        )

        result = self.repository.search(params=params)

        users_orientacao_map = {
            item.id_usuario: item.id for item in result.items if item.id_usuario
        }
        users = self.user_repository.get(
            params=GetParams(
                where=WhereClause(
                    column="id", operator="in", value=list(users_orientacao_map.keys())
                )
            )
        )
        logger.info(
            f"Returning {len(result.items)} orientacoes juridicas of total {result.total} found"
        )

        atendidos, atendidos_map = (
            self.atendido_repository.get_related_with_orientacao_juridica(
                [item.id for item in result.items if item.id is not None]
            )
        )

        filled_items: list[OrientacaoJuridicaListItem] = []
        for item in result.items:
            related_user = (
                next(
                    (
                        user
                        for user in users
                        if user.id == users_orientacao_map[item.id_usuario]
                    ),
                    None,
                )
                if item.id_usuario
                else None
            )
            related_atendidos = (
                [
                    atendido
                    for atendido in atendidos
                    if atendido.id in atendidos_map.get(item.id, [])
                ]
                if item.id
                else []
            )

            assert item.id is not None
            filled_items.append(
                OrientacaoJuridicaListItem(
                    id=item.id,
                    area_direito=item.area_direito,
                    sub_area=item.sub_area,
                    descricao=item.descricao,
                    atendidos=[atendido.nome for atendido in related_atendidos],
                    usuario=related_user,
                    data_criacao=item.data_criacao,
                    status=item.status == 1,
                )
            )

        return PaginatedResult(
            items=filled_items,
            total=result.total,
            page=result.page,
            per_page=result.per_page,
        )

    def delete(self, id: int):
        logger.info(f"Deleting orientacao juridica with id: {id}")
        result = self.repository.delete(id)
        logger.info(f"Orientacao juridica deleted successfully with id: {id}")
        return result

    # TODO: Devemos usar transactions aqui
    def create(
        self, orientacao_input: OrientacaoJuridicaCreate, id_usuario: int
    ) -> OrientacaoJuridica:
        logger.info(
            f"Creating orientacao juridica with area_direito: {orientacao_input.area_direito}, created by user: {id_usuario}, atendidos count: {len(orientacao_input.atendidos_ids) if orientacao_input.atendidos_ids else 0}"
        )

        orientacao_data = orientacao_input.model_dump(exclude={"atendidos_ids"})
        orientacao_data["id_usuario"] = id_usuario
        orientacao_data["status"] = 1
        orientacao_data["data_criacao"] = datetime.now()
        orientacao = OrientacaoJuridica.model_validate(
            obj=orientacao_data,
        )

        orientacao_id = self.repository.create(orientacao)

        if orientacao_input.atendidos_ids:
            atendidos = self.atendido_repository.get(
                params=GetParams(
                    where=WhereClause(
                        column="id", operator="in", value=orientacao_input.atendidos_ids
                    )
                )
            )
            logger.info(
                f"Linked {len(orientacao_input.atendidos_ids)} atendidos to orientacao juridica: {orientacao_id}"
            )
            self.repository.add_related_atendidos(
                orientacao_id, [atendido.id for atendido in atendidos]
            )

        created_orientacao = self.repository.find_by_id(orientacao_id)
        if not created_orientacao:
            logger.error(
                f"Could not find created orientacao juridica with id: {orientacao_id}"
            )
            raise ValueError("Something went wrong while creating orientacao juridica")

        logger.info(
            f"Orientacao juridica created successfully with id: {orientacao_id}"
        )
        return created_orientacao

    def update(
        self, id: int, orientacao_input: OrientacaoJuridicaUpdate
    ) -> OrientacaoJuridica:
        logger.info(f"Updating orientacao juridica with id: {id}")
        existing = self.repository.find_by_id(id)
        if not existing:
            logger.error(f"Update failed: orientacao juridica not found with id: {id}")
            raise ValueError(f"Orientacao juridica with id {id} not found")

        update_data = orientacao_input.model_dump(
            exclude_none=True, exclude={"atendidos_ids"}
        )
        updated_data = {**existing.model_dump(), **update_data}
        orientacao = OrientacaoJuridica.model_validate(updated_data)

        self.repository.update(id, orientacao)

        if orientacao_input.atendidos_ids is not None:
            atendidos = self.atendido_repository.get(
                params=GetParams(
                    where=WhereClause(
                        column="id", operator="in", value=orientacao_input.atendidos_ids
                    )
                )
            )
            self.repository.add_related_atendidos(
                id, [atendido.id for atendido in atendidos]
            )
            logger.info(
                f"Updated orientacao juridica {id} with {len(orientacao_input.atendidos_ids)} linked atendidos"
            )

        logger.info(f"Orientacao juridica updated successfully with id: {id}")

        updated = self.repository.find_by_id(id)
        assert updated is not None

        return updated
