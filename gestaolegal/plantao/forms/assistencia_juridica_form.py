from wtforms import SelectField, SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from gestaolegal.plantao.forms import FIELD_LIMITS
from gestaolegal.plantao.models import assistencia_jud_areas_atendidas, assistencia_jud_regioes
from gestaolegal.usuario.forms import EnderecoForm, MSG_NaoPodeEstarEmBranco, MSG_SelecioneUmaOpcaoLista


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
                max=FIELD_LIMITS["celular"],
                message=f"Por favor, use no máximo {FIELD_LIMITS['celular']} caracteres para o telefone.",
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

