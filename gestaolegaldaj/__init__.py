import os
from functools import wraps
from flask import Flask, render_template, current_app
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from flask_mail import Mail     --> Quando usar e-mail, precisa dessa biblioteca

login_manager = LoginManager()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'w8oyUPlywjAAN51OXBdfJUZ8icsRCCP7'

############################################################
################## BANCO DE DADOS ##########################
############################################################

app.config['SQLALCHEMY_DATABASE_URI'] =  "mysql+pymysql://gestaolegalnew:bd@gestaolegal@gestaolegalnew.mysql.dbaas.com.br/gestaolegalnew"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_recycle": 10}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app,db, compare_type = True)

#############################################################
########### VARIÁVEIS/FUNÇÕES DO TEMPLATE ###################
#############################################################
from gestaolegaldaj.usuario.models import usuario_urole_roles
@app.context_processor
def insere_usuario_roles():
    return dict(usuario_urole_roles = usuario_urole_roles)

from gestaolegaldaj.usuario.models import tipo_bolsaUsuario
@app.context_processor
def insere_tipo_bolsaUsuario():
    return dict(tipo_bolsaUsuario = tipo_bolsaUsuario)

from gestaolegaldaj.usuario.models import sexo_usuario
@app.context_processor
def insere_sexo_usuario():
    return dict(sexo_usuario = sexo_usuario)

from gestaolegaldaj.usuario.models import estado_civilUsuario
@app.context_processor
def insere_estado_civilUsuario():
    return dict(estado_civilUsuario = estado_civilUsuario)

from gestaolegaldaj.plantao.models import como_conheceu_daj
@app.context_processor
def insere_como_conheceu_dajUsuario():
    return dict(como_conheceu_daj = como_conheceu_daj)

from gestaolegaldaj.plantao.forms import assistido_fisicoOuJuridico
@app.context_processor
def insere_assistido_fisicoOuJuridico():
    return dict(assistido_fisicoOuJuridico = assistido_fisicoOuJuridico)

############################################################
####################### USUARIO PADRAO #####################
############################################################

app.config['ADMIN_PADRAO'] = 10

############################################################
####################### PAGINAÇÃO ##########################
############################################################

app.config['USUARIOS_POR_PAGINA'] = 20
app.config['ATENDIDOS_POR_PAGINA'] = 20

############################################################
######################## EMAIL #############################
############################################################

# EMAIL DEVE SER CONFIGURADO ANTES DE USAR (apague este comentário depois de configurar)
'''
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL']=True
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
'''

#############################################################
################## CONFIGURA LOGIN ##########################
#############################################################

from flask import redirect, flash, url_for

login_manager.init_app(app)
login_manager.login_view = "usuario.login"
login_manager.login_message = "Por favor, faça o login para acessar esta página."

def login_required(role=["ANY"]):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):

            if not current_user.is_authenticated:
               return current_app.login_manager.unauthorized()
            urole = current_user.urole
            if ( (urole not in role) and (role != ["ANY"])):
                flash("Você não tem permissão para acessar essa página!", "warning")
                return redirect(url_for('principal.index'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

#############################################################
####################### MODELS ##############################
#############################################################

from gestaolegaldaj.usuario.models import Usuario

#############################################################
####################### BLUEPRINTS ##########################
#############################################################

from gestaolegaldaj.principal.views import principal
from gestaolegaldaj.usuario.views import usuario
from gestaolegaldaj.plantao.views import plantao

app.register_blueprint(principal)
app.register_blueprint(usuario, url_prefix='/usuario')
app.register_blueprint(plantao, url_prefix='/plantao')
