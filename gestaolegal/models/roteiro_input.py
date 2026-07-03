from gestaolegal.models.base_model import BaseModel


class RoteiroUpsertInput(BaseModel):
    area_direito: str
    link: str | None = None
