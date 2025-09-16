from typing import Any

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    HiddenField,
    SubmitField,
    TimeField,
)
from wtforms.validators import (
    InputRequired,
)

from .base_form_mixin import BaseFormMixin

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
