from dataclasses import dataclass
from datetime import datetime


@dataclass
class Arquivo:
    """Arquivo geral (documentos da organização), como na v2."""

    titulo: str
    nome: str
    descricao: str | None = None
    # Nulos em registros herdados da v2 (arquivo em ARQUIVOS_DIR/nome).
    caminho: str | None = None
    data_criacao: datetime | None = None
    id_criado_por: int | None = None
    id: int | None = None
