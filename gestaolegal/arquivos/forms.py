from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length


class ArquivoForm(FlaskForm):
    titulo = StringField(
        "Título",
        validators=[
            InputRequired("Campo obrigatório"),
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
    submit = SubmitField("Enviar")
