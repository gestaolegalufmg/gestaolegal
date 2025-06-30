from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from gestaolegal.models.atendido import Atendido
from gestaolegal.models.endereco import Endereco
from gestaolegal.plantao.forms.cadastro_atendido_form import CadastroAtendidoForm
from gestaolegal.plantao.forms.tornar_assistido_form import TornarAssistidoForm
from gestaolegal.plantao.models import (
    Assistido,
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
from gestaolegal.usuario.forms import EnderecoForm
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


def dados_atendimento(atendido: Atendido) -> dict[str, str]:
    return {
        "Nome": _safe_str(atendido.nome),
        "Data de Nascimento": _format_date(atendido.data_nascimento),
        "CPF": _safe_str(atendido.cpf),
        "CNPJ": _safe_str(atendido.cnpj),
        "Celular": _safe_str(atendido.celular),
        "E-mail": _safe_str(atendido.email),
    }


def dados_assistido(assistido: Assistido) -> dict[str, str]:
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


def dados_endereco(atendido: Atendido) -> dict[str, str]:
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


def _vehicle_data(assistido: Assistido) -> dict[str, str]:
    if not assistido.possui_veiculos:
        return {}

    return {
        "Veículo": _safe_str(assistido.possui_veiculos_obs),
        "Quantidade de Veículos": _safe_str(assistido.quantos_veiculos),
        "Ano do Veículo": _safe_str(assistido.ano_veiculo),
    }


def _health_data(assistido: Assistido) -> dict[str, str]:
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


def dados_renda(assistido: Assistido) -> dict[str, str]:
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


def orientacoes(atendido: Atendido) -> dict[str, str] | str:
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
            value = f"<a href='/plantao/orientacao_juridica/{orientacao.id}' target='_blank'>{value}</a>"

        return key, value

    return dict(
        format_orientacao(i, orientacao)
        for i, orientacao in enumerate(atendido.orientacoesJuridicas, 1)
    )


def casos(atendido: Atendido, assistido: Assistido | None) -> dict[str, str] | str:
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
    atendido: Atendido,
    assistido: Assistido | None,
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


def build_address_from_form_data(form: EnderecoForm) -> Endereco:
    return Endereco(
        logradouro=form.logradouro.data,
        numero=form.numero.data,
        complemento=form.complemento.data,
        bairro=form.bairro.data,
        cep=form.cep.data,
        cidade=form.cidade.data,
        estado=form.estado.data,
    )


def build_atendido_from_form_data(
    form: CadastroAtendidoForm, endereco: Endereco
) -> Atendido:
    atendido = Atendido(
        nome=form.nome.data,
        data_nascimento=form.data_nascimento.data,
        cpf=form.cpf.data,
        cnpj=form.cnpj.data,
        telefone=form.telefone.data,
        celular=form.celular.data,
        email=form.email.data,
        estado_civil=form.estado_civil.data,
        como_conheceu=form.como_conheceu.data,
        indicacao_orgao=form.indicacao_orgao.data,
        procurou_outro_local=form.procurou_outro_local.data,
        procurou_qual_local=form.procurou_qual_local.data,
        obs=form.obs_atendido.data,
        endereco_id=endereco.id,
        pj_constituida=form.pj_constituida.data,
        repres_legal=form.repres_legal.data,
        nome_repres_legal=form.nome_repres_legal.data,
        cpf_repres_legal=form.cpf_repres_legal.data,
        contato_repres_legal=form.contato_repres_legal.data,
        rg_repres_legal=form.rg_repres_legal.data,
        nascimento_repres_legal=form.nascimento_repres_legal.data,
        pretende_constituir_pj=form.pretende_constituir_pj.data,
        status=1,
    )

    atendido.setIndicacao_orgao(form.indicacao_orgao.data, atendido.como_conheceu)

    atendido.setCnpj(atendido.pj_constituida, form.cnpj.data, form.repres_legal.data)

    atendido.setRepres_legal(
        atendido.repres_legal,
        atendido.pj_constituida,
        form.nome_repres_legal.data,
        form.cpf_repres_legal.data,
        form.contato_repres_legal.data,
        form.rg_repres_legal.data,
        form.nascimento_repres_legal.data,
    )

    atendido.setProcurou_qual_local(
        atendido.procurou_outro_local, form.procurou_qual_local.data
    )

    return atendido


def update_atendido_from_form_data(form: CadastroAtendidoForm, atendido: Atendido):
    atendido.nome = form.nome.data
    atendido.data_nascimento = form.data_nascimento.data
    atendido.cpf = form.cpf.data
    atendido.cnpj = form.cnpj.data
    atendido.telefone = form.telefone.data
    atendido.celular = form.celular.data
    atendido.email = form.email.data
    atendido.estado_civil = form.estado_civil.data
    atendido.como_conheceu = form.como_conheceu.data
    atendido.indicacao_orgao = form.indicacao_orgao.data
    atendido.procurou_outro_local = form.procurou_outro_local.data
    atendido.procurou_qual_local = form.procurou_qual_local.data
    atendido.obs = form.obs_atendido.data
    atendido.pj_constituida = form.pj_constituida.data
    atendido.repres_legal = form.repres_legal.data
    atendido.nome_repres_legal = form.nome_repres_legal.data
    atendido.cpf_repres_legal = form.cpf_repres_legal.data
    atendido.contato_repres_legal = form.contato_repres_legal.data
    atendido.rg_repres_legal = form.rg_repres_legal.data
    atendido.nascimento_repres_legal = form.nascimento_repres_legal.data
    atendido.pretende_constituir_pj = form.pretende_constituir_pj.data

    if not atendido.endereco:
        raise Exception()

    atendido.endereco.logradouro = form.logradouro.data
    atendido.endereco.numero = form.numero.data
    atendido.endereco.complemento = form.complemento.data
    atendido.endereco.bairro = form.bairro.data
    atendido.endereco.cep = form.cep.data
    atendido.endereco.cidade = form.cidade.data
    atendido.endereco.estado = form.estado.data

    return atendido


def build_assistido_from_form_data(
    form: TornarAssistidoForm, atendido: Atendido
) -> Assistido:
    return Assistido(
        id_atendido=atendido.id,
        sexo=form.sexo.data,
        raca=form.raca.data,
        profissao=form.profissao.data,
        rg=form.rg.data,
        grau_instrucao=form.grau_instrucao.data,
        salario=form.salario.data,
        beneficio=form.qual_beneficio.data,
        contribui_inss=form.contribui_inss.data,
        qtd_pessoas_moradia=form.qtd_pessoas_moradia.data,
        renda_familiar=form.renda_familiar.data,
        participacao_renda=form.participacao_renda.data,
        tipo_moradia=form.tipo_moradia.data,
        possui_outros_imoveis=bool(form.possui_outros_imoveis.data),
        quantos_imoveis=form.quantos_imoveis.data,
        possui_veiculos=bool(form.possui_veiculos.data),
        possui_veiculos_obs=form.possui_veiculos_obs.data,
        quantos_veiculos=form.quantos_veiculos.data,
        ano_veiculo=form.ano_veiculo.data,
        doenca_grave_familia=form.doenca_grave_familia.data,
        pessoa_doente=form.pessoa_doente.data,
        pessoa_doente_obs=form.pessoa_doente_obs.data,
        gastos_medicacao=form.gastos_medicacao.data,
        obs=form.obs_assistido.data,
        # area_direito=form.area_direito.data,
        # observacoes=form.observacoes.data,
    )


def update_assistido_from_form_data(
    atendido: Atendido,
    assistido: Assistido,
    form_atendido: CadastroAtendidoForm,
    form_assistido: TornarAssistidoForm,
) -> tuple[Atendido, Assistido]:
    atendido = assistido.atendido
    atendido.nome = form_atendido.nome.data
    atendido.data_nascimento = form_atendido.data_nascimento.data
    atendido.cpf = form_atendido.cpf.data
    atendido.cnpj = form_atendido.cnpj.data
    atendido.telefone = form_atendido.telefone.data
    atendido.celular = form_atendido.celular.data
    atendido.email = form_atendido.email.data
    atendido.estado_civil = form_atendido.estado_civil.data
    atendido.como_conheceu = form_atendido.como_conheceu.data
    atendido.indicacao_orgao = form_atendido.indicacao_orgao.data
    atendido.procurou_outro_local = form_atendido.procurou_outro_local.data
    atendido.procurou_qual_local = form_atendido.procurou_qual_local.data
    atendido.obs = form_atendido.obs_atendido.data
    atendido.pj_constituida = form_atendido.pj_constituida.data
    atendido.repres_legal = form_atendido.repres_legal.data
    atendido.nome_repres_legal = form_atendido.nome_repres_legal.data
    atendido.cpf_repres_legal = form_atendido.cpf_repres_legal.data
    atendido.contato_repres_legal = form_atendido.contato_repres_legal.data
    atendido.rg_repres_legal = form_atendido.rg_repres_legal.data
    atendido.nascimento_repres_legal = form_atendido.nascimento_repres_legal.data
    atendido.pretende_constituir_pj = form_atendido.pretende_constituir_pj.data

    atendido.endereco.logradouro = form_atendido.logradouro.data
    atendido.endereco.numero = form_atendido.numero.data
    atendido.endereco.complemento = form_atendido.complemento.data
    atendido.endereco.bairro = form_atendido.bairro.data
    atendido.endereco.cep = form_atendido.cep.data
    atendido.endereco.cidade = form_atendido.cidade.data
    atendido.endereco.estado = form_atendido.estado.data

    assistido.sexo = form_assistido.sexo.data
    assistido.profissao = form_assistido.profissao.data
    assistido.raca = form_assistido.raca.data
    assistido.rg = form_assistido.rg.data
    assistido.grau_instrucao = form_assistido.grau_instrucao.data
    assistido.salario = form_assistido.salario.data
    assistido.beneficio = form_assistido.beneficio.data
    assistido.qual_beneficio = form_assistido.qual_beneficio.data
    assistido.contribui_inss = form_assistido.contribui_inss.data
    assistido.qtd_pessoas_moradia = form_assistido.qtd_pessoas_moradia.data
    assistido.renda_familiar = form_assistido.renda_familiar.data
    assistido.participacao_renda = form_assistido.participacao_renda.data
    assistido.tipo_moradia = form_assistido.tipo_moradia.data
    assistido.possui_outros_imoveis = (
        form_assistido.possui_outros_imoveis.data == "True"
    )
    assistido.quantos_imoveis = form_assistido.quantos_imoveis.data
    assistido.possui_veiculos = form_assistido.possui_veiculos.data == "True"
    assistido.doenca_grave_familia = form_assistido.doenca_grave_familia.data
    assistido.obs = form_assistido.obs_assistido.data

    # Set conditional fields
    atendido.setIndicacao_orgao(
        form_atendido.indicacao_orgao.data, atendido.como_conheceu
    )
    atendido.setCnpj(
        atendido.pj_constituida,
        form_atendido.cnpj.data,
        form_atendido.repres_legal.data,
    )
    atendido.setRepres_legal(
        atendido.repres_legal,
        atendido.pj_constituida,
        form_atendido.nome_repres_legal.data,
        form_atendido.cpf_repres_legal.data,
        form_atendido.contato_repres_legal.data,
        form_atendido.rg_repres_legal.data,
        form_atendido.nascimento_repres_legal.data,
    )
    atendido.setProcurou_qual_local(
        atendido.procurou_outro_local, form_atendido.procurou_qual_local.data
    )

    assistido.setCamposVeiculo(
        assistido.possui_veiculos,
        form_assistido.possui_veiculos_obs.data,
        form_assistido.quantos_veiculos.data,
        form_assistido.ano_veiculo.data,
    )
    assistido.setCamposDoenca(
        assistido.doenca_grave_familia,
        form_assistido.pessoa_doente.data,
        form_assistido.pessoa_doente_obs.data,
        form_assistido.gastos_medicacao.data,
    )

    return atendido, assistido
