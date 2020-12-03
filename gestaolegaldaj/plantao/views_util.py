from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from flask_paginate import Pagination, get_page_args

from gestaolegaldaj import app,db, login_required
from gestaolegaldaj.usuario.models import Usuario, usuario_urole_roles, Endereco
from gestaolegaldaj.plantao.models import Atendido, Assistido, AssistidoPessoaJuridica
from gestaolegaldaj.plantao.forms import CadastroAtendidoForm, TornarAssistidoForm, EditarAssistidoForm

##############################################################
################## CONSTANTES ################################
##############################################################

tipos_busca_atendidos = {
        'TODOS' : 'todos',
        'ATENDIDOS': 'atendidos',
        'ASSISTIDOS': 'assistidos'
    }

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
    entidade_atendido.area_juridica        = form.area_juridica.data
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
   form.area_juridica.data         = entidade_atendido.area_juridica
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
            flash("Erro validação Formulario","warning")
            for erro in (form.errors.items()):
                print(erro)
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
    entidade_assistido.contribui_inss        = form.contribui_inss.data
    entidade_assistido.qtd_pessoas_moradia   = form.qtd_pessoas_moradia.data
    entidade_assistido.renda_familiar        = form.renda_familiar.data
    entidade_assistido.participacao_renda    = form.participacao_renda.data
    entidade_assistido.tipo_moradia          = form.tipo_moradia.data
    entidade_assistido.possui_outros_imoveis = form.possui_outros_imoveis.data
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
