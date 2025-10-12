from gestaolegal.models.base_model import BaseModel


class ArquivoCasoCreateInput(BaseModel):
    id_caso: int
    link_arquivo: str
