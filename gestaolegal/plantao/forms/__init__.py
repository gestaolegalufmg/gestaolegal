from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    HiddenField,
    SubmitField,
    TimeField,
)
from wtforms.validators import (
    DataRequired,
    ValidationError,
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
FIELD_LIMITS = {
    "nome": 80,
    "cpf": 14,
    "cnpj": 18,
    "telefone": 18,
    "celular": 18,
    "areajuridica": 80,
    "comoconheceu": 80,
    "indicacaoOrgao": 80,
    "procurouOutroLocal": 80,
    "obs": 1000,
    "logradouro": 100,
    "numero": 8,
    "complemento": 100,
    "bairro": 100,
    "cep": 9,
    "profissao": 80,
    "sit_receita": 100,
    "qual_veiculo": 100,
    "ano_veiculo": 5,
    "rg": 50,
    "sede_outros": 100,
    "qts_func": 7,
    "descricao": 2000,
}


#####################################################
############### CUSTOM VALIDATORS ###################
#####################################################


class RequiredIf:
    """
    Custom validator that makes a field required based on another field's value.
    Modern replacement for the old RequiredIf validator.
    """

    def __init__(self, fieldname, value=None, message=None, **kwargs):
        self.fieldname = fieldname
        self.value = value
        self.message = message
        self.kwargs = kwargs

    def __call__(self, form, field):
        other_field = form._fields.get(self.fieldname)
        if other_field is None:
            raise Exception(f'No field named "{self.fieldname}" in form')

        # Check if multiple conditions need to be met
        conditions_met = True

        # Check main fieldname condition
        if self.value is not None:
            if other_field.data != self.value:
                conditions_met = False
        else:
            if not other_field.data:
                conditions_met = False

        # Check additional kwargs conditions
        for kwarg_fieldname, kwarg_value in self.kwargs.items():
            kwarg_field = form._fields.get(kwarg_fieldname)
            if kwarg_field and kwarg_field.data != kwarg_value:
                conditions_met = False
                break

        if conditions_met and not field.data:
            message = self.message or "This field is required."
            raise ValidationError(message)


class RequiredIfInputRequired(RequiredIf):
    """
    Similar to RequiredIf but for numeric fields that need InputRequired behavior.
    """

    def __call__(self, form, field):
        other_field = form._fields.get(self.fieldname)
        if other_field is None:
            raise Exception(f'No field named "{self.fieldname}" in form')

        if other_field.data == self.value and field.data is None:
            message = self.message or "This field is required."
            raise ValidationError(message)


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
