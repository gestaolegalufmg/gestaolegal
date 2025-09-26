from typing import Any

from flask import flash
from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    AnyOf,
    Email,
    InputRequired,
    Length,
    Optional,
    ValidationError,
)

from gestaolegal.common.constants import (
    UserRole,
    estado_civilUsuario,
    sexo_usuario,
    tipo_bolsaUsuario,
)
from gestaolegal.forms import (
    MSG_EscolhaUmaData,
    MSG_SelecioneUmaOpcaoLista,
    RequiredIf,
    max_celular,
    max_cpf,
    max_ferias,
    max_horario_atendimento,
    max_matricula,
    max_nome,
    max_oab,
    max_obs,
    max_profissao,
    max_rg,
    max_suplente,
    max_telefone,
)
from gestaolegal.forms.base_form_mixin import BaseFormMixin
from gestaolegal.forms.endereco_form_mixin import EnderecoFieldsMixin


class EditarUsuarioForm(EnderecoFieldsMixin, BaseFormMixin, FlaskForm):
    def validaData(form, field):
        if field.data <= form.data_entrada.data:
            flash("A data de saída deve ser posterior à data de entrada.", "warning")
            raise ValidationError(
                "A data de saída deve ser posterior à data de entrada."
            )

    def validaDatadaBolsa(form, field):
        if field.data <= form.inicio_bolsa.data:
            flash(
                "A data de fim da bolsa deve ser posterior à data de início.", "warning"
            )
            raise ValidationError(
                "A data de fim da bolsa deve ser posterior à data de início."
            )

    nome = StringField(
        "Nome",
        validators=[
            InputRequired(),
            Length(
                max=max_nome,
                message="O nome não pode conter mais de {} caracteres!".format(
                    max_nome
                ),
            ),
        ],
    )

    email = StringField(
        "Endereço de e-mail",
        validators=[
            InputRequired(),
            Email(
                "Formato de email inválido! Certifique-se de que ele foi digitado corretamente."
            ),
        ],
    )

    urole = SelectField(
        "Função no sistema",
        choices=[
            (UserRole.USER, "Usuário"),
            (UserRole.ADMINISTRADOR, "Administrador"),
            (UserRole.ORIENTADOR, "Orientador"),
            (UserRole.COLAB_PROJETO, "Colaborador de projeto"),
            (UserRole.ESTAGIARIO_DIREITO, "Estagiário de Direito"),
            (UserRole.COLAB_EXTERNO, "Colaborador externo"),
            (UserRole.PROFESSOR, "Professor"),
        ],
        validators=[
            InputRequired(),
            AnyOf(
                [role.value for role in UserRole],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    sexo = SelectField(
        "Sexo",
        choices=[
            (sexo_usuario["MASCULINO"][0], sexo_usuario["MASCULINO"][1]),
            (sexo_usuario["FEMININO"][0], sexo_usuario["FEMININO"][1]),
            (sexo_usuario["OUTROS"][0], sexo_usuario["OUTROS"][1]),
        ],
        validators=[
            InputRequired(),
            AnyOf(
                [sexo_usuario[key][0] for key in sexo_usuario],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    rg = StringField(
        "RG",
        validators=[
            InputRequired(),
            Length(
                max=max_rg,
                message="Por favor, use no máximo {} caracteres para o RG.".format(
                    max_rg
                ),
            ),
        ],
    )

    cpf = StringField(
        "CPF",
        validators=[
            Optional(),
            Length(
                max=max_cpf,
                message="Por favor, use no máximo {} caracteres para o CPF.".format(
                    max_cpf
                ),
            ),
        ],
    )

    profissao = StringField(
        "Profissão",
        validators=[
            InputRequired(),
            Length(
                max=max_profissao,
                message="Por favor, use no máximo {} caracteres para descrever a profissão.".format(
                    max_profissao
                ),
            ),
        ],
    )

    estado_civil = SelectField(
        "Estado civil",
        choices=[
            (estado_civilUsuario["SOLTEIRO"][0], estado_civilUsuario["SOLTEIRO"][1]),
            (estado_civilUsuario["CASADO"][0], estado_civilUsuario["CASADO"][1]),
            (
                estado_civilUsuario["DIVORCIADO"][0],
                estado_civilUsuario["DIVORCIADO"][1],
            ),
            (estado_civilUsuario["VIUVO"][0], estado_civilUsuario["VIUVO"][1]),
            (estado_civilUsuario["SEPARADO"][0], estado_civilUsuario["SEPARADO"][1]),
            (estado_civilUsuario["UNIAO"][0], estado_civilUsuario["UNIAO"][1]),
        ],
        validators=[
            InputRequired(),
            AnyOf(
                [estado_civilUsuario[key][0] for key in estado_civilUsuario],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )

    nascimento = DateField(
        "Data de nascimento",
        validators=[InputRequired()],
    )

    telefone = StringField(
        "Telefone fixo",
        validators=[
            Optional(),
            Length(
                max=max_telefone,
                message="Por favor, use no máximo {} caracteres para o telefone fixo.".format(
                    max_telefone
                ),
            ),
        ],
    )

    celular = StringField(
        "Telefone celular",
        validators=[
            InputRequired(),
            Length(
                max=max_celular,
                message="Por favor, use no máximo {} caracteres para o telefone celular.".format(
                    max_celular
                ),
            ),
        ],
    )

    obs = TextAreaField(
        "Fichas e observações",
        validators=[
            Optional(),
            Length(
                max=max_obs,
                message="Por favor, use no máximo {} caracteres para as observações.".format(
                    max_obs
                ),
            ),
        ],
    )

    oab = StringField(
        "OAB",
        validators=[
            Optional(),
            Length(
                max=max_oab,
                message="Por favor, use no máximo {} caracteres para o número da OAB.".format(
                    max_oab
                ),
            ),
        ],
    )

    data_entrada = DateField(
        "Data de entrada",
        validators=[InputRequired()],
    )
    data_saida = DateField("Data de saída", validators=[Optional(), validaData])

    matricula = StringField(
        "Matrícula",
        validators=[
            Optional(),
            Length(
                max=max_matricula,
                message="Por favor, use no máximo {} caracteres para o número de matrícula.".format(
                    max_matricula
                ),
            ),
        ],
    )

    bolsista = SelectField(
        "É bolsista?",
        choices=[(True, "Sim"), (False, "Não")],
        coerce=bool,
        validators=[InputRequired()],
    )

    tipo_bolsa = SelectField(
        "Tipo de bolsa",
        choices=[
            (tipo_bolsaUsuario["FUMP"][0], tipo_bolsaUsuario["FUMP"][1]),
            (tipo_bolsaUsuario["VALE"][0], tipo_bolsaUsuario["VALE"][1]),
            (tipo_bolsaUsuario["PROEX"][0], tipo_bolsaUsuario["PROEX"][1]),
            (tipo_bolsaUsuario["OUTRA"][0], tipo_bolsaUsuario["OUTRA"][1]),
        ],
        validators=[
            RequiredIf(
                "bolsista",
                True,
                message=MSG_SelecioneUmaOpcaoLista.format("fim da bolsa"),
            ),
            AnyOf(
                [tipo_bolsaUsuario[key][0] for key in tipo_bolsaUsuario],
                message="Desculpe, ocorreu um erro. Por favor, atualize a página.",
            ),
        ],
    )
    #     #TODO
    #     #dia_atendimento     = DateField('Dia em que realizará atendimento', validators=[Optional()])
    horario_atendimento = StringField(
        "Dia da semana e horário de atendimento",
        validators=[
            Optional(),
            Length(
                max=max_horario_atendimento,
                message='Por favor, use no máximo {} caracteres para o campo "Dia da Semana e Horário de Atendimento".'.format(
                    max_horario_atendimento
                ),
            ),
        ],
    )

    suplente = StringField(
        "Suplente",
        validators=[
            Optional(),
            Length(
                max=max_suplente,
                message="Por favor, use no máximo {} caracteres para o campo suplente.".format(
                    max_suplente
                ),
            ),
        ],
    )

    ferias = StringField(
        "Férias",
        validators=[
            Optional(),
            Length(
                max=max_ferias,
                message="Por favor, use no máximo {} caracteres para as férias.".format(
                    max_ferias
                ),
            ),
        ],
    )

    cert_atuacao_DAJ = SelectField(
        "Usuário faz jus ao certificado de atuação na DAJ?",
        choices=[("sim", "Sim"), ("nao", "Não")],
        validators=[InputRequired()],
    )

    inicio_bolsa = DateField(
        "Data de início da bolsa",
        validators=[
            RequiredIf(
                "bolsista",
                True,
                message=MSG_EscolhaUmaData.format("de início da bolsa"),
            )
        ],
    )
    fim_bolsa = DateField(
        "Data de fim da bolsa", validators=[Optional(), validaDatadaBolsa]
    )

    def _postprocess_data(self) -> dict[str, Any]:
        result = dict(self.data)
        return result


class CadastrarUsuarioForm(EditarUsuarioForm):
    senha = PasswordField(
        "Senha",
        validators=[
            InputRequired(),
        ],
    )

    confirmacao = PasswordField(
        "Confirme a senha",
        validators=[
            InputRequired(),
        ],
    )

    submit = SubmitField("Cadastrar")


class EditarSenhaForm(BaseFormMixin, FlaskForm):
    senha = PasswordField(
        "Nova senha",
        validators=[
            InputRequired(),
        ],
        render_kw={"placeholder": "Escolha uma senha segura", "maxlength": "60"},
    )

    confirmacao = PasswordField(
        "Confirme sua senha",
        validators=[
            InputRequired(),
        ],
        render_kw={"placeholder": "Confirme sua senha", "maxlength": "60"},
    )
