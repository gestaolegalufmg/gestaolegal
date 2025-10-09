from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    from gestaolegal.models.assistido import Assistido


class AssistidoPessoaJuridica(BaseModel):
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
