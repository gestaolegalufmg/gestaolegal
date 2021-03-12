from gestaolegaldaj import db

acoes = {
    'CAD_NOVO_CASO': 'Cadastrado no caso {}',
    'ABERTURA_PLANTAO': 'Abertura do plantão',#notificar orientadores e estagiarios
    'EVENTO': 'Cadastrado no evento {}',
    'LEMBRETE': 'Cadastrado no lembrete {}'
}


class Notificacao(db.Model):

    __tablename__ = 'notificacao'

    id_executor_acao  = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    executor_acao     = db.relationship('Usuario', foreign_keys = [id_executor_acao])

    id_usu_notificar = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    usu_notificar    = db.relationship('Usuario', foreign_keys = [id_usu_notificar])

    id           = db.Column(db.Integer, primary_key = True)
    acao         = db.Column(db.String(200, collation = 'latin1_general_ci'),  nullable=False)
    data         = db.Column(db.Date, nullable = False)
    