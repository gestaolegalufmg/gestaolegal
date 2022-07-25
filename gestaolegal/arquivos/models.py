from gestaolegal import db

class Arquivo(db.Model):
    __tablename__ = 'arquivos'

    id                    = db.Column(db.Integer, primary_key = True)
    titulo                = db.Column(db.String(150,  collation = 'latin1_general_ci'),  nullable=False)
    descricao             = db.Column(db.Text(collation = 'latin1_general_ci'))
    nome                  = db.Column(db.Text(collation = 'latin1_general_ci'),  nullable=False)


