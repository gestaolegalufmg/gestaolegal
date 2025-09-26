from typing import Any

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    FloatField,
    HiddenField,
    SubmitField,
    TimeField,
)
from wtforms.validators import (
    InputRequired,
    ValidationError,
)

from gestaolegal.forms.base_form_mixin import BaseFormMixin

orientacao_AdminOuCivil = {
    "ADMINISTRADOR": ("adm", "Administrador"),
    "CIVEL": ("civ", "Cível"),
}

# Error messages
MSG_NaoPodeEstarEmBranco = "{} não pode estar em branco!"
MSG_SelecioneUmaOpcaoLista = "Por favor selecione uma opção de {} da lista"
MSG_EscolhaUmaData = "Por favor, escolha uma data {}"

# Field length limits
