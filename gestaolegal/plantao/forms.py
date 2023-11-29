from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    FloatField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
    HiddenField,
    TimeField,
)
from wtforms.validators import (
    AnyOf,
    DataRequired,
    Email,
    InputRequired,
    Length,
    NumberRange,
    Optional,
    StopValidation,
)

from gestaolegal.plantao.models import (
    Assistido,
    AssistidoPessoaJuridica,
    Atendido,
    area_atuacao,
    area_do_direito,
    beneficio,
    como_conheceu_daj,
    contribuicao_inss,
    enquadramento,
    escolaridade,
    moradia,
    orgao_reg,
    participacao_renda,
    qual_pessoa_doente,
    raca_cor,
    regiao_bh,
    se_administrativo,
    se_civel,
    assistencia_jud_areas_atendidas,
    assistencia_jud_regioes,
)
from gestaolegal.usuario.forms import EnderecoForm
from gestaolegal.usuario.models import (
    estado_civilUsuario,
    sexo_usuario,
    tipo_bolsaUsuario,
    usuario_urole_roles,
)
from gestaolegal.utils.forms import MyFloatField, RequiredIf, RequiredIf_InputRequired

#####################################################
##################### CONSTANTES ####################
#####################################################

orientacao_AdminOuCivil = {
    "ADMINISTRADOR": ("adm", "Administrador"),
    "CIVEL": ("civ", "Cível"),
}

MSG_NaoPodeEstarEmBranco = "{} não pode estar em branco!"
MSG_SelecioneUmaOpcaoLista = "Por favor selecione uma opção de {} da lista"
MSG_EscolhaUmaData = "Por favor, escolha uma data {}"

max_nome = 80
max_cpf = 14
max_cnpj = 18
max_telefone = 18
max_celular = 18
max_areajuridica = 80
max_comoconheceu = 80
max_indicacaoOrgao = 80
max_procurouOutroLocal = 80
max_obs = 1000
max_logradouro = 100
max_numero = 8
max_complemento = 100
max_bairro = 100
max_cep = 9
max_profissao = 80
max_sit_receita = 20
max_qual_veiculo = 100
max_ano_veiculo = 5
max_obs = 1000
max_rg = 50
max_profissao = 80
max_qual_veiculo = 100
max_ano_veiculo = 5
max_sit_receita = 100
max_sede_outros = 100
max_qts_func = 7
max_descricao = 2000


#####################################################
################## FORMS ############################
#####################################################
class OrientacaoJuridicaForm(FlaskForm):
    area_direito = SelectField(
        "Área do Direito",
        choices=[
            (area_do_direito["AMBIENTAL"][0], area_do_direito["AMBIENTAL"][1]),
            (
                area_do_direito["ADMINISTRATIVO"][0],
                area_do_direito["ADMINISTRATIVO"][1],
            ),
            (area_do_direito["CIVEL"][0], area_do_direito["CIVEL"][1]),
            (area_do_direito["EMPRESARIAL"][0], area_do_direito["EMPRESARIAL"][1]),
            (area_do_direito["PENAL"][0], area_do_direito["PENAL"][1]),
            (area_do_direito["TRABALHISTA"][0], area_do_direito["TRABALHISTA"][1]),
        ],
        validators=[
            DataRequired(MSG_SelecioneUmaOpcaoLista.format("da área do direito")),
            AnyOf(
                [area_do_direito[key][0] for key in area_do_direito],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    sub_area = SelectField(
        "Sub-área Cível",
        choices=[
            (se_civel["CONSUMIDOR"][0], se_civel["CONSUMIDOR"][1]),
            (se_civel["CONTRATOS"][0], se_civel["CONTRATOS"][1]),
            (se_civel["FAMILIA"][0], se_civel["FAMILIA"][1]),
            (se_civel["REAIS"][0], se_civel["REAIS"][1]),
            (
                se_civel["RESPONSABILIDADE_CIVIL"][0],
                se_civel["RESPONSABILIDADE_CIVIL"][1],
            ),

            (se_civel["SUCESSOES"][0], se_civel["SUCESSOES"][1]),
        ],
        validators=[
            RequiredIf(
                area_direito=area_do_direito["CIVEL"][0],
                message=MSG_SelecioneUmaOpcaoLista.format("da sub-área Cível"),
            ),
            AnyOf(
                [se_civel[key][0] for key in se_civel],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    sub_areaAdmin = SelectField(
        "Sub-área Administrativo",
        choices=[
            (
                se_administrativo["ADMINISTRATIVO"][0],
                se_administrativo["ADMINISTRATIVO"][1],
            ),
            (
                se_administrativo["PREVIDENCIARIO"][0],
                se_administrativo["PREVIDENCIARIO"][1],
            ),
            (se_administrativo["TRIBUTARIO"][0], se_administrativo["TRIBUTARIO"][1]),

        ],
        validators=[
            RequiredIf(
                area_direito=area_do_direito["ADMINISTRATIVO"][0],
                message=MSG_SelecioneUmaOpcaoLista.format("da sub-área Administrativo"),
            ),
            AnyOf(
                [se_administrativo[key][0] for key in se_administrativo],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    descricao = TextAreaField(
        "Breve descrição da Orientação Jurídica dada",
        validators=[
            Optional(),
            Length(
                max=max_descricao,
                message="A descrição não pode conter mais de {} caracteres!".format(
                    max_descricao
                ),
            ),
        ],
    )


class CadastroOrientacaoJuridicaForm(OrientacaoJuridicaForm):
    encaminhar_outras_aj = SelectField(
        "Encaminhamento para outras Assistências Judiciárias",
        choices=[(True, "Sim"), (False, "Não")],
        coerce=lambda x: x
        == "True",  # https://stackoverflow.com/questions/33429510/wtforms-selectfield-not-properly-coercing-for-booleans
        validators=[
            InputRequired(
                MSG_SelecioneUmaOpcaoLista.format(
                    'de "Encaminhamento para outras Assistências Judiciárias"'
                )
            )
        ],
        default="False",
    )


class CadastroAtendidoForm(EnderecoForm):
    nome = StringField(
        "Nome",
        validators=[
            DataRequired(MSG_NaoPodeEstarEmBranco.format("O nome")),
            Length(
                max=max_nome,
                message="O nome não pode conter mais de {} caracteres!".format(
                    max_nome
                ),
            ),
        ],
    )

    email = StringField(
        "Endereço de e-mail",
        # validators=[
        #     DataRequired(MSG_NaoPodeEstarEmBranco.format("O e-mail")),
        #     Email(
        #         "Formato de email inválido! Certifique-se de que ele foi digitado corretamente."
        #     ),
        # ],
    )

    data_nascimento = DateField(
        "Data de nascimento",
        validators=[DataRequired(MSG_EscolhaUmaData.format("de nascimento"))],
    )

    cpf = StringField(
        "CPF",
        validators=[
            Length(
                max=max_cpf,
                message="Por favor, use no máximo {} caracteres para o CPF.".format(
                    max_cpf
                ),
            ),
        ],
    )

    cnpj = StringField(
        "CNPJ",
        validators=[
            Optional(),
            Length(
                max=max_cnpj,
                message="Por favor, use no máximo {} caracteres para o CPF.".format(
                    max_cnpj
                ),
            ),
        ],
    )

    telefone = StringField(
        "Telefone fixo",
        validators=[
            Optional(),
            Length(
                max=max_telefone,
                message="Por favor, use no máximo {} caracteres para o telefone fixo.".format(
                    max_telefone
                ),
            ),
        ],
    )

    celular = StringField(
        "Telefone celular",
        validators=[
            DataRequired(MSG_NaoPodeEstarEmBranco.format("O telefone celular")),
            Length(
                max=max_celular,
                message="Por favor, use no máximo {} caracteres para o telefone celular.".format(
                    max_celular
                ),
            ),
        ],
    )

    estado_civil = SelectField(
        "Estado civil",
        choices=[
            (estado_civilUsuario["SOLTEIRO"][0], estado_civilUsuario["SOLTEIRO"][1]),
            (estado_civilUsuario["CASADO"][0], estado_civilUsuario["CASADO"][1]),
            (
                estado_civilUsuario["DIVORCIADO"][0],
                estado_civilUsuario["DIVORCIADO"][1],
            ),
            (estado_civilUsuario["VIUVO"][0], estado_civilUsuario["VIUVO"][1]),
            (estado_civilUsuario["SEPARADO"][0], estado_civilUsuario["SEPARADO"][1]),
            (estado_civilUsuario["UNIAO"][0], estado_civilUsuario["UNIAO"][1]),
        ],
        validators=[
            DataRequired(MSG_SelecioneUmaOpcaoLista.format("de estado civil")),
            AnyOf(
                [estado_civilUsuario[key][0] for key in estado_civilUsuario],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    como_conheceu = SelectField(
        "Como ficou sabendo da DAJ/Direito Vivo?",
        choices=[
            (como_conheceu_daj["ASSISTIDOS"][0], como_conheceu_daj["ASSISTIDOS"][1]),
            (como_conheceu_daj["INTEGRANTES"][0], como_conheceu_daj["INTEGRANTES"][1]),
            (
                como_conheceu_daj["ORGAOSPUBLICOS"][0],
                como_conheceu_daj["ORGAOSPUBLICOS"][1],
            ),
            (
                como_conheceu_daj["MEIOSCOMUNICACAO"][0],
                como_conheceu_daj["MEIOSCOMUNICACAO"][1],
            ),
            (como_conheceu_daj["NUCLEOS"][0], como_conheceu_daj["NUCLEOS"][1]),
            (como_conheceu_daj["CONHECIDOS"][0], como_conheceu_daj["CONHECIDOS"][1]),
            (como_conheceu_daj["OUTROS"][0], como_conheceu_daj["OUTROS"][1]),
        ],
        validators=[
            DataRequired(
                MSG_SelecioneUmaOpcaoLista.format('de "Como conheceu a DAJ?"')
            ),
            AnyOf(
                [como_conheceu_daj[key][0] for key in como_conheceu_daj],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    indicacao_orgao = StringField(
        "Qual foi o órgão?",
        validators=[
            RequiredIf(
                como_conheceu=como_conheceu_daj["ORGAOSPUBLICOS"][0],
                message=MSG_NaoPodeEstarEmBranco.format('"Qual foi o órgão?"'),
            ),
            Length(
                max=max_indicacaoOrgao,
                message='Por favor, use no máximo {} caracteres para o campo "Qual foi o órgão?".'.format(
                    max_indicacaoOrgao
                ),
            ),
        ],
    )

    procurou_outro_local = SelectField(
        "Você procurou outro local para resolver a demanda antes de vir à DAJ?",
        choices=[(True, "Sim"), (False, "Não")],
        coerce=lambda x: x
        == "True",  # https://stackoverflow.com/questions/33429510/wtforms-selectfield-not-properly-coercing-for-booleans
        validators=[
            InputRequired(
                MSG_SelecioneUmaOpcaoLista.format(
                    'de "Você procurou outro local para resolver a demanda antes de vir à DAJ?"'
                )
            )
        ],
    )

    procurou_qual_local = StringField(
        "Qual local?",
        validators=[
            RequiredIf(
                procurou_outro_local=True,
                message=MSG_NaoPodeEstarEmBranco.format('"Qual local?"'),
            ),
            Length(
                max=max_procurouOutroLocal,
                message='Por favor, use no máximo {} caracteres para o campo "Qual local?".'.format(
                    max_procurouOutroLocal
                ),
            ),
        ],
    )

    obs_atendido = TextAreaField(
        "Observações",
        validators=[
            Optional(),
            Length(
                max=max_obs,
                message="Por favor, use no máximo {} caracteres para as observações.".format(
                    max_obs
                ),
            ),
        ],
    )

    pj_constituida = SelectField(
        "Existe Pessoa Jurídica constituída?",
        choices=[(True, "Sim"), (False, "Não")],
        coerce=lambda x: x
        == "True",  # https://stackoverflow.com/questions/33429510/wtforms-selectfield-not-properly-coercing-for-booleans
        validators=[
            InputRequired(
                MSG_SelecioneUmaOpcaoLista.format(
                    'de "Existe Pessoa Jurídica constituída?"'
                )
            )
        ],
    )

    repres_legal = SelectField(
        "O atendido é o representante legal?",
        choices=[(True, "Sim"), (False, "Não")],
        coerce=lambda x: x
        == "True",  # https://stackoverflow.com/questions/33429510/wtforms-selectfield-not-properly-coercing-for-booleans
        validators=[
            InputRequired(
                MSG_SelecioneUmaOpcaoLista.format(
                    'de "O atendido é o representante legal? "'
                )
            )
        ],
        default="True",
    )

    ###Dados Representante Legal Atendido com Pessoa Juridica Constituida

    nome_repres_legal = StringField(
        "Nome do representante legal:",
        validators=[
            RequiredIf(
                repres_legal=False,
                pj_constituida=True,
                message=MSG_NaoPodeEstarEmBranco.format(
                    "O Nome do representante legal"
                ),
            ),
            Length(
                max=max_nome,
                message="O nome não pode conter mais de {} caracteres!".format(
                    max_nome
                ),
            ),
        ],
    )

    cpf_repres_legal = StringField(
        "CPF do representante legal:",
        validators=[
            Optional(),
            Length(
                max=max_cpf,
                message="Por favor, use no máximo {} caracteres para o CPF.".format(
                    max_cpf
                ),
            ),
        ],
    )

    contato_repres_legal = StringField(
        "Telefone de contato do representante legal:",
        validators=[
            Optional(),
            Length(
                max=max_telefone,
                message="Por favor, use no máximo {} caracteres para o telefone fixo.".format(
                    max_telefone
                ),
            ),
        ],
    )
    rg_repres_legal = StringField(
        "RG do representante legal",
        validators=[
            Optional(),
            Length(
                max=max_rg,
                message="Por favor, use no máximo {} caracteres para o RG.".format(
                    max_rg
                ),
            ),
        ],
    )

    nascimento_repres_legal = DateField(
        "Data de nascimento do representante legal",
        validators=[
            Optional(),
        ],
    )

    pretende_constituir_pj = SelectField(
        "Pretende-se constituir Pessoa Jurídica?",
        choices=[(True, "Sim"), (False, "Não")],
        coerce=lambda x: x
        == "True",  # https://stackoverflow.com/questions/33429510/wtforms-selectfield-not-properly-coercing-for-booleans
        validators=[Optional()],
    )


class TornarAssistidoForm(FlaskForm):
    pj_constituida = SelectField(
        "Existe PJ constituída?",
        choices=[(True, "Sim"), (False, "Não")],
        coerce=lambda x: x == "True",
        validators=[Optional()],
    )

    ############ Dados gerais de ambos tipos de assistidos ############

    sexo = SelectField(
        "Sexo/Gênero",
        choices=[
            (sexo_usuario["MASCULINO"][0], sexo_usuario["MASCULINO"][1]),
            (sexo_usuario["FEMININO"][0], sexo_usuario["FEMININO"][1]),
            (sexo_usuario["OUTROS"][0], sexo_usuario["OUTROS"][1]),
        ],
        validators=[
            DataRequired(MSG_SelecioneUmaOpcaoLista.format("de Sexo/Gênero")),
            AnyOf(
                [sexo_usuario[key][0] for key in sexo_usuario],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )
    profissao = StringField(
        "Profissão",
        validators=[
            DataRequired(MSG_NaoPodeEstarEmBranco.format("A profissão")),
            Length(
                max=max_profissao,
                message="Por favor, use no máximo {} caracteres para descrever a profissão.".format(
                    max_profissao
                ),
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
            DataRequired(MSG_SelecioneUmaOpcaoLista.format('"de raça/cor"')),
            AnyOf(
                [raca_cor[key][0] for key in raca_cor],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    rg = StringField(
        "RG",
        validators=[
            DataRequired(MSG_NaoPodeEstarEmBranco.format("O RG")),
            Length(
                max=max_rg,
                message="Por favor, use no máximo {} caracteres para o RG.".format(
                    max_rg
                ),
            ),
        ],
    )

    ######################### Pessoa Física ##################
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
            DataRequired(MSG_SelecioneUmaOpcaoLista.format('de "Grau de instrução"')),
            AnyOf(
                [escolaridade[key][0] for key in escolaridade],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    salario = MyFloatField(
        "Salário",
        validators=[
            InputRequired(MSG_NaoPodeEstarEmBranco.format("O salário")),
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
            DataRequired(
                MSG_SelecioneUmaOpcaoLista.format('"Recebe algum benefício social?"')
            ),
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
                beneficio="outro",
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
            DataRequired(
                MSG_SelecioneUmaOpcaoLista.format(
                    'de "Contribui para a previdência social"'
                )
            ),
            AnyOf(
                [contribuicao_inss[key][0] for key in contribuicao_inss],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    qtd_pessoas_moradia = IntegerField(
        "Quantas pessoas moram com você?",
        validators=[
            InputRequired(
                MSG_NaoPodeEstarEmBranco.format("Quantas pessoas moram com você")
            ),
            NumberRange(
                min=0,
                max=999999999,
                message="Por favor, use no máximo {} numeros.".format(999999999),
            ),
        ],
    )

    renda_familiar = MyFloatField(
        "Qual o valor da renda familiar?",
        validators=[
            InputRequired(
                MSG_NaoPodeEstarEmBranco.format('"Qual o valor da renda familiar?"')
            ),
            NumberRange(
                min=0,
                max=999999999,
                message="Por favor, use no máximo {} numeros.".format(999999999),
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
            DataRequired(
                MSG_SelecioneUmaOpcaoLista.format(
                    'de "Qual a sua posição em relação à renda familiar?"'
                )
            ),
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
            DataRequired(
                MSG_SelecioneUmaOpcaoLista.format('de "A família reside em:"')
            ),
            AnyOf(
                [moradia[key][0] for key in moradia],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    possui_outros_imoveis = SelectField(
        "A família possui outros imóveis?",
        choices=[(True, "Sim"), (False, "Não")],
        coerce=lambda x: x
        == "True",  # https://stackoverflow.com/questions/33429510/wtforms-selectfield-not-properly-coercing-for-booleans
        validators=[
            InputRequired(
                MSG_SelecioneUmaOpcaoLista.format(
                    'de "A família possui outros imóveis?"'
                )
            )
        ],
    )

    quantos_imoveis = IntegerField(
        "Quantos outros imóveis a família tem?",
        validators=[
            RequiredIf(
                possui_outros_imoveis=True,
                message=MSG_NaoPodeEstarEmBranco.format(
                    '"Quantos outros imóveis a família tem?"'
                ),
            ),
            NumberRange(
                min=0,
                max=999999999,
                message="Por favor, use no máximo {} numeros.".format(999999999),
            ),
        ],
    )

    possui_veiculos = SelectField(
        "A família possui veículos?",
        choices=[(True, "Sim"), (False, "Não")],
        coerce=lambda x: x
        == "True",  # https://stackoverflow.com/questions/33429510/wtforms-selectfield-not-properly-coercing-for-booleans
        validators=[
            InputRequired(
                message=MSG_SelecioneUmaOpcaoLista.format(
                    'de "A família possui veículos?"'
                )
            )
        ],
    )

    possui_veiculos_obs = StringField(
        "Qual é o veículo?",
        validators=[
            RequiredIf(
                possui_veiculos=True,
                message=MSG_NaoPodeEstarEmBranco.format('"Qual é o veículo?"'),
            ),
            Length(
                max=max_qual_veiculo,
                message="Por favor, use no máximo {} caracteres para descrever a profissão.".format(
                    max_qual_veiculo
                ),
            ),
        ],
    )

    quantos_veiculos = IntegerField(
        "Quantos veículos?",
        validators=[
            RequiredIf(
                possui_veiculos=True,
                message=MSG_NaoPodeEstarEmBranco.format('"Quantos veículos?"'),
            ),
            NumberRange(
                min=0,
                max=999999999,
                message="Por favor, use no máximo {} numeros.".format(999999999),
            ),
        ],
    )

    ano_veiculo = StringField(
        "Qual o ano do veículo?",
        validators=[
            RequiredIf(
                possui_veiculos=True,
                message=MSG_NaoPodeEstarEmBranco.format('"Qual o ano do veículo?"'),
            ),
            Length(
                max=max_ano_veiculo,
                message="Por favor, use no máximo {} caracteres para descrever a profissão.".format(
                    max_ano_veiculo
                ),
            ),
        ],
    )

    doenca_grave_familia = SelectField(
        "Há pessoas com doença grave na família?",
        choices=[("sim", "Sim"), ("nao", "Não"), ("nao_inf", "Não informou")],
        validators=[
            DataRequired(
                MSG_SelecioneUmaOpcaoLista.format(
                    '"Há pessoas com doença grave na família?"'
                )
            )
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
                doenca_grave_familia="sim",
                message=MSG_SelecioneUmaOpcaoLista.format('"Pessoa doente:"'),
            ),
            AnyOf(
                [qual_pessoa_doente[key][0] for key in qual_pessoa_doente],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    pessoa_doente_obs = StringField(
        "Outros: ",
        validators=[
            RequiredIf(
                doenca_grave_familia="sim",
                pessoa_doente=qual_pessoa_doente["OUTROS"][0],
                message=MSG_NaoPodeEstarEmBranco.format('"Outros"'),
            )
        ],
    )

    gastos_medicacao = MyFloatField(
        "Valores gastos com medicação",
        validators=[
            RequiredIf_InputRequired(
                doenca_grave_familia="sim",
                message=MSG_NaoPodeEstarEmBranco.format(
                    '"Valores gastos com medicação"'
                ),
            ),
            NumberRange(
                min=0,
                max=999999999,
                message="Por favor, use no máximo {} numeros.".format(999999999),
            ),
        ],
    )

    obs_assistido = TextAreaField(
        "Observações adicionais",
        validators=[
            Optional(),
            Length(
                max=max_obs,
                message="Por favor, use no máximo {} caracteres para descrever a profissão.".format(
                    max_obs
                ),
            ),
        ],
    )
    # ##################################################################
    # # ############# Pessoa Jurídica

    socios = StringField("Sócios da Pessoa Jurídica", validators=[Optional()])

    situacao_receita = SelectField(
        "Situação perante a Receita Federal",
        choices=[("Ativa", "Ativa"), ("Baixada", "Baixada"), ("Outras", "Outras")],
        validators=[
            RequiredIf(
                pj_constituida=True,
                message=MSG_NaoPodeEstarEmBranco.format(
                    "A situação perante a Receita Federal"
                ),
            ),
            Length(
                max=max_sit_receita,
                message="Por favor, use no máximo {} caracteres para descrever a profissão.".format(
                    max_sit_receita
                ),
            ),
        ],
    )

    enquadramento = SelectField(
        "Enquadramento",
        choices=[
            (
                enquadramento["MICROEMPREENDEDOR_INDIVIDUAL"][0],
                enquadramento["MICROEMPREENDEDOR_INDIVIDUAL"][1],
            ),
            (enquadramento["MICROEMPRESA"][0], enquadramento["MICROEMPRESA"][1]),
            (
                enquadramento["EMPRESA_PEQUENO_PORTE"][0],
                enquadramento["EMPRESA_PEQUENO_PORTE"][1],
            ),
            (enquadramento["OUTROS"][0], enquadramento["OUTROS"][1]),
        ],
        validators=[
            RequiredIf(
                pj_constituida=True,
                message=MSG_SelecioneUmaOpcaoLista.format(" de Enquadramento"),
            ),
            AnyOf(
                [enquadramento[key][0] for key in enquadramento],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    sede_bh = SelectField(
        "Sede constituída ou a constituir em Belo Horizonte?",
        choices=[(True, "Sim"), (False, "Não")],
        coerce=lambda x: x
        == "True",  # https://stackoverflow.com/questions/33429510/wtforms-selectfield-not-properly-coercing-for-booleans
        validators=[
            RequiredIf_InputRequired(
                pj_constituida=True,
                message=MSG_SelecioneUmaOpcaoLista.format(
                    'de "Sede constituída ou a constituir em Belo Horizonte?"'
                ),
            )
        ],
    )

    regiao_sede_bh = SelectField(
        "Qual seria a região, em caso de sede em belo horizonte?",
        choices=[
            (regiao_bh["BARREIRO"][0], regiao_bh["BARREIRO"][1]),
            (regiao_bh["PAMPULHA"][0], regiao_bh["PAMPULHA"][1]),
            (regiao_bh["VENDA_NOVA"][0], regiao_bh["VENDA_NOVA"][1]),
            (regiao_bh["NORTE"][0], regiao_bh["NORTE"][1]),
            (regiao_bh["NORDESTE"][0], regiao_bh["NORDESTE"][1]),
            (regiao_bh["NOROESTE"][0], regiao_bh["NOROESTE"][1]),
            (regiao_bh["LESTE"][0], regiao_bh["LESTE"][1]),
            (regiao_bh["OESTE"][0], regiao_bh["OESTE"][1]),
            (regiao_bh["SUL"][0], regiao_bh["SUL"][1]),
            (regiao_bh["CENTRO_SUL"][0], regiao_bh["CENTRO_SUL"][1]),
        ],
        validators=[
            RequiredIf(
                pj_constituida=True,
                sede_bh=True,
                message=MSG_SelecioneUmaOpcaoLista.format(
                    'de "Qual seria a região, em caso de sede em belo horizonte?"'
                ),
            ),
            AnyOf(
                [regiao_bh[key][0] for key in regiao_bh],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    regiao_sede_outros = StringField(
        "Não sendo em Belo Horizonte, qual seria o local da sede constituída ou a constituir?",
        validators=[
            RequiredIf(
                pj_constituida=True,
                sede_bh=False,
                message=MSG_NaoPodeEstarEmBranco.format(
                    '"Não sendo em Belo Horizonte, qual seria o local da sede constituída ou a constituir?"'
                ),
            ),
            Length(
                max=max_sede_outros,
                message="Por favor, use no máximo {} caracteres para descrever a profissão.".format(
                    max_sede_outros
                ),
            ),
        ],
    )

    area_atuacao = SelectField(
        "Área de atuação",
        choices=[
            (
                area_atuacao["PRODUCAO_CIRCULACAO_BENS"][0],
                area_atuacao["PRODUCAO_CIRCULACAO_BENS"][1],
            ),
            (
                area_atuacao["PRESTACAO_SERVICOS"][0],
                area_atuacao["PRESTACAO_SERVICOS"][1],
            ),
            (area_atuacao["ATIVIDADE_RURAL"][0], area_atuacao["ATIVIDADE_RURAL"][1]),
            (area_atuacao["OUTROS"][0], area_atuacao["OUTROS"][1]),
        ],
        validators=[
            RequiredIf(
                pj_constituida=True,
                message=MSG_SelecioneUmaOpcaoLista.format("Área de atuação"),
            ),
            AnyOf(
                [area_atuacao[key][0] for key in area_atuacao],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    negocio_nascente = SelectField(
        "É negócio nascente?",
        choices=[(True, "Sim"), (False, "Não")],
        coerce=lambda x: x
        == "True",  # https://stackoverflow.com/questions/33429510/wtforms-selectfield-not-properly-coercing-for-booleans
        validators=[
            RequiredIf_InputRequired(
                pj_constituida=True,
                message=MSG_SelecioneUmaOpcaoLista.format('de "É negócio nascente?"'),
            )
        ],
    )

    orgao_registro = SelectField(
        "Órgão competente pelo registro do ato constitutivo",
        choices=[
            (orgao_reg["JUCEMG"][0], orgao_reg["JUCEMG"][1]),
            (orgao_reg["CARTORIO_PJ"][0], orgao_reg["CARTORIO_PJ"][1]),
        ],
        validators=[
            RequiredIf(
                pj_constituida=True,
                message=MSG_SelecioneUmaOpcaoLista.format(
                    'de "Órgão competente pelo registro do ato constitutivo"'
                ),
            )
        ],
    )

    faturamento_anual = MyFloatField(
        "Faturamento anual",
        validators=[
            RequiredIf_InputRequired(
                pj_constituida=True,
                message=MSG_NaoPodeEstarEmBranco.format("Faturamento anual"),
            ),
            NumberRange(
                min=0,
                max=999999999,
                message="Por favor, insira um valor entre 0 e {}.".format(999999999),
            ),
        ],
    )

    ultimo_balanco_neg = SelectField(
        "O balanço patrimonial do último ano foi negativo?",
        choices=[("0", "Sim"), ("1", "Não"), ("nao_se_aplica", "Não se aplica")],
        validators=[
            RequiredIf_InputRequired(
                pj_constituida=True,
                message=MSG_SelecioneUmaOpcaoLista.format(
                    'de "O balanço patrimonial do último ano foi negativo?"'
                ),
            )
        ],
    )

    resultado_econ_neg = SelectField(
        "O resultado econômico do último ano foi negativo?",
        choices=[("sim", "Sim"), ("nao", "Não"), ("nao_aplica", "Não se aplica")],
        validators=[
            RequiredIf(
                pj_constituida=True,
                message=MSG_SelecioneUmaOpcaoLista.format(
                    'de "O resultado econômico do último ano foi negativo?"'
                ),
            )
        ],
    )

    tem_funcionarios = SelectField(
        "Tem funcionários?",
        choices=[("sim", "Sim"), ("nao", "Não"), ("nao_aplica", "Não se aplica")],
        validators=[
            RequiredIf(
                pj_constituida=True,
                message=MSG_SelecioneUmaOpcaoLista.format('de "Tem funcionários?"'),
            )
        ],
    )

    qtd_funcionarios = StringField(
        "Em caso positivo, quantos funcionários?",
        validators=[
            RequiredIf(
                pj_constituida=True,
                tem_funcionarios="sim",
                message=MSG_NaoPodeEstarEmBranco.format(
                    '"Em caso positivo, quantos funcionários?"'
                ),
            ),
            Length(
                max=max_qts_func,
                message="Por favor, use no máximo {} caracteres para descrever a profissão.".format(
                    max_qts_func
                ),
            ),
        ],
    )


class EditarAssistidoForm(CadastroAtendidoForm, TornarAssistidoForm):
    e_isso = None


class AssistenciaJudiciariaForm(EnderecoForm):
    nome = StringField(
        "Nome",
        validators=[
            DataRequired(MSG_NaoPodeEstarEmBranco.format("O nome")),
            Length(
                max=max_nome,
                message="Por favor, use no máximo {} caracteres para o telefone".format(
                    max_nome
                ),
            ),
        ],
    )

    areas_atendidas = SelectMultipleField(
        "Áreas do Direito",
        choices=[
            (
                assistencia_jud_areas_atendidas["AMBIENTAL"][0],
                assistencia_jud_areas_atendidas["AMBIENTAL"][1],
            ),
            (
                assistencia_jud_areas_atendidas["ADMINISTRATIVO"][0],
                assistencia_jud_areas_atendidas["ADMINISTRATIVO"][1],
            ),
            (
                assistencia_jud_areas_atendidas["CIVEL"][0],
                assistencia_jud_areas_atendidas["CIVEL"][1],
            ),
            (
                assistencia_jud_areas_atendidas["EMPRESARIAL"][0],
                assistencia_jud_areas_atendidas["EMPRESARIAL"][1],
            ),
            (
                assistencia_jud_areas_atendidas["PENAL"][0],
                assistencia_jud_areas_atendidas["PENAL"][1],
            ),
            (
                assistencia_jud_areas_atendidas["TRABALHISTA"][0],
                assistencia_jud_areas_atendidas["TRABALHISTA"][1],
            ),
        ],
        validators=[
            DataRequired("Escolha pelo menos uma área do Direito!"),
        ],
    )

    regiao = SelectField(
        "Região",
        choices=[
            (assistencia_jud_regioes["NORTE"][0], assistencia_jud_regioes["NORTE"][1]),
            (assistencia_jud_regioes["SUL"][0], assistencia_jud_regioes["SUL"][1]),
            (assistencia_jud_regioes["LESTE"][0], assistencia_jud_regioes["LESTE"][1]),
            (assistencia_jud_regioes["OESTE"][0], assistencia_jud_regioes["OESTE"][1]),
            (
                assistencia_jud_regioes["NOROESTE"][0],
                assistencia_jud_regioes["NOROESTE"][1],
            ),
            (
                assistencia_jud_regioes["CENTRO_SUL"][0],
                assistencia_jud_regioes["CENTRO_SUL"][1],
            ),
            (
                assistencia_jud_regioes["NORDESTE"][0],
                assistencia_jud_regioes["NORDESTE"][1],
            ),
            (
                assistencia_jud_regioes["PAMPULHA"][0],
                assistencia_jud_regioes["PAMPULHA"][1],
            ),
            (
                assistencia_jud_regioes["BARREIRO"][0],
                assistencia_jud_regioes["BARREIRO"][1],
            ),
            (
                assistencia_jud_regioes["VENDA_NOVA"][0],
                assistencia_jud_regioes["VENDA_NOVA"][1],
            ),
            (
                assistencia_jud_regioes["CONTAGEM"][0],
                assistencia_jud_regioes["CONTAGEM"][1],
            ),
            (assistencia_jud_regioes["BETIM"][0], assistencia_jud_regioes["BETIM"][1]),
        ],
        validators=[DataRequired(MSG_SelecioneUmaOpcaoLista.format('de "Região"'))],
    )

    telefone = StringField(
        "Telefone",
        validators=[
            DataRequired(MSG_NaoPodeEstarEmBranco.format("O telefone")),
            Length(
                max=max_celular,
                message="Por favor, use no máximo {} caracteres para o telefone".format(
                    max_celular
                ),
            ),
        ],
    )

    email = StringField(
        "Endereço de e-mail",
        validators=[
            DataRequired(MSG_NaoPodeEstarEmBranco.format("O email")),
            Email(
                "Formato de e-mail inválido! Certifique-se de que ele foi digitado corretamente."
            ),
        ],
    )

    submit = SubmitField("Cadastrar")


class AbrirPlantaoForm(FlaskForm):
    data_abertura = DateField(
        "Data de abertura",
        validators=[DataRequired(MSG_EscolhaUmaData.format("de abertura"))],
    )
    hora_abertura = TimeField(
        "Horário de Abertura",
        validators=[DataRequired("Por favor, escolha um horário de abertura.")],
    )


class SelecionarDuracaoPlantaoForm(FlaskForm):
    hdnDiasEscolhidos = HiddenField("Dias escolhidos")
    hdnDataAbertura = HiddenField("Data de abertura")
    hdnDataFechamento = HiddenField("Data de fechamento")
    hdnHoraAbertura = HiddenField("Hora de abertura")
    hdnHoraFechamento = HiddenField("Hora de fechamento")
    submit = SubmitField("Confirmar")


class FecharPlantaoForm(FlaskForm):
    data_fechamento = DateField(
        "Data de fechamento",
        validators=[DataRequired(MSG_EscolhaUmaData.format("de fechamento"))],
    )
    hora_fechamento = TimeField(
        "Horário de fechamento",
        validators=[DataRequired("Por favor, escolha um horário de fechamento.")],
    )
