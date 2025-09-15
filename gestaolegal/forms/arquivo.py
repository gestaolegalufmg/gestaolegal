from flask_wtf import FlaskForm
from wtforms import FileField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length

from gestaolegal.forms.plantao.base_form_mixin import BaseFormMixin


class ArquivoForm(BaseFormMixin, FlaskForm):
    titulo = StringField(
        "Título",
        validators=[
            InputRequired(),
            Length(
                max=150,
                message="O título do arquivo deve ter até 150 caracteres de comprimento",
            ),
        ],
    )
    descricao = TextAreaField(
        "Descrição",
        validators=[
            Length(max=8000, message="A descrição deve no máximo 8000 caracteres")
        ],
    )
    arquivo = FileField("Arquivo")
