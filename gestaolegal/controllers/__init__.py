from .arquivo_controller import arquivo_controller
from .assistencia_judiciaria_controller import assistencia_judiciaria_controller
from .atendido_controller import atendido_controller
from .casos_controller import casos_controller
from .notificacoes_controller import notificacoes_controller
from .orientacao_juridica_controller import orientacao_juridica_controller
from .plantao_controller import plantao_controller
from .principal_controller import principal_controller
from .relatorio_controller import relatorios_controller
from .user_controller import usuario_controller

routes = [
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
]
