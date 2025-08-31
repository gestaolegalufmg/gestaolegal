from wtforms import DateField, SelectField, StringField, TextAreaField
from wtforms.validators import (
    AnyOf,
    DataRequired,
    Email,
    InputRequired,
    Length,
    Optional,
)

from gestaolegal.plantao.forms import FIELD_LIMITS, RequiredIf
from gestaolegal.plantao.forms.base_form_mixin import BaseFormMixin
from gestaolegal.plantao.models import como_conheceu_daj
from gestaolegal.usuario.forms import (
    EnderecoForm,
    MSG_EscolhaUmaData,
    MSG_NaoPodeEstarEmBranco,
    MSG_SelecioneUmaOpcaoLista,
)
from gestaolegal.usuario.models import estado_civilUsuario


class CadastroAtendidoForm(EnderecoForm, BaseFormMixin):
    nome = StringField(
        "Nome",
        validators=[
            DataRequired(MSG_NaoPodeEstarEmBranco.format("O nome")),
            Length(
                max=FIELD_LIMITS["nome"],
                message=f"O nome não pode conter mais de {FIELD_LIMITS['nome']} caracteres!",
            ),
        ],
    )

    email = StringField(
        "Endereço de e-mail",
        validators=[Optional(), Email("Formato de email inválido!")],
    )

    data_nascimento = DateField(
        "Data de nascimento",
        validators=[DataRequired(MSG_EscolhaUmaData.format("de nascimento"))],
    )

    cpf = StringField(
        "CPF",
        validators=[
            Optional(),
            Length(
                max=FIELD_LIMITS["cpf"],
                message=f"Por favor, use no máximo {FIELD_LIMITS['cpf']} caracteres para o CPF.",
            ),
        ],
    )

    cnpj = StringField(
        "CNPJ",
        validators=[
            Optional(),
            Length(
                max=FIELD_LIMITS["cnpj"],
                message=f"Por favor, use no máximo {FIELD_LIMITS['cnpj']} caracteres para o CNPJ.",
            ),
        ],
    )

    telefone = StringField(
        "Telefone fixo",
        validators=[
            Optional(),
            Length(
                max=FIELD_LIMITS["telefone"],
                message=f"Por favor, use no máximo {FIELD_LIMITS['telefone']} caracteres para o telefone fixo.",
            ),
        ],
    )

    celular = StringField(
        "Telefone celular",
        validators=[
            DataRequired(MSG_NaoPodeEstarEmBranco.format("O telefone celular")),
            Length(
                max=FIELD_LIMITS["celular"],
                message=f"Por favor, use no máximo {FIELD_LIMITS['celular']} caracteres para o telefone celular.",
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
                "como_conheceu",
                como_conheceu_daj["ORGAOSPUBLICOS"][0],
                message=MSG_NaoPodeEstarEmBranco.format('"Qual foi o órgão?"'),
            ),
            Length(
                max=FIELD_LIMITS["indicacaoOrgao"],
                message=f'Por favor, use no máximo {FIELD_LIMITS["indicacaoOrgao"]} caracteres para o campo "Qual foi o órgão?".',
            ),
        ],
    )

    procurou_outro_local = SelectField(
        "Você procurou outro local para resolver a demanda antes de vir à DAJ?",
        choices=[("True", "Sim"), ("False", "Não")],
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
                "procurou_outro_local",
                "True",
                message=MSG_NaoPodeEstarEmBranco.format('"Qual local?"'),
            ),
            Length(
                max=FIELD_LIMITS["procurouOutroLocal"],
                message=f'Por favor, use no máximo {FIELD_LIMITS["procurouOutroLocal"]} caracteres para o campo "Qual local?".',
            ),
        ],
    )

    obs_atendido = TextAreaField(
        "Observações",
        validators=[
            Optional(),
            Length(
                max=FIELD_LIMITS["obs"],
                message=f"Por favor, use no máximo {FIELD_LIMITS['obs']} caracteres para as observações.",
            ),
        ],
    )

    pj_constituida = SelectField(
        "Existe Pessoa Jurídica constituída?",
        choices=[("1", "Sim"), ("0", "Não")],
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
        choices=[("1", "Sim"), ("0", "Não")],
        validators=[
            InputRequired(
                MSG_SelecioneUmaOpcaoLista.format(
                    'de "O atendido é o representante legal?"'
                )
            )
        ],
        default="1",
    )

    # Representative legal data fields
    nome_repres_legal = StringField(
        "Nome do representante legal:",
        validators=[
            RequiredIf(
                "repres_legal",
                "0",
                message=MSG_NaoPodeEstarEmBranco.format(
                    "O Nome do representante legal"
                ),
                pj_constituida="1",
            ),
            Length(
                max=FIELD_LIMITS["nome"],
                message=f"O nome não pode conter mais de {FIELD_LIMITS['nome']} caracteres!",
            ),
        ],
    )

    cpf_repres_legal = StringField(
        "CPF do representante legal:",
        validators=[
            Optional(),
            Length(
                max=FIELD_LIMITS["cpf"],
                message=f"Por favor, use no máximo {FIELD_LIMITS['cpf']} caracteres para o CPF.",
            ),
        ],
    )

    contato_repres_legal = StringField(
        "Telefone de contato do representante legal:",
        validators=[
            Optional(),
            Length(
                max=FIELD_LIMITS["telefone"],
                message=f"Por favor, use no máximo {FIELD_LIMITS['telefone']} caracteres para o telefone.",
            ),
        ],
    )

    rg_repres_legal = StringField(
        "RG do representante legal",
        validators=[
            Optional(),
            Length(
                max=FIELD_LIMITS["rg"],
                message=f"Por favor, use no máximo {FIELD_LIMITS['rg']} caracteres para o RG.",
            ),
        ],
    )

    nascimento_repres_legal = DateField(
        "Data de nascimento do representante legal",
        validators=[Optional()],
    )

    pretende_constituir_pj = SelectField(
        "Pretende-se constituir Pessoa Jurídica?",
        choices=[("True", "Sim"), ("False", "Não")],
        validators=[Optional()],
    )

    def populate_from_atendido(self, atendido) -> None:
        field_mapping = {
            "obs_atendido": "obs",
            "pretende_constituir_pj": "pretende_constituir_pj",
        }

        self.populate_from_entity(atendido, field_mapping)

        if hasattr(atendido, "procurou_outro_local"):
            self.procurou_outro_local.data = (
                False if atendido.procurou_outro_local == "0" else True
            )

        if hasattr(atendido, "pretende_constituir_pj"):
            self.pretende_constituir_pj.data = (
                False if atendido.pretende_constituir_pj == "0" else True
            )

        if hasattr(atendido, "endereco") and atendido.endereco:
            self.populate_from_entity(atendido.endereco)
