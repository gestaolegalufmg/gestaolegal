from wtforms import StringField
from wtforms.validators import InputRequired, Length, Optional

from gestaolegal.forms import (
    max_bairro,
    max_cep,
    max_cidade,
    max_complemento,
    max_estado,
    max_logradouro,
    max_numero,
)


class EnderecoFieldsMixin:
    logradouro = StringField(
        "Logradouro",
        validators=[
            InputRequired(),
            Length(
                max=max_logradouro,
                message="Por favor, use no máximo {} caracteres para o logradouro.".format(
                    max_logradouro
                ),
            ),
        ],
    )

    numero = StringField(
        "Número",
        validators=[
            InputRequired(),
            Length(
                max=max_numero,
                message="Por favor, use no máximo {} caracteres para o número.".format(
                    max_numero
                ),
            ),
        ],
    )

    complemento = StringField(
        "Complemento",
        validators=[
            Optional(),
            Length(
                max=max_complemento,
                message="Por favor, use no máximo {} caracteres para o complemento.".format(
                    max_complemento
                ),
            ),
        ],
    )

    bairro = StringField(
        "Bairro",
        validators=[
            InputRequired(),
            Length(
                max=max_bairro,
                message="Por favor, use no máximo {} caracteres para o bairro.".format(
                    max_bairro
                ),
            ),
        ],
    )

    cep = StringField(
        "CEP",
        validators=[
            InputRequired(),
            Length(
                max=max_cep,
                message="Por favor, use no máximo {} caracteres para o CEP.".format(
                    max_cep
                ),
            ),
        ],
    )

    cidade = StringField(
        "Cidade",
        validators=[
            InputRequired(),
            Length(
                max=max_cidade,
                message="Por favor, use no máximo {} caracteres para o nome da cidade.".format(
                    max_cidade
                ),
            ),
        ],
    )

    estado = StringField(
        "Estado",
        validators=[
            InputRequired(),
            Length(
                max=max_estado,
                message="Por favor, use no máximo {} caracteres para o estado".format(
                    max_estado
                ),
            ),
        ],
    )
