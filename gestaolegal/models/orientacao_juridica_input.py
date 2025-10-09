from gestaolegal.models.base_model import BaseModel


class OrientacaoJuridicaCreate(BaseModel):
    area_direito: str
    sub_area: str | None = None
    descricao: str
    atendidos_ids: list[int] = []


class OrientacaoJuridicaUpdate(BaseModel):
    area_direito: str | None = None
    sub_area: str | None = None
    descricao: str | None = None
    atendidos_ids: list[int] | None = None
