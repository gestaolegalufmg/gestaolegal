from flask_wtf import FlaskForm
from wtforms import SelectField, SelectMultipleField, StringField, SubmitField
from wtforms.validators import Email, InputRequired, Length

from gestaolegal.common.constants import (
    FIELD_LIMITS,
    assistencia_jud_areas_atendidas,
    assistencia_jud_regioes,
)
from gestaolegal.forms.plantao.base_form_mixin import BaseFormMixin
from gestaolegal.forms.usuario import (
    EnderecoFieldsMixin,
)


class AssistenciaJudiciariaForm(EnderecoFieldsMixin, BaseFormMixin, FlaskForm):
    nome = StringField(
        "Nome",
        validators=[
            InputRequired(),
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
        validators=[InputRequired()],
    )

    telefone = StringField(
        "Telefone",
        validators=[
            InputRequired(),
            Length(
                max=FIELD_LIMITS["telefone"],
                message=f"Por favor, use no máximo {FIELD_LIMITS['telefone']} caracteres para o telefone.",
            ),
        ],
    )

    email = StringField(
        "Email",
        validators=[
            InputRequired(),
            Email("Por favor, insira um email válido."),
        ],
    )

    regiao = SelectField(
        "Região",
        choices=[
            (assistencia_jud_regioes[key][0], assistencia_jud_regioes[key][1])
            for key in assistencia_jud_regioes
        ],
        validators=[InputRequired()],
    )

    submit = SubmitField("Cadastrar")
