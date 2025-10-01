from gestaolegal.models.user import User
from gestaolegal.repositories.base_repository import (
    BaseRepository,
    PageParams,
    WhereConditions,
)
from gestaolegal.schemas.user import UserSchema


class UserRepository(BaseRepository[UserSchema, User]):
    def __init__(self):
        super().__init__(UserSchema, User)

    def search_by_name(self, string: str, page_params: PageParams | None = None):
        return self.get(
            page_params=page_params,
            order_by=["nome"],
            where_conditions=[("nome", "ilike", f"%{string}%")],
        )

    def search(
        self,
        valor_busca: str = "",
        funcao: str = "all",
        status: str = "1",
        page_params: PageParams | None = None,
    ):
        where_conditions: WhereConditions = []

        if funcao != "all":
            where_conditions.append(("urole", "eq", funcao))

        if valor_busca:
            where_conditions.append(("nome", "ilike", f"%{valor_busca}%"))

        return self.get(
            page_params=page_params,
            order_by=["nome"],
            where_conditions=where_conditions if where_conditions else None,
            active_only=(status == "1"),
        )

    def search_general(self, busca: str, page_params: PageParams | None = None):
        where_conditions: WhereConditions = [
            ("nome", "contains", busca),
            ("cpf", "contains", busca),
        ]

        return self.get(
            page_params=page_params,
            order_by=["nome"],
            where_conditions=where_conditions,
        )
