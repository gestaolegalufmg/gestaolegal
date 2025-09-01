situacao_deferimento = {
    "AGUARDANDO_DEFERIMENTO": (
        "aguardando_deferimento",
        "Aguardando Deferimento",
        "warning",
    ),
    "ATIVO": ("ativo", "Ativo", "success"),
    "INDEFERIDO": ("indeferido", "Indeferido", "danger"),
    "ARQUIVADO": ("arquivado", "Arquivado", "dark"),
    "SOLUCIONADO": ("solucionado", "Solucionado", "info"),
}

tipo_evento = {
    "CONTATO": ("contato", "Contato"),
    "REUNIAO": ("reuniao", "Reunião"),
    "PROTOCOLO_PETICAO": ("protocolo_peticao", "Protocolo de Petição"),
    "DILIGENCIA_EXTERNA": ("diligencia_externa", "Diligência Externa"),
    "AUDIENCIA": ("audiencia", "Audiência"),
    "CONCILIACAO": ("conciliacao", "Conciliação"),
    "DECISAO_JUDICIAL": ("decisao_judicial", "Decisão Judicial"),
    "REDIST_CASO": ("redist_caso", "Redistribuição do Caso"),
    "ENCERRAMENTO_CASO": ("encerramento_caso", "Encerramento do Caso"),
    "DOCUMENTOS": ("documentos", "Documentos"),
    "OUTROS": ("outros", "Outros"),
}

acoes = {
    "CAD_NOVO_CASO": "Cadastrado no caso {}",
    "ABERTURA_PLANTAO": "Abertura do plantão",  # notificar orientadores e estagiarios
    "EVENTO": "Cadastrado no evento {} do caso {}",
    "LEMBRETE": "Cadastrado no lembrete {} do caso {}",
}
