from flask_wtf import FlaskForm
from wtforms import (DateField, SelectField, StringField, SubmitField,
                     TextAreaField, TimeField, PasswordField, HiddenField)
from wtforms.validators import AnyOf, DataRequired, Email, Length, Optional, InputRequired
from gestaolegal.usuario.models import sexo_usuario, estado_civilUsuario, tipo_bolsaUsuario, usuario_urole_roles
from gestaolegal.utils.forms import RequiredIf

#####################################################
################## CONSTANTES #######################
#####################################################

MSG_NaoPodeEstarEmBranco   = "{} não pode estar em branco!"
MSG_SelecioneUmaOpcaoLista = "Por favor seleciona uma opção de {} da lista"
MSG_EscolhaUmaData         = "Por favor, escolha uma data {}"

max_nome                = 80
max_rg                  = 18
max_cpf                 = 14
max_profissao           = 45
max_telefone            = 18
max_celular             = 18
max_obs                 = 1000
max_oab                 = 30
max_matricula           = 45
max_suplente            = 30
max_ferias              = 150
max_logradouro          = 100
max_numero              = 8
max_complemento         = 100
max_bairro              = 100
max_cep                 = 9
max_cidade              = 100
max_estado              = 30
max_horario_atendimento = 30

#####################################################
################## FORMS ############################
#####################################################

class EnderecoForm(FlaskForm):
    logradouro          = StringField('Logradouro',
                                    validators=[
                                        DataRequired(MSG_NaoPodeEstarEmBranco.format('O logradouro')),
                                        Length(max=max_logradouro, message="Por favor, use no máximo {} caracteres para o logradouro.".format(max_logradouro))
                                        ]
                                    )

    numero              = StringField('Número',
                                    validators=[
                                        DataRequired(MSG_NaoPodeEstarEmBranco.format('O numero')),
                                        Length(max=max_numero, message="Por favor, use no máximo {} caracteres para o número.".format(max_numero))
                                        ]
                                    )

    complemento         = StringField('Complemento',
                                    validators=[
                                        Optional(),
                                        Length(max=max_complemento, message="Por favor, use no máximo {} caracteres para o complemento.".format(max_complemento))
                                        ]
                                    )

    bairro              = StringField('Bairro',
                                    validators=[
                                        DataRequired(MSG_NaoPodeEstarEmBranco.format('O bairro')),
                                        Length(max=max_bairro, message="Por favor, use no máximo {} caracteres para o bairro.".format(max_bairro))
                                        ]
                                    )

    cep                 = StringField('CEP',
                                    validators=[
                                        DataRequired(MSG_NaoPodeEstarEmBranco.format('O CEP')),
                                        Length(max=max_cep, message="Por favor, use no máximo {} caracteres para o CEP.".format(max_cep))
                                        ]
                                    )

    cidade              = StringField('Cidade',
                                    validators=[
                                        DataRequired(MSG_NaoPodeEstarEmBranco.format('A cidade')),
                                        Length(max=max_cidade, message="Por favor, use no máximo {} caracteres para o nome da cidade.".format(max_cidade))
                                        ]
                                    )

    id_cidade           = HiddenField()

    estado              = StringField('Estado',
                                    validators=[
                                        DataRequired(MSG_NaoPodeEstarEmBranco.format('A cidade')),
                                        Length(max=max_estado, message="Por favor, use no máximo {} caracteres para o estado".format(max_estado))
                                        ]
                                    )
    
    id_estado           = HiddenField()

class EditarUsuarioForm(EnderecoForm):
    nome                = StringField('Nome',
                                    validators=[
                                        DataRequired(MSG_NaoPodeEstarEmBranco.format('O nome')),
                                        Length(max=max_nome, message="O nome não pode conter mais de {} caracteres!".format(max_nome))
                                        ]
                                    )

    email               = StringField('Endereço de e-mail',
                                    validators=[
                                        DataRequired(MSG_NaoPodeEstarEmBranco.format('O email')),
                                        Email("Formato de email inválido! Certifique-se de que ele foi digitado corretamente.")
                                        ]
                                    )

    urole               = SelectField('Função no sistema',
                                    choices=[
                                            (usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['ADMINISTRADOR'][1]),
                                            (usuario_urole_roles['ORIENTADOR'][0], usuario_urole_roles['ORIENTADOR'][1]),
                                            (usuario_urole_roles['COLAB_PROJETO'][0], usuario_urole_roles['COLAB_PROJETO'][1]),
                                            (usuario_urole_roles['ESTAGIARIO_DIREITO'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][1]),
                                            (usuario_urole_roles['COLAB_EXTERNO'][0], usuario_urole_roles['COLAB_EXTERNO'][1]),
                                            (usuario_urole_roles['PROFESSOR'][0], usuario_urole_roles['PROFESSOR'][1])
                                        ],
                                    validators=[
                                        DataRequired(MSG_SelecioneUmaOpcaoLista.format("urole")),
                                        AnyOf([usuario_urole_roles[key][0] for key in usuario_urole_roles],message="Desculpe, ocorreu um erro. Por favor, atualize a página.")
                                    ]
                                )

    sexo                = SelectField('Sexo',
                                    choices=[
                                        (sexo_usuario['MASCULINO'][0], sexo_usuario['MASCULINO'][1]),
                                        (sexo_usuario['FEMININO'][0], sexo_usuario['FEMININO'][1]),
                                        (sexo_usuario['OUTROS'][0],sexo_usuario['OUTROS'][1])
                                        ],
                                    validators=[
                                        DataRequired(MSG_SelecioneUmaOpcaoLista.format("sexo")),
                                        AnyOf([sexo_usuario[key][0] for key in sexo_usuario],message="Desculpe, ocorreu um erro. Por favor, atualize a página.")
                                        ]
                                    )

    rg                  = StringField('RG',
                                    validators=[
                                        DataRequired(MSG_NaoPodeEstarEmBranco.format('O RG')),
                                        Length(max=max_rg, message="Por favor, use no máximo {} caracteres para o RG.".format(max_rg))
                                    ]
                                )

    cpf                 = StringField('CPF',
                                    validators=[
                                        DataRequired(MSG_NaoPodeEstarEmBranco.format('O CPF')),
                                        Length(max=max_cpf, message="Por favor, use no máximo {} caracteres para o CPF.".format(max_cpf))
                                        ]
                                    )

    profissao           = StringField('Profissão',
                                    validators=[
                                        DataRequired(MSG_NaoPodeEstarEmBranco.format('A profissão')),
                                        Length(max=max_profissao, message="Por favor, use no máximo {} caracteres para descrever a profissão.".format(max_profissao))
                                        ]
                                    )

    estado_civil        = SelectField('Estado civil',
                                    choices=[
                                        (estado_civilUsuario['SOLTEIRO'][0],estado_civilUsuario['SOLTEIRO'][1]),
                                        (estado_civilUsuario['CASADO'][0],estado_civilUsuario['CASADO'][1]),
                                        (estado_civilUsuario['DIVORCIADO'][0],estado_civilUsuario['DIVORCIADO'][1]),
                                        (estado_civilUsuario['VIUVO'][0],estado_civilUsuario['VIUVO'][1]),
                                        (estado_civilUsuario['SEPARADO'][0],estado_civilUsuario['SEPARADO'][1]),
                                        (estado_civilUsuario['UNIAO'][0],estado_civilUsuario['UNIAO'][1])
                                        ],
                                    validators=[
                                        DataRequired(MSG_SelecioneUmaOpcaoLista.format("estado civil")),
                                        AnyOf([estado_civilUsuario[key][0] for key in estado_civilUsuario], message="Desculpe, ocorreu um erro. Por favor, atualize a página.")
                                        ]
                                    )

    nascimento          = DateField('Data de nascimento',
                                    validators=[DataRequired(MSG_EscolhaUmaData.format("de nascimento"))]
                                    )

    telefone            = StringField('Telefone fixo',
                                    validators=[
                                        Optional(),
                                        Length(max=max_telefone, message="Por favor, use no máximo {} caracteres para o telefone fixo.".format(max_telefone))
                                        ]
                                    )

    celular             = StringField('Telefone celular',
                                    validators=[
                                        DataRequired(MSG_NaoPodeEstarEmBranco.format('O telefone celular')),
                                        Length(max=max_celular, message="Por favor, use no máximo {} caracteres para o telefone celular.".format(max_celular))
                                        ]
                                    )

    obs                 = TextAreaField('Fichas e observações',
                                        validators=[
                                            Optional(),
                                            Length(max=max_obs, message="Por favor, use no máximo {} caracteres para as observações.".format(max_obs))
                                            ]
                                        )

    oab                 = StringField('OAB',
                                    validators=[
                                        Optional(),
                                        Length(max=max_oab, message="Por favor, use no máximo {} caracteres para o número da OAB.".format(max_oab))
                                        ]
                                    )

    data_entrada        = DateField('Data de entrada',
                                    validators=[DataRequired(MSG_EscolhaUmaData.format('de entrada'))]
                                    )
    data_saida          = DateField('Data de saída',
                                    validators=[Optional()]
                                    )

    matricula           = StringField('Matrícula',
                                    validators=[
                                        Optional(),
                                        Length(max=max_matricula, message="Por favor, use no máximo {} caracteres para o número de matrícula.".format(max_matricula))
                                        ]
                                    )

    bolsista            = SelectField('É bolsista?',
                                    choices=[
                                        (True,'Sim'),
                                        (False,'Não')
                                        ],
                                    coerce=lambda x: x == 'True', #https://stackoverflow.com/questions/33429510/wtforms-selectfield-not-properly-coercing-for-booleans
                                    validators=[InputRequired(MSG_SelecioneUmaOpcaoLista.format("é bolsista?"))]
                                )

    tipo_bolsa          = SelectField('Tipo de bolsa',
                                    choices=[
                                        (tipo_bolsaUsuario['FUMP'][0], tipo_bolsaUsuario['FUMP'][1]),
                                        (tipo_bolsaUsuario['VALE'][0], tipo_bolsaUsuario['VALE'][1]),
                                        (tipo_bolsaUsuario['PROEX'][0], tipo_bolsaUsuario['PROEX'][1]),
                                        (tipo_bolsaUsuario['OUTRA'][0], tipo_bolsaUsuario['OUTRA'][1])
                                        ],
                                    validators=[
                                        RequiredIf(bolsista=True, message=MSG_SelecioneUmaOpcaoLista.format('fim da bolsa')),
                                        AnyOf([tipo_bolsaUsuario[key][0] for key in tipo_bolsaUsuario], message="Desculpe, ocorreu um erro. Por favor, atualize a página.")
                                        ]
                                    )
#     #TODO
#     #dia_atendimento     = DateField('Dia em que realizará atendimento', validators=[Optional()])
    horario_atendimento = StringField('Dia da semana e horário de atendimento',
                                    validators=[Optional(),
                                                Length(max=max_horario_atendimento, message='Por favor, use no máximo {} caracteres para o campo "Dia da Semana e Horário de Atendimento".'.format(max_horario_atendimento))
                                                ]
                                )

    suplente            = StringField('Suplente',
                                    validators=[
                                        Optional(),
                                        Length(max=max_suplente, message="Por favor, use no máximo {} caracteres para o campo suplente.".format(max_suplente))
                                        ]
                                    )

    ferias              = StringField('Férias',
                                    validators=[
                                        Optional(),
                                        Length(max=max_ferias, message="Por favor, use no máximo {} caracteres para as férias.".format(max_ferias))
                                        ]
                                    )

    cert_atuacao_DAJ    = SelectField('Usuário faz jus ao certificado de atuação na DAJ?',
                                    choices=[
                                        ('sim','Sim'),
                                        ('nao','Não')
                                        ],
                                    validators=[DataRequired(MSG_SelecioneUmaOpcaoLista.format("atuação na DAJ"))]
                                )

    inicio_bolsa        = DateField('Data de início da bolsa',
                                    validators=[RequiredIf(bolsista=True, message=MSG_EscolhaUmaData.format('de início da bolsa'))]
                                )
    fim_bolsa           = DateField('Data de fim da bolsa',
                                    validators=[Optional()]
                                )

    senha               = HiddenField()# Não é usado no formulário, criado para o usuario_form.html funcionar

    confirmacao         = HiddenField()# Não é usado no formulário, criado para o usuario_form.html funcionar

    submit              = SubmitField('Alterar dados')


class CadastrarUsuarioForm(EditarUsuarioForm):
    senha               = PasswordField('Senha',
                                    validators=[
                                        DataRequired(MSG_NaoPodeEstarEmBranco.format('A senha')),
                                        ]

                                    )

    confirmacao         = PasswordField('Confirme a senha',
                                    validators=[
                                        DataRequired(MSG_NaoPodeEstarEmBranco.format('A confirmação de senha')),
                                        ]
                                    )

    id_cidade           = HiddenField()
    
    id_estado           = HiddenField()

    submit              = SubmitField('Cadastrar')
