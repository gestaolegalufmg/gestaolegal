import os
from datetime import datetime
from unicodedata import normalize

from flask import (Blueprint, abort, current_app, flash, json, redirect,
                   render_template, request, url_for)
from flask_login import current_user
from flask_paginate import Pagination, get_page_args
from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError

from gestaolegaldaj import app, db, login_required
from gestaolegaldaj.casos.forms import (CasoForm, EditarCasoForm,
                                        JustificativaIndeferimento,
                                        LembreteForm, RoteiroForm, EventoForm, ProcessoForm)
from gestaolegaldaj.casos.models import (Caso, Historico, Lembrete, Roteiro,
                                         situacao_deferimento, Evento, Processo)
from gestaolegaldaj.casos.views_utils import *
from gestaolegaldaj.plantao.forms import CadastroAtendidoForm
from gestaolegaldaj.plantao.models import Atendido
from gestaolegaldaj.plantao.views_util import *
from gestaolegaldaj.usuario.models import Usuario, usuario_urole_roles
from gestaolegaldaj.utils.models import queryFiltradaStatus

notificacoes = Blueprint('notificacoes', __name__, template_folder='templates')


@notificacoes.route('/')
@login_required()
def index():
    return render_template('notificacoes.html')