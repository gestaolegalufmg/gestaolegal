from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    HiddenField,
    SubmitField,
    TimeField,
)
from wtforms.validators import (
    DataRequired,
)

#####################################################
##################### CONSTANTS ####################
#####################################################

orientacao_AdminOuCivil = {
    "ADMINISTRADOR": ("adm", "Administrador"),
    "CIVEL": ("civ", "Cível"),
}

# Error messages
MSG_NaoPodeEstarEmBranco = "{} não pode estar em branco!"
MSG_SelecioneUmaOpcaoLista = "Por favor selecione uma opção de {} da lista"
MSG_EscolhaUmaData = "Por favor, escolha uma data {}"

# Field length limits


#####################################################
#################### FORMS ##########################
#####################################################


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


#####################################################
################ UTILITY FUNCTIONS #################
#####################################################


def convert_boolean_fields(form_data):
    """
    Utility function to convert string boolean values to actual booleans.
    Use this in your view functions to handle the boolean field conversions.

    Example usage:
        if form.validate_on_submit():
            data = convert_boolean_fields(form.data)
            # Now use 'data' instead of 'form.data'
    """
    boolean_fields = [
        "encaminhar_outras_aj",
        "procurou_outro_local",
        "pj_constituida",
        "repres_legal",
        "pretende_constituir_pj",
        "possui_outros_imoveis",
        "possui_veiculos",
        "sede_bh",
        "negocio_nascente",
    ]

    converted_data = form_data.copy()

    for field in boolean_fields:
        if field in converted_data:
            if converted_data[field] == "True":
                converted_data[field] = True
            elif converted_data[field] == "False":
                converted_data[field] = False

    return converted_data
