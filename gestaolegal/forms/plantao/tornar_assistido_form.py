from typing import Any

from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, TextAreaField
from wtforms.validators import (
    AnyOf,
    InputRequired,
    Length,
    NumberRange,
    Optional,
)

from gestaolegal.common.constants import (
    FIELD_LIMITS,
    beneficio,
    contribuicao_inss,
    escolaridade,
    moradia,
    participacao_renda,
    qual_pessoa_doente,
    raca_cor,
    sexo_usuario,
)
from gestaolegal.forms.plantao import (
    MSG_NaoPodeEstarEmBranco,
    MSG_SelecioneUmaOpcaoLista,
)
from gestaolegal.forms.plantao.base_form_mixin import BaseFormMixin
from gestaolegal.utils.forms import MyFloatField, RequiredIf


class TornarAssistidoForm(FlaskForm, BaseFormMixin):
    sexo = SelectField(
        "Sexo/Gênero",
        choices=[
            (sexo_usuario["MASCULINO"][0], sexo_usuario["MASCULINO"][1]),
            (sexo_usuario["FEMININO"][0], sexo_usuario["FEMININO"][1]),
            (sexo_usuario["OUTROS"][0], sexo_usuario["OUTROS"][1]),
        ],
        validators=[
            InputRequired(),
            AnyOf(
                [sexo_usuario[key][0] for key in sexo_usuario],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    profissao = StringField(
        "Profissão",
        validators=[
            InputRequired(),
            Length(
                max=FIELD_LIMITS["profissao"],
                message=f"Por favor, use no máximo {FIELD_LIMITS['profissao']} caracteres para descrever a profissão.",
            ),
        ],
    )

    raca = SelectField(
        "Raça/Cor (autodeclaração)",
        choices=[
            (raca_cor["INDIGENA"][0], raca_cor["INDIGENA"][1]),
            (raca_cor["PRETA"][0], raca_cor["PRETA"][1]),
            (raca_cor["PARDA"][0], raca_cor["PARDA"][1]),
            (raca_cor["AMARELA"][0], raca_cor["AMARELA"][1]),
            (raca_cor["BRANCA"][0], raca_cor["BRANCA"][1]),
            (raca_cor["NAO_DECLARADO"][0], raca_cor["NAO_DECLARADO"][1]),
        ],
        validators=[
            InputRequired(),
            AnyOf(
                [raca_cor[key][0] for key in raca_cor],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    rg = StringField(
        "RG",
        validators=[
            InputRequired(),
            Length(
                max=FIELD_LIMITS["rg"],
                message=f"Por favor, use no máximo {FIELD_LIMITS['rg']} caracteres para o RG.",
            ),
        ],
    )

    # Individual person fields
    grau_instrucao = SelectField(
        "Grau de instrução",
        choices=[
            (escolaridade["NAO_FREQUENTOU"][0], escolaridade["NAO_FREQUENTOU"][1]),
            (escolaridade["INFANTIL_INC"][0], escolaridade["INFANTIL_INC"][1]),
            (escolaridade["INFANTIL_COMP"][0], escolaridade["INFANTIL_COMP"][1]),
            (escolaridade["FUNDAMENTAL1_INC"][0], escolaridade["FUNDAMENTAL1_INC"][1]),
            (
                escolaridade["FUNDAMENTAL1_COMP"][0],
                escolaridade["FUNDAMENTAL1_COMP"][1],
            ),
            (escolaridade["FUNDAMENTAL2_INC"][0], escolaridade["FUNDAMENTAL2_INC"][1]),
            (
                escolaridade["FUNDAMENTAL2_COMP"][0],
                escolaridade["FUNDAMENTAL2_COMP"][1],
            ),
            (escolaridade["MEDIO_INC"][0], escolaridade["MEDIO_INC"][1]),
            (escolaridade["MEDIO_COMP"][0], escolaridade["MEDIO_COMP"][1]),
            (escolaridade["TECNICO_INC"][0], escolaridade["TECNICO_INC"][1]),
            (escolaridade["TECNICO_COMP"][0], escolaridade["TECNICO_COMP"][1]),
            (escolaridade["SUPERIOR_INC"][0], escolaridade["SUPERIOR_INC"][1]),
            (escolaridade["SUPERIOR_COMP"][0], escolaridade["SUPERIOR_COMP"][1]),
            (escolaridade["NAO_INFORMADO"][0], escolaridade["NAO_INFORMADO"][1]),
        ],
        validators=[
            InputRequired(),
            AnyOf(
                [escolaridade[key][0] for key in escolaridade],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    salario = MyFloatField(
        "Salário",
        validators=[
            InputRequired(),
            NumberRange(
                min=0,
                max=9999999999,
                message="Valor do salário excede os limites permitidos.",
            ),
        ],
    )

    beneficio = SelectField(
        "Recebe algum benefício social?",
        choices=[
            (
                beneficio["BENEFICIO_PRESTACAO_CONT"][0],
                beneficio["BENEFICIO_PRESTACAO_CONT"][1],
            ),
            (beneficio["RENDA_BASICA"][0], beneficio["RENDA_BASICA"][1]),
            (beneficio["BOLSA_ESCOLA"][0], beneficio["BOLSA_ESCOLA"][1]),
            (beneficio["BOLSA_MORADIA"][0], beneficio["BOLSA_MORADIA"][1]),
            (beneficio["CESTA_BASICA"][0], beneficio["CESTA_BASICA"][1]),
            (beneficio["VALEGAS"][0], beneficio["VALEGAS"][1]),
            (beneficio["NAO"][0], beneficio["NAO"][1]),
            (beneficio["NAO_INFORMOU"][0], beneficio["NAO_INFORMOU"][1]),
            (beneficio["OUTRO"][0], beneficio["OUTRO"][1]),
        ],
        validators=[
            InputRequired(),
            AnyOf(
                [beneficio[key][0] for key in beneficio],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    qual_beneficio = StringField(
        "Qual benefício?",
        validators=[
            RequiredIf(
                "beneficio",
                "outro",
                message=MSG_NaoPodeEstarEmBranco.format('"Qual benefício?"'),
            )
        ],
    )

    contribui_inss = SelectField(
        "Contribui para a previdência social",
        choices=[
            (contribuicao_inss["SIM"][0], contribuicao_inss["SIM"][1]),
            (
                contribuicao_inss["ENQ_TRABALHAVA"][0],
                contribuicao_inss["ENQ_TRABALHAVA"][1],
            ),
            (contribuicao_inss["NAO"][0], contribuicao_inss["NAO"][1]),
            (contribuicao_inss["NAO_INFO"][0], contribuicao_inss["NAO_INFO"][1]),
        ],
        validators=[
            InputRequired(),
            AnyOf(
                [contribuicao_inss[key][0] for key in contribuicao_inss],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    qtd_pessoas_moradia = IntegerField(
        "Quantas pessoas moram com você?",
        validators=[
            InputRequired(),
            NumberRange(min=0, max=999999999, message="Número inválido de pessoas."),
        ],
    )

    renda_familiar = MyFloatField(
        "Qual o valor da renda familiar?",
        validators=[
            InputRequired(),
            NumberRange(
                min=0, max=999999999, message="Valor da renda familiar inválido."
            ),
        ],
    )

    participacao_renda = SelectField(
        "Qual a sua posição em relação à renda familiar?",
        choices=[
            (
                participacao_renda["PRINCIPAL_RESPONSAVEL"][0],
                participacao_renda["PRINCIPAL_RESPONSAVEL"][1],
            ),
            (
                participacao_renda["CONTRIBUINTE"][0],
                participacao_renda["CONTRIBUINTE"][1],
            ),
            (participacao_renda["DEPENDENTE"][0], participacao_renda["DEPENDENTE"][1]),
        ],
        validators=[
            InputRequired(),
            AnyOf(
                [participacao_renda[key][0] for key in participacao_renda],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    tipo_moradia = SelectField(
        "A família reside em:",
        choices=[
            (moradia["PROPRIA_QUITADA"][0], moradia["PROPRIA_QUITADA"][1]),
            (moradia["PROPRIA_FINANCIADA"][0], moradia["PROPRIA_FINANCIADA"][1]),
            (moradia["MORADIA_CEDIDA"][0], moradia["MORADIA_CEDIDA"][1]),
            (moradia["OCUPADA_IRREGULAR"][0], moradia["OCUPADA_IRREGULAR"][1]),
            (moradia["EM_CONSTRUCAO"][0], moradia["EM_CONSTRUCAO"][1]),
            (moradia["ALUGADA"][0], moradia["ALUGADA"][1]),
            (moradia["PARENTES_OU_AMIGOS"][0], moradia["PARENTES_OU_AMIGOS"][1]),
            (moradia["SITUACAO_DE_RUA"][0], moradia["SITUACAO_DE_RUA"][1]),
        ],
        validators=[
            InputRequired(),
            AnyOf(
                [moradia[key][0] for key in moradia],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    possui_outros_imoveis = SelectField(
        "A família possui outros imóveis?",
        choices=[(True, "Sim"), (False, "Não")],
        validators=[InputRequired()],
        coerce=bool,
    )

    quantos_imoveis = IntegerField(
        "Quantos outros imóveis a família tem?",
        validators=[
            RequiredIf(
                "possui_outros_imoveis",
                True,
                message=MSG_NaoPodeEstarEmBranco.format(
                    '"Quantos outros imóveis a família tem?"'
                ),
            ),
            NumberRange(min=0, max=999999999, message="Número inválido de imóveis."),
        ],
    )

    possui_veiculos = SelectField(
        "A família possui veículos?",
        choices=[(True, "Sim"), (False, "Não")],
        validators=[InputRequired()],
        coerce=bool,
    )

    possui_veiculos_obs = StringField(
        "Qual é o veículo?",
        validators=[
            RequiredIf(
                "possui_veiculos",
                True,
                message=MSG_NaoPodeEstarEmBranco.format('"Qual é o veículo?"'),
            ),
            Length(
                max=FIELD_LIMITS["qual_veiculo"],
                message=f"Por favor, use no máximo {FIELD_LIMITS['qual_veiculo']} caracteres para descrever o veículo.",
            ),
        ],
    )

    quantos_veiculos = IntegerField(
        "Quantos veículos?",
        validators=[
            RequiredIf(
                "possui_veiculos",
                True,
                message=MSG_NaoPodeEstarEmBranco.format('"Quantos veículos?"'),
            ),
            NumberRange(min=0, max=999999999, message="Número inválido de veículos."),
        ],
    )

    ano_veiculo = StringField(
        "Qual o ano do veículo?",
        validators=[
            RequiredIf(
                "possui_veiculos",
                True,
                message=MSG_NaoPodeEstarEmBranco.format('"Qual o ano do veículo?"'),
            ),
            Length(
                max=FIELD_LIMITS["ano_veiculo"],
                message=f"Por favor, use no máximo {FIELD_LIMITS['ano_veiculo']} caracteres para o ano do veículo.",
            ),
        ],
    )

    doenca_grave_familia = SelectField(
        "Há pessoas com doença grave na família?",
        choices=[("sim", "Sim"), ("nao", "Não"), ("nao_inf", "Não informou")],
        validators=[
            InputRequired(),
        ],
    )

    pessoa_doente = SelectField(
        "Pessoa doente:",
        choices=[
            (
                qual_pessoa_doente["PROPRIA_PESSOA"][0],
                qual_pessoa_doente["PROPRIA_PESSOA"][1],
            ),
            (
                qual_pessoa_doente["CONJUGE_OU_COMPANHEIRA_COMPANHEIRO"][0],
                qual_pessoa_doente["CONJUGE_OU_COMPANHEIRA_COMPANHEIRO"][1],
            ),
            (qual_pessoa_doente["FILHOS"][0], qual_pessoa_doente["FILHOS"][1]),
            (qual_pessoa_doente["PAIS"][0], qual_pessoa_doente["PAIS"][1]),
            (qual_pessoa_doente["AVOS"][0], qual_pessoa_doente["AVOS"][1]),
            (qual_pessoa_doente["SOGROS"][0], qual_pessoa_doente["SOGROS"][1]),
            (qual_pessoa_doente["OUTROS"][0], qual_pessoa_doente["OUTROS"][1]),
        ],
        validators=[
            RequiredIf(
                "doenca_grave_familia",
                "sim",
                message=MSG_SelecioneUmaOpcaoLista.format('"Pessoa doente:"'),
            ),
            AnyOf(
                [qual_pessoa_doente[key][0] for key in qual_pessoa_doente],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    pessoa_doente_obs = StringField(
        "Outros:",
        validators=[
            RequiredIf(
                "doenca_grave_familia",
                "sim",
                pessoa_doente=qual_pessoa_doente["OUTROS"][0],
                message=MSG_NaoPodeEstarEmBranco.format('"Outros"'),
            )
        ],
    )

    gastos_medicacao = MyFloatField(
        "Valores gastos com medicação",
        validators=[
            RequiredIf(
                "doenca_grave_familia",
                "sim",
                message=MSG_NaoPodeEstarEmBranco.format(
                    '"Valores gastos com medicação"'
                ),
            ),
            NumberRange(
                min=0,
                max=999999999,
                message="Valor inválido para gastos com medicação.",
            ),
        ],
    )

    obs = TextAreaField(
        "Observações adicionais",
        validators=[
            Optional(),
            Length(
                max=FIELD_LIMITS["obs"],
                message=f"Por favor, use no máximo {FIELD_LIMITS['obs']} caracteres para as observações.",
            ),
        ],
    )

    # Legal Entity fields
    # socios = StringField("Sócios da Pessoa Jurídica", validators=[Optional()])

    # situacao_receita = SelectField(
    #     "Situação perante a Receita Federal",
    #     choices=[("Ativa", "Ativa"), ("Baixada", "Baixada"), ("Outras", "Outras")],
    #     validators=[
    #         # TODO(Andre): Entender esta situacao
    #
    #         # RequiredIf(
    #         #     "pj_constituida",
    #         #     "True",
    #         #     message=MSG_NaoPodeEstarEmBranco.format(
    #         #         "A situação perante a Receita Federal"
    #         #     ),
    #         # ),
    #         Length(
    #             max=FIELD_LIMITS["sit_receita"],
    #             message=f"Por favor, use no máximo {FIELD_LIMITS['sit_receita']} caracteres para a situação na receita.",
    #         ),
    #     ],
    # )

    # enquadramento = SelectField(
    #     "Enquadramento",
    #     choices=[
    #         (
    #             enquadramento["MICROEMPREENDEDOR_INDIVIDUAL"][0],
    #             enquadramento["MICROEMPREENDEDOR_INDIVIDUAL"][1],
    #         ),
    #         (enquadramento["MICROEMPRESA"][0], enquadramento["MICROEMPRESA"][1]),
    #         (
    #             enquadramento["EMPRESA_PEQUENO_PORTE"][0],
    #             enquadramento["EMPRESA_PEQUENO_PORTE"][1],
    #         ),
    #         (enquadramento["OUTROS"][0], enquadramento["OUTROS"][1]),
    #     ],
    #     validators=[
    #         # TODO(Andre): Entender esta situacao
    #
    #         # RequiredIf(
    #         #     "pj_constituida",
    #         #     "True",
    #         #     message=MSG_SelecioneUmaOpcaoLista.format(" de Enquadramento"),
    #         # ),
    #         AnyOf(
    #             [enquadramento[key][0] for key in enquadramento],
    #             message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
    #         ),
    #     ],
    # )

    # sede_bh = SelectField(
    #     "Sede constituída ou a constituir em Belo Horizonte?",
    #     choices=[("True", "Sim"), ("False", "Não")],
    #     validators=[
    #         # TODO(Andre): Entender esta situacao
    #
    #         # RequiredIf(
    #         #     "pj_constituida",
    #         #     "True",
    #         #     message=MSG_SelecioneUmaOpcaoLista.format(
    #         #         'de "Sede constituída ou a constituir em Belo Horizonte?"'
    #         #     ),
    #         # )
    #     ],
    # )

    # regiao_sede_bh = SelectField(
    #     "Qual seria a região, em caso de sede em belo horizonte?",
    #     choices=[
    #         (regiao_bh["BARREIRO"][0], regiao_bh["BARREIRO"][1]),
    #         (regiao_bh["PAMPULHA"][0], regiao_bh["PAMPULHA"][1]),
    #         (regiao_bh["VENDA_NOVA"][0], regiao_bh["VENDA_NOVA"][1]),
    #         (regiao_bh["NORTE"][0], regiao_bh["NORTE"][1]),
    #         (regiao_bh["NORDESTE"][0], regiao_bh["NORDESTE"][1]),
    #         (regiao_bh["NOROESTE"][0], regiao_bh["NOROESTE"][1]),
    #         (regiao_bh["LESTE"][0], regiao_bh["LESTE"][1]),
    #         (regiao_bh["OESTE"][0], regiao_bh["OESTE"][1]),
    #         (regiao_bh["SUL"][0], regiao_bh["SUL"][1]),
    #         (regiao_bh["CENTRO_SUL"][0], regiao_bh["CENTRO_SUL"][1]),
    #     ],
    #     validators=[
    #         # TODO(Andre): Entender esta situacao
    #
    #         # RequiredIf(
    #         #     "pj_constituida",
    #         #     "True",
    #         #     sede_bh="True",
    #         #     message=MSG_SelecioneUmaOpcaoLista.format(
    #         #         'de "Qual seria a região, em caso de sede em belo horizonte?"'
    #         #     ),
    #         # ),
    #         AnyOf(
    #             [regiao_bh[key][0] for key in regiao_bh],
    #             message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
    #         ),
    #     ],
    # )

    # regiao_sede_outros = StringField(
    #     "Não sendo em Belo Horizonte, qual seria o local da sede constituída ou a constituir?",
    #     validators=[
    #         # TODO(Andre): Entender esta situacao
    #         # RequiredIf(
    #         #     "pj_constituida",
    #         #     "True",
    #         #     sede_bh="False",
    #         #     message=MSG_NaoPodeEstarEmBranco.format(
    #         #         '"Não sendo em Belo Horizonte, qual seria o local da sede constituída ou a constituir?"'
    #         #     ),
    #         # ),
    #         Length(
    #             max=FIELD_LIMITS["sede_outros"],
    #             message=f"Por favor, use no máximo {FIELD_LIMITS['sede_outros']} caracteres para o local da sede.",
    #         ),
    #     ],
    # )

    # area_atuacao = SelectField(
    #     "Área de atuação",
    #     choices=[
    #         (
    #             area_atuacao["PRODUCAO_CIRCULACAO_BENS"][0],
    #             area_atuacao["PRODUCAO_CIRCULACAO_BENS"][1],
    #         ),
    #         (
    #             area_atuacao["PRESTACAO_SERVICOS"][0],
    #             area_atuacao["PRESTACAO_SERVICOS"][1],
    #         ),
    #         (area_atuacao["ATIVIDADE_RURAL"][0], area_atuacao["ATIVIDADE_RURAL"][1]),
    #         (area_atuacao["OUTROS"][0], area_atuacao["OUTROS"][1]),
    #     ],
    #     validators=[
    #         # TODO(Andre): Entender esta situacao
    #         # RequiredIf(
    #         #     "pj_constituida",
    #         #     "True",
    #         #     message=MSG_SelecioneUmaOpcaoLista.format("Área de atuação"),
    #         # ),
    #         AnyOf(
    #             [area_atuacao[key][0] for key in area_atuacao],
    #             message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
    #         ),
    #     ],
    # )

    # negocio_nascente = SelectField(
    #     "É negócio nascente?",
    #     choices=[("True", "Sim"), ("False", "Não")],
    #     validators=[
    #         # TODO(Andre): Entender esta situacao
    #         # RequiredIf(
    #         #     "pj_constituida",
    #         #     "True",
    #         #     message=MSG_SelecioneUmaOpcaoLista.format('de "É negócio nascente?"'),
    #         # )
    #     ],
    # )

    # orgao_registro = SelectField(
    #     "Órgão competente pelo registro do ato constitutivo",
    #     choices=[
    #         (orgao_reg["JUCEMG"][0], orgao_reg["JUCEMG"][1]),
    #         (orgao_reg["CARTORIO_PJ"][0], orgao_reg["CARTORIO_PJ"][1]),
    #     ],
    #     validators=[
    #         # TODO(Andre): Entender esta situacao
    #         # RequiredIf(
    #         #     "pj_constituida",
    #         #     "True",
    #         #     message=MSG_SelecioneUmaOpcaoLista.format(
    #         #         'de "Órgão competente pelo registro do ato constitutivo"'
    #         #     ),
    #         # )
    #     ],
    # )

    # faturamento_anual = MyFloatField(
    #     "Faturamento anual",
    #     validators=[
    #         # TODO(Andre): Entender esta situacao
    #         # RequiredIf(
    #         #     "pj_constituida",
    #         #     "True",
    #         #     message=MSG_NaoPodeEstarEmBranco.format("Faturamento anual"),
    #         # ),
    #         NumberRange(
    #             min=0, max=999999999, message="Valor inválido para faturamento anual."
    #         ),
    #     ],
    # )

    # ultimo_balanco_neg = SelectField(
    #     "O balanço patrimonial do último ano foi negativo?",
    #     choices=[("0", "Sim"), ("1", "Não"), ("nao_se_aplica", "Não se aplica")],
    #     validators=[
    #         # TODO(Andre): Entender esta situacao
    #         # RequiredIf(
    #         #     "pj_constituida",
    #         #     "True",
    #         #     message=MSG_SelecioneUmaOpcaoLista.format(
    #         #         'de "O balanço patrimonial do último ano foi negativo?"'
    #         #     ),
    #         # )
    #     ],
    # )

    # resultado_econ_neg = SelectField(
    #     "O resultado econômico do último ano foi negativo?",
    #     choices=[("sim", "Sim"), ("nao", "Não"), ("nao_aplica", "Não se aplica")],
    #     validators=[
    #         # TODO(Andre): Entender esta situacao
    #         # RequiredIf(
    #         #     "pj_constituida",
    #         #     "True",
    #         #     message=MSG_SelecioneUmaOpcaoLista.format(
    #         #         'de "O resultado econômico do último ano foi negativo?"'
    #         #     ),
    #         # )
    #     ],
    # )

    # tem_funcionarios = SelectField(
    #     "Tem funcionários?",
    #     choices=[("sim", "Sim"), ("nao", "Não"), ("nao_aplica", "Não se aplica")],
    #     validators=[
    #         # TODO(Andre): Entender esta situacao
    #         # RequiredIf(
    #         #     "pj_constituida",
    #         #     "True",
    #         #     message=MSG_SelecioneUmaOpcaoLista.format('de "Tem funcionários?"'),
    #         # )
    #     ],
    # )

    # qtd_funcionarios = StringField(
    #     "Em caso positivo, quantos funcionários?",
    #     validators=[
    #         # TODO(Andre): Entender esta situacao
    #         # RequiredIf(
    #         #     "pj_constituida",
    #         #     "True",
    #         #     tem_funcionarios="sim",
    #         #     message=MSG_NaoPodeEstarEmBranco.format(
    #         #         '"Em caso positivo, quantos funcionários?"'
    #         #     ),
    #         # ),
    #         Length(
    #             max=FIELD_LIMITS["qts_func"],
    #             message=f"Por favor, use no máximo {FIELD_LIMITS['qts_func']} caracteres para a quantidade de funcionários.",
    #         ),
    #     ],
    # )

    def _postprocess_data(self) -> dict[str, Any]:
        result = dict(self.data)
        result.pop("submit", None)
        return result
