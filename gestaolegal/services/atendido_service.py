from typing import Any, Callable, Literal, Optional, TypedDict, TypeVar

from gestaolegal.models.atendido import Atendido
from gestaolegal.schemas.assistido import AssistidoSchema
from gestaolegal.schemas.assistido_pessoa_juridica import AssistidoPessoaJuridicaSchema
from gestaolegal.schemas.atendido import AtendidoSchema
from gestaolegal.services.assistido_service import AssistidoService
from gestaolegal.services.base_service import BaseService
from gestaolegal.services.endereco_service import EnderecoService

T = TypeVar("T")


class PageParams(TypedDict):
    page: int
    per_page: int


class AtendidoService(BaseService[AtendidoSchema, Atendido]):
    def __init__(self):
        super().__init__(AtendidoSchema)
        self.endereco_service = EnderecoService()
        self.assistido_service = AssistidoService()

    def _to_model(self, schema_instance: AtendidoSchema) -> Atendido:
        return Atendido.from_sqlalchemy(schema_instance)

    def find_by_email(self, email: str) -> Optional[Atendido]:
        return self.find_by_field("email", email)

    def get_atendido_with_assistido_data(
        self, atendido_id: int
    ) -> Optional[
        tuple[
            Atendido, Optional[AssistidoSchema], Optional[AssistidoPessoaJuridicaSchema]
        ]
    ]:
        result = (
            self.session.query(
                AtendidoSchema, AssistidoSchema, AssistidoPessoaJuridicaSchema
            )
            .outerjoin(
                AssistidoSchema, AssistidoSchema.id_atendido == AtendidoSchema.id
            )
            .outerjoin(
                AssistidoPessoaJuridicaSchema,
                AssistidoPessoaJuridicaSchema.id_assistido == AssistidoSchema.id,
            )
            .filter(AtendidoSchema.id == atendido_id)
            .first()
        )

        if not result:
            return None

        atendido_model = self._to_model(result[0]) if result[0] else None
        assistido_model = result[1] if result[1] else None
        assistido_pj = result[2] if result[2] else None

        return atendido_model, assistido_model, assistido_pj

    def create_with_endereco(
        self, atendido_data: dict, endereco_data: dict
    ) -> Atendido:
        endereco = self.endereco_service.create(endereco_data)

        atendido_data["endereco_id"] = endereco.id
        atendido_data["status"] = 1

        return self.create(atendido_data)

    def update_with_endereco(
        self, atendido_id: int, atendido_data: dict, endereco_data: dict
    ) -> Atendido:
        atendido = self.ensure_exists(atendido_id)

        if atendido.endereco_id:
            self.endereco_service.update(atendido.endereco_id, endereco_data)
        else:
            endereco = self.endereco_service.create(endereco_data)
            atendido_data["endereco_id"] = endereco.id

        return self.update(atendido_id, atendido_data)

    def validate_email_uniqueness(
        self, email: str, exclude_id: Optional[int] = None
    ) -> tuple[bool, str]:
        existing_atendido = self.find_by_email(email)
        if existing_atendido and (
            exclude_id is None or existing_atendido.id != exclude_id
        ):
            return False, "Email já cadastrado no sistema"
        return True, ""

    def get_search_results_with_pagination(
        self,
        valor_busca: str,
        tipo_busca: str,
        paginator: Callable[..., Any] | None = None,
    ):
        search_type = tipo_busca if tipo_busca in ["atendidos", "assistidos"] else None
        return self.search_with_assistido_status_paginated(
            valor_busca, search_type, paginator
        )

    def search_with_assistido_status_paginated(
        self,
        search_term: str = "",
        search_type: Literal["atendidos", "assistidos"] | None = None,
        paginator: Callable[..., Any] | None = None,
    ):
        """Search with assistido status using new pagination system

        Args:
            search_term: Search term to filter by name, CPF, or CNPJ
            search_type: Filter by type ('atendidos', 'assistidos', or None for all)
            paginator: Optional pagination function

        Returns:
            Paginated results or list of tuples (Atendido, AssistidoSchema)
        """
        # Build the query
        query = self.session.query(AtendidoSchema, AssistidoSchema).outerjoin(
            AssistidoSchema, AssistidoSchema.id_atendido == AtendidoSchema.id
        )

        # Apply search filter
        if search_term:
            query = query.filter(
                AtendidoSchema.nome.ilike(f"%{search_term}%")
                | AtendidoSchema.cpf.ilike(f"%{search_term}%")
                | AtendidoSchema.cnpj.ilike(f"%{search_term}%")
            )

        # Apply type filter
        if search_type == "assistidos":
            query = query.filter(AssistidoSchema.id.isnot(None))
        elif search_type == "atendidos":
            query = query.filter(AssistidoSchema.id.is_(None))

        # Apply active filter and ordering
        query = self.filter_active(query)
        query = query.order_by(AtendidoSchema.nome)

        # Apply pagination if provided
        if paginator:
            result = paginator(query)
            if hasattr(result, "items"):
                # Convert the items to our model format
                result.items = [
                    (
                        self._to_model(atendido),
                        assistido if assistido else None,
                    )
                    for atendido, assistido in result.items
                ]
                return result
            else:
                # Handle case where paginator returns list directly
                return [
                    (
                        self._to_model(atendido),
                        assistido if assistido else None,
                    )
                    for atendido, assistido in result
                ]

        # Return all results if no pagination
        results = query.all()
        return [
            (
                self._to_model(atendido),
                assistido if assistido else None,
            )
            for atendido, assistido in results
        ]

    def search_with_assistido_status(
        self,
        search_term: str,
        search_type: Literal["atendidos", "assistidos"] | None = None,
        page_params: Optional[dict] = None,
    ) -> list[tuple[Atendido, Optional[AssistidoSchema]]]:
        query = self.session.query(AtendidoSchema, AssistidoSchema).outerjoin(
            AssistidoSchema, AssistidoSchema.id_atendido == AtendidoSchema.id
        )

        if search_term:
            query = query.filter(
                AtendidoSchema.nome.ilike(f"%{search_term}%")
                | AtendidoSchema.cpf.ilike(f"%{search_term}%")
                | AtendidoSchema.cnpj.ilike(f"%{search_term}%")
            )

        if search_type == "assistidos":
            query = query.filter(AssistidoSchema.id.isnot(None))
        elif search_type == "atendidos":
            query = query.filter(AssistidoSchema.id.is_(None))

        query = self.filter_active(query)
        query = query.order_by(AtendidoSchema.nome)

        if page_params:
            query = query.offset(page_params["page"] * page_params["per_page"]).limit(
                page_params["per_page"]
            )

        results = query.all()
        return [
            (
                self._to_model(atendido),
                assistido if assistido else None,
            )
            for atendido, assistido in results
        ]

    def get_paginated_search_results(
        self, termo: str, page: int, per_page: int, paginator_func
    ):
        query = self.session.query(AtendidoSchema, AssistidoSchema).outerjoin(
            AssistidoSchema, AssistidoSchema.id_atendido == AtendidoSchema.id
        )

        if termo:
            query = query.filter(
                AtendidoSchema.nome.ilike(f"%{termo}%")
                | AtendidoSchema.cpf.ilike(f"%{termo}%")
                | AtendidoSchema.cnpj.ilike(f"%{termo}%")
            )

        query = query.order_by(AtendidoSchema.nome)
        return paginator_func(query)

    def ensure_atendido_assistido_exists(
        self, atendido_id: int
    ) -> tuple[Atendido, AssistidoSchema]:
        atendido = self.ensure_exists(atendido_id)
        assistido = self.assistido_service.find_by_atendido_id(atendido_id)

        if not assistido:
            raise ValueError("Assistido não encontrado para este atendido")

        return atendido, assistido
