import os
from datetime import datetime
from unicodedata import normalize

from flask import (Blueprint, abort, current_app, flash, json, redirect,
                   render_template, request, url_for)
from flask_login import current_user
from flask_paginate import Pagination, get_page_args
from sqlalchemy import and_, or_
from sqlalchemy import null
from sqlalchemy.exc import SQLAlchemyError

from gestaolegal import app, db, login_required
from gestaolegal.casos.forms import (CasoForm,
                                     JustificativaIndeferimento,
                                     LembreteForm, RoteiroForm, EventoForm, ProcessoForm)
from gestaolegal.casos.models import (Caso, Historico, Lembrete, Roteiro,
                                      situacao_deferimento, Evento, Processo)
from gestaolegal.notificacoes.models import Notificacao
from gestaolegal.usuario.models import usuario_urole_roles
from gestaolegal.utils.models import queryFiltradaStatus

notificacoes = Blueprint('notificacoes', __name__, template_folder='templates')


@notificacoes.route('/')
@login_required()
def index():
    page = request.args.get('page', 1, type=int)
    
    notificacoes = db.session\
                     .query(Notificacao)

    if current_user.urole in [usuario_urole_roles['ORIENTADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0]]:
        notificacoes = notificacoes.filter((Notificacao.id_usu_notificar == current_user.id) | (Notificacao.id_usu_notificar == null()))
    else:
        notificacoes = notificacoes.filter(Notificacao.id_usu_notificar == current_user.id)

    notificacoes = notificacoes.order_by(Notificacao.data.desc()).paginate(page, app.config['ATENDIDOS_POR_PAGINA'], False)

    return render_template('notificacoes.html', notificacoes = notificacoes)

@notificacoes.route('/teste')
@login_required()
def teste():
    _id = 1
    """ return redirect(url_for("casos.visualizar_caso", id=_id)) 
    return redirect(url_for("plantao.pg_plantao"))  """
    return redirect(url_for("casos.visualizar_evento",id_evento=_id))