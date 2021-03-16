from functools import wraps
from flask import Flask, current_app
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail


login_manager = LoginManager()

app = Flask(__name__)

app.config["SECRET_KEY"] = "w8oyUPlywjAAN51OXBdfJUZ8icsRCCP7"
app.config["UPLOADS"] = "./static/casos"
############################################################
################## BANCO DE DADOS ##########################
############################################################

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "mysql+pymysql://gestaolegal:gestaolegal@localhost/gestaolegal"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 10}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
Migrate(app, db, compare_type=True)

#############################################################
########### VARIÁVEIS/FUNÇÕES DO TEMPLATE ###################
#############################################################
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


from gestaolegaldaj.usuario.models import usuario_urole_roles


@app.context_processor
def insere_usuario_roles():
    return dict(usuario_urole_roles=usuario_urole_roles)


from gestaolegaldaj.usuario.models import tipo_bolsaUsuario


@app.context_processor
def insere_tipo_bolsaUsuario():
    return dict(tipo_bolsaUsuario=tipo_bolsaUsuario)


from gestaolegaldaj.usuario.models import sexo_usuario


@app.context_processor
def insere_sexo_usuario():
    return dict(sexo_usuario=sexo_usuario)


from gestaolegaldaj.usuario.models import estado_civilUsuario


@app.context_processor
def insere_estado_civilUsuario():
    return dict(estado_civilUsuario=estado_civilUsuario)


from gestaolegaldaj.plantao.models import como_conheceu_daj


@app.context_processor
def insere_como_conheceu_dajUsuario():
    return dict(como_conheceu_daj=como_conheceu_daj)


from gestaolegaldaj.plantao.models import assistencia_jud_areas_atendidas


@app.context_processor
def insere_assistencia_jud_areas_atendidas():
    return dict(assistencia_jud_areas_atendidas=assistencia_jud_areas_atendidas)


from gestaolegaldaj.plantao.models import assistencia_jud_regioes


@app.context_processor
def insere_assistencia_jud_regioes():
    return dict(assistencia_jud_regioes=assistencia_jud_regioes)


from gestaolegaldaj.plantao.models import qual_pessoa_doente


@app.context_processor
def insere_qual_pessoa_doente():
    return dict(qual_pessoa_doente=qual_pessoa_doente)


from gestaolegaldaj.plantao.models import regiao_bh


@app.context_processor
def insere_regiao_bh():
    return dict(regiao_bh=regiao_bh)


from gestaolegaldaj.plantao.models import escolaridade


@app.context_processor
def insere_escolaridade():
    return dict(escolaridade=escolaridade)


from gestaolegaldaj.plantao.models import enquadramento


@app.context_processor
def insere_enquadramento():
    return dict(enquadramento=enquadramento)


from gestaolegaldaj.plantao.models import area_atuacao


@app.context_processor
def insere_area_atuacao():
    return dict(area_atuacao=area_atuacao)


from gestaolegaldaj.plantao.models import orgao_reg


@app.context_processor
def insere_orgao_reg():
    return dict(orgao_reg=orgao_reg)


from gestaolegaldaj.casos.models import situacao_deferimento


@app.context_processor
def insere_situacao_deferimento():
    return dict(situacao_deferimento=situacao_deferimento)


from gestaolegaldaj.casos.models import tipo_evento


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

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = "testedodaj@gmail.com"
app.config["MAIL_PASSWORD"] = "testedaj12345"

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
            if (urole not in role) and (role != ["ANY"]):
                flash("Você não tem permissão para acessar essa página!", "warning")
                return redirect(url_for("principal.index"))
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
from gestaolegaldaj.casos.views import casos
from gestaolegaldaj.arquivos.views import arquivos
from gestaolegaldaj.relatorios.views import relatorios
from gestaolegaldaj.notificacoes.views import notificacoes


app.register_blueprint(principal)
app.register_blueprint(usuario, url_prefix="/usuario")
app.register_blueprint(plantao, url_prefix="/plantao")
app.register_blueprint(casos, url_prefix="/casos")
app.register_blueprint(arquivos, url_prefix="/arquivos")
app.register_blueprint(relatorios, url_prefix="/relatorios")
app.register_blueprint(notificacoes, url_prefix="/notificacoes")
