from gestaolegal.common.constants import situacao_deferimento, tipo_evento

opcoes_filtro_casos = situacao_deferimento.copy()
opcoes_filtro_casos["TODOS"] = ("todos", "Todos Casos", "primary")

opcoes_filtro_meus_casos = {
    "CADASTRADO_POR_MIM": ("cad_por_mim", "Cadastrado por mim", "info")
}
opcoes_filtro_meus_casos["ATIVO"] = situacao_deferimento["ATIVO"]
opcoes_filtro_meus_casos["ARQUIVADO"] = situacao_deferimento["ARQUIVADO"]
opcoes_filtro_meus_casos["AGUARDANDO_DEFERIMENTO"] = situacao_deferimento[
    "AGUARDANDO_DEFERIMENTO"
]
opcoes_filtro_meus_casos["INDEFERIDO"] = situacao_deferimento["INDEFERIDO"]

opcoes_filtro_eventos = tipo_evento.copy()
opcoes_filtro_eventos["TODOS"] = ("todos", "Todos")
