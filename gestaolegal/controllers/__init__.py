from .api import api_controller
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
from .views.user_controller import usuario_controller

routes = [
    (api_controller, "/api"),
    (arquivo_controller, "/arquivo"),
    (assistencia_judiciaria_controller, "/assistencia_judiciaria"),
    (atendido_controller, "/atendido"),
    (casos_controller, "/casos"),
    (notificacoes_controller, "/notificacoes"),
    (orientacao_juridica_controller, "/orientacao_juridica"),
    (plantao_controller, "/plantao"),
    (principal_controller, "/"),
    (relatorios_controller, "/relatorios"),
    (usuario_controller, "/usuario"),
    (processo_controller, "/processo"),
]
