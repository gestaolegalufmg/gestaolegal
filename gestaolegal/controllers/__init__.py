from .arquivo_controller import arquivo_controller
from .assistencia_judiciaria_controller import assistencia_judiciaria_controller
from .atendido_controller import atendido_controller as atendido_controller_api
from .auth_controller import auth_controller
from .caso_controller import caso_controller
from .fila_atendimento_controller import fila_atendimento_controller
from .notificacao_controller import notificacao_controller
from .orientacao_juridica_controller import (
    orientacao_juridica_controller as orientacao_juridica_controller_api,
)
from .plantao_controller import plantao_controller
from .presenca_controller import presenca_controller
from .relatorio_controller import relatorio_controller
from .roteiro_controller import roteiro_controller
from .search_controller import search_controller
from .user_controller import user_controller

routes = [
    (auth_controller, "/api/auth"),
    (user_controller, "/api/user"),
    (atendido_controller_api, "/api/atendido"),
    (caso_controller, "/api/caso"),
    (arquivo_controller, "/api/arquivo"),
    (notificacao_controller, "/api/notificacao"),
    (orientacao_juridica_controller_api, "/api/orientacao_juridica"),
    (assistencia_judiciaria_controller, "/api/assistencia_judiciaria"),
    (fila_atendimento_controller, "/api/fila_atendimento"),
    (plantao_controller, "/api/plantao"),
    (presenca_controller, "/api/presenca"),
    (roteiro_controller, "/api/roteiro"),
    (relatorio_controller, "/api/relatorio"),
    (search_controller, "/api/search"),
]
