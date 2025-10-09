from gestaolegal.models.assistido import Assistido
from gestaolegal.models.assistido_pessoa_juridica import AssistidoPessoaJuridica
from gestaolegal.models.atendido import Atendido
from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.caso import Caso
from gestaolegal.models.endereco import Endereco
from gestaolegal.models.evento import Evento
from gestaolegal.models.orientacao_juridica import OrientacaoJuridica
from gestaolegal.models.processo import Processo
from gestaolegal.models.user import User

Assistido.model_rebuild()
Atendido.model_rebuild()
OrientacaoJuridica.model_rebuild()
Caso.model_rebuild()
Processo.model_rebuild()
Evento.model_rebuild()

__all__ = [
    "BaseModel",
    "Endereco",
    "User",
    "Assistido",
    "AssistidoPessoaJuridica",
    "Atendido",
    "OrientacaoJuridica",
    "Caso",
    "Processo",
    "Evento",
]
