from sqlalchemy import desc

from gestaolegal.models.evento import Evento
from gestaolegal.repositories.base_repository import BaseRepository, ConditionList, PageParams
from gestaolegal.schemas.evento import EventoSchema


class EventoRepository(BaseRepository[EventoSchema, Evento]):
    def __init__(self):
        super().__init__(EventoSchema, Evento)

    def get_next_event_number(self, caso_id: int) -> int:
        num_eventos_criados = (
            self.session.query(EventoSchema.num_evento)
            .filter(EventoSchema.id_caso == caso_id)
            .order_by(desc(EventoSchema.num_evento))
            .first()
        )
        return num_eventos_criados[0] + 1 if num_eventos_criados else 1

    def get_eventos_by_caso_with_filter(
        self, caso_id: int, opcao_filtro: str, page_params: PageParams
    ):
        where_conditions: ConditionList = [("id_caso", "eq", caso_id)]

        if opcao_filtro != "todos":
            where_conditions.append(("tipo", "eq", opcao_filtro))

        return self.get(
            page_params=page_params,
            where_conditions=where_conditions,
            order_by=["data_criacao"],
            order_desc=True,
        )

    def get_evento_by_numero(self, num_evento: int, caso_id: int) -> Evento | None:
        where_conditions: ConditionList = [
            ("num_evento", "eq", num_evento),
            ("id_caso", "eq", caso_id)
        ]
        return self.find(where_conditions=where_conditions)
