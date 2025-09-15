from typing import Optional

from sqlalchemy import func, or_

from gestaolegal.models.caso import Caso
from gestaolegal.repositories.base_repository import BaseRepository, ConditionList, PageParams
from gestaolegal.schemas import associacao_casos_atendidos
from gestaolegal.schemas.atendido import AtendidoSchema
from gestaolegal.schemas.caso import CasoSchema


class CasoRepository(BaseRepository[CasoSchema, Caso]):
    def __init__(self):
        super().__init__(CasoSchema, Caso)

    def create_with_clientes(
        self, caso_data: dict, clientes_ids: Optional[str] = None
    ) -> Caso:
        caso = self.create(caso_data)

        if clientes_ids:
            caso_schema = self.session.get(CasoSchema, caso.id)
            for id_cliente in clientes_ids.split(","):
                cliente = self.session.get(AtendidoSchema, int(id_cliente))
                if cliente:
                    caso_schema.clientes.append(cliente)
            self.session.commit()

        return caso

    def add_cliente_to_caso(self, caso_id: int, cliente_id: int) -> bool:
        caso_schema = self.session.get(CasoSchema, caso_id)
        if not caso_schema:
            return False

        cliente = self.session.get(AtendidoSchema, cliente_id)
        if not cliente:
            return False

        caso_schema.clientes.append(cliente)
        self.session.commit()
        return True

    def remove_cliente_from_caso(self, caso_id: int, cliente_id: int) -> bool:
        caso_schema = self.session.get(CasoSchema, caso_id)
        if not caso_schema:
            return False

        cliente = self.session.get(AtendidoSchema, cliente_id)
        if not cliente or cliente not in caso_schema.clientes:
            return False

        caso_schema.clientes.remove(cliente)
        self.session.commit()
        return True

    def get_arquivos_by_caso(self, caso_id: int):
        from gestaolegal.schemas.arquivo_caso import ArquivoCasoSchema

        return (
            self.session.query(ArquivoCasoSchema)
            .filter(ArquivoCasoSchema.id_caso == caso_id)
            .all()
        )

    def delete_arquivos_by_caso(self, caso_id: int) -> None:
        from gestaolegal.schemas.arquivo_caso import ArquivoCasoSchema

        arquivos = self.session.query(ArquivoCasoSchema).filter(
            ArquivoCasoSchema.id_caso == caso_id
        )
        for arquivo in arquivos:
            self.session.delete(arquivo)
        self.session.commit()

    def get_casos_with_filters(self, opcao_filtro: str, page_params: PageParams):
        where_conditions: ConditionList = []

        if opcao_filtro != "todos":
            where_conditions.append(("situacao_deferimento", "eq", opcao_filtro))

        return self.get(
            page_params=page_params,
            where_conditions=where_conditions if where_conditions else None,
            order_by=["data_criacao"],
            order_desc=True,
        )

    def get_casos_count_by_area(
        self, data_inicio: str, data_fim: str, areas: Optional[list[str]] = None
    ) -> list[tuple]:
        query = self.session.query(
            CasoSchema.area_direito, func.count(CasoSchema.area_direito)
        ).filter(
            CasoSchema.status,
            CasoSchema.data_criacao >= data_inicio,
            CasoSchema.data_criacao <= data_fim,
        )

        if areas:
            query = query.filter(CasoSchema.area_direito.in_(areas))

        return query.group_by(CasoSchema.area_direito).all()

    def get_casos_by_status_and_area(
        self,
        data_inicio: str,
        data_fim: str,
        areas: Optional[list[str]] = None,
        situacoes: Optional[list[str]] = None,
    ) -> list[Caso]:
        where_conditions: ConditionList = [
            ("data_criacao", "gte", data_inicio),
            ("data_criacao", "lte", data_fim),
        ]

        if areas:
            where_conditions.append(("area_direito", "in", areas))

        if situacoes:
            where_conditions.append(("situacao_deferimento", "in", situacoes))

        result = self.get(
            where_conditions=where_conditions,
            order_by=["data_criacao"],
            order_desc=True,
        )
        return result.items

    def search_by_atendido_name(
        self, busca: str, page_params: PageParams | None = None
    ):
        query = self._create_query()
        query = query.join(associacao_casos_atendidos).join(AtendidoSchema)
        query = self._apply_status_filter(query, True)

        where_clauses = [
            AtendidoSchema.status,
            AtendidoSchema.nome.ilike(f"%{busca}%"),
        ]

        for clause in where_clauses:
            query = query.where(clause)

        query = query.order_by(CasoSchema.id)

        if page_params:
            query = query.offset(
                (page_params["page"] - 1) * page_params["per_page"]
            ).limit(page_params["per_page"])

        result = query.all()
        items = [self._build_model(entity) for entity in result]
        total = query.count()

        return self._create_paginated_result(items, total, page_params)

    def get_casos_by_date_range(self, data_inicio: str, data_fim: str) -> list[Caso]:
        where_conditions: ConditionList = [
            ("data_criacao", "gte", data_inicio),
            ("data_criacao", "lte", data_fim),
        ]

        result = self.get(
            where_conditions=where_conditions,
            order_by=["data_criacao"],
            order_desc=True,
        )
        return result.items

    def _create_paginated_result(self, items, total, page_params):
        from gestaolegal.repositories.base_repository import PaginatedResult

        return PaginatedResult(
            items, total, page_params["page"] or 1, page_params["per_page"] or total
        )

    def get_meus_casos(
        self, id_usuario: int, opcao_filtro: str, page_params: PageParams
    ):
        from sqlalchemy import or_
        
        where_conditions: ConditionList = [
            or_(
                CasoSchema.id_usuario_responsavel == id_usuario,
                CasoSchema.id_orientador == id_usuario,
                CasoSchema.id_estagiario == id_usuario,
            )
        ]

        if opcao_filtro == "cad_por_mim":
            where_conditions.append(("id_criado_por", "eq", id_usuario))
        elif opcao_filtro != "todos":
            where_conditions.append(("situacao_deferimento", "eq", opcao_filtro))

        return self.get(
            page_params=page_params,
            where_conditions=where_conditions,
            order_by=["data_criacao"],
            order_desc=True,
        )
