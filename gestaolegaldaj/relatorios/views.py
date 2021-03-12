import os
from datetime import datetime
from unicodedata import normalize

from flask import (Blueprint, abort, current_app, flash, json, redirect,
                   render_template, request, url_for)
from flask_login import current_user
from flask_paginate import Pagination, get_page_args
from sqlalchemy import and_, or_, func
from sqlalchemy.exc import SQLAlchemyError

from gestaolegaldaj import app, db, login_required
from gestaolegaldaj.casos.forms import (CasoForm, EditarCasoForm,
                                        JustificativaIndeferimento,
                                        LembreteForm, RoteiroForm, EventoForm, ProcessoForm)
from gestaolegaldaj.casos.models import (Caso, Historico, Lembrete, Roteiro,
                                         situacao_deferimento, Evento, Processo)
from gestaolegaldaj.casos.views_utils import *
from gestaolegaldaj.relatorios.forms import RelatorioForm
from gestaolegaldaj.plantao.models import Atendido, assistencia_jud_areas_atendidas, OrientacaoJuridica, RegistroEntrada
from gestaolegaldaj.plantao.views_util import *
from gestaolegaldaj.usuario.models import Usuario, usuario_urole_roles
from gestaolegaldaj.utils.models import queryFiltradaStatus
from gestaolegaldaj.relatorios.views_utils import *

relatorios = Blueprint('relatorios', __name__, template_folder='templates')


@relatorios.route('/', methods=['POST', 'GET'])
@login_required()
def index():                  #vai listar os dados como o select2 entende
    form = RelatorioForm(role=[usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['PROFESSOR'][0], usuario_urole_roles['COLAB_EXTERNO'][0]])
    if request.method == 'POST':
        inicio = form.data_inicio.data
        final = form.data_final.data
        if form.area_direito.data == '':
            areas = "all"
        else:
            areas = form.area_direito.data
        if form.estagiarios.data == '':
            estag = "all"
        else:
            estag = form.estagiarios.data
        if form.tipo_relatorio.data == "horario_estag":
            return redirect(url_for('relatorios.relatorio_horarios', inicio=inicio, final=final, estag=estag))
        if form.tipo_relatorio.data == "casos_orientacao":
            return redirect(url_for('relatorios.casos_orientacao_juridica', inicio=inicio, final=final, areas=areas))
        if form.tipo_relatorio.data == "casos_cadastrados":
            return redirect(url_for('relatorios.casos_cadastrados', inicio=inicio, final=final, areas=areas)) 
        if form.tipo_relatorio.data == "casos_arquiv_soluc_ativ":
            return redirect(url_for('relatorios.casos_arq_sol_ativ', inicio=inicio, final=final, areas=areas)) 
    return render_template('relatorios.html', form = form)


@relatorios.route('/casos_orientacao_juridica/<inicio>/<final>/<areas>')
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['PROFESSOR'][0], usuario_urole_roles['COLAB_EXTERNO'][0]])
def casos_orientacao_juridica(inicio, final, areas):
    datas=[inicio, final]
    area_direito = [] if areas == "all" else areas.split(sep=',')
    orientacoes_juridicas = db.session\
                              .query(OrientacaoJuridica.area_direito, func.count(OrientacaoJuridica.area_direito))\
                              .filter(OrientacaoJuridica.status == True, OrientacaoJuridica.data_criacao >= inicio, OrientacaoJuridica.data_criacao <= final)

    if area_direito:
        orientacoes_juridicas = orientacoes_juridicas.filter(OrientacaoJuridica.area_direito.in_(area_direito))                                                   

    orientacoes_juridicas = orientacoes_juridicas.group_by(OrientacaoJuridica.area_direito).all()                                                

    data_emissao = datetime.now().date().strftime("%d/%m/%Y")
    usuario = current_user.nome

    return render_template('casos_orientacao_juridica.html', orientacoes_juridicas = orientacoes_juridicas, data_emissao = data_emissao, usuario = usuario, datas=datas)    


@relatorios.route('/casos_cadastrados/<inicio>/<final>/<areas>', methods=['POST', 'GET'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['PROFESSOR'][0], usuario_urole_roles['COLAB_EXTERNO'][0]])
def casos_cadastrados(inicio, final, areas):
    datas=[inicio, final]
    if areas == "all":
        casos = db.session.query(Caso.area_direito, func.count(Caso.area_direito)).filter(Caso.status == True, Caso.data_criacao >= inicio, Caso.data_criacao <= final).group_by(Caso.area_direito).all()   
    else:
        area_direito = areas.split(sep=',')
        casos = db.session.query(Caso.area_direito, func.count(Caso.area_direito)).filter(Caso.status == True, Caso.data_criacao >= inicio, Caso.data_criacao <= final, Caso.area_direito.in_(area_direito)).group_by(Caso.area_direito).all()
    data_emissao = datetime.now().date().strftime("%d/%m/%Y")
    usuario = current_user.nome
    return render_template('casos_cadastrados.html', casos = casos, data_emissao = data_emissao, usuario = usuario, datas=datas)        

@relatorios.route('/relatorio_horarios/<inicio>/<final>/<estag>')
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['PROFESSOR'][0], usuario_urole_roles['COLAB_EXTERNO'][0]])
def relatorio_horarios(inicio, final, estag):
    datas=[inicio, final]
    if estag == "all":
        horarios = RegistroEntrada.query.select_from(RegistroEntrada).join(Usuario).filter(RegistroEntrada.status == False, RegistroEntrada.data_saida >= inicio, RegistroEntrada.data_saida <= final, Usuario.urole == usuario_urole_roles['ESTAGIARIO_DIREITO'][0]).all()
    else:
        estagiarios = estag.split(sep=',')
        horarios = RegistroEntrada.query.filter(RegistroEntrada.status == False, RegistroEntrada.data_saida >= inicio, RegistroEntrada.data_saida <= final, RegistroEntrada.id_usuario.in_(estagiarios)).all()
    data_emissao = datetime.now().date().strftime("%d/%m/%Y")
    usuario = current_user.nome
    return render_template('relatorio_horarios.html', data_emissao = data_emissao, usuario = usuario, horarios = horarios, datas=datas)

@relatorios.route('/casos_arq_sol_ativ/<inicio>/<final>/<areas>')
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['PROFESSOR'][0], usuario_urole_roles['COLAB_EXTERNO'][0]])
def casos_arq_sol_ativ(inicio, final, areas):
    datas = [inicio, final]
    casos_por_area = []
    if areas == "all":
        area_direito = []
        for area in assistencia_jud_areas_atendidas:
            area_direito.append(assistencia_jud_areas_atendidas[area][0])
        casos = Caso.query.filter(Caso.status == True, Caso.data_criacao >= inicio, Caso.data_criacao <= final, Caso.situacao_deferimento.in_([situacao_deferimento['ATIVO'][0], situacao_deferimento['ARQUIVADO'][0], situacao_deferimento['SOLUCIONADO'][0]])).all() 
    else:
        area_direito = areas.split(sep=',')
        casos = Caso.query.filter(Caso.status == True, Caso.area_direito.in_(area_direito), Caso.data_criacao >= inicio, Caso.data_criacao <= final, Caso.situacao_deferimento.in_([situacao_deferimento['ATIVO'][0], situacao_deferimento['ARQUIVADO'][0], situacao_deferimento['SOLUCIONADO'][0]])).all()
    for area in area_direito:
        casos_por_area.append([area,  0, 0, 0])
    for caso in casos:
        i = 0
        for area in area_direito:
            if caso.area_direito == area:
                break
            else:
                i+=1
        if caso.situacao_deferimento == situacao_deferimento['ARQUIVADO'][0]:
            j = 1
        if caso.situacao_deferimento == situacao_deferimento['SOLUCIONADO'][0]:
            j = 2
        if caso.situacao_deferimento == situacao_deferimento['ATIVO'][0]:
            j = 3
        casos_por_area[i][j]+=1
    data_emissao = datetime.now().date().strftime("%d/%m/%Y")
    usuario = current_user.nome
    return render_template('casos_arq_sol_ativ.html', casos=casos_por_area, data_emissao=data_emissao, usuario=usuario, datas=datas)

@relatorios.route('/api/buscar_estagiarios',methods=['GET'])
@login_required()
def api_relatorios_buscar_estagiarios():
    termo = request.args.get('q', type=str)

    #Se nada for digitado, retornar os 5 assistidos mais recentes
    if termo:
        estagiarios = Usuario.query.filter(Usuario.status and Usuario.urole == usuario_urole_roles['ESTAGIARIO_DIREITO'][0]).filter(Usuario.nome.like(termo+'%')).order_by(Usuario.nome).all()
    else:
        estagiarios = Usuario.query.filter(Usuario.status and Usuario.urole == usuario_urole_roles['ESTAGIARIO_DIREITO'][0]).order_by(Usuario.nome).limit(5).all()

    # Dados formatados para o select2
    estagiarios_clean = [{'id':estagiario.id, 'text':estagiario.nome} for estagiario in estagiarios]
    response = app.response_class(
        response = json.dumps({'results':estagiarios_clean}),
        status = 200,
        mimetype = 'application/json'
    )
    return response

@relatorios.route('/api/buscar_area_direito',methods=['GET'])
@login_required()
def api_relatorios_buscar_area_direito():
    termo = request.args.get('q', type=str)
    areas_direito_clean = []

    if not termo:
        areas_direito_clean = [{'id':assistencia_jud_areas_atendidas[area][0], 'text':assistencia_jud_areas_atendidas[area][1]} for area in assistencia_jud_areas_atendidas]
    
    else:
        area_direito_front = {}

        for area in assistencia_jud_areas_atendidas:
            if (termo in assistencia_jud_areas_atendidas[area][1]) or (termo in area):
                area_direito_front[area] = assistencia_jud_areas_atendidas[area][1]

        
        areas_direito_clean = [{'id':assistencia_jud_areas_atendidas[area][0], 'text':area_direito_front[area]} for area in area_direito_front]



    response = app.response_class(
        response = json.dumps({'results':areas_direito_clean}),
        status = 200,
        mimetype = 'application/json'
    )
    return response