from .assistencia_judiciaria_controller import assistencia_judiciaria_controller
from .atendido_controller import atendido_controller as atendido_controller_api
from .auth_controller import auth_controller
from .caso_controller import caso_controller
from .fila_atendimento_controller import fila_atendimento_controller
from .orientacao_juridica_controller import (
    orientacao_juridica_controller as orientacao_juridica_controller_api,
)
from .relatorio_controller import relatorio_controller
from .roteiro_controller import roteiro_controller
from .search_controller import search_controller
from .user_controller import user_controller

routes = [
    (auth_controller, "/api/auth"),
    (user_controller, "/api/user"),
    (atendido_controller_api, "/api/atendido"),
    (caso_controller, "/api/caso"),
    (orientacao_juridica_controller_api, "/api/orientacao_juridica"),
    (assistencia_judiciaria_controller, "/api/assistencia_judiciaria"),
    (fila_atendimento_controller, "/api/fila_atendimento"),
    (roteiro_controller, "/api/roteiro"),
    (relatorio_controller, "/api/relatorio"),
    (search_controller, "/api/search"),
]
