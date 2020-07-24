from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from flask_paginate import Pagination, get_page_args
from datetime import datetime

from gestaolegaldaj import db, login_required, app
from gestaolegaldaj.usuario.forms import EditarUsuarioForm, CadastrarUsuarioForm
from gestaolegaldaj.usuario.models import Usuario, usuario_urole_roles, Endereco
from gestaolegaldaj.plantao.models import Atendido
from datetime import datetime

usuario = Blueprint('usuario', __name__, template_folder='templates')

@usuario.route('/relatorio', methods=['GET','POST'])
def relatorio():
    return render_template('relatorio.html')

@usuario.route('/arquivo', methods=['GET','POST'])
def arquivo():
    return render_template('arquivo.html')

@usuario.route('/plantao', methods=['GET','POST'])
def plantao():
    return render_template('plantao.html')

@usuario.route('/casos_id', methods=['GET','POST'])
def casos_esp():
    return render_template('meus_casos.html')

@usuario.route('/notificações_id', methods=['GET','POST'])
def notificaçoes():
    return render_template('notificaçoes.html')


@usuario.route('/casos', methods=['GET','POST'])
def casos():
    return render_template('casos.html')

@usuario.route('/meu_perfil', methods=['GET'])
@login_required()
def meu_perfil():
        entidade_usuario  = Usuario.query.get_or_404(current_user.id)
        entidade_endereco = entidade_usuario.endereco
        return render_template('perfil_usuario.html', usuario = entidade_usuario, endereco = entidade_endereco)

@usuario.route('/perfil/<int:id_user>', methods=['GET'])
@login_required()
def perfil_usuario(id_user):
        entidade_usuario  = Usuario.query.get_or_404(id_user)
        entidade_endereco = entidade_usuario.endereco
        return render_template('perfil_usuario.html', usuario = entidade_usuario, endereco = entidade_endereco)


@usuario.route('/editar_usuario/<int:id_user>', methods=['POST', 'GET'])
@login_required()
def editar_usuario(id_user):
    def editaDadosUsuario(entidade_usuario: Usuario, form: EditarUsuarioForm, usuario_logado: int):
        entidade_usuario.email                = form.email.data
        entidade_usuario.nome                 = form.nome.data
        entidade_usuario.urole                = form.urole.data 
        entidade_usuario.sexo                 = form.sexo.data
        entidade_usuario.rg                   = form.rg.data
        entidade_usuario.cpf                  = form.cpf.data
        entidade_usuario.profissao            = form.profissao.data
        entidade_usuario.telefone             = form.telefone.data
        entidade_usuario.celular              = form.celular.data
        entidade_usuario.obs                  = form.obs.data
        entidade_usuario.oab                  = form.oab.data
        entidade_usuario.matricula            = form.matricula.data
        entidade_usuario.setCamposBolsista(form.bolsista.data, form.tipo_bolsa.data,form.inicio_bolsa.data, form.fim_bolsa.data)
        entidade_usuario.horario_atendimento  = form.horario_atendimento.data
        entidade_usuario.data_entrada         = form.data_entrada.data
        entidade_usuario.data_saida           = form.data_saida.data
        entidade_usuario.nascimento           = form.nascimento.data
        entidade_usuario.estado_civil         = form.estado_civil.data
        entidade_usuario.endereco.logradouro  = form.logradouro.data  
        entidade_usuario.endereco.numero      = form.numero.data      
        entidade_usuario.endereco.bairro      = form.bairro.data      
        entidade_usuario.endereco.cep         = form.cep.data         
        entidade_usuario.endereco.complemento = form.complemento.data
        entidade_usuario.suplente             = form.suplente.data
        entidade_usuario.ferias               = form.ferias.data
        entidade_usuario.cert_atuacao_DAJ     = form.cert_atuacao_DAJ.data

        entidade_usuario.atualizaCamposModificao(usuario_logado)

    def setValoresFormUsuario(form: EditarUsuarioForm, entidade_usuario: Usuario):
        form.email.data                = entidade_usuario.email    
        form.nome.data                 = entidade_usuario.nome
        form.urole.data                = entidade_usuario.urole
        form.sexo.data                 = entidade_usuario.sexo
        form.rg.data                   = entidade_usuario.rg
        form.cpf.data                  = entidade_usuario.cpf
        form.profissao.data            = entidade_usuario.profissao
        form.telefone.data             = entidade_usuario.telefone
        form.celular.data              = entidade_usuario.celular
        form.obs.data                  = entidade_usuario.obs
        form.oab.data                  = entidade_usuario.oab
        form.matricula.data            = entidade_usuario.matricula
        form.bolsista.data             = entidade_usuario.bolsista
        form.tipo_bolsa.data           = entidade_usuario.tipo_bolsa
        form.inicio_bolsa.data         = entidade_usuario.inicio_bolsa
        form.fim_bolsa.data            = entidade_usuario.fim_bolsa
        form.horario_atendimento.data  = entidade_usuario.horario_atendimento
        form.data_entrada.data         = entidade_usuario.data_entrada
        form.data_saida.data           = entidade_usuario.data_saida
        form.nascimento.data           = entidade_usuario.nascimento
        form.estado_civil.data         = entidade_usuario.estado_civil
        form.suplente.data             = entidade_usuario.suplente
        form.ferias.data               = entidade_usuario.ferias
        form.cert_atuacao_DAJ.data     = entidade_usuario.cert_atuacao_DAJ
        form.logradouro.data           = entidade_usuario.endereco.logradouro
        form.numero.data               = entidade_usuario.endereco.numero
        form.bairro.data               = entidade_usuario.endereco.bairro
        form.cep.data                  = entidade_usuario.endereco.cep
        form.complemento.data          = entidade_usuario.endereco.complemento

    def renderizaTemplate(form: EditarUsuarioForm, entidade_usuario: Usuario, id_user: int, id_usuario_logado: int):
        return render_template('editar_usuario.html',
                               form = form,
                               entidade_usuario = entidade_usuario,
                               id_user = id_user,
                               id_usuario_logado = id_usuario_logado)

    def validaDadosForm(email, emailAtual):
        emailRepetido = Usuario.query.filter_by(email= email).first()

        if (emailAtual != email) and emailRepetido:
            flash("Este email já existe!","warning")
            return False
        return True

############################################# IMPLEMENTAÇÃO DA ROTA ##############################################################

    form = EditarUsuarioForm()
    if id_user > 0:
        if (not (current_user.urole in [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['PROFESSOR'][0]])) and (current_user.id != id_user):
            flash("Você não tem permissão para editar outro usuário.","warning")
            return redirect(url_for('principal.index'))    
        entidade_usuario = Usuario.query.filter_by(id = id_user).first() 
    else:
        entidade_usuario = Usuario.query.filter_by(id = current_user.get_id()).first()
        

    if not entidade_usuario:
        flash("Usuário não encontrado.","warning")
        return redirect(url_for('principal.index'))

    if request.method == "POST":

        if(not validaDadosForm(form.email.data, request.form["emailAtual"])) or (not form.validate()):
            return renderizaTemplate(form, entidade_usuario, id_user, current_user.id)

        editaDadosUsuario(entidade_usuario, form, current_user.get_id())

        db.session.commit()

        flash("Usuário alterado com sucesso!","success")
        return redirect(url_for('principal.index'))

    setValoresFormUsuario(form, entidade_usuario)

    return renderizaTemplate(form, entidade_usuario, id_user, current_user.id)

@usuario.route('/editar_senha_usuario', methods=['POST', 'GET'])
@login_required()
def editar_senha_usuario():

    if request.method == 'POST':
        
        entidade_usuario = Usuario.query.filter_by(id = current_user.get_id()).first()

        form = request.form
        confirmacao = form['confirmacao']
        senha = form['senha']

        if not entidade_usuario:
            flash("Usuário não encontrado.","danger")
            return redirect(url_for('principal.index'))

        if (confirmacao == senha):
            entidade_usuario.setSenha(senha)

            db.session.commit()

            flash("Senha alterada com sucesso!","success")
        else:
            flash("Confirmação de senha e senha estão diferentes.","warning")

        return redirect(url_for('principal.index'))

    return render_template('editar_senha_usuario.html')

@usuario.route('/cadastrar_usuario', methods = ['POST', 'GET'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['PROFESSOR'][0]])
def cadastrar_usuario():
    form = CadastrarUsuarioForm()
    if request.method == 'POST':

        senha = form.senha.data
        confirmacao = form.confirmacao.data
        email = form.email.data
        urole = form.urole.data
        nome = form.nome.data
        sexo = form.sexo.data
        rg = form.rg.data
        cpf = form.cpf.data
        profissao = form.profissao.data
        estado_civil = form.estado_civil.data
        nascimento = form.nascimento.data
        telefone = form.telefone.data
        celular = form.celular.data
        data_entrada = form.data_entrada.data
        data_saida = form.data_saida.data
        criado = datetime.now()
        bolsista = form.bolsista.data
        cert_atuacao_DAJ = form.cert_atuacao_DAJ.data
        oab = form.oab.data
        obs = form.obs.data
        matricula = form.matricula.data
        tipo_bolsa = form.tipo_bolsa.data
        horario_atendimento = form.horario_atendimento.data
        inicio_bolsa = form.inicio_bolsa.data
        fim_bolsa = form.fim_bolsa.data
        suplente = form.suplente.data
        ferias = form.ferias.data

        emailRepetido = Usuario.query.filter_by(email= email).first()

        if (confirmacao != senha ):
            flash("Confirmação de senha e senha estão diferentes.","warning")
            return render_template('cadastro.html', form = form)
        elif (emailRepetido):
            flash("Este email já está em uso.","warning")
            return render_template('cadastro.html', form = form) 
        else:

            if not (form.validate()):
                return render_template('cadastro.html', form = form)
            else:
                #entidade_cidade = Cidade(cidade = cidade)

                entidade_endereco = Endereco(logradouro = form.logradouro.data, numero = form.numero.data,
                                             complemento = form.complemento.data, bairro = form.bairro.data, cep = form.cep.data)

                entidade_usuario = Usuario(email = email, senha = senha, urole = urole, nome = nome, sexo = sexo, 
                                           rg = rg, cpf = cpf, profissao = profissao, estado_civil = estado_civil, 
                                           nascimento = nascimento, telefone = telefone, celular = celular, 
                                           data_entrada = data_entrada, data_saida = data_saida, criado = criado, 
                                           criadopor = current_user.get_id(), cert_atuacao_DAJ = cert_atuacao_DAJ, 
                                           endereco_id = entidade_endereco.id, endereco = entidade_endereco, 
                                           oab = oab, obs = obs, matricula = matricula, horario_atendimento = horario_atendimento,
                                           suplente = suplente, ferias = ferias,
                                           status = True)

                entidade_usuario.setSenha(senha)
                entidade_usuario.setCamposBolsista(bolsista, tipo_bolsa, inicio_bolsa, fim_bolsa)

                db.session.add(entidade_usuario)
                db.session.commit()
                flash("Usuário cadastrado!","success")

        return redirect(url_for('principal.index'))

    return render_template('cadastro.html', form = form)

@usuario.route('/login', methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        form = request.form

        login = form["login"]
        senha = form["senha"]

        loginUsuario = Usuario.query.filter_by(email=login).first()
        if (loginUsuario):
            checaSenha = Usuario.checa_senha(loginUsuario, senha)
            if (checaSenha):
                login_user(loginUsuario)
                flash("Você foi logado com sucesso!","success")
                return redirect(url_for('principal.index'))
            else:
                flash("Senha inválida!","warning")
        else:
            flash("Email inválido!","warning")


    return render_template('login.html')

@usuario.route('/logout')
def logout():
    if (current_user):
        flash("Logout feito com sucesso!","info")
        logout_user()
    else:
        flash("Você precisa estar logado para continuar","info")
    return redirect(url_for('usuario.login'))

@usuario.route('/listar_usuarios')
@login_required()
def listar_usuarios():
    page = request.args.get('page', 1, type=int)
    usuarios = Usuario.query.filter(Usuario.status != False).paginate(page, app.config['USUARIOS_POR_PAGINA'], False)
    if not usuarios:
        flash("Não há usuários cadastrados no sistema.","info")
        return redirect(url_for('principal.index'))

    return render_template('listar_usuarios.html', usuarios = usuarios, admin_padrao = app.config['ADMIN_PADRAO'])

@usuario.route('/excluir_usuario/')
@login_required()
def excluir_usuario():
    entidade_usuario = Usuario.query.filter_by(id = current_user.get_id()).first()
    if entidade_usuario.id == app.config['ADMIN_PADRAO']:
        flash("O administrador padrão não pode ser excluído.","warning")
        return redirect(url_for('principal.index'))

    db.session.delete(entidade_usuario)
    db.session.commit()
    return redirect(url_for('principal.index'))

@usuario.route('/admin_excluir_usuario_lista/',methods=['POST', 'GET'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0]])
def admin_excluir_usuario_lista():

    entidade_usuario_atual = Usuario.query.get_or_404(current_user.get_id())

    if request.method == 'POST':
        form = request.form
        form_id = form["id"]
        entidade_usuario = Usuario.query.get_or_404(form_id)

        if entidade_usuario.id == app.config['ADMIN_PADRAO']:
            flash("O administrador padrão não pode ser excluído.","warning")
            return redirect(url_for('principal.index'))

        if entidade_usuario_atual.id == entidade_usuario.id:
            flash("Você não tem permissão para executar esta ação.","warning")
            return redirect(url_for('principal.index'))

        db.session.delete(entidade_usuario)
        db.session.commit()
        flash("Usuário excluído","Success")
    return redirect(url_for('usuario.listar_usuarios'))

@usuario.route('/inativar_usuario_lista/', methods=['POST', 'GET'])
@login_required()
def inativar_usuario_lista():
    if request.method == 'POST':
        form = request.form
        form_id = form["id"]
        entidade_usuario = Usuario.query.get_or_404(form_id)

        if entidade_usuario.id == current_user.get_id():
            flash("Você não tem permissão para executar esta ação.","warning")
            return redirect(url_for('principal.index'))

        if entidade_usuario.id == app.config['ADMIN_PADRAO']:
            flash("O administrador padrão não pode ser inativado.","warning")
            return redirect(url_for('principal.index'))

        entidade_usuario.status = False
        db.session.commit()
        flash("Usuário inativado","Success")
    return redirect(url_for('principal.index'))


