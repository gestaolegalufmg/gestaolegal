from werkzeug.exceptions import default_exceptions
from gestaolegal import db
from datetime import datetime
from gestaolegal.usuario.models import Usuario

# Relacionamento Casos <--> Atendidos
associacao_casos_atendidos = db.Table('casos_atendidos', db.metadata,
                                        db.Column('id_caso', db.Integer, db.ForeignKey('casos.id')),
                                        db.Column('id_atendido', db.Integer, db.ForeignKey('atendidos.id'))
                                    )

situacao_deferimento = {
    'AGUARDANDO_DEFERIMENTO': ('aguardando_deferimento', 'Aguardando Deferimento','warning'),
    'ATIVO': ('ativo', 'Ativo', 'success'),
    'INDEFERIDO': ('indeferido', 'Indeferido', 'danger'),
    'ARQUIVADO': ('arquivado', 'Arquivado', 'dark'),
    'SOLUCIONADO': ('solucionado', 'Solucionado', 'info')
}

tipo_evento = {
    'CONTATO': ('contato','Contato'),
    'REUNIAO': ('reuniao','Reunião'),
    'PROTOCOLO_PETICAO': ('protocolo_peticao','Protocolo de Petição'),
    'DILIGENCIA_EXTERNA': ('diligencia_externa','Diligência Externa'),
    'AUDIENCIA': ('audiencia','Audiência'),
    'CONCILIACAO': ('conciliacao','Conciliação'),
    'DECISAO_JUDICIAL': ('decisao_judicial','Decisão Judicial'),
    'REDIST_CASO': ('redist_caso','Redistribuição do Caso'),
    'ENCERRAMENTO_CASO': ('encerramento_caso','Encerramento do Caso'),
    'DOCUMENTOS': ('documentos','Documentos'),
    'OUTROS': ('outros','Outros')
}

class Caso(db.Model):
    __tablename__ = 'casos'

    id                     = db.Column(db.Integer, primary_key = True)

    id_usuario_responsavel = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable = False)
    usuario_responsavel    = db.relationship('Usuario', foreign_keys = [id_usuario_responsavel])

    area_direito           = db.Column(db.String(50, collation = 'latin1_general_ci'), nullable = False)
    sub_area               = db.Column(db.String(50, collation = 'latin1_general_ci'))

    clientes               = db.relationship('Atendido', secondary = associacao_casos_atendidos, back_populates='casos')

    id_orientador          = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    orientador             = db.relationship('Usuario', foreign_keys = [id_orientador])

    id_estagiario          = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    estagiario             = db.relationship('Usuario', foreign_keys = [id_estagiario])

    id_colaborador         = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    colaborador            = db.relationship('Usuario', foreign_keys = [id_colaborador])

    data_criacao           = db.Column(db.DateTime, nullable = False)
    id_criado_por          = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable= False)
    criado_por             = db.relationship('Usuario', foreign_keys = [id_criado_por])

    data_modificacao       = db.Column(db.DateTime)
    id_modificado_por      = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    modificado_por         = db.relationship('Usuario', foreign_keys = [id_modificado_por])

    situacao_deferimento   = db.Column(db.String(50, collation = 'latin1_general_ci'), nullable = False, default='aguardando_deferimento')
    justif_indeferimento   = db.Column(db.String(280, collation = 'latin1_general_ci'), nullable = True)

    status                 = db.Column(db.Boolean, default = True, nullable = False)
    descricao              = db.Column(db.Text(collation = 'latin1_general_ci'))

    numero_ultimo_processo = db.Column(db.Integer, nullable = True)

    def setSubAreas(self, area_direito, sub_area, sub_areaAdmin):
        if area_direito == 'civel':
            self.sub_area = sub_area
        elif area_direito == 'administrativo':
            self.sub_area = sub_areaAdmin
        else:
            self.sub_area = null()

class ArquivoCaso(db.Model):
    __tablename__ = 'arquivosCaso'

    id              = db.Column(db.Integer, primary_key=True)
    link_arquivo    = db.Column(db.String(300, collation = 'latin1_general_ci'))

    id_caso         = db.Column(db.Integer, db.ForeignKey('casos.id', ondelete='CASCADE'))

class Roteiro(db.Model):
    __tablename__ = 'documentos_roteiro'

    id                     = db.Column(db.Integer, primary_key = True)
    area_direito           = db.Column(db.String(50, collation = 'latin1_general_ci'), nullable = False)
    link                   = db.Column(db.String(1000, collation = 'latin1_general_ci'))

class Lembrete(db.Model):
    __tablename__ = 'lembretes'

    id                     = db.Column(db.Integer, primary_key = True)
    id_do_criador          = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable = False)
    criador                = db.relationship('Usuario', foreign_keys = [id_do_criador])
    id_caso                = db.Column(db.Integer, db.ForeignKey('casos.id'), nullable = False)
    caso                   = db.relationship('Caso', foreign_keys = [id_caso])
    id_usuario             = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable = False)
    usuario                = db.relationship('Usuario', foreign_keys = [id_usuario])
    data_criacao           = db.Column(db.DateTime, nullable = False)
    data_lembrete          = db.Column(db.DateTime, nullable = False)
    descricao              = db.Column(db.String(1000, collation = 'latin1_general_ci'), nullable = False)
    status                 = db.Column(db.Boolean, default = True, nullable = False)


class Historico(db.Model):
    __tablename__ = 'historicos'

    id                     = db.Column(db.Integer, primary_key = True)
    id_usuario             = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable = False)
    usuario                = db.relationship("Usuario", lazy="joined")
    id_caso                = db.Column(db.Integer, db.ForeignKey("casos.id"), nullable = False)
    caso                   = db.relationship("Caso", lazy="joined")
    data                   = db.Column(db.DateTime, nullable = False)

class Processo(db.Model):
    __tablename__ = 'processos'

    id                     = db.Column(db.Integer, primary_key = True)
    especie                = db.Column(db.String(25, collation = 'latin1_general_ci'), nullable = False)
    numero                 = db.Column(db.Integer,unique = True)
    identificacao          = db.Column(db.Text(collation = 'latin1_general_ci'))
    vara                   = db.Column(db.String(200, collation = 'latin1_general_ci'))
    link                   = db.Column(db.String(1000, collation = 'latin1_general_ci'))
    probabilidade          = db.Column(db.String(25, collation = 'latin1_general_ci'))    
    posicao_assistido      = db.Column(db.String(25, collation = 'latin1_general_ci'))
    valor_causa_inicial    = db.Column(db.Integer)
    valor_causa_atual      = db.Column(db.Integer)
    data_distribuicao      = db.Column(db.Date)
    data_transito_em_julgado = db.Column(db.Date)
    obs                    = db.Column(db.Text(collation = 'latin1_general_ci'))
    id_caso                = db.Column(db.Integer, db.ForeignKey("casos.id"), nullable = False)
    caso                   = db.relationship("Caso", lazy="joined")
    status                 = db.Column(db.Boolean, default = True, nullable = False)
    id_criado_por          = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable= False, default = 1)
    criado_por             = db.relationship('Usuario', foreign_keys = [id_criado_por])

class Evento(db.Model):
    __tablename__ = 'eventos'

    id                     = db.Column(db.Integer, primary_key = True)
    id_caso                = db.Column(db.Integer, db.ForeignKey("casos.id"), nullable = False)
    caso                   = db.relationship("Caso")

    num_evento             = db.Column(db.Integer, default = 0)
    tipo                   = db.Column(db.String(50,collation = 'latin1_general_ci'), nullable = False)
    descricao              = db.Column(db.String(1000, collation = 'latin1_general_ci'))
    arquivo                = db.Column(db.String(100, collation = 'latin1_general_ci'))
    data_evento            = db.Column(db.Date, nullable = False)

    data_criacao           = db.Column(db.DateTime, nullable = False)
    id_criado_por          = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable= False)

    id_usuario_responsavel = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable = True)
    usuario_responsavel    = db.relationship('Usuario', foreign_keys = [id_usuario_responsavel])

    criado_por             = db.relationship('Usuario', foreign_keys = [id_criado_por])
    status                 = db.Column(db.Boolean, default = True, nullable = False)
