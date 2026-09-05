from dataclasses import dataclass
from datetime import datetime


@dataclass
class Arquivo:
    """Arquivo geral (documentos da organização), como na v2."""

    titulo: str
    nome: str
    descricao: str | None = None
    # Referência relativa à categoria "arquivos" da raiz privada. Nulo em
    # registros herdados da v2, que o migrador (f10-f12) preenche; enquanto
    # for nulo, o download responde 404 tratado.
    caminho: str | None = None
    data_criacao: datetime | None = None
    id_criado_por: int | None = None
    id: int | None = None
