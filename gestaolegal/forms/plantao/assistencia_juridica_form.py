from wtforms import SelectField, SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length

from gestaolegal.common.constants import (
    FIELD_LIMITS,
    assistencia_jud_areas_atendidas,
    assistencia_jud_regioes,
)
from gestaolegal.forms.usuario import (
    EnderecoForm,
    MSG_NaoPodeEstarEmBranco,
    MSG_SelecioneUmaOpcaoLista,
)


class AssistenciaJudiciariaForm(EnderecoForm):
    nome = StringField(
        "Nome",
        validators=[
            DataRequired(MSG_NaoPodeEstarEmBranco.format("O nome")),
            Length(
                max=FIELD_LIMITS["nome"],
                message=f"Por favor, use no máximo {FIELD_LIMITS['nome']} caracteres para o nome.",
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
        validators=[DataRequired("Escolha pelo menos uma área do Direito!")],
    )

    telefone = StringField(
        "Telefone",
        validators=[
            DataRequired(MSG_NaoPodeEstarEmBranco.format("O telefone")),
            Length(
                max=FIELD_LIMITS["telefone"],
                message=f"Por favor, use no máximo {FIELD_LIMITS['telefone']} caracteres para o telefone.",
            ),
        ],
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(MSG_NaoPodeEstarEmBranco.format("O email")),
            Email("Por favor, insira um email válido."),
        ],
    )

    regiao = SelectField(
        "Região",
        choices=[
            (assistencia_jud_regioes[key][0], assistencia_jud_regioes[key][1])
            for key in assistencia_jud_regioes
        ],
        validators=[DataRequired(MSG_SelecioneUmaOpcaoLista.format("uma região"))],
    )

    submit = SubmitField("Cadastrar")
