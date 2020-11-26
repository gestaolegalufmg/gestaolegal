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

casos = Blueprint('casos', __name__, template_folder='templates')


@casos.route('/')
@login_required()
def index():
    page = request.args.get('page', 1, type=int)
    opcao_filtro = request.args.get('opcao_filtro', opcoes_filtro_casos['TODOS'][0], type=str)

    casos = query_opcoes_filtro_casos(opcao_filtro).paginate(page, app.config['CASOS_POR_PAGINA'], False)
    
    return render_template(
                            'lista_casos.html', 
                            opcoes_filtro_casos = opcoes_filtro_casos,
                            **params_busca_casos(casos, ROTA_PAGINACAO_CASOS, opcao_filtro) 
                            )

@casos.route('/ajax_filtro_casos')
@login_required()
def ajax_filtro_casos():
    page = request.args.get('page', 1, type=int)
    opcao_filtro = request.args.get('opcao_filtro', opcoes_filtro_casos['TODOS'][0], type=str)

    casos = query_opcoes_filtro_casos(opcao_filtro).paginate(page, app.config['CASOS_POR_PAGINA'], False)


    return render_template(
                            'busca_casos.html', 
                            **params_busca_casos(casos, ROTA_PAGINACAO_CASOS, opcao_filtro) 
                            )

@casos.route('/novo_caso', methods=['GET','POST'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0],usuario_urole_roles['ESTAGIARIO_DIREITO'][0],])
def novo_caso():
    _form = CasoForm()
    if _form.validate_on_submit():

        arquivo = request.files.get('arquivo')
        nome_arquivo = None

        _caso = Caso(
            area_direito            = _form.area_direito.data,
            id_usuario_responsavel  = current_user.id,
            id_orientador           = int(_form.orientador.data) if _form.orientador.data else None,
            data_criacao            = datetime.now(),
            id_criado_por           = current_user.id,
            data_modificacao        = datetime.now(),
            id_modificado_por       = current_user.id,
            arquivo                 = (datetime.now().strftime("%d%m%Y") + '.' + (arquivo.filename.split(".")[1])) if arquivo else None,
            descricao               = _form.descricao.data,
        )

        for id_cliente in _form.clientes.data.split(sep=','):
            cliente = Atendido.query.get(int(id_cliente))
            _caso.clientes.append(cliente)
        
        db.session.add(_caso)
        db.session.commit()

        if arquivo:
            nome_arquivo = f'caso_{_caso.id}_{datetime.now().strftime("%d%m%Y")}.{arquivo.filename.split(".")[1]}'
            arquivo.save(os.path.join(current_app.root_path,'static','casos', nome_arquivo))

        flash('Caso criado com sucesso!','success')
        return redirect(url_for('casos.index'))

    return render_template('novo_caso.html', form = _form)

#Visualizar caso
@casos.route('/visualizar/<int:id>', methods=['GET'])
@login_required()
def visualizar_caso(id):
    _caso = Caso.query.filter_by(status = True, id = id).first()
    if not _caso: abort(404)
    processos = Processo.query.filter_by(id_caso = id, status = True).all()
    _lembrete = Lembrete.query.filter_by(status = True, id_caso = id).first()
    return render_template('visualizar_caso.html', caso = _caso, processos = processos, lembrete=_lembrete)

@casos.route('/deferir_caso/<int:id_caso>', methods=['POST', 'GET'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['PROFESSOR'][0]])
def deferir_caso(id_caso):
    entidade_caso = Caso.query.filter_by(id = id_caso).first()
    if not entidade_caso:
        flash("Caso não encontrado.","warning")
        return redirect(url_for('casos.index'))

    entidade_caso.situacao_deferimento = situacao_deferimento['ATIVO'][0]
    db.session.add(entidade_caso)
    db.session.commit()
    flash("Caso deferido!","success")
    return redirect(url_for('casos.index'))

@casos.route('/indeferir/<id_caso>', methods=['POST','GET'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0],usuario_urole_roles['PROFESSOR'][0]])
def indeferir_caso(id_caso):
    _form = JustificativaIndeferimento()
    if request.method == 'POST':
        _id = id_caso
        _justificativa = request.form['justificativa']
        if not _justificativa:
            flash('É necessário fornecer uma justificativa para o indeferimento!', 'danger')
            return redirect(url_for('visualizar_caso', id = _id))
            
        _caso = Caso.query.filter_by(status = True, id = _id).first()
        _caso.situacao_deferimento = situacao_deferimento['INDEFERIDO'][0]
        _caso.justif_indeferimento = _justificativa

        db.session.add(_caso)
        db.session.commit()
        flash('Indeferimento realizado.','success')
        return redirect(url_for('casos.visualizar_caso', id = _id))
    return render_template('justificativa.html',form=_form)

@casos.route('/associa_caso', methods=['GET','POST'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['PROFESSOR'][0] ])
def associa_caso():
    _form = CasoForm()

    # if _form.validate_on_submit():
    #     _caso = Caso(
    #         id_usuario_responsavel  = current_user.id,
    #         clientes                = _form.clientes.data.split(sep=',')
    #         id_orientador           = _form.orientador.data
    #         data_criacao            = datetime.now
    #         id_criado_por           = current_user.id
    #         data_modificacao        = datetime.now
    #         id_modificado_por       = current_user.id
    #     )
    #     db.session.add(_caso)
    #     flash('Caso criado com sucesso!','success')
    #     return redirect(url_for('casos.index'))
    return render_template('associa_caso.html', form = _form)

@casos.route('editar_caso/<id_caso>', methods=['GET', 'POST'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0],usuario_urole_roles['ESTAGIARIO_DIREITO'][0],usuario_urole_roles['PROFESSOR'][0],usuario_urole_roles['ORIENTADOR'][0],usuario_urole_roles['COLAB_EXTERNO'][0]])
def editar_caso(id_caso):
    def setValoresCaso(form : EditarCasoForm, entidade_caso: Caso):
        form.clientes.data = entidade_caso.clientes
        form.orientador.data = entidade_caso.orientador
        form.area_direito.data = entidade_caso.area_direito
        form.descricao.data = entidade_caso.descricao
        form.situacao_deferimento.data = entidade_caso.situacao_deferimento

    def setDadosCaso(form : EditarCasoForm, entidade_caso: Caso):
        entidade_caso.clientes = form.clientes.data
        entidade_caso.orientador = form.orientador.data
        entidade_caso.area_direito = form.area_direito.data
        entidade_caso.descricao = form.descricao.data
        entidade_caso.situacao_deferimento = form.situacao_deferimento.data 

############################## IMPLEMENTAÇÃO DA ROTA ###########################################################3

    entidade_caso = Caso.query.filter_by(id = id_caso, status = True).first()

    if not entidade_caso:
        flash("Não existe um caso com esse ID.", 'warning')
        return redirect(url_for('casos.index'))

    form = EditarCasoForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template('editar_caso.html', form = form)

        setDadosCaso(form, entidade_caso)
        db.session.commit()
        cadastrar_historico(current_user.id,id_caso) # Cadastra um novo histórico de edição
        flash('Caso editado com sucesso!',"success")
        return redirect(url_for('casos.index'))

    setValoresCaso(form, entidade_caso)

    return render_template('editar_caso.html', form = form)

@casos.route('/api/buscar_assistido',methods=['GET'])
@login_required()
def api_casos_buscar_assistido():
    termo = request.args.get('q', type=str)

    #Se nada for digitado, retornar os 5 assistidos mais recentes
    if termo:
        _assistidos = Atendido.query.join(Assistido).filter(or_(Atendido.cpf.like(termo+'%'),Atendido.cnpj.like(termo+'%'),Atendido.nome.like(termo+'%'))).filter(Atendido.status.is_(True)).order_by(Atendido.nome).all()
    else:
        _assistidos = Atendido.query.join(Assistido).filter(Atendido.status.is_(True)).order_by(Atendido.nome).limit(5).all()

    # Dados formatados para o select2
    assistidos_clean = [{'id':assistido.id, 'text':assistido.nome, 'cpf':assistido.cpf, 'cnpj':assistido.cnpj} for assistido in _assistidos]
    response = app.response_class(
        response = json.dumps({'results':assistidos_clean}),
        status = 200,
        mimetype = 'application/json'
    )
    return response


@casos.route('/api/buscar_usuario',methods=['GET'])
@login_required()
def api_casos_buscar_usuario():
    termo = request.args.get('q', type=str)
    if termo:
        _usuarios = Usuario.query.filter(Usuario.nome.like(termo+'%')).filter(Usuario.status.is_(True)).order_by(Usuario.nome).all()
    else:
        _usuarios = Usuario.query.filter(Usuario.status.is_(True)).order_by(Usuario.nome).limit(5).all()

    # Dados formatados para o select2
    usuarios_clean = [{'id':usuario.id, 'text':usuario.nome} for usuario in _usuarios]
    response = app.response_class(
        response = json.dumps({'results':usuarios_clean}),
        status = 200,
        mimetype = 'application/json'
    )
    return response

@casos.route('/api/buscar_roteiro',methods=['GET'])
@login_required()
def api_casos_buscar_roteiro():
    termo = request.args.get('termo', type=str)
    if termo:
        _roteiro = Roteiro.query.filter_by(area_direito=termo).first()
        if _roteiro: 
            roteiro_clean = {'link': _roteiro.link}
        else:
            roteiro_clean = {'link': ''}
    else:
        roteiro_clean = {'link': ''}

    response = app.response_class(
        response = json.dumps(roteiro_clean),
        status = 200,
        mimetype = 'application/json'
    )
    return response

@casos.route('/api/buscar_casos',methods=['GET'])
@login_required()
def api_casos_buscar_casos():
    id_caso = request.args.get('q', type=str)
    if id_caso:
        _casos = Caso.query.filter(Caso.id.like(id_caso+'%')).filter(Caso.status.is_(True)).order_by(Caso.id).all()
    else:
        _casos = Caso.query.filter(Caso.status.is_(True)).order_by(Caso.id).limit(5).all()

    
    if not _casos:
        response = app.response_class(
        response = json.dumps({'id': 1, 'text':'Não há casos cadastrados no sistema'}),
        status = 200,
        mimetype = 'application/json'
    )
        return response

        # Dados formatados para o select2
    casos_clean = [{'id':_casos[i].id, 'text': 'Caso ' + str(_casos[i].id)} for i in range(0,len(_casos))]

    response = app.response_class(
        response = json.dumps({'results':casos_clean}),
        status = 200,
        mimetype = 'application/json'
    )
    return response

#Cadastrar/editar links de roteiro
@casos.route('/links_roteiro', methods=['GET','POST'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['PROFESSOR'][0], usuario_urole_roles['COLAB_PROJETO'][0], usuario_urole_roles['COLAB_EXTERNO'][0]])
def editar_roteiro():
    _form = RoteiroForm()
    if _form.validate_on_submit():
        _roteiro = Roteiro.query.filter_by(area_direito = _form.area_direito.data).first() or Roteiro()

        _roteiro.area_direito = _form.area_direito.data 
        _roteiro.link = _form.link.data

        db.session.add(_roteiro)
        db.session.commit()
        flash('Alteração realizada com sucesso!', 'success')
        return redirect(url_for('casos.editar_roteiro'))

    _roteiros = Roteiro.query.all()
    return render_template('links_roteiro.html', form=_form, roteiros=_roteiros)

# Rota para página de eventos
@casos.route('/eventos/<id_caso>')
@login_required()
def eventos(id_caso):
    page = request.args.get('page', 1, type=int)
    _eventos = Evento.query.filter_by(id_caso = id_caso, status = True).paginate(page, app.config['CASOS_POR_PAGINA'], False)
    if not _eventos.items:
        flash('Não há eventos cadastrados para este caso.','warning')
        return redirect(url_for('casos.visualizar_caso', id = id_caso))

    return render_template('eventos.html', caso_id = id_caso, eventos = _eventos)

# Rota para página de lembretes
@casos.route('/lembretes/<id_caso>')
@login_required()
def lembretes(id_caso):
    _lembretes = Lembrete.query.filter_by(status = True, id_caso = id_caso).order_by(Lembrete.data_criacao.desc()).all()
    return render_template('lembretes.html', caso_id = id_caso, lembretes=_lembretes)

@casos.route('/cadastrar_lembrete/<int:id_do_caso>', methods=['GET','POST'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['ORIENTADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0], usuario_urole_roles['COLAB_EXTERNO'][0]])
def cadastrar_lembrete(id_do_caso):
    _form = LembreteForm()
    
    if _form.validate_on_submit():
        
        _lembrete = Lembrete(
            id_caso = id_do_caso,
            id_usuario = int(_form.usuarios.data),
            data_lembrete = _form.data.data,
            descricao  = _form.lembrete.data      
        )

        _lembrete.id_do_criador = current_user.id
        _lembrete.data_criacao = datetime.now()

        db.session.add(_lembrete)
        db.session.commit()      
        flash('Lembrete enviado com sucesso!', 'success')
        return redirect(url_for('casos.index'))

    return render_template('novo_lembrete.html', form = _form )

@casos.route('/editar_lembrete/<id_lembrete>',methods=['GET','POST'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['ORIENTADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0], usuario_urole_roles['COLAB_EXTERNO'][0]])
def editar_lembrete(id_lembrete):
    def setValoresLembrete(_form : LembreteForm, entidade_lembrete : Lembrete):
        _form.usuarios.data = entidade_lembrete.id_usuario
        _form.data.data = entidade_lembrete.data_lembrete
        _form.lembrete.data  = entidade_lembrete.descricao
    def setDadosLembrete(form : LembreteForm, entidade_lembrete : Lembrete):
  
        entidade_lembrete.id_usuario = int(_form.usuarios.data)
        entidade_lembrete.data_lembrete = _form.data.data
        entidade_lembrete.descricao = _form.lembrete.data

############################## IMPLEMENTAÇÃO DA ROTA ###########################################################

    entidade_lembrete = Lembrete.query.filter_by(id = id_lembrete, status = True).first()

    if not entidade_lembrete:
        flash("Não existe um lembrete com esse ID.", 'warning')
        return redirect(url_for('casos.index'))

    _form = LembreteForm()
   
    if request.method == 'POST':
        if not _form.validate():
            return render_template('editar_lembrete.html', form = _form)

        setDadosLembrete(_form, entidade_lembrete)
        db.session.commit()
        flash("Lembrete editado com sucesso!", 'success')
        return redirect(url_for('casos.lembretes', id_caso = entidade_lembrete.id_caso))

    setValoresLembrete(_form, entidade_lembrete)
    entidade_usuario_notificado = Usuario.query.filter_by(id = entidade_lembrete.id_usuario, status = True).first()
    return render_template('editar_lembrete.html', form = _form, usuario = entidade_usuario_notificado.nome )

@casos.route('/excluir_lembrete/<id_lembrete>', methods=['GET','POST'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['ORIENTADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0], usuario_urole_roles['COLAB_EXTERNO'][0]])
def excluir_lembrete(id_lembrete):

    entidade_usuario = Usuario.query.filter_by(id = current_user.id, status = True).first()
    entidade_lembrete = db.session.query(Lembrete).get(id_lembrete)
    
    if entidade_usuario.urole != 'admin':
        if entidade_lembrete.id_do_criador == entidade_usuario.id:
            entidade_lembrete.status = False
            db.session.commit() 
            flash("Lembrete excluído com sucesso!", 'success')
            return redirect((url_for('casos.lembretes', id_caso = entidade_lembrete.id_caso)))      
        else:
            flash("Você não possui autorização!", 'warning')
            return redirect((url_for('casos.lembretes', id_caso = entidade_lembrete.id_caso)))           
    else:    
        entidade_lembrete.status = False
        db.session.commit() 
        flash("Lembrete excluído com sucesso!", 'success')
        return redirect((url_for('casos.lembretes', id_caso = entidade_lembrete.id_caso)))

# Função de cadastrar um novo histórico
def cadastrar_historico(id_usuario,id_caso):

    historico = Historico()
    usuario = db.session.query(Usuario).filter((Usuario.id == id_usuario)).first()
    caso = db.session.query(Caso).filter((Caso.id == id_caso)).first()

    historico.id_usuario = usuario.id
    historico.id_caso = caso.id
    historico.data = datetime.now()

    try:
        db.session.add(historico)
        db.session.commit()
    except SQLAlchemyError as e:
        erro = str(e.__dict__['orig'])
        flash(erro,"danger")
        return False

    return True

# Rota para visualização de um novo histórico
@casos.route('/historico/<id_caso>')
def historico(id_caso):
    historicos = db.session.query(Historico,Caso,Usuario).select_from(Historico).join(Caso).filter((Caso.id == id_caso) & (Usuario.id == Historico.id_usuario)).all()
    return render_template('historico.html', historicos = historicos, caso_id = id_caso)


# Meus casos
@casos.route('/meus_casos')
@login_required()
def meus_casos():
    page = request.args.get('page', 1, type=int)
    opcao_filtro = request.args.get('opcao_filtro', opcoes_filtro_meus_casos['ATIVO'][0], type=str)

    casos = query_opcoes_filtro_meus_casos(current_user.id, opcao_filtro).paginate(page, app.config['CASOS_POR_PAGINA'], False)

    titulo_total = titulo_total_meus_casos(casos.total)
    
    return render_template(
                            'meus_casos.html', 
                            opcoes_filtro_meus_casos = opcoes_filtro_meus_casos, 
                            titulo_total = titulo_total,
                            **params_busca_casos(casos, ROTA_PAGINACAO_MEUS_CASOS, opcao_filtro)
                           ) 

@casos.route('/ajax_filtro_meus_casos')
@login_required()
def ajax_filtro_meus_casos():
    page = request.args.get('page', 1, type=int)
    opcao_filtro = request.args.get('opcao_filtro', opcoes_filtro_meus_casos['ATIVO'][0], type=str)

    casos = query_opcoes_filtro_meus_casos(current_user.id, opcao_filtro).paginate(page, app.config['CASOS_POR_PAGINA'], False)

    titulo_total = titulo_total_meus_casos(casos.total)

    return render_template(
                            'busca_casos.html', 
                            titulo_total = titulo_total,
                            **params_busca_casos(casos, ROTA_PAGINACAO_MEUS_CASOS, opcao_filtro)
                           ) 

@casos.route('/novo_evento/<int:id_caso>', methods=['GET','POST'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['ORIENTADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0], usuario_urole_roles['COLAB_EXTERNO'][0]])
def novo_evento(id_caso):
    _form = EventoForm()
    if _form.validate_on_submit():
        
        arquivo = request.files.get('arquivo')
        nome_arquivo = None
        
        _evento = Evento(
            id_caso       = id_caso,
            tipo          = _form.tipo.data,
            descricao     = _form.descricao.data,
            data_evento   = _form.data_evento.data,
            arquivo       = (datetime.now().strftime("%d%m%Y") + '.' + (arquivo.filename.split(".")[1]) if arquivo else None),
            data_criacao  = datetime.now(),
            id_criado_por = current_user.id,
        )

        db.session.add(_evento)
        db.session.commit()

        if arquivo:
            nome_arquivo = f'evento_{_evento.id}_{datetime.now().strftime("%d%m%Y")}.{arquivo.filename.split(".")[1]}'
            arquivo.save(os.path.join(current_app.root_path,'static','eventos', nome_arquivo))

        flash('Evento criado com sucesso!','success')
        return redirect(url_for('casos.visualizar_caso', id = id_caso))

    return render_template('novo_evento.html', form = _form, id_caso = id_caso)

# Rota para página de editar eventos
@casos.route('/editar_evento/<id_evento>', methods = ['POST', 'GET'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['ORIENTADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0], usuario_urole_roles['COLAB_EXTERNO'][0]])
def editar_evento(id_evento):
    def setValoresEvento(form : EventoForm, entidade_evento: Evento):
        form.tipo.data = entidade_evento.tipo
        form.descricao.data = entidade_evento.descricao
        form.data_evento.data = entidade_evento.data_evento

    def setDadosEvento(form : EventoForm, entidade_evento: Evento):
        entidade_evento.tipo = form.tipo.data
        entidade_evento.descricao = form.descricao.data
        entidade_evento.data_evento = form.data_evento.data

    entidade_evento = Evento.query.filter_by(id = id_evento, status = True).first()
    if not entidade_evento:
        flash("Esse evento não existe!", "warning")
        return redirect(url_for("casos.index"))
 
    form = EventoForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template('editar_evento.html', form = form, id_evento = id_evento)
        
        arquivo = request.files.get('arquivo')
        nome_arquivo = None
        setDadosEvento(form, entidade_evento)
        entidade_evento.arquivo = (datetime.now().strftime("%d%m%Y") + '.' + (arquivo.filename.split(".")[1]) if arquivo else None)
        if arquivo:
            nome_arquivo = f'evento_{entidade_evento.id}_{datetime.now().strftime("%d%m%Y")}.{arquivo.filename.split(".")[1]}'
            arquivo.save(os.path.join(current_app.root_path,'static','eventos', nome_arquivo),)

        db.session.commit()
        flash("Evento editado com sucesso!", "success")
        return redirect(url_for('casos.eventos', id_caso = entidade_evento.id_caso))

    setValoresEvento(form, entidade_evento)
    return render_template('editar_evento.html', form = form, id_evento = id_evento)

@casos.route('/excluir_evento/<id_evento>', methods=['GET','POST'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['ORIENTADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0], usuario_urole_roles['COLAB_EXTERNO'][0]])
def excluir_evento(id_evento):

    entidade_usuario = Usuario.query.filter_by(id = current_user.id, status = True).first()
    entidade_evento = db.session.query(Evento).get(id_evento)
    
    if entidade_usuario.urole != 'admin':
        if entidade_evento.id_criado_por == entidade_usuario.id:
            entidade_evento.status = False
            db.session.commit() 
            flash("Evento excluído com sucesso!", 'success')
            return redirect((url_for('casos.eventos', id_caso = entidade_evento.id_caso)))      
        else:
            flash("Você não possui autorização!", 'warning')
            return redirect((url_for('casos.eventos', id_caso = entidade_evento.id_caso)))           
    else:    
        entidade_evento.status = False
        db.session.commit() 
        flash("Evento excluído com sucesso!", 'success')
        return redirect((url_for('casos.eventos', id_caso = entidade_evento.id_caso)))

# Rota para a página de visualizar eventos
@casos.route('/visualizar_evento/<id_evento>')
@login_required()
def visualizar_evento(id_evento):

    entidade_evento = Evento.query.filter_by(id = id_evento, status = True).first()
    if not entidade_evento:
        flash("Evento inexistente!", "warning")
        return redirect(url_for('casos.index'))

    return render_template('visualizar_evento.html', entidade_evento = entidade_evento)

@casos.route('/novo_processo/<id_caso>', methods=['POST', 'GET'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['ORIENTADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0], usuario_urole_roles['COLAB_EXTERNO'][0]])
def novo_processo(id_caso):

    entidade_caso = Caso.query.filter_by(id = id_caso, status = True).first()
    if not entidade_caso:
        flash('Não é possível associar um processo a esse caso!', 'warning')
        return redirect(url_for('casos.index'))

    form = ProcessoForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template('novo_processo.html', form = form)

        entidade_processo = Processo(
                                    especie                  = form.especie.data,
                                    numero                   = form.numero.data,
                                    identificacao            = form.identificacao.data,
                                    vara                     = form.vara.data,
                                    link                     = form.link.data,  
                                    probabilidade            = form.probabilidade.data,
                                    posicao_assistido        = form.posicao_assistido.data,
                                    valor_causa_inicial      = form.valor_causa.data,
                                    valor_causa_atual        = form.valor_causa.data,
                                    data_distribuicao        = form.data_distribuicao.data,
                                    data_transito_em_julgado = form.data_transito_em_julgado.data,
                                    obs                      = form.obs.data,
                                    id_caso                  = entidade_caso.id,
                                    id_criado_por            = current_user.id 
            )

        db.session.add(entidade_processo)
        db.session.commit()
        flash('Processo associado com sucesso!', "success")
        return redirect(url_for('casos.index'))

    return render_template('novo_processo.html', form = form)

@casos.route('/processo/<int:id_processo>', methods=['GET'])
@login_required()
def visualizar_processo(id_processo):
    id_caso = request.args.get('id_caso', -1, type = int)
    _processo = Processo.query.filter_by(id = id_processo, status = True).first_or_404()
    return render_template('visualizar_processo.html', processo = _processo, id_caso = id_caso )

# Cadastrar evento
@casos.route('/cadastrar_evento')
def cadastrar_evento():
    return render_template('novo_evento.html')

@casos.route('/excluir_caso/<id_caso>', methods=['GET','POST'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0]])
def excluir_caso(id_caso):
    rota_paginacao = request.args.get('rota_paginacao', ROTA_PAGINACAO_CASOS, type=str)

    caso = db.session.query(Caso).get(id_caso)

    caso.status = False
    db.session.commit() 

    return redirect(url_for(rota_paginacao))

@casos.route('/excluir_processo/<id_processo>', methods=['GET','POST'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['ORIENTADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0], usuario_urole_roles['COLAB_EXTERNO'][0]])
def excluir_processo(id_processo):
    def validaExclusao(processo: Processo):
        if current_user.urole == usuario_urole_roles['ADMINISTRADOR'][0]:
            return True
        if current_user.id == processo.id_criado_por:
            return True

        return False  



    id_caso = request.args.get('id_caso', -1, type = int)
    
    processo = queryFiltradaStatus(Processo).filter_by(id = id_processo).first()

    if validaExclusao(processo):
        processo.status = False
        db.session.commit()
        flash('Processo excluído!', 'success')
    else:
        flash('Você não pode excluir este processo.', 'warning')
    return redirect(url_for('casos.visualizar_caso', id = id_caso))

@casos.route("/editar_processo/<id_processo>", methods=['POST', 'GET'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['ORIENTADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0], usuario_urole_roles['COLAB_EXTERNO'][0]])
def editar_processo(id_processo):
    def setValoresProcesso(form : ProcessoForm, entidade_processo: Processo):
        form.especie.data = entidade_processo.especie
        form.numero.data = entidade_processo.numero
        form.identificacao.data = entidade_processo.identificacao
        form.vara.data = entidade_processo.vara
        form.link.data = entidade_processo.link
        form.probabilidade.data = entidade_processo.probabilidade
        form.posicao_assistido.data = entidade_processo.posicao_assistido
        form.valor_causa.data = entidade_processo.valor_causa_atual
        form.data_distribuicao.data = entidade_processo.data_distribuicao
        form.data_transito_em_julgado.data = entidade_processo.data_transito_em_julgado
        form.obs.data = entidade_processo.obs

    def setDadosProcesso(form : ProcessoForm, entidade_processo: Processo):
        entidade_processo.especie = form.especie.data
        entidade_processo.numero = form.numero.data
        entidade_processo.identificacao = form.identificacao.data
        entidade_processo.vara = form.vara.data
        entidade_processo.link = form.link.data
        entidade_processo.probabilidade = form.probabilidade.data
        entidade_processo.posicao_assistido = form.posicao_assistido.data
        entidade_processo.valor_causa_atual = form.valor_causa.data
        entidade_processo.data_distribuicao = form.data_distribuicao.data
        entidade_processo.data_transito_em_julgado = form.data_transito_em_julgado.data
        entidade_processo.obs = form.obs.data

    entidade_processo = Processo.query.filter_by(id = id_processo, status = True).first()
    if not entidade_processo:
        flash('Esse processo não existe!', "warning")
        return redirect(url_for('casos.index'))
    form = ProcessoForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template('editar_processo.html', form = form, id_processo = id_processo)
        setDadosProcesso(form, entidade_processo)
        db.session.commit()
        flash('Processo editado com sucesso!', "success")
        return redirect(url_for('casos.processos', id_caso = entidade_processo.id_caso))

    setValoresProcesso(form, entidade_processo)
    return render_template('editar_processo.html', form = form, id_processo = id_processo)
