from flask_wtf import FlaskForm
from wtforms import HiddenField, SubmitField, SelectField, StringField, TextAreaField, DateField, FileField, FloatField
from wtforms.validators import InputRequired, DataRequired, Optional, AnyOf
from gestaolegal.plantao.forms import area_do_direito, assistencia_jud_areas_atendidas
from gestaolegal.casos.models import situacao_deferimento
from gestaolegal.plantao.models import se_civel, se_administrativo
from gestaolegal.utils.forms import RequiredIf

class CasoForm(FlaskForm):
    clientes     = HiddenField(validators=[InputRequired('Por favor, selecione pelo menos um cliente para associar ao caso')])
    area_direito = SelectField('Área do Direito', choices=[(assistencia_jud_areas_atendidas[key][0],assistencia_jud_areas_atendidas[key][1]) for key in assistencia_jud_areas_atendidas])
    sub_area     = SelectField('Sub-área Cível',
                                choices=[
                                    (se_civel['CONSUMIDOR'][0],se_civel['CONSUMIDOR'][1]),
                                    (se_civel['CONTRATOS'][0],se_civel['CONTRATOS'][1]),
                                    (se_civel['RESPONSABILIDADE_CIVIL'][0],se_civel['RESPONSABILIDADE_CIVIL'][1]),
                                    (se_civel['REAIS'][0],se_civel['REAIS'][1]),
                                    (se_civel['FAMILIA'][0],se_civel['FAMILIA'][1]),
                                    (se_civel['SUCESSOES'][0],se_civel['SUCESSOES'][1])
                                    ],
                                validators=[
                                    RequiredIf(area_direito = area_do_direito['CIVEL'][0]),
                                    AnyOf([se_civel[key][0] for key in se_civel])
                                    ]
                                )

    sub_areaAdmin= SelectField('Sub-área Administrativo',
                                choices=[
                                    (se_administrativo['PREVIDENCIARIO'][0],se_administrativo['PREVIDENCIARIO'][1]),
                                    (se_administrativo['TRIBUTARIO'][0],se_administrativo['TRIBUTARIO'][1])
                                    ],
                                validators=[
                                    RequiredIf(area_direito = area_do_direito['ADMINISTRATIVO'][0]),
                                    AnyOf([se_administrativo[key][0] for key in se_administrativo])
                                    ]
                                )
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
                                                                        ('solucionado', 'Solucionado'),
                                                                        ('aguardando_deferimento', 'Aguardando Deferimento')
                                                                    ],
                                                                validators = [Optional()])
    situacao_deferimento_indeferido = SelectField('Status do caso', choices=[
                                                                             ('indeferido','Indeferido'),
                                                                             ('ativo','Ativo'),
                                                                             ('aguardando_deferimento', 'Aguardando Deferimento')
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
    numero                   = FloatField('Número', validators=[DataRequired("Por favor, informe o número do processo.")])
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
    valor_causa              = FloatField('Valor da Causa', validators=[DataRequired("Por favor, informe o valor da causa.")])
    data_distribuicao        = DateField('Data da distribuição', validators=[DataRequired("Por favor, escolha uma Data de Distribuição.")])
    data_transito_em_julgado = DateField('Data do trânsito em julgado', validators=[Optional()])
    obs                      = TextAreaField('Observações')
    submit                   = SubmitField('Associar Processo')
    save_button              = SubmitField('Salvar Alterações')

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