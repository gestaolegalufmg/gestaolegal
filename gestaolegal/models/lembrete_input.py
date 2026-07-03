from datetime import datetime

from gestaolegal.models.base_model import BaseModel


class LembreteCreateInput(BaseModel):
    id_usuario: int
    data_lembrete: datetime
    descricao: str


class LembreteUpdateInput(BaseModel):
    id_usuario: int | None = None
    data_lembrete: datetime | None = None
    descricao: str | None = None
