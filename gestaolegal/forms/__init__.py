from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    FloatField,
    HiddenField,
    SubmitField,
    TimeField,
    ValidationError,
)
from wtforms.validators import InputRequired

from gestaolegal.forms.base_form_mixin import BaseFormMixin

MSG_NaoPodeEstarEmBranco = "{} não pode estar em branco!"
MSG_SelecioneUmaOpcaoLista = "Por favor seleciona uma opção de {} da lista"
MSG_EscolhaUmaData = "Por favor, escolha uma data {}"

max_nome = 80
max_rg = 18
max_cpf = 14
max_profissao = 45
max_telefone = 18
max_celular = 18
max_obs = 1000
max_oab = 30
max_matricula = 45
max_suplente = 30
max_ferias = 150
max_logradouro = 100
max_numero = 8
max_complemento = 100
max_bairro = 100
max_cep = 9
max_cidade = 100
max_estado = 30
max_horario_atendimento = 30


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


class MyFloatField(FloatField):
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = float(valuelist[0].replace(",", "."))
            except ValueError:
                self.data = None
                raise ValueError(self.gettext("Not a valid float value"))


class AbrirPlantaoForm(BaseFormMixin, FlaskForm):
    data_abertura = DateField("Data de abertura", validators=[InputRequired()])

    hora_abertura = TimeField("Horário de Abertura", validators=[InputRequired()])


class SelecionarDuracaoPlantaoForm(BaseFormMixin, FlaskForm):
    hdnDiasEscolhidos = HiddenField("Dias escolhidos")
    hdnDataAbertura = HiddenField("Data de abertura")
    hdnDataFechamento = HiddenField("Data de fechamento")
    hdnHoraAbertura = HiddenField("Hora de abertura")
    hdnHoraFechamento = HiddenField("Hora de fechamento")
    submit = SubmitField("Confirmar")


class FecharPlantaoForm(BaseFormMixin, FlaskForm):
    data_fechamento = DateField(
        "Data de fechamento",
        validators=[InputRequired()],
    )

    hora_fechamento = TimeField(
        "Horário de fechamento",
        validators=[InputRequired()],
    )
