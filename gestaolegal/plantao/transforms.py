from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from gestaolegal.models.assistido import Assistido as AssistidoModel
from gestaolegal.models.atendido import Atendido as AtendidoModel
from gestaolegal.plantao.models import (
    AssistidoPessoaJuridica,
    area_atuacao,
    beneficio,
    contribuicao_inss,
    enquadramento,
    escolaridade,
    moradia,
    orgao_reg,
    participacao_renda,
    qual_pessoa_doente,
    regiao_bh,
)
from gestaolegal.usuario.models import sexo_usuario


@dataclass(frozen=True)
class CardInfo:
    title: str
    body: Mapping[str, str | None] | str


def _safe_lookup(
    choices: dict[str, tuple], key: Any, default: str = "Não informado"
) -> str:
    if key is None:
        return default
    return next(
        (
            choice_value[1]
            for choice_value in choices.values()
            if choice_value[0] == key
        ),
        default,
    )


def _format_currency(value: Any) -> str:
    if value is None:
        return "Não informado"
    try:
        return f"R$ {str(value).replace('.', ',')}"
    except (ValueError, AttributeError):
        return "Não informado"


def _format_date(date_obj: Any) -> str:
    if date_obj is None:
        return "Não informado"
    try:
        return date_obj.strftime("%d/%m/%Y")
    except (ValueError, AttributeError):
        return "Não informado"


def _safe_str(value: Any) -> str:
    return str(value) if value is not None else "Não informado"


def _yes_no(condition: bool) -> str:
    return "Sim" if condition else "Não"


def dados_atendimento(atendido: AtendidoModel) -> dict[str, str]:
    return {
        "Nome": _safe_str(atendido.nome),
        "Data de Nascimento": _format_date(atendido.data_nascimento),
        "CPF": _safe_str(atendido.cpf),
        "CNPJ": _safe_str(atendido.cnpj),
        "Celular": _safe_str(atendido.celular),
        "E-mail": _safe_str(atendido.email),
    }


def dados_assistido(assistido: AssistidoModel) -> dict[str, str]:
    return {
        "Sexo": _safe_lookup(sexo_usuario, assistido.sexo),
        "Profissão": _safe_str(assistido.profissao),
        "Raça": _safe_str(assistido.raca),
        "RG": _safe_str(assistido.rg),
        "Grau de Instrução": _safe_lookup(escolaridade, assistido.grau_instrucao),
        "Salário": _format_currency(assistido.salario),
    }


def dados_pj(assistido_pj: AssistidoPessoaJuridica) -> dict[str, str]:
    return {
        "Situação Receita": _safe_str(assistido_pj.situacao_receita),
        "Enquadramento": _safe_lookup(enquadramento, assistido_pj.enquadramento),
        "Área de Atuação": _safe_lookup(area_atuacao, assistido_pj.area_atuacao),
        "Órgão de Registro": _safe_lookup(orgao_reg, assistido_pj.orgao_registro),
        "Faturamento Anual": _format_currency(assistido_pj.faturamento_anual),
    }


def dados_endereco(atendido: AtendidoModel) -> dict[str, str]:
    if not hasattr(atendido, "endereco") or not atendido.endereco:
        return {}

    endereco = atendido.endereco
    cidade_parts = [
        part
        for part in [
            getattr(endereco, "cidade", None),
            getattr(endereco, "estado", None),
        ]
        if part
    ]
    cidade_estado = ", ".join(cidade_parts) if cidade_parts else "Não informado"

    return {
        "Logradouro": _safe_str(endereco.logradouro),
        "Número": _safe_str(endereco.numero),
        "Complemento": _safe_str(endereco.complemento),
        "Bairro": _safe_str(endereco.bairro),
        "CEP": _safe_str(endereco.cep),
        "Cidade": cidade_estado,
    }


def _vehicle_data(assistido: AssistidoModel) -> dict[str, str]:
    if not assistido.possui_veiculos:
        return {}

    return {
        "Veículo": _safe_str(assistido.possui_veiculos_obs),
        "Quantidade de Veículos": _safe_str(assistido.quantos_veiculos),
        "Ano do Veículo": _safe_str(assistido.ano_veiculo),
    }


def _health_data(assistido: AssistidoModel) -> dict[str, str]:
    doenca_map = {"sim": "Sim", "nao": "Não", None: "Não Informou"}
    doenca_resposta = doenca_map.get(assistido.doenca_grave_familia, "Não Informou")

    base_data = {"Há pessoas com doença grave na família?": doenca_resposta}

    if assistido.doenca_grave_familia != "sim":
        return base_data

    return {
        **base_data,
        "Pessoa doente": _safe_lookup(qual_pessoa_doente, assistido.pessoa_doente),
        "Gasto em medicamentos": _format_currency(assistido.gastos_medicacao),
    }


def dados_renda(assistido: AssistidoModel) -> dict[str, str]:
    base_data = {
        "Benefício Social": _safe_lookup(beneficio, assistido.beneficio),
        "Contribui para a previdência social": _safe_lookup(
            contribuicao_inss, assistido.contribui_inss
        ),
        "Quantidade de pessoas que moram na mesma casa": _safe_str(
            assistido.qtd_pessoas_moradia
        ),
        "Renda Familiar": _format_currency(assistido.renda_familiar),
        "Posição em relação à renda familiar": _safe_lookup(
            participacao_renda, assistido.participacao_renda
        ),
        "Residência": _safe_lookup(moradia, assistido.tipo_moradia),
        "Possui outros imóveis": _yes_no(assistido.possui_outros_imoveis),
        "Possui veículos": _yes_no(assistido.possui_veiculos),
    }

    return {
        **base_data,
        **_vehicle_data(assistido),
        **_health_data(assistido),
        "Observações": _safe_str(assistido.obs),
    }


def dados_juridicos(assistido_pj: AssistidoPessoaJuridica) -> dict[str, str]:
    local_sede = (
        _safe_lookup(regiao_bh, assistido_pj.regiao_sede_bh)
        if assistido_pj.sede_bh
        else _safe_str(assistido_pj.regiao_sede_outros)
    )

    balance_map = {"1": "Sim", "0": "Não"}
    result_map = {"sim": "Sim", "nao": "Não"}
    employees_map = {"sim": "Sim", "nao": "Não"}

    base_data = {
        "Enquadramento": _safe_lookup(enquadramento, assistido_pj.enquadramento),
        "Sócios da Pessoa Jurídica": _safe_str(assistido_pj.socios),
        "Situação perante a Receita Federal": _safe_str(assistido_pj.situacao_receita),
        "Sede constituída ou a constituir em Belo Horizonte?": _yes_no(
            assistido_pj.sede_bh
        ),
        "Local da Sede": local_sede,
        "Área de atuação": _safe_lookup(area_atuacao, assistido_pj.area_atuacao),
        "É negócio nascente?": _yes_no(assistido_pj.negocio_nascente),
        "Órgão competente": _safe_lookup(orgao_reg, assistido_pj.orgao_registro),
        "Faturamento anual": _format_currency(assistido_pj.faturamento_anual),
        "O balanço patrimonial do último ano foi negativo?": balance_map.get(
            assistido_pj.ultimo_balanco_neg, "Não se aplica"
        ),
        "O resultado econômico do último ano foi negativo?": result_map.get(
            assistido_pj.resultado_econ_neg, "Não se Aplica"
        ),
        "Tem funcionários?": employees_map.get(
            assistido_pj.tem_funcionarios, "Não se Aplica"
        ),
    }

    funcionarios_data = (
        {"Quantidade de Funcionários": _safe_str(assistido_pj.qtd_funcionarios)}
        if assistido_pj.tem_funcionarios == "sim"
        else {}
    )

    return {**base_data, **funcionarios_data}


def orientacoes(atendido: AtendidoModel) -> dict[str, str] | str:
    if (
        not hasattr(atendido, "orientacoesJuridicas")
        or not atendido.orientacoesJuridicas
    ):
        return "Não há nenhuma orientação jurídica vinculada"

    def format_orientacao(i: int, orientacao: Any) -> tuple[str, str]:
        key = f"Orientação {i}"
        area = (
            orientacao.area_direito.capitalize()
            if orientacao.area_direito
            else "Área não informada"
        )
        data = _format_date(orientacao.data_criacao)
        value = f"{area} - {data}"

        if hasattr(orientacao, "id") and orientacao.id:
            value = f"<a href='/orientacao_juridica/orientacao_juridica/{orientacao.id}' target='_blank'>{value}</a>"

        return key, value

    return dict(
        format_orientacao(i, orientacao)
        for i, orientacao in enumerate(atendido.orientacoesJuridicas, 1)
    )


def casos(
    atendido: AtendidoModel, assistido: AssistidoModel | None
) -> dict[str, str] | str:
    if not hasattr(atendido, "casos") or not atendido.casos or not assistido:
        return "Não há nenhum caso vinculado"

    def format_caso(i: int, caso: Any) -> tuple[str, str]:
        key = f"Caso {i}"
        area = (
            caso.area_direito.capitalize()
            if caso.area_direito
            else "Área não informada"
        )

        value = area
        if hasattr(caso, "sub_area") and caso.sub_area:
            value += f" - {caso.sub_area.capitalize()}"

        if hasattr(caso, "id") and caso.id:
            value = f"<a href='/casos/visualizar/{caso.id}' target='_blank'>{value}</a>"

        return key, value

    return dict(format_caso(i, caso) for i, caso in enumerate(atendido.casos, 1))


def build_cards(
    atendido: AtendidoModel,
    assistido: AssistidoModel | None,
    assistido_pj: AssistidoPessoaJuridica | None = None,
) -> list[CardInfo]:
    base_cards = [
        CardInfo("Dados de Atendimento", dados_atendimento(atendido)),
        CardInfo("Endereço", dados_endereco(atendido)),
        CardInfo("Orientações Jurídicas", orientacoes(atendido)),
    ]

    assistido_cards = (
        [
            CardInfo("Dados de Assistido", dados_assistido(assistido)),
            CardInfo("Casos Vinculados", casos(atendido, assistido)),
            CardInfo("Renda e Patrimônio", dados_renda(assistido)),
        ]
        if assistido
        else []
    )

    pj_cards = (
        [
            CardInfo("Dados PJ", dados_pj(assistido_pj)),
            CardInfo("Dados Jurídicos", dados_juridicos(assistido_pj)),
        ]
        if assistido_pj
        else []
    )

    return [*base_cards, *assistido_cards, *pj_cards]
