from dataclasses import dataclass
from gestaolegal.models.assistido import Assistido

@dataclass(frozen=True)
class AssistidoPessoaJuridica:
    id: int | None
    id_assistido: int
    assistido: "Assistido"
    socios: str | None
    situacao_receita: str
    enquadramento: str
    sede_bh: bool
    regiao_sede_bh: str | None
    regiao_sede_outros: str | None
    area_atuacao: str
    negocio_nascente: bool
    orgao_registro: str
    faturamento_anual: float
    ultimo_balanco_neg: str | None
    resultado_econ_neg: str | None
    tem_funcionarios: str
    qtd_funcionarios: str | None

    def __post_init__(self):
        return
