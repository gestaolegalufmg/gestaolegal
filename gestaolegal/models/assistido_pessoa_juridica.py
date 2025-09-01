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
        assistido_pessoa_juridica: "AssistidoPessoaJuridicaSchema",
    ) -> "AssistidoPessoaJuridica":
        return AssistidoPessoaJuridica(
            id=assistido_pessoa_juridica.id,
            id_assistido=assistido_pessoa_juridica.id_assistido,
            assistido=assistido_pessoa_juridica.assistido,
            socios=assistido_pessoa_juridica.socios,
            situacao_receita=assistido_pessoa_juridica.situacao_receita,
            enquadramento=assistido_pessoa_juridica.enquadramento,
            sede_bh=assistido_pessoa_juridica.sede_bh,
            regiao_sede_bh=assistido_pessoa_juridica.regiao_sede_bh,
            regiao_sede_outros=assistido_pessoa_juridica.regiao_sede_outros,
            area_atuacao=assistido_pessoa_juridica.area_atuacao,
            negocio_nascente=assistido_pessoa_juridica.negocio_nascente,
            orgao_registro=assistido_pessoa_juridica.orgao_registro,
            faturamento_anual=assistido_pessoa_juridica.faturamento_anual,
            ultimo_balanco_neg=assistido_pessoa_juridica.ultimo_balanco_neg,
            resultado_econ_neg=assistido_pessoa_juridica.resultado_econ_neg,
            tem_funcionarios=assistido_pessoa_juridica.tem_funcionarios,
            qtd_funcionarios=assistido_pessoa_juridica.qtd_funcionarios,
        )
