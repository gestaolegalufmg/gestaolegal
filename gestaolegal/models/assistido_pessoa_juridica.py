from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.assistido import Assistido


@dataclass
class AssistidoPessoaJuridica:
    id_assistido: int
    assistido: "Assistido"
    situacao_receita: str
    enquadramento: str
    sede_bh: bool
    area_atuacao: str
    negocio_nascente: bool
    orgao_registro: str
    faturamento_anual: float
    tem_funcionarios: str

    id: int | None = None
    socios: str | None = None
    regiao_sede_bh: str | None = None
    regiao_sede_outros: str | None = None
    ultimo_balanco_neg: str | None = None
    resultado_econ_neg: str | None = None
    qtd_funcionarios: str | None = None
