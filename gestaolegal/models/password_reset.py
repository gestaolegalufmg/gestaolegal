from dataclasses import dataclass
from datetime import datetime


@dataclass
class PasswordResetToken:
    """Pedido de recuperação de senha.

    O token em claro nunca é guardado: `token_hash` é o SHA-256 do valor que
    foi enviado por e-mail. `usado_em` preenchida = token já consumido.
    """

    usuario_id: int
    token_hash: str
    expira_em: datetime
    criado_em: datetime
    usado_em: datetime | None = None
    id: int | None = None
