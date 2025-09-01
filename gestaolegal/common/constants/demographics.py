"""
Demographic constants for the application.
"""

raca_cor = {
    "INDIGENA": ("indigena", "Indígena"),
    "PRETA": ("preta", "Preta"),
    "PARDA": ("parda", "Parda"),
    "AMARELA": ("amarela", "Amarela"),
    "BRANCA": ("branca", "Branca"),
    "NAO_DECLARADO": ("nao_declarado", "Prefere não declarar"),
}

escolaridade = {
    "NAO_FREQUENTOU": ("nao_frequentou", "Não frequentou a escola"),
    "INFANTIL_INC": ("infantil_inc", "Educação infantil incompleta"),
    "INFANTIL_COMP": ("infantil_comp", "Educação infantil completa"),
    "FUNDAMENTAL1_INC": (
        "fundamental1_inc",
        "Ensino fundamental - 1° ao 5° ano incompletos",
    ),
    "FUNDAMENTAL1_COMP": (
        "fundamental1_comp",
        "Ensino fundamental - 1° ao 5° ano completos",
    ),
    "FUNDAMENTAL2_INC": (
        "fundamental2_inc",
        "Ensino fundamental - 6° ao 9° ano incompletos",
    ),
    "FUNDAMENTAL2_COMP": (
        "fundamental2_comp",
        "Ensino fundamental - 6° ao 9° ano completos",
    ),
    "MEDIO_INC": ("medio_inc", "Ensino médio incompleto"),
    "MEDIO_COMP": ("medio_comp", "Ensino médio completo"),
    "TECNICO_INC": ("tecnico_inc", "Curso técnico incompleto"),
    "TECNICO_COMP": ("tecnico_comp", "Curso técnico completo"),
    "SUPERIOR_INC": ("superior_inc", "Ensino superior incompleto"),
    "SUPERIOR_COMP": ("superior_comp", "Ensino superior completo"),
    "NAO_INFORMADO": ("nao_info", "Não informou"),
}

sexo_usuario = {
    "MASCULINO": ("M", "Masculino"),
    "FEMININO": ("F", "Feminino"),
    "OUTROS": ("O", "Outro"),
}

estado_civilUsuario = {
    "SOLTEIRO": ("solteiro", "Solteiro"),
    "CASADO": ("casado", "Casado"),
    "DIVORCIADO": ("divorciado", "Divorciado"),
    "SEPARADO": ("separado", "Separado"),
    "UNIAO": ("uniao", "União estável"),
    "VIUVO": ("viuvo", "Viúvo"),
}

regiao_bh = {
    "BARREIRO": ("barreiro", "Barreiro"),
    "PAMPULHA": ("pampulha", "Pampulha"),
    "VENDA_NOVA": ("venda nova", "Venda Nova"),
    "NORTE": ("norte", "Norte"),
    "NORDESTE": ("nordeste", "Nordeste"),
    "NOROESTE": ("noroeste", "Noroeste"),
    "LESTE": ("leste", "Leste"),
    "OESTE": ("oeste", "Oeste"),
    "SUL": ("sul", "Sul"),
    "CENTRO_SUL": ("centro_sul", "Centro-Sul"),
}
