from flask_wtf import FlaskForm
from wtforms import HiddenField, SubmitField, SelectField, StringField, TextAreaField, DateField, FileField, FloatField
from wtforms.validators import InputRequired, DataRequired, Optional

tipos_relatorio = {
    "HORARIOS" : ('horario_estag','Horário de chegada e saída dos estagiários'),
    "CASOS_ORIENTACAO"   : ('casos_orientacao','N° de casos Orientação Jurídica'),
    "CASOS_CADASTRADOS" : ('casos_cadastrados', 'N° de casos cadastrados'),
    "ARQUIV_SOLUC_ATIV"   : ('casos_arquiv_soluc_ativ','N° de casos arquivados / solucionados / ativos')
}

class RelatorioForm(FlaskForm):
	tipo_relatorio = SelectField('Tipo de relátorio', choices=[
                                                                        ('horario_estag','Horário de chegada e saída dos estagiários'),
                                                                        ('casos_orientacao','N° de casos Orientação Jurídica'),
                                                                        ('casos_cadastrados', 'N° de casos cadastrados'),
                                                                        ('casos_arquiv_soluc_ativ','N° de casos arquivados / solucionados / ativos')

									])
	estagiarios = HiddenField()
	area_direito = HiddenField()
	data_inicio = DateField(validators=[DataRequired()])
	data_final  = DateField(validators=[DataRequired()])
	submit = SubmitField('Gerar Relatório')