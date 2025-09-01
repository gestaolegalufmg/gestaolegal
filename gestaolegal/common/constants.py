from .constants.business import (
    como_conheceu_daj,
    enquadramento,
    tipo_bolsaUsuario,
)
from .constants.demographics import (
    escolaridade,
    estado_civilUsuario,
    raca_cor,
    regiao_bh,
    sexo_usuario,
)
from .constants.field_limits import FIELD_LIMITS
from .constants.legal_areas import (
    area_atuacao,
    area_do_direito,
    assistencia_jud_areas_atendidas,
    assistencia_jud_regioes,
    orgao_reg,
    se_administrativo,
    se_civel,
)
from .constants.legal_proceedings import (
    acoes,
    situacao_deferimento,
    tipo_evento,
)
from .constants.search import (
    tipos_busca_atendidos,
)
from .constants.social_benefits import (
    beneficio,
    contribuicao_inss,
    moradia,
    participacao_renda,
    qual_pessoa_doente,
)
from .constants.time import (
    meses,
)
from .constants.user_roles import UserRole

# Re-export all constants for backward compatibility
__all__ = [
    "FIELD_LIMITS",
    "area_do_direito",
    "se_civel",
    "se_administrativo",
    "assistencia_jud_areas_atendidas",
    "assistencia_jud_regioes",
    "area_atuacao",
    "orgao_reg",
    "raca_cor",
    "escolaridade",
    "sexo_usuario",
    "estado_civilUsuario",
    "regiao_bh",
    "beneficio",
    "contribuicao_inss",
    "participacao_renda",
    "moradia",
    "qual_pessoa_doente",
    "enquadramento",
    "como_conheceu_daj",
    "tipo_bolsaUsuario",
    "situacao_deferimento",
    "tipo_evento",
    "acoes",
    "tipos_busca_atendidos",
    "meses",
    "UserRole",
]
