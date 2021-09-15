import os
from datetime import datetime
from unicodedata import normalize

from flask import (Blueprint, flash, redirect, render_template, request, url_for, current_app)
from flask_login import current_user
from gestaolegal import db, login_required, app
from gestaolegal.arquivos.forms import ArquivoForm
from gestaolegal.arquivos.models import Arquivo
from gestaolegal.usuario.models import usuario_urole_roles

arquivos = Blueprint('arquivos', __name__, template_folder='templates')


@arquivos.route('/')
@login_required()
def index():
    page = request.args.get('page', 1, type=int)
    arquivos = Arquivo.query.paginate(page, app.config['ARQUIVOS_POR_PAGINA'], False)
    return render_template('arquivos.html', arquivos = arquivos)

@arquivos.route('/cadastrar_arquivo', methods = ['GET','POST'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['PROFESSOR'][0], usuario_urole_roles['COLAB_PROJETO'][0], usuario_urole_roles['COLAB_EXTERNO'][0]])
def cadastrar_arquivo():
    _form = ArquivoForm()
    if _form.validate_on_submit():
        arquivo = request.files.get(_form.arquivo.name)
        if not arquivo:
        	flash('Você precisa adicionar um arquivo.','warning')
        	return redirect(url_for('arquivos.cadastrar_arquivo'))
        _arquivo = Arquivo(
            titulo = _form.titulo.data,
            descricao = _form.descricao.data,
            nome = arquivo.filename
        )
        arquivo.save(os.path.join(current_app.root_path,'static','arquivos', arquivo.filename))
        db.session.add(_arquivo)
        db.session.commit()
        flash('Arquivo adicionado','success')
        return redirect(url_for('arquivos.index'))

    return render_template('cadastrar_arquivo.html', form = _form)

@arquivos.route('/editar_arquivo/<int:id>', methods = ['GET','POST'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['PROFESSOR'][0], usuario_urole_roles['COLAB_PROJETO'][0], usuario_urole_roles['COLAB_EXTERNO'][0]])
def editar_arquivo(id):
    _arquivo = Arquivo.query.get_or_404(id)
    _form = ArquivoForm()

    if _form.validate_on_submit():
        arquivo = request.files.get(_form.arquivo.name)
        _arquivo.titulo = _form.titulo.data,
        _arquivo.descricao = _form.descricao.data

        if arquivo.filename:
            local_arquivo = os.path.join(current_app.root_path,'static','arquivos', _arquivo.nome)
            if os.path.exists(local_arquivo):
                os.remove(local_arquivo)
            
            _arquivo.nome = arquivo.filename
            arquivo.save(os.path.join(current_app.root_path,'static','arquivos', arquivo.filename))

        db.session.commit()
        flash('Arquivo editado','success')
        return redirect(url_for('arquivos.visualizar_arquivo', id = id))

    _form.titulo.data = _arquivo.titulo
    _form.descricao.data = _arquivo.descricao

    return render_template('editar_arquivo.html', form = _form)


@arquivos.route('/visualizar_arquivo/<int:id>')
@login_required()
def visualizar_arquivo(id):
    _arquivo = Arquivo.query.get_or_404(id)
    return render_template('visualizar_arquivo.html', arquivo = _arquivo)

@arquivos.route('/excluir_arquivo/<int:id>')
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['PROFESSOR'][0], usuario_urole_roles['COLAB_PROJETO'][0]])
def excluir_arquivo(id):
    _arquivo = Arquivo.query.get_or_404(id)
    local_arquivo = os.path.join(current_app.root_path,'static','arquivos', _arquivo.nome)

    if os.path.exists(local_arquivo):
        os.remove(local_arquivo)
    
    db.session.delete(_arquivo)
    db.session.commit()

    flash('arquivo excluido.')

    return redirect(url_for('arquivos.index'))
