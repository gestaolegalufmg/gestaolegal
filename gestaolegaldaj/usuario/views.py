from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from flask_paginate import Pagination, get_page_args
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_mail import Message

from gestaolegaldaj import db, login_required, app, mail
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
        entidade_usuario.endereco.cidade      = form.cidade.data
        entidade_usuario.endereco.estado      = form.estado.data

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
        form.cidade.data               = entidade_usuario.endereco.cidade
        form.estado.data               = entidade_usuario.endereco.estado

    def renderizaTemplate(form: EditarUsuarioForm, entidade_usuario: Usuario, id_user: int, id_usuario_logado: int, id_usuario_padrao: int):
        return render_template('editar_usuario.html',
                               form = form,
                               entidade_usuario = entidade_usuario,
                               id_user = id_user,
                               id_usuario_logado = id_usuario_logado,
                               id_usuario_padrao = id_usuario_padrao)

    def validaDadosForm(email, emailAtual):
        emailRepetido = Usuario.query.filter_by(email= email).first()

        if (emailAtual != email) and emailRepetido:
            flash("Este email já existe!","warning")
            return False
        return True

    def validaEntidade_usuario(entidade_usuario: Usuario):
        if not entidade_usuario:
            flash("Usuário não encontrado.","warning")
            return False

        if (entidade_usuario.id == app.config['ADMIN_PADRAO']) and (int(current_user.get_id()) != app.config['ADMIN_PADRAO']):
            flash("O administrador padrão só pode ser alterado por si próprio.","warning")
            return False
        
        if entidade_usuario.status == False:
            flash("Este usuário está inativo.","warning")
            return False

        return True

############################################# IMPLEMENTAÇÃO DA ROTA ##############################################################

    form = EditarUsuarioForm()
    if id_user > 0:
        if (not (current_user.urole in [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['PROFESSOR'][0]])) and (current_user.id != id_user):
            flash("Você não tem permissão para editar outro usuário.","warning")
            return redirect(url_for('principal.index'))    
        entidade_usuario = Usuario.query.filter_by(id = id_user, status = True).first() 
    else:
        entidade_usuario = Usuario.query.filter_by(id = current_user.get_id(), status = True).first()   

    if not validaEntidade_usuario(entidade_usuario):
        return redirect(url_for('principal.index'))       

    if request.method == "POST":
        if entidade_usuario.id == app.config['ADMIN_PADRAO']:
            form.urole.data = usuario_urole_roles['ADMINISTRADOR'][0]

        if(not validaDadosForm(form.email.data, request.form["emailAtual"])) or (not form.validate()):
            return renderizaTemplate(form, entidade_usuario, id_user, current_user.id, app.config['ADMIN_PADRAO'])

        editaDadosUsuario(entidade_usuario, form, current_user.get_id())

        db.session.commit()

        flash("Usuário alterado com sucesso!","success")
        return redirect(url_for('principal.index'))

    setValoresFormUsuario(form, entidade_usuario)

    return renderizaTemplate(form, entidade_usuario, id_user, current_user.id, app.config['ADMIN_PADRAO'])

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
            return redirect(url_for('principal.index'))
        else:
            flash("Confirmação de senha e senha estão diferentes.","warning")
            return render_template('editar_senha_usuario.html')

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

                entidade_endereco = Endereco(logradouro = form.logradouro.data, numero = form.numero.data,
                                             complemento = form.complemento.data, bairro = form.bairro.data, cep = form.cep.data,
                                             cidade = form.cidade.data,
                                             estado = form.estado.data)

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
    usuarios = db.session.query(Usuario).all()
    if usuarios is None:
        criar_usuarios()
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

@usuario.route('/inativar_usuario_lista/', methods=['POST', 'GET'])
@login_required(role = usuario_urole_roles['ADMINISTRADOR'][0])
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
        flash("Usuário inativado.","Success")
    return redirect(url_for('principal.index'))

@usuario.route('/muda_senha_admin', methods=['POST'])
@login_required(role = usuario_urole_roles['ADMINISTRADOR'][0])
def muda_senha_admin():
    id_usuario = request.form['id']

    return render_template('nova_senha.html', id_usuario = id_usuario)

@usuario.route('/confirma_senha', methods=['POST'])
@login_required(role = usuario_urole_roles['ADMINISTRADOR'][0])
def confirma_senha():
    bcrypt = Bcrypt()
    usuario = Usuario.query.get_or_404(int(request.form['id_usuario']))
    if request.form['senha'] == request.form['confirmar_senha']:
        senha = bcrypt.generate_password_hash(request.form['senha'])
        usuario.senha = senha
        usuario.chave_recuperacao = False
        db.session.commit()
        flash('Sua senha foi alterada com sucesso.','success')
        return redirect(url_for('usuario.listar_usuarios'))
    else:
        flash('As senhas não são iguais','warning')
        return redirect(url_for('usuario.listar_usuarios'))

# def emailRecuperacao(usuario):
#     usuario.chave_recuperacao = True
#     db.session.commit()
#     titulo = "Recuperação de senha Gestão Legal"
#     token = usuario.tokenRecuperacao() # Gera o token para o usuário em questão
#     msg = Message(titulo,sender="gestaolegaldaj@gmail.com",recipients=[usuario.email]) # Constrói o corpo da mensagem
#     msg.body = f''' Solicitação de recuperação/alteração de senha.

#     Se você solicitou este serviço, por favor, clique no link abaixo:
#     {url_for('usuario.nova_senha',_token=token, _external=True)}

#     Caso você não tenha solicitado este serviço, por favor ignore essa mensagem.
#     '''
#     mail.send(msg)

# @usuario.route('/recuperar_senha',methods=['POST','GET'])
# def recuperar_senha():
#     if request.method == 'POST':
#         usuario = db.session.query(Usuario).filter((Usuario.email == request.form['email'])).first()
#         if usuario is None:
#             flash("E-mail não cadastrado.","warning")
#             return redirect(url_for('usuario.recuperar_senha'))
#         emailRecuperacao(usuario)
#         flash('E-mail enviado','success')
#         return redirect(url_for('usuario.login'))
#     return render_template('recuperar_senha.html')

# @usuario.route('/nova_senha/<_token>', methods=['POST','GET'])
# def nova_senha(_token):
#     usuario = Usuario.verificaToken(_token)
#     if usuario is None:
#         flash('Token inválido.','warning')
#         return redirect(url_for('usuario.login'))
#     bcrypt = Bcrypt()
#     if usuario.chave_recuperacao:
#         if request.method == 'POST':
#             if request.form['senha'] == request.form['confirmar_senha']:
#                 senha = bcrypt.generate_password_hash(request.form['senha'])
#                 usuario.senha = senha
#                 usuario.chave_recuperacao = False
#                 db.session.commit()
#                 flash('Sua senha foi alterada com sucesso.','success')
#                 return redirect(url_for('usuario.login'))
#             else:
#                 flash('As senhas não são iguais','warning')
#     else:
#         flash('Erro! Por favor refaça a operação','warning')
#         return redirect(url_for('usuario.recuperar_senha'))
#     return render_template('nova_senha.html')

def criar_usuarios():
    # Administrador
    admin_endereco = Endereco(logradouro = "rua dos bobos", numero = "0",
                                             complemento = "uma casa que não tem nada", bairro = "coqueiros", cep = "31888450",
                                             cidade = "Belo Horizonte",
                                             estado = "MG")
    admin = Usuario(email = "administrador@daj.com",senha = "administrador", urole = "admin", nome = "Administrador", sexo = "M",
                    rg = "23213329080", cpf = "1234567890", profissao = "teste", estado_civil = "solteiro",
                    nascimento = '1999-04-19', telefone = "12345567", celular = "12345567",
                    data_entrada = '2020-05-05', data_saida = '2020-05-06', criado = datetime.now(), criadopor = 1, 
                    endereco_id = admin_endereco.id, endereco = admin_endereco,
                    oab = "teste123", obs = "obs", matricula = "123456743", horario_atendimento = "17:00:00",
                    suplente = "teste", ferias = "teste", status = True)
    admin.setSenha("administrador")
    admin.setCamposBolsista(0,None, None, None)
    # Orientador
    orientador_endereco = Endereco(logradouro = "rua dos bobos", numero = "0",
                                             complemento = "uma casa que não tem nada", bairro = "coqueiros", cep = "30888450",
                                             cidade = "Belo Horizonte",
                                             estado = "MG")
    orientador = Usuario(email = "orientador@daj.com",senha = "orientador", urole = "orient", nome = "Orientador", sexo = "M",
                    rg = "23213329080", cpf = "1234567890", profissao = "teste", estado_civil = "solteiro",
                    nascimento = '1999-04-19', telefone = "12345567", celular = "12345567",
                    data_entrada = '2020-05-05', data_saida = '2020-05-06', criado = datetime.now(), criadopor = 1, 
                    endereco_id = orientador_endereco.id, endereco = orientador_endereco,
                    oab = "teste123", obs = "obs", matricula = "123456743", horario_atendimento = "17:00:00",
                    suplente = "teste", ferias = "teste", status = True)
    orientador.setSenha("orientador")
    orientador.setCamposBolsista(0,None, None, None)
    # Colaborador de projetos
    colaborador_proj_endereco = Endereco(logradouro = "rua dos bobos", numero = "0",
                                             complemento = "uma casa que não tem nada", bairro = "coqueiros", cep = "30888450",
                                             cidade = "Belo Horizonte",
                                             estado = "MG")
    colaborador_proj = Usuario(email = "colaboradorprojetos@daj.com",senha = "colabprojetos", urole = "colab_proj", nome = "Colaborador de Projeto", sexo = "M",
                    rg = "23213329080", cpf = "1234567890", profissao = "teste", estado_civil = "solteiro",
                    nascimento = '1997-02-19', telefone = "973550701", celular = "973550701",
                    data_entrada = '2020-05-05', data_saida = '2020-05-06', criado = datetime.now(), criadopor = 1, 
                    endereco_id = colaborador_proj_endereco.id, endereco = colaborador_proj_endereco,
                    oab = "teste123", obs = "obs", matricula = "123456743", horario_atendimento = "17:00:00",
                    suplente = "teste", ferias = "teste", status = True)
    colaborador_proj.setSenha("colabprojetos")
    colaborador_proj.setCamposBolsista(0,None, None, None)
    # Estagiário
    estagiario_endereco = Endereco(logradouro = "rua dos bobos", numero = "0",
                                             complemento = "uma casa que não tem nada", bairro = "coqueiros", cep = "30888450",
                                             cidade = "Belo Horizonte",
                                             estado = "MG")
    estagiario = Usuario(email = "estagiariodireito@daj.com",senha = "estagiario", urole = "estag_direito", nome = "Estagiário de Direito", sexo = "M",
                    rg = "23213329080", cpf = "1234567890", profissao = "teste", estado_civil = "solteiro",
                    nascimento = '1997-02-19', telefone = "973550701", celular = "973550701",
                    data_entrada = '2020-05-05', data_saida = '2020-05-06', criado = datetime.now(), criadopor = 1, 
                    endereco_id = estagiario_endereco.id, endereco = estagiario_endereco,
                    oab = "teste123", obs = "obs", matricula = "123456743", horario_atendimento = "17:00:00",
                    suplente = "teste", ferias = "teste", status = True)
    estagiario.setSenha("estagiario")
    estagiario.setCamposBolsista(0,None, None, None)
    # Colaborador externo 
    colaborador_ext_endereco = Endereco(logradouro = "rua dos bobos", numero = "0",
                                             complemento = "uma casa que não tem nada", bairro = "coqueiros", cep = "30888450",
                                             cidade = "Belo Horizonte",
                                             estado = "MG")
    colaborador_ext = Usuario(email = "colaboradorexterno@daj.com",senha = "colabexterno", urole = "colab_ext", nome = "Colaborador Externo", sexo = "M",
                    rg = "23213329080", cpf = "1234567890", profissao = "teste", estado_civil = "solteiro",
                    nascimento = '1997-02-19', telefone = "973550701", celular = "973550701",
                    data_entrada = '2020-05-05', data_saida = '2020-05-06', criado = datetime.now(), criadopor = 1, 
                    endereco_id = colaborador_ext_endereco.id, endereco = colaborador_ext_endereco,
                    oab = "teste123", obs = "obs", matricula = "123456743", horario_atendimento = "17:00:00",
                    suplente = "teste", ferias = "teste", status = True)
    colaborador_ext.setSenha("colabexterno")
    colaborador_ext.setCamposBolsista(0,None, None, None)
    # Professor
    professor_endereco = Endereco(logradouro = "rua dos bobos", numero = "0",
                                             complemento = "uma casa que não tem nada", bairro = "coqueiros", cep = "30888450",
                                             cidade = "Belo Horizonte",
                                             estado = "MG")
    professor = Usuario(email = "professor@daj.com",senha = "1234", urole = "prof", nome = "Professor", sexo = "M",
                    rg = "23213329080", cpf = "1234567890", profissao = "professor", estado_civil = "solteiro",
                    nascimento = '1997-02-19', telefone = "973550701", celular = "973550701",
                    data_entrada = '2020-05-05', data_saida = '2020-05-06', criado = datetime.now(), criadopor = 1, 
                    endereco_id = professor_endereco.id, endereco = professor_endereco,
                    oab = "teste123", obs = "obs", matricula = "123456743", horario_atendimento = "17:00:00",
                    suplente = "teste", ferias = "teste", status = True)
    professor.setSenha("1234")
    professor.setCamposBolsista(0,None, None, None)

    db.session.add_all([admin,orientador,colaborador_proj,estagiario,colaborador_ext,professor])
    db.session.commit()

