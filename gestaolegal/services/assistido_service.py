import logging
from typing import Optional

from gestaolegal.models.assistido import Assistido
from gestaolegal.schemas.assistido import AssistidoSchema
from gestaolegal.schemas.assistido_pessoa_juridica import AssistidoPessoaJuridicaSchema
from gestaolegal.services.base_service import BaseService

logger = logging.getLogger(__name__)


class AssistidoService(BaseService[AssistidoSchema, Assistido]):
    def __init__(self):
        super().__init__(AssistidoSchema)

    def _to_model(self, schema_instance: AssistidoSchema) -> Assistido:
        return Assistido.from_sqlalchemy(schema_instance)

    def find_by_atendido_id(self, atendido_id: int) -> Optional[Assistido]:
        result = (
            self.session.query(AssistidoSchema)
            .filter(AssistidoSchema.id_atendido == atendido_id)
            .first()
        )
        return self._to_model(result) if result else None

    def get_by_atendido_ids(self, atendido_ids: list[int]) -> list[Assistido]:
        results = (
            self.filter_active(self.session.query(AssistidoSchema))
            .filter(AssistidoSchema.id_atendido.in_(atendido_ids))
            .all()
        )
        return [self._to_model(result) for result in results]

    def get_with_pessoa_juridica(
        self, assistido_id: int
    ) -> tuple[Assistido, Optional[AssistidoPessoaJuridicaSchema]]:
        result = (
            self.session.query(AssistidoSchema, AssistidoPessoaJuridicaSchema)
            .outerjoin(
                AssistidoPessoaJuridicaSchema,
                AssistidoPessoaJuridicaSchema.id_assistido == AssistidoSchema.id,
            )
            .filter(AssistidoSchema.id == assistido_id)
            .first()
        )

        if not result:
            raise ValueError(f"Assistido with id {assistido_id} not found")

        assistido = self._to_model(result[0]) if result[0] else None
        pessoa_juridica = result[1] if result[1] else None

        return assistido, pessoa_juridica
