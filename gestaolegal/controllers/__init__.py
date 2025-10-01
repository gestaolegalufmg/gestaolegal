from .api import api_controller
from .api.auth_controller import auth_controller
from .views.arquivo_controller import arquivo_controller
from .views.assistencia_judiciaria_controller import assistencia_judiciaria_controller
from .views.atendido_controller import atendido_controller
from .views.casos_controller import casos_controller
from .views.notificacoes_controller import notificacoes_controller
from .views.orientacao_juridica_controller import orientacao_juridica_controller
from .views.plantao_controller import plantao_controller
from .views.principal_controller import principal_controller
from .views.processo_controller import processo_controller
from .views.relatorio_controller import relatorios_controller
from .api.user_controller import user_controller
from .api.atendido_controller import atendido_controller as atendido_controller_api
from .api.caso_controller import caso_controller
from .api.arquivo_controller import arquivo_controller as arquivo_controller_api
from .api.notificacao_controller import notificacao_controller
from .api.relatorio_controller import relatorio_controller as relatorio_controller_api
from .api.unified_controller import unified_controller
from .api.plantao_controller import plantao_controller as plantao_controller_api

routes = [
    (api_controller, "/api"),
    (auth_controller, "/api/auth"),
    (user_controller, "/api/user"),
    (atendido_controller_api, "/api/atendido"),
    (caso_controller, "/api/caso"),
    (arquivo_controller_api, "/api/arquivo"),
    (notificacao_controller, "/api/notificacao"),
    (relatorio_controller_api, "/api/relatorio"),
    (unified_controller, "/api/unified"),
    (plantao_controller_api, "/api/plantao"),
    (arquivo_controller, "/arquivo"),
    (assistencia_judiciaria_controller, "/assistencia_judiciaria"),
    (atendido_controller, "/atendido"),
    (casos_controller, "/casos"),
    (notificacoes_controller, "/notificacoes"),
    (orientacao_juridica_controller, "/orientacao_juridica"),
    (plantao_controller, "/plantao"),
    (principal_controller, "/"),
    (relatorios_controller, "/relatorios"),
    (processo_controller, "/processo"),
]
