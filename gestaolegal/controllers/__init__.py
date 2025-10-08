from .atendido_controller import atendido_controller as atendido_controller_api
from .auth_controller import auth_controller
from .caso_controller import caso_controller
from .orientacao_juridica_controller import (
    orientacao_juridica_controller as orientacao_juridica_controller_api,
)
from .search_controller import search_controller
from .user_controller import user_controller

routes = [
    (auth_controller, "/api/auth"),
    (user_controller, "/api/user"),
    (atendido_controller_api, "/api/atendido"),
    (caso_controller, "/api/caso"),
    (orientacao_juridica_controller_api, "/api/orientacao_juridica"),
    (search_controller, "/api/search"),
]
