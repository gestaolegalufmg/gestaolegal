from datetime import datetime, date

from flask import Blueprint, flash, redirect, render_template, request, url_for, session, json
from flask_login import current_user
from flask_paginate import Pagination, get_page_args
from sqlalchemy import desc, asc, null
from sqlalchemy.orm import load_only

from gestaolegaldaj import app, db, login_required
from gestaolegaldaj.plantao.forms import (CadastroAtendidoForm,
                                          EditarAssistidoForm,
                                          OrientacaoJuridicaForm,
                                          TornarAssistidoForm,
                                          AssistenciaJudiciariaForm,
                                          CadastroOrientacaoJuridicaForm,
                                          AbrirPlantaoForm,
                                          SelecionarDuracaoPlantaoForm,
                                          FecharPlantaoForm)
from gestaolegaldaj.plantao.forms import assistencia_jud_areas_atendidas
from gestaolegaldaj.plantao.models import (Assistido,
                                           AssistidoPessoaJuridica, Atendido,
                                           OrientacaoJuridica, AssistenciaJudiciaria,
                                           AssistenciaJudiciaria_xOrientacaoJuridica,
                                           Atendido_xOrientacaoJuridica, DiasMarcadosPlantao,
                                           DiaPlantao, Plantao) 
from gestaolegaldaj.plantao.views_util import *
from gestaolegaldaj.usuario.models import (Endereco, Usuario,
                                           usuario_urole_roles)
from gestaolegaldaj.utils.models import queryFiltradaStatus

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
                                     cep = form.cep.data,
                                     cidade = form.cidade.data,
                                     estado = form.estado.data
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
                                     obs                     = form.obs_atendido.data,
                                     endereco_id             = entidade_endereco.id,
                                     pj_constituida          = form.pj_constituida.data,
                                     repres_legal            = form.repres_legal.data,
                                     nome_repres_legal       = form.nome_repres_legal.data,
                                     cpf_repres_legal        = form.cpf_repres_legal.data,
                                     contato_repres_legal    = form.contato_repres_legal.data,
                                     rg_repres_legal         = form.rg_repres_legal.data,
                                     nascimento_repres_legal = form.nascimento_repres_legal.data,
                                     pretende_constituir_pj  = form.pretende_constituir_pj.data,
                                     status = 1
                                     )
        entidade_atendido.setIndicacao_orgao(form.indicacao_orgao.data, entidade_atendido.como_conheceu)
        entidade_atendido.setCnpj(entidade_atendido.pj_constituida, form.cnpj.data, form.repres_legal.data)

        entidade_atendido.setRepres_legal(entidade_atendido.repres_legal, 
                                          entidade_atendido.pj_constituida,
                                          form.nome_repres_legal.data,
                                          form.cpf_repres_legal.data, 
                                          form.contato_repres_legal.data,
                                          form.rg_repres_legal.data,
                                          form.nascimento_repres_legal.data)

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
        return redirect(url_for('plantao.listar_atendidos'))

    return render_template('cadastro_novo_atendido.html', form = form)

@plantao.route('/busca_atendidos_assistidos',methods=['GET','POST'])
@login_required()
def busca_atendidos_assistidos():
    page = request.args.get('page', 1, type=int)
    tipo_busca = request.args.get('tipo_busca', tipos_busca_atendidos['TODOS'], type=str)
    busca = request.args.get('valor_busca', '', type=str)
    if tipo_busca == tipos_busca_atendidos['TODOS']:
        atendidos_assistidos = busca_todos_atendidos_assistidos(busca, page)
    elif tipo_busca == tipos_busca_atendidos['ATENDIDOS']:
        atendidos_assistidos = (Atendido.query
                                        .filter(((Atendido.nome.contains(busca)) | (Atendido.cpf.contains(busca)) | (Atendido.cnpj.contains(busca))) & (Atendido.status == True))
                                        .outerjoin(Assistido)
                                        .filter(Assistido.atendido == None)
                                        .order_by(Atendido.nome)
                                        .paginate(page, app.config['ATENDIDOS_POR_PAGINA'], False))
        atendidos_assistidos.items = [(x, None) for x in atendidos_assistidos.items]
    elif tipo_busca == tipos_busca_atendidos['ASSISTIDOS']:
        atendidos_assistidos = (db.session
                                  .query(Atendido, Assistido)
                                  .filter(((Atendido.nome.contains(busca)) | (Atendido.cpf.contains(busca)) | (Atendido.cnpj.contains(busca))) & (Atendido.status == True))
                                  .outerjoin(Assistido)
                                  .filter(Assistido.atendido != None)
                                  .order_by(Atendido.nome)
                                  .paginate(page, app.config['ATENDIDOS_POR_PAGINA'], False))

    return render_template("busca_atendidos.html", atendidos_assistidos = atendidos_assistidos, tipos_busca_atendidos=tipos_busca_atendidos)

### Retorna lista de atendidos

@plantao.route('/atendidos_assistidos',methods=['GET','POST'])
@login_required()
def listar_atendidos():
    page = request.args.get('page', 1, type=int)
     
    atendidos_assistidos = busca_todos_atendidos_assistidos('', page)

    return render_template("lista_atendidos.html", atendidos_assistidos = atendidos_assistidos, tipos_busca_atendidos=tipos_busca_atendidos)

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
    page = request.args.get('page', 1, type=int)

    if request.method == 'POST':
        form = request.form
        id = form["id"]
        entidade_atendido = Atendido.query.filter_by(id = id).first()

        if not entidade_atendido:
            flash("Este atendido não existe!","warning")
            return redirect(url_for('plantao.listar_atendidos'))

        entidade_atendido.status = False
        db.session.commit()
        flash('Atendido excluído com sucesso!',"success")
    return redirect(url_for('plantao.listar_atendidos'))

####Editar Atendido
@plantao.route('/editar_atendido/<id_atendido>', methods=['POST', 'GET'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['COLAB_PROJETO'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0]])
def editar_atendido(id_atendido):
############################################# IMPLEMENTAÇÃO DA ROTA ##############################################################

    entidade_atendido = Atendido.query.filter_by(id = id_atendido, status=True).first()

    if not entidade_atendido:
        flash("Este atendido não existe!","warning")
        return redirect(url_for('plantao.listar_atendidos'))

    form = CadastroAtendidoForm()
    if request.method == 'POST':

        if not validaDadosEditar_atendidoForm(form, request.form['emailAtual']):
            return render_template('editar_atendido.html', atendido = entidade_atendido, form = form)

        setDadosAtendido(entidade_atendido, form)
        db.session.commit()
        flash('Atendido editado com sucesso!',"success")
        return redirect(url_for('plantao.listar_atendidos'))

    setValoresFormAtendido(entidade_atendido, form)

    return render_template('editar_atendido.html', atendido = entidade_atendido, form = form)

@plantao.route('/tornar_assistido/<id_atendido>', methods=['POST', 'GET'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0]])
def tornar_assistido(id_atendido):
############################################# IMPLEMENTAÇÃO DA ROTA ##############################################################

    entidade_atendido = Atendido.query.filter_by(id = id_atendido).first()
    atendidoRepetido = Assistido.query.filter_by(id_atendido= id_atendido).first()

    if not entidade_atendido:
        flash("Este atendido não existe!","warning")
        return redirect(url_for('plantao.listar_atendidos'))

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

        return redirect(url_for('plantao.listar_atendidos'))

    return render_template('tornar_assistido.html', atendido = entidade_atendido, form = form)

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
        form.possui_veiculos_obs.data   = entidade_assistido.possui_veiculos_obs
        form.doenca_grave_familia.data  = entidade_assistido.doenca_grave_familia
        form.obs_assistido.data         = entidade_assistido.obs
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

    entidade_assistido = Assistido.query.filter_by(id_atendido = id_atendido).outerjoin(Atendido).filter_by(status=True).first()
    if not entidade_assistido:
        flash("Este assistido não existe!","warning")
        return redirect(url_for('plantao.listar_atendidos'))
        
    entidade_assistido_pj = AssistidoPessoaJuridica.query.filter_by(id_assistido = entidade_assistido.id).first()
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

        db.session.commit()
        flash('Assistido editado com sucesso!', 'success')
        return redirect(url_for('plantao.listar_atendidos'))

    setValoresFormAtendido(entidade_assistido.atendido, form)
    setValoresFormAssistido(entidade_assistido, form)
    if entidade_assistido_pj:
        setValoresFormAssistidoPessoaJuridica(entidade_assistido_pj, form)

    return render_template('editar_assistido.html', atendido = entidade_assistido.atendido, form = form)

@plantao.route('/cadastro_orientacao_juridica/', methods=['POST', 'GET'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0]])
def cadastro_orientacao_juridica():
    def CriaOrientacao(form: CadastroOrientacaoJuridicaForm):
        entidade_orientacao = OrientacaoJuridica(area_direito       = form.area_direito.data,
                                                 descricao          = form.descricao.data,
                                                 status             = True
                                                 )
        entidade_orientacao.setSubAreas(form.area_direito.data, form.sub_area.data, form.sub_areaAdmin.data)
        return entidade_orientacao


    page = request.args.get('page', 1, type=int)
    form = CadastroOrientacaoJuridicaForm()
    if request.method == 'POST':

        if not form.validate():
            return render_template('cadastro_orientacao_juridica.html', form = form)

        entidade_orientacao = CriaOrientacao(form)
        db.session.add(entidade_orientacao)
        db.session.commit()

        flash("Orientação jurídica cadastrada!","success")
        return redirect(url_for('plantao.associacao_orientacao_juridica', id_orientacao = entidade_orientacao.id, encaminhar_outras_aj = form.encaminhar_outras_aj.data))

    return render_template('cadastro_orientacao_juridica.html', form = form)

@plantao.route('/encaminha_assistencia_judiciaria/<int:id_orientacao>', methods=['POST', 'GET'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0], usuario_urole_roles['PROFESSOR'][0]])
def encaminha_assistencia_judiciaria(id_orientacao):
    assistencias_judiciarias = db.session.query(AssistenciaJudiciaria).all()

    if request.method == 'POST':
        list_ids = request.form.getlist('dados[]') # Recebendo a lista de id's da requisição ajax
        
        for item in list_ids:
            aj_oj = AssistenciaJudiciaria_xOrientacaoJuridica()
            aj_oj.id_orientacaoJuridica = id_orientacao
            aj_oj.id_assistenciaJudiciaria = item 
            db.session.add(aj_oj)
            db.session.commit()
        flash("Orientação encaminhada.","success")
        return redirect(url_for('plantao.perfil_oj',id = id_orientacao))
            
    return render_template('encaminha_assistencia_judiciaria.html', assistencias_judiciarias = assistencias_judiciarias, id_orientacao = id_orientacao)

@plantao.route('/ajax_multiselect_associa_aj_oj/<int:orientacao_id>', methods=['POST', 'GET'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0], usuario_urole_roles['PROFESSOR'][0]])
def ajax_multiselect_associa_aj_oj(orientacao_id):
    q = request.args.get('q')

    if q == None:
        resultado_json = {"results": []}
    else:
        orientacao_juridica = OrientacaoJuridica.query.filter_by(id=orientacao_id).first()

        relacoes_aj_oj = (db.session.query(AssistenciaJudiciaria_xOrientacaoJuridica.id_assistenciaJudiciaria)
                                                                   .filter_by(id_orientacaoJuridica = orientacao_juridica.id)
                                                                   .all())
        relacoes_aj_oj = [x[0] for x in relacoes_aj_oj]

        assistencias_judiciarias = (AssistenciaJudiciaria.query 
                                                         .filter(AssistenciaJudiciaria.areas_atendidas.contains(orientacao_juridica.area_direito) & AssistenciaJudiciaria.nome.contains(q)
                                                                & (AssistenciaJudiciaria.status == True)
                                                                & (~AssistenciaJudiciaria.id.in_(relacoes_aj_oj)))
                                                         .all())

        resultado_json = {"results": [{"id": aj.id, "text": aj.nome} for aj in assistencias_judiciarias]}

    response = app.response_class(
        response = json.dumps(resultado_json),
        status = 200,
        mimetype = 'application/json'
    )
    return response 
@plantao.route('/associa_orientacao_juridica/<int:id_orientacao>', defaults={'id_atendido': 0}, methods=['POST', 'GET'])
@plantao.route('/associa_orientacao_juridica/<int:id_orientacao>/<int:id_atendido>', methods=['POST', 'GET'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0], usuario_urole_roles['PROFESSOR'][0]])
def associacao_orientacao_juridica(id_orientacao, id_atendido):
    def associa_ajs_a_oj(lista_aj: list, id_orientacao: int):
        relacoes_aj_oj = (db.session.query(AssistenciaJudiciaria_xOrientacaoJuridica.id_assistenciaJudiciaria)
                                                                   .filter_by(id_orientacaoJuridica = id_orientacao)
                                                                   .all())
        relacoes_aj_oj = [x[0] for x in relacoes_aj_oj]                                                             
        for id_aj in lista_aj:
            if not (int(id_aj) in relacoes_aj_oj):
                associacao = AssistenciaJudiciaria_xOrientacaoJuridica(id_orientacaoJuridica = id_orientacao,
                                                                       id_assistenciaJudiciaria = id_aj)
                db.session.add(associacao)
                db.session.flush()

############################################# IMPLEMENTAÇÃO DA ROTA ##############################################################
    encaminhar_outras_aj = request.args.get('encaminhar_outras_aj', 'False', type=str)
    page = request.args.get('page', 1, type=int)

    if request.method == "POST":
        lista_aj = request.form.getlist('id_multiselect_aj')
        entidade_atendido = Atendido.query.filter_by(id = id_atendido).first() 
        
        orientacao = OrientacaoJuridica.query.filter_by(id = id_orientacao).first()
       
        if not entidade_atendido:
            flash("Este atendido não existe!","warning")
            return redirect(url_for('plantao.associacao_orientacao_juridica', id_orientacao = id_orientacao, encaminhar_outras_aj=encaminhar_outras_aj))
              
            
        else: 
            entidade_atendido.orientacoesJuridicas.append(orientacao)
            db.session.add(entidade_atendido)
            db.session.commit()
            flash('Orientação Jurídica associada com sucesso!',"success")   

            if lista_aj:
               associa_ajs_a_oj(lista_aj, id_orientacao)
               db.session.commit()
            
        return redirect(url_for('plantao.associacao_orientacao_juridica', id_orientacao = id_orientacao, encaminhar_outras_aj=encaminhar_outras_aj))
    blacklist = Atendido.query.outerjoin(Atendido_xOrientacaoJuridica).filter(Atendido_xOrientacaoJuridica.id_orientacaoJuridica == id_orientacao, Atendido.status == True)
    blacklist_ids = []
    for atendido in blacklist:
        blacklist_ids.append(atendido.id)
    lista = Atendido.query.filter(~Atendido.id.in_(blacklist_ids), Atendido.status == True).paginate(page, app.config['ATENDIDOS_POR_PAGINA'], False)
    orientacao_entidade = OrientacaoJuridica.query.get(id_orientacao)

    return render_template('associa_orientacao_juridica.html', lista = lista.items, pagination=lista, orientacao_entidade= orientacao_entidade, encaminhar_outras_aj = encaminhar_outras_aj)

# Busca dos atendidos para associar a uma orientação jurídica
@plantao.route('/busca_atendidos_oj/', defaults={'_busca': None})
@plantao.route('/busca_atendidos_oj/<_busca>', methods=['POST','GET'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0]])
def busca_atendidos_oj(_busca):

    encaminhar_outras_aj = request.args.get('encaminhar_outras_aj')
    id_orientacao_entidade = request.args.get('id_orientacao_entidade')

    orientacao_entidade = OrientacaoJuridica.query.get(id_orientacao_entidade)

    blacklist = Atendido.query.outerjoin(Atendido_xOrientacaoJuridica).filter(Atendido_xOrientacaoJuridica.id_orientacaoJuridica == id_orientacao_entidade)
    blacklist_ids = []
    for atendido in blacklist:
        blacklist_ids.append(atendido.id)

    if _busca is None:
        atendidos = Atendido.query.filter(~Atendido.id.in_(blacklist_ids), Atendido.status == True)
    else:       
        atendidos = Atendido.query.filter((~Atendido.id.in_(blacklist_ids) & Atendido.status == True) & ((Atendido.nome.contains(_busca)) | (Atendido.cpf.contains(_busca))))
       
    return render_template("busca_associa_orientacao_juridica.html", lista=atendidos, orientacao_entidade=orientacao_entidade, encaminhar_outras_aj=encaminhar_outras_aj)

@plantao.route('/excluir_orientacao_juridica/', methods=['POST'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0]])
def excluir_oj():
    id = request.form["id"]
    entidade = OrientacaoJuridica.query.get_or_404(int(id))
    entidade.status = False
    db.session.add(entidade)
    db.session.commit()
    flash("orientação jurídica excluída.", "success")
    return redirect(url_for('plantao.orientacoes_juridicas'))


@plantao.route('/perfil_assistido/<int:_id>', methods=['GET'])
@login_required()
def perfil_assistido(_id):
    assistido = (queryFiltradaStatus(Atendido).filter(Atendido.id == _id)
                                              .add_entity(Assistido)
                                              .add_entity(AssistidoPessoaJuridica)
                                              .outerjoin(Assistido, Assistido.id_atendido == Atendido.id)
                                              .outerjoin(AssistidoPessoaJuridica, AssistidoPessoaJuridica.id_assistido == Assistido.id)
                                              .first())
    return render_template('perfil_assistidos.html', assistido = assistido)

############################################# ASSISTÊNCIA JUDICIÁRIA ##############################################################

@plantao.route('/nova_assistencia_judiciaria/', methods=['GET','POST'])
@login_required(role=[usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['COLAB_PROJETO'][0], usuario_urole_roles['COLAB_EXTERNO'][0],usuario_urole_roles['PROFESSOR'][0]])
def nova_assistencia_judiciaria():
    def setAssistenciaJudiciaria(form: AssistenciaJudiciariaForm):
        endereco = Endereco(
            logradouro  = form.logradouro.data,
            numero      = form.numero.data,
            complemento = form.complemento.data,
            bairro      = form.bairro.data,
            cep         = form.cep.data,
            cidade      = form.cidade.data,
            estado      = form.estado.data
        )
        db.session.add(endereco)
        db.session.flush()

        saida = AssistenciaJudiciaria(
            nome                = form.nome.data,
            regiao              = form.regiao.data,
            endereco_id         = endereco.id,
            telefone            = form.telefone.data,
            email               = form.email.data,
            status              = True
        )

        saida.setAreas_atendidas(form.areas_atendidas.data)

        return saida



    _form = AssistenciaJudiciariaForm()
    if _form.validate_on_submit():
            entidade = setAssistenciaJudiciaria(_form)
            db.session.add(entidade)
            db.session.commit()
            flash("Assistência judiciária criada com sucesso!", "success")
            return redirect(url_for('plantao.listar_assistencias_judiciarias'))
    else:
        return render_template('cadastro_assistencia_judiciaria.html', form = _form)

@plantao.route('/editar_assistencia_judiciaria/<int:id_assistencia_judiciaria>',methods=['POST','GET'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['PROFESSOR'][0], usuario_urole_roles['COLAB_PROJETO'][0], usuario_urole_roles['COLAB_EXTERNO'][0]])
def editar_assistencia_judiciaria(id_assistencia_judiciaria):

    def setDadosAssistenciaJudiciaria(form: AssistenciaJudiciariaForm, assistenciaJuridica: AssistenciaJudiciaria):
        assistenciaJuridica.nome                = form.nome.data
        assistenciaJuridica.regiao              = form.regiao.data
        assistenciaJuridica.setAreas_atendidas(form.areas_atendidas.data)
        assistenciaJuridica.telefone            = form.telefone.data
        assistenciaJuridica.email               = form.email.data
        assistenciaJuridica.endereco.logradouro  = form.logradouro.data
        assistenciaJuridica.endereco.numero      = form.numero.data
        assistenciaJuridica.endereco.complemento = form.complemento.data
        assistenciaJuridica.endereco.bairro      = form.bairro.data
        assistenciaJuridica.endereco.cep         = form.cep.data
        assistenciaJuridica.endereco.cidade      = form.cidade.data
        assistenciaJuridica.endereco.estado      = form.estado.data

    def setAssistenciaJuridicaForm(form: AssistenciaJudiciariaForm, assistenciaJuridica: AssistenciaJudiciaria):
        form.nome.data          = assistenciaJuridica.nome
        form.regiao.data        = assistenciaJuridica.regiao
        form.areas_atendidas.data = assistenciaJuridica.getAreas_atendidas()
        form.telefone.data      = assistenciaJuridica.telefone
        form.email.data         = assistenciaJuridica.email

        form.logradouro.data  = assistenciaJuridica.endereco.logradouro
        form.numero.data      = assistenciaJuridica.endereco.numero
        form.complemento.data = assistenciaJuridica.endereco.complemento
        form.bairro.data      = assistenciaJuridica.endereco.bairro
        form.cep.data         = assistenciaJuridica.endereco.cep
        form.cidade.data      = assistenciaJuridica.endereco.cidade
        form.estado.data      = assistenciaJuridica.endereco.estado

############################################# IMPLEMENTAÇÃO DA ROTA ##############################################################

    assistencia_juridica = AssistenciaJudiciaria.query.filter_by(id=id_assistencia_judiciaria, status=True).first()
    form = AssistenciaJudiciariaForm()

    if not assistencia_juridica:
        flash("Assistência judiciária não encontrada!", "warning")
        return redirect(url_for('plantao.listar_assistencias_judiciarias'))

    if form.validate_on_submit():
        setDadosAssistenciaJudiciaria(form, assistencia_juridica)
        db.session.commit()
        flash("Assistência judiciária editada com sucesso!", "success")
        return redirect(url_for('plantao.listar_assistencias_judiciarias'))

    setAssistenciaJuridicaForm(form, assistencia_juridica)

    return render_template("editar_assistencia_juridica.html", form = form)


# Rota de teste da Visualização da assistência judiciária
@plantao.route('/assistencias_judiciarias/',methods=['POST','GET'])
@login_required()
def listar_assistencias_judiciarias():
    page = request.args.get('page', 1, type=int)
    _assistencias = AssistenciaJudiciaria.query.filter_by(status = True).order_by('nome').paginate(page, app.config['ATENDIDOS_POR_PAGINA'], False)

    return render_template("lista_assistencia_judiciaria.html", assistencias = _assistencias)

# Página de orientações jurídicas
@plantao.route('/orientacoes_juridicas')
@login_required()
def orientacoes_juridicas():
    page = request.args.get('page', 1, type=int)
    orientacoes = OrientacaoJuridica.query.filter_by(status = True).order_by(OrientacaoJuridica.id.desc()).paginate(page, app.config['ATENDIDOS_POR_PAGINA'], False)

    return render_template('orientacoes_juridicas.html', orientacoes = orientacoes)

# Perfil de orientações jurídicas
@plantao.route('/orientacao_juridica/<id>')
@login_required()
def perfil_oj(id):
    _orientacao = OrientacaoJuridica.query.get_or_404(id) 
    atendidos_envolvidos = (queryFiltradaStatus(Atendido)
                            .outerjoin(Atendido_xOrientacaoJuridica)
                            .filter(Atendido_xOrientacaoJuridica.id_orientacaoJuridica == _orientacao.id)
                            .order_by(Atendido.nome)
                            .all())

    assistencias_envolvidas = AssistenciaJudiciaria_xOrientacaoJuridica.query.filter_by(id_orientacaoJuridica = _orientacao.id).all()


    return render_template('perfil_orientacao_juridica.html', orientacao = _orientacao, atendidos = atendidos_envolvidos, assistencias = assistencias_envolvidas)

@plantao.route('/editar_orientacao_juridica/<id_oj>', methods = ['POST', 'GET'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['PROFESSOR'][0]])
def editar_orientacao_juridica(id_oj):

    def setDadosOrientacaoJuridica(entidade_orientacao: OrientacaoJuridica, form: OrientacaoJuridicaForm):
        entidade_orientacao.area_direito = form.area_direito.data
        entidade_orientacao.descricao = form.descricao.data
        entidade_orientacao.setSubAreas(entidade_orientacao.area_direito, form.sub_area.data, form.sub_areaAdmin.data)

    def setOrientacaoJuridicaForm(entidade_orientacao: OrientacaoJuridica, form: OrientacaoJuridicaForm):
        form.area_direito.data = entidade_orientacao.area_direito
        form.sub_area.data = entidade_orientacao.sub_area
        form.descricao.data = entidade_orientacao.descricao

############################################# IMPLEMENTAÇÃO DA ROTA ##############################################################

    entidade_orientacao = OrientacaoJuridica.query.filter_by(id = id_oj, status=True).first()

    if not entidade_orientacao:
        flash("Essa orientação não existe!", 'warning')
        return redirect(url_for('plantao.orientacoes_juridicas'))

    form = OrientacaoJuridicaForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template('editar_orientacao_juridica.html', form = form)

        setDadosOrientacaoJuridica(entidade_orientacao, form)
        db.session.commit()
        flash("Orientação Jurídica editada com sucesso!", 'success')
        return redirect(url_for('plantao.orientacoes_juridicas'))

    setOrientacaoJuridicaForm(entidade_orientacao, form)
    return render_template('editar_orientacao_juridica.html', form = form, orientacao = entidade_orientacao)

# Busca da página de orientações jurídicas
@plantao.route('/busca_oj/', defaults={'_busca': None})
@plantao.route('/busca_oj/<_busca>',methods=['GET'])
@login_required()
def busca_oj(_busca):
    page = request.args.get('page', 1, type=int)
    if _busca is None:
        orientacoes = queryFiltradaStatus(OrientacaoJuridica).order_by(OrientacaoJuridica.id.desc()).paginate(page, app.config['ATENDIDOS_POR_PAGINA'], False)
    else:
        orientacoes = (queryFiltradaStatus(OrientacaoJuridica).outerjoin(Atendido_xOrientacaoJuridica, OrientacaoJuridica.id == Atendido_xOrientacaoJuridica.id_orientacaoJuridica)
                                                              .outerjoin(Atendido, Atendido.id == Atendido_xOrientacaoJuridica.id_atendido)
                                                              .filter(((Atendido.nome.contains(_busca)) | (Atendido.cpf.contains(_busca))) )
                                                              .order_by(OrientacaoJuridica.id.desc())
                                                              .paginate(page, app.config['ATENDIDOS_POR_PAGINA'], False))
    
    return render_template('busca_orientacoes_juridicas.html', orientacoes = orientacoes)

# Excluir assistência judiciária
@plantao.route('/excluir_assistencia_judiciaria/<_id>')
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0]])
def excluir_assistencia_judiciaria(_id):
    aj = db.session.query(AssistenciaJudiciaria).filter_by(id=_id).first()
    if aj is None:
        flash("Assistência judiciária não encontrada.","warning")
        return redirect(url_for('plantao.listar_assistencias_judiciarias'))
    aj.status = False
    db.session.add(aj)
    db.session.commit()
    flash("Assistência judiciária excluída com sucesso.","success")
    return redirect(url_for('plantao.listar_assistencias_judiciarias'))

# Busca da página de assistências judiciárias
@plantao.route('/busca_assistencia_judiciaria/', defaults={'_busca': None})
@plantao.route('/busca_assistencia_judiciaria/<_busca>', methods=['GET'])
@login_required()
def busca_assistencia_judiciaria(_busca):
    page = request.args.get('page', 1, type=int)
    if _busca is None:
        assistencias = db.session.query(AssistenciaJudiciaria).filter_by(status = True).order_by(AssistenciaJudiciaria.nome.asc()).paginate(page, app.config['ATENDIDOS_POR_PAGINA'], False)
    else:
        assistencias = (db.session
                          .query(AssistenciaJudiciaria)
                          .filter(AssistenciaJudiciaria.nome.contains(_busca) & (AssistenciaJudiciaria.status == True))
                          .order_by(AssistenciaJudiciaria.nome.asc())
                          .paginate(page, app.config['ATENDIDOS_POR_PAGINA'], False))
    result = []
    for item in assistencias.items:
        result.append(item)
    response = app.response_class(
        response = json.dumps(serializar(result)),
        status = 200,
        mimetype = 'application/json'
    )
    return response

# Página da assistência judiciária
@plantao.route('/perfil_assistencia_judiciaria/<_id>')
@login_required()
def perfil_assistencia_judiciaria(_id):
    aj = db.session.query(AssistenciaJudiciaria,Endereco).select_from(AssistenciaJudiciaria).join(Endereco).filter((AssistenciaJudiciaria.id == _id)).first()
    if aj is None:
        flash('Assistência judiciária não encontrada.','warning')
        return redirect(url_for('plantao.listar_assistencias_judiciarias'))
    return render_template('visualizar_assistencia_judiciaria.html', aj = aj)

    return render_template("edicao_aj.html", form = form)


# Página de plantao
@plantao.route('/pagina_plantao', methods = ['POST', 'GET'])
@login_required()
def pg_plantao():
    dias_usuario_atual = DiasMarcadosPlantao.query.filter_by(id_usuario = current_user.id).all()

    return render_template('pagina_plantao.html', datas_plantao = dias_usuario_atual, numero_plantao = numero_plantao_a_marcar(current_user.id))

@plantao.route('/ajax_obter_escala_plantao', methods = ['GET'])
@login_required()
def ajax_obter_escala_plantao():
    escala = []

    datas_ja_marcadas = DiasMarcadosPlantao.query.all()
    for registro in datas_ja_marcadas:
        if registro.usuario.status:
            escala.append({
                'nome':registro.usuario.nome,
                'day':registro.data_marcada.day,
                'month': registro.data_marcada.month,
                'year':registro.data_marcada.year
            })
    return app.response_class(
                                response = json.dumps(escala),
                                status = 200,
                                mimetype = 'application/json')


@plantao.route('/ajax_confirma_data_plantao', methods = ['POST', 'GET'])
@login_required()
def ajax_confirma_data_plantao():
    def cria_json(lista_datas, mensagem, tipo_mensagem: str):
        return {
            'lista_datas': lista_datas,
            'mensagem': mensagem,
            'tipo_mensagem': tipo_mensagem,
            'numero_plantao': numero_plantao_a_marcar(current_user.id)
        }

    dias_abertos_plantao = DiaPlantao.query.filter_by(status = 1).all()
    lista_dias_abertos = []
    for dia_aberto in dias_abertos_plantao:
        lista_dias_abertos.append(dia_aberto.data)

    ano = request.args.get('ano')
    mes = request.args.get('mes')
    dia = request.args.get('dia')
    data_marcada = date(int(ano), int(mes), int(dia))
    tipo_mensagem = ''
    mensagem = ''
    resultado_json = {}

    dias_usuario_marcado = DiasMarcadosPlantao.query.filter_by(id_usuario = current_user.id).all()

    validacao = (data_marcada in lista_dias_abertos) and ((current_user.urole == 'orient') or (current_user.urole == 'estag_direito'))
    if not validacao:
        tipo_mensagem = 'warning'
        mensagem = 'Data selecionada não foi aberta para plantão ou você não é um Orientador/Estagiário.'
        resultado_json = cria_json(render_template('lista_datas_plantao.html', datas_plantao = dias_usuario_marcado), mensagem, tipo_mensagem)
        return app.response_class(
                                    response = json.dumps(resultado_json),
                                    status = 200,
                                    mimetype = 'application/json'
                                )
    
    if not confirma_disponibilidade_dia(lista_dias_abertos, data_marcada):
        tipo_mensagem = 'warning'
        mensagem = 'Não há vagas disponíveis na data selecionada, tente outro dia.'
        resultado_json = cria_json(render_template('lista_datas_plantao.html', datas_plantao = dias_usuario_marcado), mensagem, tipo_mensagem)
        return app.response_class(
                                    response = json.dumps(resultado_json),
                                    status = 200,
                                    mimetype = 'application/json'
                                ) 
    

    if len(dias_usuario_marcado) >= 2:
        tipo_mensagem = 'warning'
        mensagem = 'Você já tem 2 plantões cadastrados.'
        resultado_json = cria_json(render_template('lista_datas_plantao.html', datas_plantao = dias_usuario_marcado), mensagem, tipo_mensagem)
        return app.response_class(
                                    response = json.dumps(resultado_json),
                                    status = 200,
                                    mimetype = 'application/json'
                                ) 

    
    dia_marcado = DiasMarcadosPlantao(data_marcada = data_marcada,
                                      id_usuario = current_user.id)
    db.session.add(dia_marcado)
    db.session.commit()
    mensagem = "Data de plantão cadastrada!"
    tipo_mensagem = "success"
    dias_usuario_atual = DiasMarcadosPlantao.query.filter_by(id_usuario = current_user.id).all()
    resultado_json = cria_json(render_template('lista_datas_plantao.html', datas_plantao = dias_usuario_atual), mensagem, tipo_mensagem)
    return app.response_class(
                                response = json.dumps(resultado_json),
                                status = 200,
                                mimetype = 'application/json'
                            )

@plantao.route('/ajax_disponibilidade_de_vagas', methods = ['POST', 'GET'])
@login_required()
def ajax_disponibilidade_de_vagas():

    ano = request.args.get('ano')
    mes = request.args.get('mes')
    dias_no_mes = request.args.get('dias_deste_mes')

    dias = []

    dias_abertos_plantao = DiaPlantao.query.filter_by(status = 1).all()
    lista_dias_abertos = []
    
    for dia_aberto in dias_abertos_plantao:
        lista_dias_abertos.append(dia_aberto.data)
    
    for dia in range(1,int(dias_no_mes)+1):
        data_marcada = date(int(ano), int(mes), int(dia))
        if confirma_disponibilidade_dia(lista_dias_abertos,data_marcada):
            index = {'Dia' : str(dia), 'Vagas' : True}
            dias.append(index)
        else:
            index = {'Dia' : str(dia), 'Vagas' : False}
            dias.append(index)
    
    response = app.response_class(
        response = json.dumps(dias),
        status = 200,
        mimetype = 'application/json'
    )
    return response

# Registro de presença do plantao
@plantao.route('/registro_presenca')
@login_required()
def reg_presenca():
    return render_template('registro_presenca.html')


@plantao.route('/confirmar_presenca')
@login_required()
def confirmar_presenca():
    return render_template('confirmar_presenca.html')


@plantao.route('/configurar_abertura', methods=['POST', 'GET'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['COLAB_PROJETO'][0]])
def configurar_abertura():
    form_abrir = AbrirPlantaoForm()
    form_fechar = FecharPlantaoForm()
    a = datetime.now()
    _form = SelecionarDuracaoPlantaoForm()

    # if _form.validate_on_submit():
    #     dias_escolhidos = _form.hdnDiasEscolhidos.data.split(sep=',')     #quando nenhum dia é selecionado, o split retorna vazio, e o resto da funcção nao sabe trabalhar com isso
    #     d = DiaPlantao.query.filter(DiaPlantao.data >= datetime(a.year,a.month,1)).all()

    #     #Inativa todos os dias cadastrados no mês, reativando aqueles que foram escolhidos na página
    #     for dia in d:
    #         dia.status = False

    #     for dia in dias_escolhidos:
    #         k = datetime(a.year,a.month,int(dia))   
    #         if not k in dia: #Se o dia não foi cadastrado ainda, adicionar um registro novo
    #             x = DiaPlantao(dia = k)
    #             db.session.add(x)
    #         else:
    #             dia.Ativo = True
        
    #     db.session.commit()
    
    if form_abrir.validate_on_submit():
        data_de_abertura = Plantao.query.first()
        data_escolhida = form_abrir.data_abertura.data
        hora_escolhida = form_abrir.hora_abertura.data

        if not data_de_abertura:
            data_de_abertura = Plantao(data_abertura = datetime.combine(data_escolhida, hora_escolhida))

            db.session.add(data_de_abertura)
            db.session.commit()

            app.config['ID_PLANTAO'] = data_de_abertura.id
            flash('Dia de abertura do plantão definida!', 'success')
            return resposta_configura_abertura()

        data_de_abertura.data_abertura = datetime.combine(data_escolhida, hora_escolhida)
        db.session.commit()

        flash('Dia de abertura do plantão definida!', 'success')
        return resposta_configura_abertura()


    return render_template('configurar_abertura.html', form_fechar=form_fechar, form_abrir=form_abrir,periodo = f"{a.month}/{a.year}", form = _form)

@plantao.route('/editar_abertura', methods=['POST','GET'])
@login_required(role = [usuario_urole_roles['ADMINISTRADOR'][0], usuario_urole_roles['COLAB_PROJETO'][0]])
def editar_abertura():
    form_abrir = AbrirPlantaoForm()
    form_fechar = FecharPlantaoForm()

    if form_abrir.validate_on_submit():
        data_de_abertura = Plantao.query.first()
        data_escolhida = form_abrir.data_abertura.data
        hora_escolhida = form_abrir.hora_abertura.data

        data_de_abertura.data_abertura = datetime.combine(data_escolhida, hora_escolhida)
        db.session.commit()

        flash('Dia de abertura do plantão definida!', 'success')
        return resposta_configura_abertura()

    return render_template('editar_abertura.html', form_fechar=form_fechar, form_abrir=form_abrir)