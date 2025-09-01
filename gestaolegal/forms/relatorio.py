from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    FileField,
    FloatField,
    HiddenField,
    IntegerField,
    MultipleFileField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import AnyOf, DataRequired, InputRequired, Optional

from gestaolegal.common.constants import (
    area_do_direito,
    assistencia_jud_areas_atendidas,
    se_administrativo,
    se_civel,
)
from gestaolegal.utils.forms import RequiredIf


class CasoForm(FlaskForm):
    orientador = HiddenField()
    estagiario = HiddenField()
    colaborador = HiddenField()
    area_direito = SelectField(
        "Área do Direito",
        choices=[
            (
                assistencia_jud_areas_atendidas[key][0],
                assistencia_jud_areas_atendidas[key][1],
            )
            for key in assistencia_jud_areas_atendidas
        ],
    )
    sub_area = SelectField(
        "Sub-área Cível",
        choices=[
            (se_civel["CONSUMIDOR"][0], se_civel["CONSUMIDOR"][1]),
            (se_civel["CONTRATOS"][0], se_civel["CONTRATOS"][1]),
            (
                se_civel["RESPONSABILIDADE_CIVIL"][0],
                se_civel["RESPONSABILIDADE_CIVIL"][1],
            ),
            (se_civel["REAIS"][0], se_civel["REAIS"][1]),
            (se_civel["FAMILIA"][0], se_civel["FAMILIA"][1]),
            (se_civel["SUCESSOES"][0], se_civel["SUCESSOES"][1]),
        ],
        validators=[
            RequiredIf("area_direito", area_do_direito["CIVEL"][0]),
            AnyOf([se_civel[key][0] for key in se_civel]),
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
            RequiredIf("area_direito", area_do_direito["ADMINISTRATIVO"][0]),
            AnyOf([se_administrativo[key][0] for key in se_administrativo]),
        ],
    )
    descricao = TextAreaField("Descrição")
    situacao_deferimento_ativo = SelectField(
        "Status do caso",
        choices=[
            ("ativo", "Ativo"),
            ("arquivado", "Arquivado"),
            ("solucionado", "Solucionado"),
            ("aguardando_deferimento", "Aguardando Deferimento"),
        ],
        validators=[Optional()],
    )
    situacao_deferimento_indeferido = SelectField(
        "Status do caso",
        choices=[
            ("indeferido", "Indeferido"),
            ("ativo", "Ativo"),
            ("aguardando_deferimento", "Aguardando Deferimento"),
        ],
        validators=[Optional()],
    )
    submit = SubmitField("Enviar")


class NovoCasoForm(CasoForm):
    """
    Este form tem o campo de clientes a mais do que no caso do form. O cliente é informado apenas no momento da criação do
    caso e não na edição. A alteração de clientes (assistidos) é feita na listagem de casos. Não sei muito bem por que foi
    feita esta opção. TODO: rever no futuro a possibilidade de editar os clientes (assistidos) na tela de edição.
    """

    clientes = HiddenField(
        validators=[
            InputRequired(
                "Por favor, selecione pelo menos um cliente para associar ao caso"
            )
        ]
    )


class RoteiroForm(FlaskForm):
    area_direito = SelectField(
        "Área do Direito",
        choices=[
            (
                assistencia_jud_areas_atendidas[key][0],
                assistencia_jud_areas_atendidas[key][1],
            )
            for key in assistencia_jud_areas_atendidas
        ],
        validators=[InputRequired("Campo obrigaatório")],
    )
    link = StringField("Link para o roteiro (http://exemplo.com.br)")
    submit = SubmitField("Atualizar")


class JustificativaIndeferimento(FlaskForm):
    justificativa = TextAreaField(
        "Justificativa para o indeferimento do caso", validators=[DataRequired()]
    )
    submit = SubmitField("Enviar")


class LembreteForm(FlaskForm):
    usuarios = HiddenField(
        validators=[InputRequired("Por favor, selecione pelo menos um usuário")]
    )
    lembrete = TextAreaField("Descrião da tarefa", validators=[DataRequired()])
    data = DateField("Data de notificação", validators=[DataRequired()])
    submit = SubmitField("Enviar")


class ProcessoForm(FlaskForm):
    especie = SelectField(
        "Espécie",
        choices=[("judicial", "Judicial"), ("extrajudicial", "Extrajudicial")],
        validators=[DataRequired("Por favor selecione uma opção de espécie da lista")],
    )
    numero = IntegerField(
        "Número",
        validators=[
            DataRequired("Por favor, utilize apenas números para preencher o campo.")
        ],
    )
    identificacao = StringField("Identificação")
    vara = StringField("Vara, unidade jurisdicional, turma e/ou câmara")
    link = StringField("Link")
    probabilidade = SelectField(
        "Probabilidade de Ganho",
        choices=[
            ("possivel", "Possível"),
            ("provavel", "Provável"),
            ("remota", "Remota"),
        ],
    )
    posicao_assistido = SelectField(
        "Posição do Assistido",
        choices=[
            ("autor", "Autor"),
            ("reu", "Réu"),
            ("terceiro", "Terceiro"),
            ("interessado", "Interessado"),
        ],
    )
    valor_causa = FloatField(
        "Valor da Causa",
        validators=[DataRequired("Por favor, informe o valor da causa.")],
    )
    data_distribuicao = DateField(
        "Data da distribuição",
        validators=[DataRequired("Por favor, escolha uma Data de Distribuição.")],
    )
    data_transito_em_julgado = DateField(
        "Data do trânsito em julgado", validators=[Optional()]
    )
    obs = TextAreaField("Observações")
    submit = SubmitField("Associar Processo")
    save_button = SubmitField("Salvar Alterações")


class EventoForm(FlaskForm):
    usuario = HiddenField()
    tipo = SelectField(
        "Tipo de Evento",
        choices=[
            ("contato", "Contato"),
            ("reuniao", "Reunião"),
            ("protocolo_peticao", "Protocolo de Petição"),
            ("diligencia_externa", "Diligência Externa"),
            ("audiencia", "Audiência"),
            ("conciliacao", "Conciliação"),
            ("decisao_judicial", "Decisão Judicial"),
            ("redist_caso", "Redistribuição do Caso"),
            ("encerramento_caso", "Encerramento do Caso"),
            ("documentos", "Documentos"),
            ("outros", "Outros"),
        ],
        validators=[InputRequired("Por favor, selecione pelo menos uma opção")],
    )
    data_evento = DateField(
        "Data do Ocorrido", validators=[InputRequired("Por favor, selecione uma data")]
    )
    descricao = TextAreaField(
        "Descrição do Evento",
        validators=[InputRequired("Por favor, selecione pelo menos uma opção")],
    )
    submit = SubmitField("Enviar")


class ArquivoCasoForm(FlaskForm):
    arquivo = FileField("Arquivo")
    submit = SubmitField("Enviar")


class ArquivosEventoForm(FlaskForm):
    arquivos = MultipleFileField("Arquivos")
    submit = SubmitField("Enviar")


class EditarArquivoDeEventoForm(FlaskForm):
    arquivo = FileField("Arquivo")
    submit = SubmitField("Enviar")


class RelatorioForm(FlaskForm):
    tipo_relatorio = SelectField(
        "Tipo de relátorio",
        choices=[
            ("horario_usuarios", "Horário de chegada e saída dos usuários"),
            ("casos_orientacao", "N° de casos Orientação Jurídica"),
            ("casos_cadastrados", "N° de casos cadastrados"),
            (
                "casos_arquiv_soluc_ativ",
                "N° de casos arquivados / solucionados / ativos",
            ),
        ],
    )
    usuarios = HiddenField()
    area_direito = HiddenField()
    data_inicio = DateField(validators=[DataRequired()])
    data_final = DateField(validators=[DataRequired()])
    submit = SubmitField("Gerar Relatório")
