from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.schemas.assistido import AssistidoSchema
    from gestaolegal.schemas.assistido_pessoa_juridica import (
        AssistidoPessoaJuridicaSchema,
    )


@dataclass(frozen=True)
class AssistidoPessoaJuridica:
    id: int | None
    id_assistido: int
    assistido: "AssistidoSchema"
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

    @staticmethod
    def from_sqlalchemy(
        assistido_pessoa_juridica_schema: "AssistidoPessoaJuridicaSchema",
    ) -> "AssistidoPessoaJuridica":
        assistido_pessoa_juridica_items = assistido_pessoa_juridica_schema.to_dict()
        return AssistidoPessoaJuridica(**assistido_pessoa_juridica_items)
