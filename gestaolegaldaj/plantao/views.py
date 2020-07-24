from flask import Blueprint, flash, redirect, render_template, request, url_for, session, json
from flask_login import current_user
from flask_paginate import Pagination, get_page_args

from gestaolegaldaj import app, db, login_required
from gestaolegaldaj.plantao.forms import (CadastroAtendidoForm,
                                          EditarAssistidoForm,
                                          OrientacaoJuridicaForm,
                                          TornarAssistidoForm,
                                          assistido_fisicoOuJuridico,
                                          EditarAJ)
from gestaolegaldaj.plantao.models import (Assistido,
                                           AssistidoPessoaJuridica, Atendido,
                                           OrientacaoJuridica)
from gestaolegaldaj.plantao.views_util import *
from gestaolegaldaj.usuario.models import (Endereco, Usuario,
                                           usuario_urole_roles)

plantao = Blueprint('plantao', __name__, template_folder='templates')

####Cadastrar Atendido
@plantao.route('/novo_atendimento', methods=['GET','POST'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['COLAB_PROJETO'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0]])
def cadastro_na():
    def validaDadosForm(form: CadastroAtendidoForm):
        emailRepetido = Atendido.query.filter_by(email= form.email.data).first()

        if not form.validate():
            return False
        if (emailRepetido):
            flash("Este email já está em uso.","warning")
            return False
        return True
    def CriaAtendido(form: CadastroAtendidoForm):
        entidade_endereco = Endereco(logradouro = form.logradouro.data,
                                     numero = form.numero.data,
                                     complemento = form.complemento.data,
                                     bairro = form.bairro.data,
                                     cep = form.cep.data
                                     )
        db.session.add(entidade_endereco)
        db.session.flush()
        entidade_atendido = Atendido(nome                    = form.nome.data,
                                     data_nascimento         = form.data_nascimento.data,
                                     cpf                     = form.cpf.data,
                                     cnpj                    = form.cnpj.data,
                                     telefone                = form.telefone.data,
                                     celular                 = form.celular.data,
                                     email                   = form.email.data,
                                     estado_civil            = form.estado_civil.data,
                                     area_juridica           = form.area_juridica.data,
                                     como_conheceu           = form.como_conheceu.data,
                                     indicacao_orgao         = form.indicacao_orgao.data,
                                     procurou_outro_local    = form.procurou_outro_local.data,
                                     procurou_qual_local     = form.procurou_qual_local.data,
                                     obs                     = form.obs.data,
                                     endereco_id             = entidade_endereco.id,
                                     pj_constituida          = form.pj_constituida.data,
                                     repres_legal            = form.repres_legal.data,
                                     nome_repres_legal       = form.nome_repres_legal.data,
                                     cpf_repres_legal        = form.cpf_repres_legal.data,
                                     contato_repres_legal    = form.contato_repres_legal.data,
                                     rg_repres_legal         = form.rg_repres_legal.data,
                                     nascimento_repres_legal = form.nascimento_repres_legal.data,
                                     pretende_constituir_pj  = form.pretende_constituir_pj.data
                                     )
        entidade_atendido.setIndicacao_orgao(form.indicacao_orgao.data, entidade_atendido.como_conheceu)
        entidade_atendido.setCnpj(entidade_atendido.pj_constituida, form.cnpj.data, form.repres_legal.data)
        entidade_atendido.setRepres_legal(entidade_atendido.repres_legal, form.nome_repres_legal.data, 
                                      form.cpf_repres_legal.data, form.contato_repres_legal.data, 
                                      form.rg_repres_legal.data, form.nascimento_repres_legal.data)
        entidade_atendido.setProcurou_qual_local(entidade_atendido.procurou_outro_local, form.procurou_qual_local.data)

        return entidade_atendido

############################################# IMPLEMENTAÇÃO DA ROTA ##############################################################

    form = CadastroAtendidoForm()

    if request.method == 'POST':

        if not validaDadosForm(form):
            return render_template('cadastro_novo_atendido.html', form = form)

        db.session.add(CriaAtendido(form))
        db.session.commit()

        flash("Atendido cadastrado!","success")
        return redirect(url_for('principal.index'))

    return render_template('cadastro_novo_atendido.html', form = form)

#### Listar atendidos (com busca)
@plantao.route('/atendidos_assistidos',methods=['GET','POST'])
@login_required()
def listar_atendidos():
    page = request.args.get('page', 1, type=int)
    if request.method == 'POST':
        busca = request.get_data().decode("utf-8")
        atendidos = Atendido.query.filter((Atendido.nome.contains(busca)) | (Atendido.cpf.contains(busca)) | (Atendido.cnpj.contains(busca))).order_by('nome').paginate(page, app.config['USUARIOS_POR_PAGINA'], False)
        assistidos = Assistido.query.all()
        lista_assistidos = list()
        for assistido in assistidos:
            lista_assistidos.append(assistido.id_atendido)
        return render_template("busca_atendidos.html", atendidos = atendidos, assistidos = assistidos, lista_assistidos = lista_assistidos)

    else:
        atendidos = Atendido.query.order_by('nome').paginate(page, app.config['ATENDIDOS_POR_PAGINA'], False)
        assistidos = Assistido.query.all()
        lista_assistidos = list()
        for assistido in assistidos:
            lista_assistidos.append(assistido.id_atendido)
    return render_template("lista_atendidos.html", atendidos = atendidos, assistidos = assistidos, lista_assistidos = lista_assistidos)

#### Listar todos Atendidos (faz parte da busca dos atendidos)
@plantao.route('/todos_atendidos',methods=['GET'])
@login_required()
def todos_atendidos():
    if request.method == 'GET':
        atendidos = Atendido.query.order_by('nome')
        assistidos = Assistidos.query.all()
        return render_template("todos_atendidos.html", atendidos = atendidos, assistidos = assistidos)

### Dados do atendido
@plantao.route('/dados_atendido/<int:id>',methods=['GET'])
@login_required()
def dados_atendido(id):
    _atendido = Atendido.query.get_or_404(id)
    _form = CadastroAtendidoForm()
    setValoresFormAtendido(_atendido, _form)
    _form.id_atendido = _atendido.id
    return render_template('dados_atendido.html', form = _form)

####Excluir Atendido
@plantao.route('/excluir_atendido/',methods=['POST', 'GET'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0]])
def excluir_atendido():

    entidade_atendido_atual = Atendido.query.filter_by(id = current_user.get_id()).first()

    if request.method == 'POST':
        form = request.form
        id = form["id"]
        entidade_atendido = Atendido.query.filter_by(id = id).first()

        if entidade_atendido_atual == entidade_atendido:
            flash("Você não tem permissão para executar esta ação.","warning")
            return redirect(url_for('principal.index'))

        db.session.delete(entidade_atendido)
        db.session.commit()
    lista = Atendido.query.all()
    return render_template("listar_atendidos.html", atendidos = atendidos, assistidos = assistidos, lista_assistidos = lista_assistidos)

####Editar Atendido
@plantao.route('/editar_atendido/<id_atendido>', methods=['POST', 'GET'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['COLAB_PROJETO'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0]])
def editar_atendido(id_atendido):
############################################# IMPLEMENTAÇÃO DA ROTA ##############################################################

    entidade_atendido = Atendido.query.filter_by(id = id_atendido).first()

    if not entidade_atendido:
        flash("Este atendido não existe!","warning")
        return redirect(url_for('principal.index'))

    form = CadastroAtendidoForm()
    if request.method == 'POST':

        if not validaDadosEditar_atendidoForm(form, request.form['emailAtual']):
            return render_template('editar_atendido.html', atendido = entidade_atendido, form = form)

        setDadosAtendido(entidade_atendido, form)
        db.session.commit()
        flash('Atendido editado com sucesso!',"success")
        return redirect(url_for('principal.index'))

    setValoresFormAtendido(entidade_atendido, form)
    # form.cpfOuCnpj.render_kw = {}
    # if (AssistidoPessoaFisica.query.filter_by(id_atendido = id_atendido).first()) or (AssistidoPessoaJuridica.query.filter_by(id_atendido = id_atendido).first()):
    #     form.cpfOuCnpj.render_kw['disabled'] = 'disabled'

    return render_template('editar_atendido.html', atendido = entidade_atendido, form = form)

@plantao.route('/tornar_assistido/<id_atendido>', methods=['POST', 'GET'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0]])
def tornar_assistido(id_atendido):
############################################# IMPLEMENTAÇÃO DA ROTA ##############################################################

    entidade_atendido = Atendido.query.filter_by(id = id_atendido).first()
    atendidoRepetido = Assistido.query.filter_by(id_atendido= id_atendido).first()

    if not entidade_atendido:
        flash("Este atendido não existe!","warning")
        return redirect(url_for('principal.index'))

    if (atendidoRepetido):
        flash("Este Assistido já existe!","warning")
        return redirect(url_for('plantao.listar_atendidos'))

    form = TornarAssistidoForm()

    form.pj_constituida.data = False if entidade_atendido.pj_constituida == '0' else True

    if request.method == 'POST':
        if not form.validate():
           # flash("Erro validação Formulario","warning")
            return render_template('tornar_assistido.html', atendido = entidade_atendido, form = form)

        entidade_assistido = Assistido()
        entidade_assistido.id_atendido = id_atendido

        setDadosGeraisAssistido(entidade_assistido, form)

        db.session.add(entidade_assistido)
        db.session.commit()

        if entidade_atendido.pj_constituida == '1':
            entidade_assistidoPessoaJuridica = AssistidoPessoaJuridica()
            entidade_assistidoPessoaJuridica.id_assistido = entidade_assistido.id

            setDadosAssistidoPessoaJuridica(entidade_assistidoPessoaJuridica, form)

            db.session.add(entidade_assistidoPessoaJuridica)
            db.session.commit()

        flash('Assistido cadastrado com sucesso!',"success")

        return redirect(url_for('principal.index'))

    return render_template('tornar_assistido.html', atendido = entidade_atendido, form = form)

@plantao.route('/excluir_assistido/<tipo>/<int:id_assistido>', methods=['POST'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0]])
def excluir_assistido(tipo, id_assistido):
    if tipo == 'F':
        entidade = Assistido.query.get_or_404(id_assistido)
    elif tipo == 'J':
        entidade = AssistidoPessoaJuridica.query.get_or_404(id_assistido)
    else:
        flash("Operação inválida!","danger")
        return(redirect(url_for('plantao.listar_assistidos', Jud_Fis = tipo)))
    db.session.delete(entidade)
    db.session.commit()
    flash("Exclusão concluída! Note que os dados básicos de atendimento não são excluídos com esta operação.","success")
    return(redirect(url_for('plantao.listar_assistidos', Jud_Fis = tipo)))

@plantao.route('/editar_assistido/<id_atendido>/', methods=['POST', 'GET'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['COLAB_PROJETO'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0]])
def editar_assistido(id_atendido):
    def setValoresFormAssistido(entidade_assistido: Assistido, form: TornarAssistidoForm):
        form.sexo.data                  = entidade_assistido.sexo
        form.raca.data                  = entidade_assistido.raca
        form.profissao.data             = entidade_assistido.profissao
        form.rg.data                    = entidade_assistido.rg
        form.grau_instrucao.data        = entidade_assistido.grau_instrucao
        form.salario.data               = entidade_assistido.salario
        form.beneficio.data             = entidade_assistido.beneficio
        form.contribui_inss.data        = entidade_assistido.contribui_inss
        form.qtd_pessoas_moradia.data   = entidade_assistido.qtd_pessoas_moradia
        form.renda_familiar.data        = entidade_assistido.renda_familiar
        form.participacao_renda.data    = entidade_assistido.participacao_renda
        form.tipo_moradia.data          = entidade_assistido.tipo_moradia
        form.possui_outros_imoveis.data = entidade_assistido.possui_outros_imoveis
        form.possui_veiculos.data       = entidade_assistido.possui_veiculos
        form.doenca_grave_familia.data  = entidade_assistido.doenca_grave_familia
        form.obs.data                   = entidade_assistido.obs
        form.quantos_veiculos.data      = entidade_assistido.quantos_veiculos
        form.ano_veiculo.data           = entidade_assistido.ano_veiculo
        form.pessoa_doente.data         = entidade_assistido.pessoa_doente
        form.pessoa_doente_obs.data     = entidade_assistido.pessoa_doente_obs
        form.gastos_medicacao.data      = entidade_assistido.gastos_medicacao

    def setValoresFormAssistidoPessoaJuridica(entidade_assistido_pj: AssistidoPessoaJuridica, form: TornarAssistidoForm):
        form.socios.data                = entidade_assistido_pj.socios
        form.situacao_receita.data      = entidade_assistido_pj.situacao_receita
        form.enquadramento.data         = entidade_assistido_pj.enquadramento
        form.sede_bh.data               = entidade_assistido_pj.sede_bh
        form.area_atuacao.data          = entidade_assistido_pj.area_atuacao
        form.negocio_nascente.data      = entidade_assistido_pj.negocio_nascente
        form.orgao_registro.data        = entidade_assistido_pj.orgao_registro
        form.faturamento_anual.data     = entidade_assistido_pj.faturamento_anual
        form.ultimo_balanco_neg.data    = entidade_assistido_pj.ultimo_balanco_neg
        form.resultado_econ_neg.data    = entidade_assistido_pj.resultado_econ_neg
        form.tem_funcionarios.data      = entidade_assistido_pj.tem_funcionarios
        form.qtd_funcionarios.data      = entidade_assistido_pj.qtd_funcionarios
        form.regiao_sede_bh.data        = entidade_assistido_pj.regiao_sede_bh
        form.regiao_sede_outros.data    = entidade_assistido_pj.regiao_sede_outros

############################################# IMPLEMENTAÇÃO DA ROTA ##############################################################

    entidade_assistido = Assistido.query.filter_by(id_atendido = id_atendido).first()
    entidade_assistido_pj = AssistidoPessoaJuridica()
    if not entidade_assistido:
        flash("Este assistido não existe!","warning")
        return redirect(url_for('principal.index'))

    form = EditarAssistidoForm()
    if request.method == 'POST':
        if not validaDadosEditar_atendidoForm(form, request.form['emailAtual']):
            return render_template('editar_assistido.html', atendido = entidade_assistido.atendido, form = form)

        setDadosGeraisAssistido(entidade_assistido, form)
        setDadosAtendido(entidade_assistido.atendido, form)
        entidade_assistido_pj = AssistidoPessoaJuridica.query.filter_by(id_assistido = entidade_assistido.id).first()
        if entidade_assistido.atendido.pj_constituida:
            if not entidade_assistido_pj:
                entidade_assistido_pj = AssistidoPessoaJuridica()
                entidade_assistido_pj.id_assistido = entidade_assistido.id
                setDadosAssistidoPessoaJuridica(entidade_assistido_pj, form)
                db.session.add(entidade_assistido_pj)
            else:
                setDadosAssistidoPessoaJuridica(entidade_assistido_pj, form)
        else:
            if entidade_assistido_pj:
                db.session.delete(entidade_assistido_pj)

        #TODO REVER ESSE TRECHO 
        id_orientacaoJuridica   = 0

        db.session.commit()
        flash('Assistido editado com sucesso!', 'success')
        return redirect(url_for('principal.index'))

    setValoresFormAtendido(entidade_assistido.atendido, form)
    setValoresFormAssistido(entidade_assistido, form)
    if entidade_assistido.atendido.pj_constituida:
        setValoresFormAssistidoPessoaJuridica(entidade_assistido_pj, form)

    return render_template('editar_assistido.html', atendido = entidade_assistido.atendido, form = form)

@plantao.route('/cadastro_orientacao_juridica/', methods=['POST', 'GET'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0]])
def cadastro_orientacao_juridica():
    page = request.args.get('page', 1, type=int)
    subArea=None;
    def CriaOrientacao(form: OrientacaoJuridicaForm):
        entidade_orientacao = OrientacaoJuridica(area_direito       = form.area_direito.data,
                                                 sub_area           = subArea,
                                                 descricao          = form.descricao.data
                                                 )
        return entidade_orientacao
    form = OrientacaoJuridicaForm()
    if request.method == 'POST':

        if not form.validate():
            return render_template('cadastro_orientacao_juridica.html', form = form)

        if form.area_direito.data=="civel":
            subArea=form.sub_area.data
        elif form.area_direito.data=="administrativo":
            subArea=form.sub_areaAdmin.data


        db.session.add(CriaOrientacao(form))
        db.session.commit()

        flash("Orientação jurídica cadastrada!","success")
        lista = Atendido.query.paginate(page, app.config['ATENDIDOS_POR_PAGINA'], False)
        result = []
        for item in lista.items:
          if item.id_orientacaoJuridica is None:
            result.append(item)
        orientacao = OrientacaoJuridica.query.order_by("id")
        orientacao_entidade = orientacao[-1]
        return render_template('associa_orientacao_juridica.html', lista = result, pagination=lista, orientacao_entidade= orientacao_entidade)

    return render_template('cadastro_orientacao_juridica.html', form = form)

# Busca dos atendidos para associar a uma orientação jurídica
@plantao.route('/busca_atendidos_oj/', defaults={'_busca': None})
@plantao.route('/busca_atendidos_oj/<_busca>', methods=['POST','GET'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0]])
def busca_atendidos_oj(_busca):
    if _busca is None:
        atendidos = db.session.query(Atendido).filter(Atendido.id_orientacaoJuridica == None).all()
    else:
        atendidos = db.session.query(Atendido).filter(((Atendido.nome.contains(_busca)) | (Atendido.cpf.contains(_busca))) & (Atendido.id_orientacaoJuridica == None) ).all()
    response = app.response_class(
        response = json.dumps(serializar(atendidos)),
        status = 200,
        mimetype = 'application/json'
    )
    return response

def serializar(lista):
	return [x.as_dict() for x in lista]

@plantao.route('/associa_orientacao_juridica/<id_orientacao>/<id_atendido>', methods=['POST', 'GET'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0]])
def associa_orientacao_juridica(id_orientacao,id_atendido):
    page = request.args.get('page', 1, type=int)
    lista = Atendido.query.paginate(page, app.config['ATENDIDOS_POR_PAGINA'], False)
    orientacao = OrientacaoJuridica.query.get_or_404(id_orientacao)
    form=CadastroAtendidoForm()
    entidade_atendido = Atendido.query.filter_by(id = id_atendido).first()
    if not entidade_atendido:
        flash("Este atendido não existe!","warning")
        return redirect(url_for('principal.index'))
    else:
        if not entidade_atendido.id_orientacaoJuridica:
            form = CadastroAtendidoForm()
            setValoresFormAtendido(entidade_atendido, form)
            form.id_atendido = entidade_atendido.id
            form.id_orientacaoJuridica.data = id_orientacao
            setDadosAtendido(entidade_atendido, form)
            db.session.commit()
            flash('Orientação Jurídica associada com sucesso!',"success")
            result = []
            for item in lista.items:
              if item.id_orientacaoJuridica is None:
                result.append(item)
            return render_template('associa_orientacao_juridica.html', lista=result, pagination=lista, orientacao_entidade=orientacao)
    setValoresFormAtendido(entidade_atendido, form)
    result = []
    for item in lista.items:
      if item.id_orientacaoJuridica is None:
        result.append(item)
    return render_template('associa_orientacao_juridica.html', lista = result, pagination=lista, orientacao_entidade=orientacao)

@plantao.route('/perfil_assistido/<int:_id>', methods=['GET'])
@login_required()
def perfil_assistido(_id):
    assistido = db.session.query(Atendido,Assistido,AssistidoPessoaJuridica).select_from(Atendido).outerjoin(Assistido).outerjoin(AssistidoPessoaJuridica).filter((Atendido.id == _id) | (Assistido.id_atendido == _id) | (AssistidoPessoaJuridica.id == _id)).first()
    
    return render_template('perfil_assistidos.html', assistido = assistido)

# Rota de teste da edição da assistência judiciária
@plantao.route('/edicao_aj',methods=['POST','GET'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['PROFESSOR'][0], usuario_urole_roles['COLAB_PROJETO'][0], usuario_urole_roles['COLAB_EXTERNO'][0]])
def edicao_aj():
    form = EditarAJ()

    return render_template("edicao_aj.html", form = form)