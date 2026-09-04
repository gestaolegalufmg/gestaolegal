from gestaolegal.models.base_model import BaseModel


class UnidadeCreateInput(BaseModel):
    nome: str
    sigla: str
    ativa: bool = True


class UnidadeUpdateInput(BaseModel):
    nome: str | None = None
    sigla: str | None = None
    ativa: bool | None = None
