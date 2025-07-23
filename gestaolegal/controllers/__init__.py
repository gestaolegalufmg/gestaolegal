from gestaolegal import app
from gestaolegal.controllers.assistencia_judiciaria_controller import (
    assistencia_judiciaria_controller,
)
from gestaolegal.controllers.atendido_controller import atendido_controller
from gestaolegal.controllers.orientacao_juridica_controller import (
    orientacao_juridica_controller,
)

app.register_blueprint(atendido_controller, url_prefix="/atendido")
app.register_blueprint(
    assistencia_judiciaria_controller, url_prefix="/assistencia_judiciaria"
)
app.register_blueprint(
    orientacao_juridica_controller, url_prefix="/orientacao_juridica"
)
