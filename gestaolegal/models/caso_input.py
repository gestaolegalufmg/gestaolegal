from gestaolegal.models.base_model import BaseModel


class CasoCreateInput(BaseModel):
    id_usuario_responsavel: int
    area_direito: str
    sub_area: str | None = None
    id_orientador: int | None = None
    id_estagiario: int | None = None
    id_colaborador: int | None = None
    situacao_deferimento: str
    justif_indeferimento: str | None = None
    descricao: str | None = None
    ids_clientes: list[int] = []


class CasoUpdateInput(BaseModel):
    id_usuario_responsavel: int | None = None
    area_direito: str | None = None
    sub_area: str | None = None
    id_orientador: int | None = None
    id_estagiario: int | None = None
    id_colaborador: int | None = None
    situacao_deferimento: str | None = None
    justif_indeferimento: str | None = None
    descricao: str | None = None
    ids_clientes: list[int] | None = None
