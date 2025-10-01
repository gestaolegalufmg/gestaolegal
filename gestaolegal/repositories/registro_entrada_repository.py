from typing import Optional

from gestaolegal.models.registro_entrada import RegistroEntrada
from gestaolegal.repositories.base_repository import BaseRepository, WhereConditions
from gestaolegal.schemas.registro_entrada import RegistroEntradaSchema


class RegistroEntradaRepository(BaseRepository[RegistroEntradaSchema, RegistroEntrada]):
    def __init__(self):
        super().__init__(RegistroEntradaSchema, RegistroEntrada)

    def get_registros_by_date_range_and_users(
        self, data_inicio: str, data_fim: str, usuarios_ids: Optional[list[str]] = None
    ) -> list[RegistroEntrada]:
        """Get registros within date range and optionally filtered by users"""
        where_conditions: WhereConditions = [
            ("status", "eq", False),
            ("data_saida", "gte", data_inicio),
            ("data_saida", "lte", data_fim),
        ]

        if usuarios_ids:
            where_conditions.append(("id_usuario", "in", usuarios_ids))

        result = self.get(
            where_conditions=where_conditions,
            order_by=["data_saida"],
            order_desc=True,
        )
        return result.items

    def get_registros_with_join_by_date_range_and_users(
        self, data_inicio: str, data_fim: str, usuarios_ids: Optional[list[str]] = None
    ):
        """Get registros with user join for reports"""
        from gestaolegal.schemas.user import UserSchema

        query = (
            self.session.query(RegistroEntradaSchema)
            .select_from(RegistroEntradaSchema)
            .join(UserSchema)
            .filter(
                ~RegistroEntradaSchema.status,
                RegistroEntradaSchema.data_saida >= data_inicio,
                RegistroEntradaSchema.data_saida <= data_fim,
            )
        )

        if usuarios_ids:
            query = query.filter(RegistroEntradaSchema.id_usuario.in_(usuarios_ids))

        return query.all()
