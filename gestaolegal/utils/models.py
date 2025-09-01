from gestaolegal.database import get_db

# EXEMPLO 1: atendidos = queryFiltradaStatus(Atendido).all()

# EXEMPLO 2: as duas queries ABAIXO são EQUIVALENTES
#   from gestaolegaldaj.utils.models import queryFiltradaStatus
#   from gestaolegaldaj.plantao.models import OrientacaoJuridica, AssistenciaJudiciaria, AssistenciaJudiciaria_xOrientacaoJuridica
#   sem_queryFiltradaStatus = (db.session.query(Atendido)
#                               .filter(Atendido.status == True)
#                               .add_entity(OrientacaoJuridica)
#                               .filter(OrientacaoJuridica.status == True)
#                               .add_entity(AssistenciaJudiciaria)
#                               .filter(AssistenciaJudiciaria.status == True)
#                               .outerjoin(AssistenciaJudiciaria_xOrientacaoJuridica, AssistenciaJudiciaria_xOrientacaoJuridica.id_orientacaoJuridica == OrientacaoJuridica.id)
#                               .filter(AssistenciaJudiciaria_xOrientacaoJuridica.id_assistenciaJudiciaria == AssistenciaJudiciaria.id)
#                               .filter(Atendido.nome.contains('Alcione'))
#                               .all()
#                               )
#   com_queryFiltradaStatus = (queryFiltradaStatus(Atendido, [OrientacaoJuridica, AssistenciaJudiciaria])
#                               .outerjoin(AssistenciaJudiciaria_xOrientacaoJuridica, AssistenciaJudiciaria_xOrientacaoJuridica.id_orientacaoJuridica == OrientacaoJuridica.id)
#                               .filter(AssistenciaJudiciaria_xOrientacaoJuridica.id_assistenciaJudiciaria == AssistenciaJudiciaria.id)
#                               .filter(Atendido.nome.contains('Alcione'))
#                               .all()
#                               )
#   print('SEM FUNCAO DE QUERY FILTRADA:-----------------------------------------------------------')
#   print(sem_queryFiltradaStatus)
#   print('COM FUNCAO DE QUERY FILTRADA:-----------------------------------------------------------')
#   print(com_queryFiltradaStatus)


def queryFiltradaStatus(
    entidade_principal, outras_entidades: list = [], status: bool = True
):
    db = get_db()

    query_final = db.session.query(entidade_principal).filter(
        entidade_principal.status == status
    )

    if outras_entidades:
        for entidade in outras_entidades:
            query_final = query_final.add_entity(entidade).filter(
                entidade.status == status
            )

    return query_final
