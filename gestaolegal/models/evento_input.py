from datetime import date
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    pass


# O anexo não é campo de entrada: quem grava o arquivo e escreve a referência
# em `eventos.arquivo` é o `EventoService`, a partir do `FileStorage` do
# multipart. Aceitar a string aqui deixaria o cliente gravar um caminho
# arbitrário na coluna.
class EventoCreateInput(BaseModel):
    id_caso: int | None = None
    num_evento: int | None = None
    tipo: str
    descricao: str | None = None
    data_evento: date
    id_usuario_responsavel: int | None = None
    status: bool = True


class EventoUpdateInput(BaseModel):
    id_caso: int | None = None
    num_evento: int | None = None
    tipo: str | None = None
    descricao: str | None = None
    data_evento: date | None = None
    id_usuario_responsavel: int | None = None
    status: bool | None = None
