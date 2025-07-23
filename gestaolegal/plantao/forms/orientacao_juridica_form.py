from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField
from wtforms.validators import AnyOf, DataRequired, InputRequired, Length, Optional

from gestaolegal.common.constants import area_do_direito
from gestaolegal.plantao.forms import FIELD_LIMITS, RequiredIf
from gestaolegal.plantao.models import se_administrativo, se_civel
from gestaolegal.usuario.forms import MSG_SelecioneUmaOpcaoLista


class OrientacaoJuridicaForm(FlaskForm):
    area_direito = SelectField(
        "Área do Direito",
        choices=[
            (area_do_direito["AMBIENTAL"][0], area_do_direito["AMBIENTAL"][1]),
            (
                area_do_direito["ADMINISTRATIVO"][0],
                area_do_direito["ADMINISTRATIVO"][1],
            ),
            (area_do_direito["CIVEL"][0], area_do_direito["CIVEL"][1]),
            (area_do_direito["EMPRESARIAL"][0], area_do_direito["EMPRESARIAL"][1]),
            (area_do_direito["PENAL"][0], area_do_direito["PENAL"][1]),
            (area_do_direito["TRABALHISTA"][0], area_do_direito["TRABALHISTA"][1]),
        ],
        validators=[
            DataRequired(MSG_SelecioneUmaOpcaoLista.format("da área do direito")),
            AnyOf(
                [area_do_direito[key][0] for key in area_do_direito],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    sub_area = SelectField(
        "Sub-área Cível",
        choices=[
            (se_civel["CONSUMIDOR"][0], se_civel["CONSUMIDOR"][1]),
            (se_civel["CONTRATOS"][0], se_civel["CONTRATOS"][1]),
            (se_civel["FAMILIA"][0], se_civel["FAMILIA"][1]),
            (se_civel["REAIS"][0], se_civel["REAIS"][1]),
            (
                se_civel["RESPONSABILIDADE_CIVIL"][0],
                se_civel["RESPONSABILIDADE_CIVIL"][1],
            ),
            (se_civel["SUCESSOES"][0], se_civel["SUCESSOES"][1]),
        ],
        validators=[
            RequiredIf(
                "area_direito",
                area_do_direito["CIVEL"][0],
                message=MSG_SelecioneUmaOpcaoLista.format("da sub-área Cível"),
            ),
            AnyOf(
                [se_civel[key][0] for key in se_civel],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    sub_areaAdmin = SelectField(
        "Sub-área Administrativo",
        choices=[
            (
                se_administrativo["ADMINISTRATIVO"][0],
                se_administrativo["ADMINISTRATIVO"][1],
            ),
            (
                se_administrativo["PREVIDENCIARIO"][0],
                se_administrativo["PREVIDENCIARIO"][1],
            ),
            (se_administrativo["TRIBUTARIO"][0], se_administrativo["TRIBUTARIO"][1]),
        ],
        validators=[
            RequiredIf(
                "area_direito",
                area_do_direito["ADMINISTRATIVO"][0],
                message=MSG_SelecioneUmaOpcaoLista.format("da sub-área Administrativo"),
            ),
            AnyOf(
                [se_administrativo[key][0] for key in se_administrativo],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    descricao = TextAreaField(
        "Breve descrição da Orientação Jurídica dada",
        validators=[
            Optional(),
            Length(
                max=FIELD_LIMITS["descricao"],
                message=f"A descrição não pode conter mais de {FIELD_LIMITS['descricao']} caracteres!",
            ),
        ],
    )


class CadastroOrientacaoJuridicaForm(OrientacaoJuridicaForm):
    encaminhar_outras_aj = SelectField(
        "Encaminhamento para outras Assistências Judiciárias",
        choices=[("True", "Sim"), ("False", "Não")],
        validators=[
            InputRequired(
                MSG_SelecioneUmaOpcaoLista.format(
                    'de "Encaminhamento para outras Assistências Judiciárias"'
                )
            )
        ],
        default="False",
    )

    def validate_encaminhar_outras_aj(self, field):
        """Custom validation to convert string to boolean."""
        if field.data == "True":
            field.data = True
        elif field.data == "False":
            field.data = False
