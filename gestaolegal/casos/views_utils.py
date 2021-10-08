from sqlalchemy import or_, desc

from gestaolegal import db
from gestaolegal.casos.models import Caso, situacao_deferimento, tipo_evento, Evento
from gestaolegal.utils.models import queryFiltradaStatus

ROTA_PAGINACAO_CASOS = "casos.index"
ROTA_PAGINACAO_EVENTOS = "casos.eventos"

ROTA_PAGINACAO_MEUS_CASOS = "casos.meus_casos"
TITULO_TOTAL_MEUS_CASOS = "Total de Casos: {}"

opcoes_filtro_casos = situacao_deferimento
opcoes_filtro_casos['TODOS'] = ('todos', 'Todos Casos')

opcoes_filtro_meus_casos = {
    'CADASTRADO_POR_MIM': ('cad_por_mim', 'Cadastrado por mim')
}
opcoes_filtro_meus_casos['ATIVO'] = situacao_deferimento['ATIVO']
opcoes_filtro_meus_casos['ARQUIVADO'] = situacao_deferimento['ARQUIVADO']

opcoes_filtro_eventos = tipo_evento
opcoes_filtro_eventos['TODOS'] = ('todos', 'Todos')


def query_opcoes_filtro_casos(opcao_filtro):
    if opcao_filtro == opcoes_filtro_casos['TODOS'][0]:
        return queryFiltradaStatus(Caso).order_by(Caso.data_criacao.desc())
    elif (opcao_filtro == opcoes_filtro_casos[key][0] for key in opcoes_filtro_casos):
        return queryFiltradaStatus(Caso).filter(Caso.situacao_deferimento == opcao_filtro).order_by(
            Caso.data_criacao.desc())
    else:
        return None


def query_meus_casos(id_usuario: int):
    return queryFiltradaStatus(Caso) \
        .filter(or_(Caso.id_usuario_responsavel == id_usuario, Caso.id_orientador == id_usuario,
                    Caso.id_estagiario == id_usuario)) \
        .order_by(Caso.data_criacao.desc())


def titulo_total_meus_casos(numero_casos):
    return TITULO_TOTAL_MEUS_CASOS.format(numero_casos)


def query_opcoes_filtro_meus_casos(id_usuario, opcao_filtro):
    if opcao_filtro == opcoes_filtro_meus_casos['CADASTRADO_POR_MIM'][0]:
        return query_meus_casos(id_usuario) \
            .filter(Caso.id_criado_por == id_usuario)

    elif (opcao_filtro == opcoes_filtro_meus_casos[key][0] for key in opcoes_filtro_meus_casos):
        return query_meus_casos(id_usuario) \
            .filter(Caso.situacao_deferimento == opcao_filtro)
    else:
        return None


def params_busca_casos(casos, rota_paginacao, opcao_filtro=None):
    return {'casos': casos,
            'rota_paginacao': rota_paginacao,
            'opcao_filtro': opcao_filtro}


def query_opcoes_filtro_eventos(id_caso, opcao_filtro):
    if opcao_filtro == opcoes_filtro_eventos['TODOS'][0]:
        return queryFiltradaStatus(Evento) \
            .filter_by(id_caso=id_caso) \
            .order_by(Evento.data_criacao.desc())
    elif (opcao_filtro == opcoes_filtro_eventos[key][0] for key in opcoes_filtro_eventos):
        return queryFiltradaStatus(Evento) \
            .filter_by(id_caso=id_caso) \
            .filter(Evento.tipo == opcao_filtro) \
            .order_by(Evento.data_criacao.desc())
    else:
        return None


def params_busca_eventos(eventos, rota_paginacao, caso_id, opcao_filtro=None):
    return {'eventos': eventos,
            'rota_paginacao': rota_paginacao,
            'opcao_filtro': opcao_filtro,
            'caso_id': caso_id}


def get_num_eventos_atual(caso_id):
    num_eventos_criados = (db.session.query(Evento.num_evento)
                           .filter(
        Evento.id_caso == caso_id
    )
                           .order_by(desc(Evento.num_evento))
                           .first())
    return num_eventos_criados[0] + 1 if num_eventos_criados else 1
