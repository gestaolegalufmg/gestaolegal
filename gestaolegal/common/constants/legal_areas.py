area_do_direito = {
    "ADMINISTRATIVO": ("administrativo", "Administrativo"),
    "AMBIENTAL": ("ambiental", "Ambiental"),
    "CIVEL": ("civel", "Civel"),
    "EMPRESARIAL": ("empresarial", "Empresarial"),
    "PENAL": ("penal", "Penal"),
    "TRABALHISTA": ("trabalhista", "Trabalhista"),
}

se_civel = {
    "CONSUMIDOR": ("consumidor", "Consumidor"),
    "CONTRATOS": ("contratos", "Contratos"),
    "FAMILIA": ("familia", "Família"),
    "REAIS": ("reais", "Reais"),
    "RESPONSABILIDADE_CIVIL": ("resp_civil", "Responsabilidade Civil"),
    "SUCESSOES": ("sucessoes", "Sucessões"),
}

se_administrativo = {
    "ADMINISTRATIVO": ("administrativo", "Administrativo"),
    "PREVIDENCIARIO": ("previdenciario", "Previdenciário"),
    "TRIBUTARIO": ("tributario", "Tributário"),
}

assistencia_jud_areas_atendidas = {
    "ADMINISTRATIVO": (
        area_do_direito["ADMINISTRATIVO"][0],
        area_do_direito["ADMINISTRATIVO"][1],
    ),
    "AMBIENTAL": (area_do_direito["AMBIENTAL"][0], area_do_direito["AMBIENTAL"][1]),
    "CIVEL": (area_do_direito["CIVEL"][0], area_do_direito["CIVEL"][1]),
    "EMPRESARIAL": (
        area_do_direito["EMPRESARIAL"][0],
        area_do_direito["EMPRESARIAL"][1],
    ),
    "PENAL": (area_do_direito["PENAL"][0], area_do_direito["PENAL"][1]),
    "TRABALHISTA": (
        area_do_direito["TRABALHISTA"][0],
        area_do_direito["TRABALHISTA"][1],
    ),
}

assistencia_jud_regioes = {
    "NORTE": ("norte", "Norte"),
    "SUL": ("sul", "Sul"),
    "LESTE": ("leste", "Leste"),
    "OESTE": ("oeste", "Oeste"),
    "NOROESTE": ("noroeste", "Noroeste"),
    "CENTRO_SUL": ("centro_sul", "Centro-Sul"),
    "NORDESTE": ("nordeste", "Nordeste"),
    "PAMPULHA": ("pampulha", "Pampulha"),
    "BARREIRO": ("barreiro", "Barreiro"),
    "VENDA_NOVA": ("venda_nova", "Venda Nova"),
    "CONTAGEM": ("contagem", "Contagem"),
    "BETIM": ("betim", "Betim"),
}

area_atuacao = {
    "PRODUCAO_CIRCULACAO_BENS": (
        "producao_circ_bens",
        "Produção e/ou circulação de bens",
    ),
    "PRESTACAO_SERVICOS": ("prestacao_serviços", "Prestação de serviços"),
    "ATIVIDADE_RURAL": ("atividade_rural", "Atividade rural"),
    "OUTROS": ("outros", "Outros"),
}

orgao_reg = {
    "JUCEMG": ("jucemg", "JUNTA COMERCIAL DO ESTADO DE MINAS GERAIS"),
    "CARTORIO_PJ": ("cartorio_pj", "CARTÓRIO DE REGISTRO CIVIL DAS PESSOAS JURÍDICAS"),
}
