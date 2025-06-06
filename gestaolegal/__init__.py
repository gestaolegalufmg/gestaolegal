import configparser

config = configparser.ConfigParser()
import os
from functools import wraps

from flask import Flask, current_app
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy


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
config.read("config.ini")

app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

app.config["COMPANY_NAME"] = os.environ.get("COMPANY_NAME", "Gestão Legal")
app.config["COMPANY_COLOR"] = os.environ.get("COMPANY_COLOR", "#1758ac")

if flask_env == "development":
    config.read(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "config_test.ini")
    )

app.config["SECRET_KEY"] = config["SECRET_KEY"]["key"]
app.config["UPLOADS"] = "./static/casos"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB limit

############################################################
################## BANCO DE DADOS ##########################
############################################################

db_user = config["MYSQL"]["user"]
db_password = config["MYSQL"]["password"]
db_host = config["MYSQL"]["host"]
db = config["MYSQL"]["db"]

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://{user}:{password}@{host}/{db}".format(
        user=db_user, password=db_password, host=db_host, db=db
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
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 465
    app.config["MAIL_USE_SSL"] = True
    app.config["MAIL_USERNAME"] = "cassio@setter.global"
    app.config["MAIL_PASSWORD"] = "bgmxdotawlytmtvp"

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
        entidade_usuario = Usuario.query.get(int(id_usuario))
        return entidade_usuario.nome
    else:
        return "Não Há"


app.jinja_env.globals.update(formatarTipoDeEvento=formatarTipoDeEvento)
app.jinja_env.globals.update(formatarNomeDoUsuario=formatarNomeDoUsuario)

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
