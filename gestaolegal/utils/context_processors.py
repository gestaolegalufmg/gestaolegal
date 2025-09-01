from gestaolegal.common.constants import (
    UserRole,
    area_atuacao,
    assistencia_jud_areas_atendidas,
    assistencia_jud_regioes,
    beneficio,
    como_conheceu_daj,
    contribuicao_inss,
    enquadramento,
    escolaridade,
    estado_civilUsuario,
    moradia,
    orgao_reg,
    participacao_renda,
    qual_pessoa_doente,
    regiao_bh,
    sexo_usuario,
    situacao_deferimento,
    tipo_bolsaUsuario,
    tipo_evento,
)
from gestaolegal.utils.color_system import generate_color_palette


def inject_company_config():
    """Inject company configuration into template context."""
    from flask import current_app
    
    company_color = current_app.config["COMPANY_COLOR"]
    color_palette = generate_color_palette(company_color)
    
    return dict(
        company_name=current_app.config["COMPANY_NAME"],
        company_color=company_color,
        color_palette=color_palette,
    )


def processor_tipo_classe():
    """Add tipo_classe function to template context."""

    def tipo_classe(var: object, tipo: str):
        return var.__class__.__name__ == tipo

    return dict(tipo_classe=tipo_classe)


def processor_formata_float():
    """Add formata_float function to template context."""

    def formata_float(numero: float):
        lista_char = list(str(numero))

        for i in range(len(lista_char)):
            if lista_char[i] == ".":
                lista_char[i] = ","
                break
        return "".join(lista_char)

    return dict(formata_float=formata_float)


def insere_usuario_roles():
    """Add UserRole enum to template context."""
    return dict(UserRole=UserRole)


def insere_tipo_bolsaUsuario():
    """Add tipo_bolsaUsuario to template context."""
    return dict(tipo_bolsaUsuario=tipo_bolsaUsuario)


def insere_sexo_usuario():
    """Add sexo_usuario to template context."""
    return dict(sexo_usuario=sexo_usuario)


def insere_estado_civilUsuario():
    """Add estado_civilUsuario to template context."""
    return dict(estado_civilUsuario=estado_civilUsuario)


def insere_como_conheceu_dajUsuario():
    """Add como_conheceu_daj to template context."""
    return dict(como_conheceu_daj=como_conheceu_daj)


def insere_assistencia_jud_areas_atendidas():
    """Add assistencia_jud_areas_atendidas to template context."""
    return dict(assistencia_jud_areas_atendidas=assistencia_jud_areas_atendidas)


def insere_assistencia_jud_regioes():
    """Add assistencia_jud_regioes to template context."""
    return dict(assistencia_jud_regioes=assistencia_jud_regioes)


def insere_beneficio():
    """Add beneficio to template context."""
    return dict(beneficio=beneficio)


def insere_contribuicao_inss():
    """Add contribuicao_inss to template context."""
    return dict(contribuicao_inss=contribuicao_inss)


def insere_participacao_renda():
    """Add participacao_renda to template context."""
    return dict(participacao_renda=participacao_renda)


def insere_moradia():
    """Add moradia to template context."""
    return dict(moradia=moradia)


def insere_qual_pessoa_doente():
    """Add qual_pessoa_doente to template context."""
    return dict(qual_pessoa_doente=qual_pessoa_doente)


def insere_regiao_bh():
    """Add regiao_bh to template context."""
    return dict(regiao_bh=regiao_bh)


def insere_escolaridade():
    """Add escolaridade to template context."""
    return dict(escolaridade=escolaridade)


def insere_enquadramento():
    """Add enquadramento to template context."""
    return dict(enquadramento=enquadramento)


def insere_area_atuacao():
    """Add area_atuacao to template context."""
    return dict(area_atuacao=area_atuacao)


def insere_orgao_reg():
    """Add orgao_reg to template context."""
    return dict(orgao_reg=orgao_reg)


def insere_situacao_deferimento():
    """Add situacao_deferimento to template context."""
    return dict(situacao_deferimento=situacao_deferimento)


def insere_tipo_evento():
    """Add tipo_evento to template context."""
    return dict(tipo_evento=tipo_evento)
