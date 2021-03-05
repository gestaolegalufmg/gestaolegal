from flask_wtf import FlaskForm
from wtforms import HiddenField, SubmitField, SelectField, StringField, TextAreaField, DateField, FileField, FloatField
from wtforms.validators import InputRequired, DataRequired, Optional
from gestaolegaldaj.plantao.forms import area_do_direito, assistencia_jud_areas_atendidas
from gestaolegaldaj.casos.models import situacao_deferimento

class CasoForm(FlaskForm):
    clientes     = HiddenField(validators=[InputRequired('Por favor, selecione pelo menos um cliente para associar ao caso')])
    area_direito = SelectField('Área do Direito', choices=[(assistencia_jud_areas_atendidas[key][0],assistencia_jud_areas_atendidas[key][1]) for key in assistencia_jud_areas_atendidas])
    descricao    = TextAreaField('Descrição')
    submit       = SubmitField('Enviar')

class EditarCasoForm(FlaskForm):
    orientador   = HiddenField()
    estagiario   = HiddenField()
    colaborador  = HiddenField()
    area_direito = SelectField('Área do Direito', choices=[(assistencia_jud_areas_atendidas[key][0],assistencia_jud_areas_atendidas[key][1]) for key in assistencia_jud_areas_atendidas])
    descricao    = TextAreaField('Descrição')
    situacao_deferimento_ativo = SelectField('Status do caso', choices=[
                                                                        ('ativo','Ativo'),
                                                                        ('arquivado','Arquivado'),
                                                                        ('solucionado', 'Solucionado')
                                                                    ],
                                                                validators = [Optional()])
    situacao_deferimento_indeferido = SelectField('Status do caso', choices=[
                                                                             ('indeferido','Indeferido'),
                                                                             ('ativo','Ativo')
                                                                        ],
                                                                    validators = [Optional()])

class RoteiroForm(FlaskForm):
    area_direito = SelectField('Área do Direito', choices=[(assistencia_jud_areas_atendidas[key][0],assistencia_jud_areas_atendidas[key][1]) for key in assistencia_jud_areas_atendidas], validators=[InputRequired('Campo obrigaatório')])
    link         = StringField('Link para o roteiro (http://exemplo.com.br)')
    submit       = SubmitField('Atualizar')

class JustificativaIndeferimento(FlaskForm):
    justificativa = TextAreaField("Justificativa para o indeferimento do caso",validators=[DataRequired()])
    submit        = SubmitField('Enviar') 

class LembreteForm(FlaskForm):
    usuarios   = HiddenField(validators=[InputRequired('Por favor, selecione pelo menos um usuário')])
    lembrete = TextAreaField("Descrião da tarefa",validators=[DataRequired()])
    data = DateField('Data de notificação', validators= [DataRequired()])
    submit       = SubmitField('Enviar')

class ProcessoForm(FlaskForm):
    especie                  = SelectField('Espécie',
                                        choices=[
                                                ('judicial', 'Judicial'),
                                                ('extrajudicial', 'Extrajudicial')
                                            ],
                                        validators=[DataRequired("Por favor selecione uma opção de espécie da lista")]
                                        )
    numero                   = FloatField('Número')
    identificacao            = StringField('Identificação')
    vara                     = StringField('Vara, unidade jurisdicional, turma e/ou câmara')
    link                     = StringField('Link')
    probabilidade            = SelectField('Probabilidade de Ganho',
                            choices=[
                                    ('possivel','Possível'),
                                    ('provavel','Provável'),
                                    ('remota','Remota')
                                ]
                            )   
    posicao_assistido        = SelectField('Posição do Assistido',
                                choices=[
                                        ('autor','Autor'),
                                        ('reu','Réu'),
                                        ('terceiro','Terceiro'),
                                        ('interessado','Interessado')
                                    ]
                                )
    valor_causa              = FloatField('Valor da Causa')
    data_distribuicao        = DateField('Data da distribuição')
    data_transito_em_julgado = DateField('Data do trânsito em julgado')
    obs                      = TextAreaField('Observações')
    submit                   = SubmitField('Associar Processo')

class EventoForm(FlaskForm):
    usuario   = HiddenField()
    tipo                   = SelectField('Tipo de Evento',
                                choices=[
                                        ('contato','Contato'),
                                        ('reuniao','Reunião'),
                                        ('protocolo_peticao','Protocolo de Petição'),
                                        ('diligencia_externa','Diligência Externa'),
                                        ('audiencia','Audiência'),
                                        ('conciliacao','Conciliação'),
                                        ('decisao_judicial','Decisão Judicial'),
                                        ('redist_caso','Redistribuição do Caso'),
                                        ('encerramento_caso','Encerramento do Caso'),
                                        ('outros','Outros')
                                    ],
                                validators=[InputRequired('Por favor, selecione pelo menos uma opção')]
                            )
    data_evento            = DateField('Data do Ocorrido', validators=[InputRequired('Por favor, selecione uma data')])
    descricao              = TextAreaField('Descrição do Evento', validators=[InputRequired('Por favor, selecione pelo menos uma opção')])
    arquivo                = FileField('Anexar arquivo')
    submit                 = SubmitField('Enviar')