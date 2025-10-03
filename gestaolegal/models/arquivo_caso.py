from dataclasses import dataclass

from gestaolegal.models.base_model import BaseModel


@dataclass(frozen=True)
class ArquivoCaso(BaseModel):
    id: int
    link_arquivo: str | None
    id_caso: int

    def __post_init__(self):
        return
