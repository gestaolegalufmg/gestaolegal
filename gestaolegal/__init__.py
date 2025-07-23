import os
from functools import wraps
from dotenv import load_dotenv

from flask import Flask, current_app
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

load_dotenv()


class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = environ.get("HTTP_X_FORWARDED_PROTO")
        if scheme:
            environ["wsgi.url_scheme"] = scheme
        return self.app(environ, start_response)


flask_env = os.environ.get("FLASK_ENV")
login_manager = LoginManager()

app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

app.config["COMPANY_NAME"] = os.environ.get("COMPANY_NAME", "Gestão Legal")
app.config["COMPANY_COLOR"] = os.environ.get("COMPANY_COLOR", "#1758ac")

# Security Configuration
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise ValueError("SECRET_KEY environment variable is required")

app.config["UPLOADS"] = "./static/casos"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB limit

# CSRF Configuration
app.config["WTF_CSRF_TIME_LIMIT"] = 3600  # 1 hour in seconds
app.config["WTF_CSRF_SSL_STRICT"] = False  # Allow HTTP in development

############################################################
################## BANCO DE DADOS ##########################
############################################################

# Database configuration from environment variables
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_host = os.environ.get("DB_HOST")
db_name = os.environ.get("DB_NAME")

# Validate required database environment variables
if not all([db_user, db_password, db_host, db_name]):
    raise ValueError("All database environment variables (DB_USER, DB_PASSWORD, DB_HOST, DB_NAME) are required")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://{user}:{password}@{host}/{db}".format(
        user=db_user, password=db_password, host=db_host, db=db_name
    )
)
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 10}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


#############################################################
########### VARIÁVEIS/FUNÇÕES DO TEMPLATE ###################
#############################################################
@app.context_processor
def inject_company_config():
    return dict(
        company_name=app.config["COMPANY_NAME"],
        company_color=app.config["COMPANY_COLOR"],
    )


@app.context_processor
def processor_tipo_classe():
    def tipo_classe(var: object, tipo: str):
        return var.__class__.__name__ == tipo

    return dict(tipo_classe=tipo_classe)


@app.context_processor
def processor_formata_float():
    def formata_float(numero: float):
        lista_char = list(str(numero))

        for i in range(len(lista_char)):
            if lista_char[i] == ".":
                lista_char[i] = ","
                break
        return "".join(lista_char)

    return dict(formata_float=formata_float)


from gestaolegal.usuario.models import usuario_urole_roles


@app.context_processor
def insere_usuario_roles():
    return dict(usuario_urole_roles=usuario_urole_roles)


from gestaolegal.usuario.models import tipo_bolsaUsuario


@app.context_processor
def insere_tipo_bolsaUsuario():
    return dict(tipo_bolsaUsuario=tipo_bolsaUsuario)


from gestaolegal.usuario.models import sexo_usuario


@app.context_processor
def insere_sexo_usuario():
    return dict(sexo_usuario=sexo_usuario)


from gestaolegal.usuario.models import estado_civilUsuario


@app.context_processor
def insere_estado_civilUsuario():
    return dict(estado_civilUsuario=estado_civilUsuario)


from gestaolegal.plantao.models import como_conheceu_daj


@app.context_processor
def insere_como_conheceu_dajUsuario():
    return dict(como_conheceu_daj=como_conheceu_daj)


from gestaolegal.plantao.models import assistencia_jud_areas_atendidas


@app.context_processor
def insere_assistencia_jud_areas_atendidas():
    return dict(assistencia_jud_areas_atendidas=assistencia_jud_areas_atendidas)


from gestaolegal.plantao.models import assistencia_jud_regioes


@app.context_processor
def insere_assistencia_jud_regioes():
    return dict(assistencia_jud_regioes=assistencia_jud_regioes)


from gestaolegal.plantao.models import beneficio


@app.context_processor
def insere_beneficio():
    return dict(beneficio=beneficio)


from gestaolegal.plantao.models import contribuicao_inss


@app.context_processor
def insere_contribuicao_inss():
    return dict(contribuicao_inss=contribuicao_inss)


from gestaolegal.plantao.models import participacao_renda


@app.context_processor
def insere_participacao_renda():
    return dict(participacao_renda=participacao_renda)


from gestaolegal.plantao.models import moradia


@app.context_processor
def insere_moradia():
    return dict(moradia=moradia)


from gestaolegal.plantao.models import qual_pessoa_doente


@app.context_processor
def insere_qual_pessoa_doente():
    return dict(qual_pessoa_doente=qual_pessoa_doente)


from gestaolegal.plantao.models import regiao_bh


@app.context_processor
def insere_regiao_bh():
    return dict(regiao_bh=regiao_bh)


from gestaolegal.plantao.models import escolaridade


@app.context_processor
def insere_escolaridade():
    return dict(escolaridade=escolaridade)


from gestaolegal.plantao.models import enquadramento


@app.context_processor
def insere_enquadramento():
    return dict(enquadramento=enquadramento)


from gestaolegal.plantao.models import area_atuacao


@app.context_processor
def insere_area_atuacao():
    return dict(area_atuacao=area_atuacao)


from gestaolegal.plantao.models import orgao_reg


@app.context_processor
def insere_orgao_reg():
    return dict(orgao_reg=orgao_reg)


from gestaolegal.casos.models import situacao_deferimento


@app.context_processor
def insere_situacao_deferimento():
    return dict(situacao_deferimento=situacao_deferimento)


from gestaolegal.casos.models import tipo_evento


@app.context_processor
def insere_tipo_evento():
    return dict(tipo_evento=tipo_evento)


############################################################
####################### USUARIO PADRAO #####################
############################################################

app.config["ADMIN_PADRAO"] = 10

############################################################
####################### PAGINAÇÃO ##########################
############################################################

app.config["USUARIOS_POR_PAGINA"] = 20
app.config["HISTORICOS_POR_PAGINA"] = 20
app.config["ATENDIDOS_POR_PAGINA"] = 20
app.config["ASSISTENCIA_JURIDICA_POR_PAGINA"] = 20
app.config["CASOS_POR_PAGINA"] = 20
app.config["ARQUIVOS_POR_PAGINA"] = 20
app.config["EVENTOS_POR_PAGINA"] = 20

############################################################
######################## EMAIL #############################
############################################################

# app.config["MAIL_SERVER"] = "smtp.gmail.com"
# app.config["MAIL_PORT"] = 465
# app.config["MAIL_USE_SSL"] = True
# app.config["MAIL_USERNAME"] = "testedodaj@gmail.com"
# app.config["MAIL_PASSWORD"] = "testedaj12345"
if flask_env == "development":
    app.config["MAIL_SERVER"] = "mailpit"
    app.config["MAIL_PORT"] = 1025
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USE_TLS"] = False
    app.config["MAIL_USERNAME"] = None
    app.config["MAIL_PASSWORD"] = None
    app.config["MAIL_DEFAULT_SENDER"] = "development@gestaolegal.com"
else:
    app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", "465"))
    app.config["MAIL_USE_SSL"] = os.environ.get("MAIL_USE_SSL", "True").lower() == "true"
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")

mail = Mail(app)


#############################################################
########## FUNCAO (GLOBAL) PARA FORMATAR TEXTO ##############
#############################################################


def formatarTipoDeEvento(string):
    return {
        "contato": "Contato",
        "reuniao": "Reunião",
        "protocolo_peticao": "Protocolo de Petição",
        "diligencia_externa": "Diligência Externa",
        "audiencia": "Audiência",
        "conciliacao": "Conciliação",
        "decisao_judicial": "Decisão Judicial",
        "redist_caso": "Redistribuição do Caso",
        "encerramento_caso": "Encerramento do Caso",
        "outros": "Outros",
        "documentos": "Documentos",
        "redist_caso": "Redistribuição do Caso",
    }.get(string, "outros")


def formatarNomeDoUsuario(id_usuario):
    if id_usuario:
        entidade_usuario = db.session.get(Usuario, int(id_usuario))
        return entidade_usuario.nome
    else:
        return "Não Há"


def formatarSituacaoDeferimento(situacao):
    for key in situacao_deferimento:
        if situacao_deferimento[key][0] == situacao:
            return situacao_deferimento[key][1]
    return situacao


app.jinja_env.globals.update(formatarTipoDeEvento=formatarTipoDeEvento)
app.jinja_env.globals.update(formatarNomeDoUsuario=formatarNomeDoUsuario)
app.jinja_env.globals.update(formatarSituacaoDeferimento=formatarSituacaoDeferimento)

#############################################################
################## CONFIGURA LOGIN ##########################
#############################################################

from flask import flash, redirect, url_for

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
            if (urole not in role) and (role != ["ANY"]):
                flash("Você não tem permissão para acessar essa página!", "warning")
                return redirect(url_for("principal.index"))
            return fn(*args, **kwargs)

        return decorated_view

    return wrapper


#############################################################
####################### MODELS ##############################
#############################################################

from gestaolegal.arquivos.views import arquivos
from gestaolegal.casos.views import casos
from gestaolegal.controllers.assistencia_judiciaria_controller import (
    assistencia_judiciaria_controller,
)
from gestaolegal.controllers.atendido_controller import atendido_controller
from gestaolegal.controllers.orientacao_juridica_controller import (
    orientacao_juridica_controller,
)
from gestaolegal.notificacoes.views import notificacoes
from gestaolegal.plantao.views import plantao

#############################################################
####################### BLUEPRINTS ##########################
#############################################################
from gestaolegal.principal.views import principal
from gestaolegal.relatorios.views import relatorios
from gestaolegal.usuario.models import Usuario
from gestaolegal.usuario.views import usuario

app.register_blueprint(principal)
app.register_blueprint(usuario, url_prefix="/usuario")
app.register_blueprint(plantao, url_prefix="/plantao")
app.register_blueprint(casos, url_prefix="/casos")
app.register_blueprint(arquivos, url_prefix="/arquivos")
app.register_blueprint(relatorios, url_prefix="/relatorios")
app.register_blueprint(notificacoes, url_prefix="/notificacoes")
