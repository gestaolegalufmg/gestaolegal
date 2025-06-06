from flask import (Blueprint, redirect,
                   render_template, request, url_for)
from flask_login import current_user
from gestaolegal import app, db, login_required
from gestaolegal.notificacoes.models import Notificacao
from gestaolegal.usuario.models import usuario_urole_roles

notificacoes = Blueprint('notificacoes', __name__, template_folder='templates')


@notificacoes.route('/')
@login_required()
def index():
    page = request.args.get('page', 1, type=int)
    
    notificacoes = db.session\
                     .query(Notificacao)

    if current_user.urole in [usuario_urole_roles['ORIENTADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0]]:
        notificacoes = notificacoes.filter((Notificacao.id_usu_notificar == current_user.id) | (Notificacao.id_usu_notificar == None))
    else:
        notificacoes = notificacoes.filter(Notificacao.id_usu_notificar == current_user.id)

    notificacoes = notificacoes.order_by(Notificacao.data.desc()).paginate(
        page=page, per_page=app.config['ATENDIDOS_POR_PAGINA'], error_out=False
    )

    return render_template('notificacoes.html', notificacoes = notificacoes)

@notificacoes.route('/pagina/<notificacao_acao>')
@login_required()
def pagina(notificacao_acao):
    splitted = notificacao_acao.split(" ")

    if(splitted[2] == 'plantão'):
        return redirect(url_for("plantao.pg_plantao"))
    
    elif(splitted[2] == 'caso'):
        return redirect(url_for("casos.visualizar_caso", id = int(splitted[3]))) 

    elif(splitted[2] == 'evento'):
        return redirect(url_for("casos.visualizar_evento", num_evento=int(splitted[3]), id_caso=int(splitted[6])))
    return redirect(url_for("casos.lembretes", id_caso=int(splitted[6]), num_lembrete=int(splitted[3])))
    
