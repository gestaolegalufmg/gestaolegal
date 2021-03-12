from gestaolegaldaj import app
from gestaolegaldaj.utils.models import queryFiltradaStatus
from sqlalchemy import or_

ROTA_PAGINACAO_RELATORIOS = "relatorios.index"

areas_direito = {
    "consumidor":               "Consumidor",
    "contratos":                "Contratos",
    "trabalhista":              "Trabalhista",
    "administrativo":           "Administrativo",
    "previdenciario":           "Previdenciário",
    "sucessoes":                "Sucessões",
    "familia":                  "Família",
    "penal":                    "Penal",
    "ambiental":                "Ambiental",
    "tributario":               "Tributário",
    "civel":                    "Cível"
}