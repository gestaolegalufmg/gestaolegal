from datetime import date, datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from flask_paginate import Pagination, get_page_args

from gestaolegal import app,db, login_required
from gestaolegal.usuario.models import Usuario, usuario_urole_roles, Endereco
from gestaolegal.plantao.models import (Atendido,
                                        Assistido,
                                        AssistidoPessoaJuridica,
                                        DiasMarcadosPlantao,
                                        Plantao,
                                        AssistenciaJudiciaria,
                                        assistencia_jud_areas_atendidas,
                                        DiaPlantao)
from gestaolegal.plantao.forms import CadastroAtendidoForm, TornarAssistidoForm, EditarAssistidoForm, AbrirPlantaoForm, FecharPlantaoForm
from sqlalchemy import null

##############################################################
################## CONSTANTES ################################
##############################################################

tipos_busca_atendidos = {
        'TODOS' : 'todos',
        'ATENDIDOS': 'atendidos',
        'ASSISTIDOS': 'assistidos'
    }

filtro_busca_assistencia_judiciaria = assistencia_jud_areas_atendidas
filtro_busca_assistencia_judiciaria['TODAS'] = ('todas' , 'Todas') 

##############################################################
################## FUNCOES ###################################
##############################################################

def setDadosAtendido(entidade_atendido: Atendido, form):
    entidade_atendido.nome                 = form.nome.data
    entidade_atendido.data_nascimento      = form.data_nascimento.data
    entidade_atendido.cpf                  = form.cpf.data
    entidade_atendido.telefone             = form.telefone.data
    entidade_atendido.celular              = form.celular.data
    entidade_atendido.email                = form.email.data
    entidade_atendido.estado_civil         = form.estado_civil.data
    entidade_atendido.como_conheceu        = form.como_conheceu.data
    entidade_atendido.procurou_outro_local = form.procurou_outro_local.data
    entidade_atendido.obs                  = form.obs_atendido.data
    entidade_atendido.endereco.logradouro  = form.logradouro.data
    entidade_atendido.endereco.numero      = form.numero.data
    entidade_atendido.endereco.complemento = form.complemento.data
    entidade_atendido.endereco.bairro      = form.bairro.data
    entidade_atendido.endereco.cep         = form.cep.data
    entidade_atendido.endereco.cidade      = form.cidade.data
    entidade_atendido.endereco.estado      = form.estado.data
    entidade_atendido.pj_constituida       = form.pj_constituida.data
    entidade_atendido.pretende_constituir_pj = form.pretende_constituir_pj.data

    entidade_atendido.setIndicacao_orgao(form.indicacao_orgao.data, entidade_atendido.como_conheceu)
    entidade_atendido.setCnpj(entidade_atendido.pj_constituida, form.cnpj.data, form.repres_legal.data)
    entidade_atendido.setRepres_legal(entidade_atendido.repres_legal, entidade_atendido.pj_constituida,form.nome_repres_legal.data,
                                      form.cpf_repres_legal.data, form.contato_repres_legal.data,
                                      form.rg_repres_legal.data, form.nascimento_repres_legal.data)
    entidade_atendido.setProcurou_qual_local(entidade_atendido.procurou_outro_local, form.procurou_qual_local.data)

def setValoresFormAtendido(entidade_atendido: Atendido, form: CadastroAtendidoForm):
   form.nome.data                  = entidade_atendido.nome
   form.data_nascimento.data       = entidade_atendido.data_nascimento
   form.telefone.data              = entidade_atendido.telefone
   form.celular.data               = entidade_atendido.celular
   form.email.data                 = entidade_atendido.email
   form.estado_civil.data          = entidade_atendido.estado_civil
   form.como_conheceu.data         = entidade_atendido.como_conheceu
   form.indicacao_orgao.data       = entidade_atendido.indicacao_orgao
   form.procurou_outro_local.data  = False if entidade_atendido.procurou_outro_local == '0' else True
   form.procurou_qual_local.data   = entidade_atendido.procurou_qual_local
   form.obs_atendido.data          = entidade_atendido.obs
   form.cpf.data                   = entidade_atendido.cpf
   form.cnpj.data                  = entidade_atendido.cnpj
   form.logradouro.data            = entidade_atendido.endereco.logradouro
   form.numero.data                = entidade_atendido.endereco.numero
   form.complemento.data           = entidade_atendido.endereco.complemento
   form.bairro.data                = entidade_atendido.endereco.bairro
   form.cep.data                   = entidade_atendido.endereco.cep
   form.cidade.data                = entidade_atendido.endereco.cidade
   form.estado.data                = entidade_atendido.endereco.estado
   form.pj_constituida.data        = False if entidade_atendido.pj_constituida == '0' else True
   form.repres_legal.data          = False if entidade_atendido.repres_legal == '0' else True
   form.nome_repres_legal.data     = entidade_atendido.nome_repres_legal
   form.cpf_repres_legal.data      = entidade_atendido.cpf_repres_legal
   form.contato_repres_legal.data  = entidade_atendido.contato_repres_legal
   form.rg_repres_legal.data       = entidade_atendido.rg_repres_legal
   form.nascimento_repres_legal.data  = entidade_atendido.nascimento_repres_legal
   form.pretende_constituir_pj.data = False if entidade_atendido.pretende_constituir_pj == '0' else True

def validaDadosEditar_atendidoForm(form, emailAtual: str):
        emailRepetido = Atendido.query.filter_by(email= form.email.data).first()

        if not form.validate():
            return False
        if (emailRepetido) and (form.email.data != emailAtual):
            flash("Este email já está em uso.","warning")
            return False
        return True

def setDadosGeraisAssistido(entidade_assistido, form: TornarAssistidoForm):
    entidade_assistido.sexo                  = form.sexo.data
    entidade_assistido.raca                  = form.raca.data
    entidade_assistido.profissao             = form.profissao.data
    entidade_assistido.rg                    = form.rg.data
    entidade_assistido.grau_instrucao        = form.grau_instrucao.data
    entidade_assistido.salario               = form.salario.data
    entidade_assistido.beneficio             = form.beneficio.data
    entidade_assistido.qual_beneficio        = form.qual_beneficio.data
    entidade_assistido.contribui_inss        = form.contribui_inss.data
    entidade_assistido.qtd_pessoas_moradia   = form.qtd_pessoas_moradia.data
    entidade_assistido.renda_familiar        = form.renda_familiar.data
    entidade_assistido.participacao_renda    = form.participacao_renda.data
    entidade_assistido.tipo_moradia          = form.tipo_moradia.data
    entidade_assistido.possui_outros_imoveis = form.possui_outros_imoveis.data
    entidade_assistido.quantos_imoveis       = form.quantos_imoveis.data
    entidade_assistido.possui_veiculos       = form.possui_veiculos.data
    entidade_assistido.doenca_grave_familia  = form.doenca_grave_familia.data
    entidade_assistido.obs                   = form.obs_assistido.data

    entidade_assistido.setCamposVeiculo(entidade_assistido.possui_veiculos,
                                                    form.possui_veiculos_obs.data,
                                                    form.quantos_veiculos.data,
                                                    form.ano_veiculo.data)
    entidade_assistido.setCamposDoenca(entidade_assistido.doenca_grave_familia,
                                                   form.pessoa_doente.data, form.pessoa_doente_obs.data,
                                                   form.gastos_medicacao.data)

def setDadosAssistidoPessoaJuridica(entidade_assistidoPessoaJuridica: AssistidoPessoaJuridica, form: TornarAssistidoForm):
    entidade_assistidoPessoaJuridica.socios                    = form.socios.data
    entidade_assistidoPessoaJuridica.situacao_receita          = form.situacao_receita.data
    entidade_assistidoPessoaJuridica.enquadramento             = form.enquadramento.data
    entidade_assistidoPessoaJuridica.sede_bh                   = form.sede_bh.data
    entidade_assistidoPessoaJuridica.area_atuacao              = form.area_atuacao.data
    entidade_assistidoPessoaJuridica.negocio_nascente          = form.negocio_nascente.data
    entidade_assistidoPessoaJuridica.orgao_registro            = form.orgao_registro.data
    entidade_assistidoPessoaJuridica.faturamento_anual         = form.faturamento_anual.data
    entidade_assistidoPessoaJuridica.ultimo_balanco_neg        = form.ultimo_balanco_neg.data
    entidade_assistidoPessoaJuridica.resultado_econ_neg        = form.resultado_econ_neg.data
    entidade_assistidoPessoaJuridica.tem_funcionarios          = form.tem_funcionarios.data

    entidade_assistidoPessoaJuridica.setQtd_funcionarios(entidade_assistidoPessoaJuridica.tem_funcionarios, form.qtd_funcionarios.data)
    entidade_assistidoPessoaJuridica.setCamposRegiao_sede(entidade_assistidoPessoaJuridica.sede_bh, form.regiao_sede_bh.data, form.regiao_sede_outros.data)

def serializar(lista):
	return [x.as_dict() for x in lista]

def busca_todos_atendidos_assistidos(busca, page):
    return (db.session
              .query(Atendido, Assistido)
              .outerjoin(Assistido)
              .filter(((Atendido.nome.contains(busca)) | (Atendido.cpf.contains(busca)) | (Atendido.cnpj.contains(busca))) & (Atendido.status == True))
              .order_by(Atendido.nome)
              .paginate(page, app.config['ATENDIDOS_POR_PAGINA'], False))

def numero_plantao_a_marcar(id_usuario: int):

    dias_marcados = DiasMarcadosPlantao.query.filter_by(id_usuario = id_usuario).all()
    
    return len(dias_marcados) + 1

def checa_vagas_em_todos_dias(dias_disponiveis: list, urole: str) -> bool:
    """
    Função que retorna verdadeiro caso NÃO exista vagas para um determinado tipo de usuario
    """
    if urole == usuario_urole_roles['ORIENTADOR'][0]:
        orientador_no_dia = []              #essa lista armazena se todos os dias tem ou nao um orientador ja cadastrado num dia, true caso sim e false do contrario
        for i in range(0,len(dias_disponiveis)):
            seletor_banco_de_dados = DiasMarcadosPlantao.query.filter_by(data_marcada = dias_disponiveis[i]).all()
            for data in seletor_banco_de_dados:
                if data.usuario.urole == usuario_urole_roles['ORIENTADOR'][0]:
                    orientador_no_dia.append(True)
                    break
        
        if len(orientador_no_dia) < len(dias_disponiveis):
            return False
        else:
            return True
    else:
        tres_estagiarios_no_dia = []             #essa lista armazena se todos os dias tem ou nao 3 ou mais estagiarios ja cadastrados num dia, true caso sim e false do contrario
        for i in range(0, len(dias_disponiveis)):
            seletor_banco_de_dados = DiasMarcadosPlantao.query.filter_by(data_marcada = dias_disponiveis[i]).all()
            numero_de_estagiarios_no_dia = 0
            for data in seletor_banco_de_dados:
                if data.usuario.urole == 'estag_direito':
                    numero_de_estagiarios_no_dia += 1

            if numero_de_estagiarios_no_dia >= 3:
                tres_estagiarios_no_dia.append(True)
            else:
                tres_estagiarios_no_dia.append(False)
        
        if False in tres_estagiarios_no_dia:
            return False
        else:
            return True
                

def confirma_disponibilidade_dia(dias_disponiveis: list, data: date):
    """
    Função que retorna verdadeiro caso uma data esteja disponível para marcar um plantão.
    """

    urole_usuario = current_user.urole
    consulta_data_marcada = DiasMarcadosPlantao.query.filter_by(data_marcada = data).all()
    numero_orientador = 0
    numero_estagiario = 0

    for data in consulta_data_marcada:
        if data.usuario.urole == usuario_urole_roles['ORIENTADOR'][0]:
            numero_orientador += 1
        else:
            numero_estagiario += 1

    if (urole_usuario == usuario_urole_roles['ORIENTADOR'][0]) and (numero_orientador >= 1):
        if checa_vagas_em_todos_dias(dias_disponiveis, urole_usuario):
            return True
        return False

    elif (urole_usuario == usuario_urole_roles['ESTAGIARIO_DIREITO'][0]) and (numero_estagiario >= 3):
        if checa_vagas_em_todos_dias(dias_disponiveis, urole_usuario):
            return True
        return False
    else:
        return True

def resposta_configura_abertura() -> redirect:
    return redirect(url_for('plantao.pg_plantao'))

def atualiza_data_abertura(form: AbrirPlantaoForm, plantao: Plantao):
    data_escolhida = form.data_abertura.data
    hora_escolhida = form.hora_abertura.data

    plantao.data_abertura = datetime.combine(data_escolhida, hora_escolhida)
    db.session.commit()

def atualiza_data_fechamento(form: FecharPlantaoForm, plantao: Plantao):
    data_escolhida = form.data_fechamento.data
    hora_escolhida = form.hora_fechamento.data

    plantao.data_fechamento = datetime.combine(data_escolhida, hora_escolhida)
    db.session.commit()

def set_abrir_plantao_form(form: AbrirPlantaoForm, plantao: Plantao):
    if plantao:
        if plantao.data_abertura:
            form.data_abertura.data = plantao.data_abertura.date()
            form.hora_abertura.data = plantao.data_abertura.time() 

def set_fechar_plantao_form(form: FecharPlantaoForm, plantao: Plantao):
    if plantao:
        if plantao.data_fechamento:
            form.data_fechamento.data = plantao.data_fechamento.date()
            form.hora_fechamento.data = plantao.data_fechamento.time()
    
def vagas_restantes(dias_disponiveis: list, data: date):
  num_max = 0
  if data not in dias_disponiveis:
      return 0
  for i in range(0, len(dias_disponiveis)):
    vagas_preenchidas = db.session.query(DiasMarcadosPlantao, Usuario.urole).select_from(DiasMarcadosPlantao).join(Usuario).filter(Usuario.urole == current_user.urole, DiasMarcadosPlantao.data_marcada == dias_disponiveis[i]).all()
    if(len(vagas_preenchidas)>num_max):
      num_max = len(vagas_preenchidas)
    if current_user.urole == usuario_urole_roles['ORIENTADOR'][0]:
      if num_max < 1:
        num_max = 1
    if current_user.urole == usuario_urole_roles['ESTAGIARIO_DIREITO'][0]:
      if num_max < 3:
        num_max = 3
  vagas_no_dia = db.session.query(DiasMarcadosPlantao, Usuario.urole).select_from(DiasMarcadosPlantao).join(Usuario).filter(Usuario.urole == current_user.urole, DiasMarcadosPlantao.data_marcada == data).all()
  if not current_user.urole in [usuario_urole_roles['ORIENTADOR'][0], usuario_urole_roles['ESTAGIARIO_DIREITO'][0]]:
      return "Sem limites"
  else:
    return (num_max - len(vagas_no_dia))

def query_busca_assistencia_judiciaria(query_base, busca):
    if busca is None:
        return query_base.filter_by(status = True).order_by(AssistenciaJudiciaria.nome.asc())

    return query_base\
            .filter(AssistenciaJudiciaria.nome.contains(busca) & (AssistenciaJudiciaria.status == True))\
            .order_by(AssistenciaJudiciaria.nome.asc())

def query_filtro_assistencia_judiciaria(query_base, filtro):
    if filtro == filtro_busca_assistencia_judiciaria['TODAS'][0]:
        return query_base.filter_by(status = True)

    return query_base\
            .filter((AssistenciaJudiciaria.areas_atendidas.contains(filtro)) & (AssistenciaJudiciaria.status == True))

def valida_fim_plantao(plantao: Plantao):
    if plantao:
        if plantao.data_fechamento:
            if plantao.data_fechamento < datetime.now():
                try:
                    DiaPlantao.query.delete()
                    db.session.flush()

                    plantao.data_fechamento = null()
                    plantao.data_abertura = null()
                    db.session.commit()
                except:
                    db.session.rollback()
                    return False
    
    return True