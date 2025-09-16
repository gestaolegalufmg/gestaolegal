from typing import Any

from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, TextAreaField
from wtforms.validators import (
    AnyOf,
    Email,
    InputRequired,
    Length,
    Optional,
)

from gestaolegal.common.constants import (
    FIELD_LIMITS,
    como_conheceu_daj,
    estado_civilUsuario,
)
from gestaolegal.forms.base_form_mixin import BaseFormMixin
from gestaolegal.forms.endereco_form_mixin import EnderecoFieldsMixin
from gestaolegal.forms import (
    MSG_NaoPodeEstarEmBranco,
    RequiredIf,
)


class CadastroAtendidoForm(EnderecoFieldsMixin, BaseFormMixin, FlaskForm):
    nome = StringField(
        "Nome",
        validators=[
            InputRequired(),
            Length(
                max=FIELD_LIMITS["nome"],
                message=f"O nome não pode conter mais de {FIELD_LIMITS['nome']} caracteres!",
            ),
        ],
        render_kw={"maxlength": FIELD_LIMITS["nome"]},
    )

    email = StringField(
        "Endereço de e-mail",
        validators=[Optional(), Email("Formato de email inválido!")],
        render_kw={
            "maxlength": FIELD_LIMITS.get("email", 120),
            "inputmode": "email",
            "type": "email",
        },
    )

    data_nascimento = DateField(
        "Data de nascimento",
        validators=[InputRequired()],
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
        render_kw={"maxlength": FIELD_LIMITS["cpf"]},
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
        render_kw={"maxlength": FIELD_LIMITS["cnpj"]},
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
        render_kw={"maxlength": FIELD_LIMITS["telefone"], "inputmode": "tel"},
    )

    celular = StringField(
        "Telefone celular",
        validators=[
            InputRequired(),
            Length(
                max=FIELD_LIMITS["celular"],
                message=f"Por favor, use no máximo {FIELD_LIMITS['celular']} caracteres para o telefone celular.",
            ),
        ],
        render_kw={"maxlength": FIELD_LIMITS["celular"], "inputmode": "tel"},
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
            InputRequired(),
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
            InputRequired(),
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
        render_kw={"maxlength": FIELD_LIMITS["indicacaoOrgao"]},
    )

    procurou_outro_local = SelectField(
        "Você procurou outro local para resolver a demanda antes de vir à DAJ?",
        choices=[(True, "Sim"), (False, "Não")],
        validators=[InputRequired()],
        coerce=bool,
    )

    procurou_qual_local = StringField(
        "Qual local?",
        validators=[
            RequiredIf(
                "procurou_outro_local",
                True,
                message=MSG_NaoPodeEstarEmBranco.format('"Qual local?"'),
            ),
            Length(
                max=FIELD_LIMITS["procurouOutroLocal"],
                message=f'Por favor, use no máximo {FIELD_LIMITS["procurouOutroLocal"]} caracteres para o campo "Qual local?".',
            ),
        ],
        render_kw={"maxlength": FIELD_LIMITS["procurouOutroLocal"]},
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
        render_kw={"maxlength": FIELD_LIMITS["obs"]},
    )

    pj_constituida = SelectField(
        "Existe Pessoa Jurídica constituída?",
        choices=[(True, "Sim"), (False, "Não")],
        validators=[InputRequired()],
        coerce=bool,
    )

    repres_legal = SelectField(
        "O atendido é o representante legal?",
        choices=[(True, "Sim"), (False, "Não")],
        validators=[InputRequired()],
        default=True,
        coerce=bool,
    )

    # Representative legal data fields
    nome_repres_legal = StringField(
        "Nome do representante legal:",
        validators=[
            RequiredIf(
                "repres_legal",
                False,
                message=MSG_NaoPodeEstarEmBranco.format(
                    "O Nome do representante legal"
                ),
                pj_constituida=True,
            ),
            Length(
                max=FIELD_LIMITS["nome"],
                message=f"O nome não pode conter mais de {FIELD_LIMITS['nome']} caracteres!",
            ),
        ],
        render_kw={"maxlength": FIELD_LIMITS["nome"]},
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
        render_kw={"maxlength": FIELD_LIMITS["cpf"]},
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
        render_kw={"maxlength": FIELD_LIMITS["telefone"], "inputmode": "tel"},
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
        render_kw={"maxlength": FIELD_LIMITS["rg"]},
    )

    nascimento_repres_legal = DateField(
        "Data de nascimento do representante legal",
        validators=[Optional()],
    )

    pretende_constituir_pj = SelectField(
        "Pretende-se constituir Pessoa Jurídica?",
        choices=[(True, "Sim"), (False, "Não")],
        validators=[Optional()],
        coerce=bool,
    )

    def _postprocess_data(self) -> dict[str, Any]:
        result = dict(self.data)
        boolean_fields = [
            "procurou_outro_local",
            "pj_constituida",
            "repres_legal",
            "pretende_constituir_pj",
        ]

        for key in boolean_fields:
            if key in result:
                result[key] = "1" if bool(result[key]) else "0"

        if "obs_atendido" in result:
            result["obs"] = result.pop("obs_atendido")

        return result
