import hashlib
import logging
import secrets
from datetime import datetime, timedelta

from gestaolegal.config import Config
from gestaolegal.database.session import transaction
from gestaolegal.exceptions import ValidationException
from gestaolegal.models.user import UserInfo
from gestaolegal.repositories.password_reset_repository import PasswordResetRepository
from gestaolegal.repositories.user_repository import UserRepository
from gestaolegal.services.usuario_service import UsuarioService
from gestaolegal.utils.mail_service import enviar_link_recuperacao

logger = logging.getLogger(__name__)

MSG_LINK_INVALIDO = "Link inválido ou expirado. Peça um novo link para redefinir a sua senha."


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class PasswordResetService:
    """Recuperação de senha por e-mail ("esqueci minha senha" da v2).

    O usuário pede o link, recebe um token opaco por e-mail e escolhe a senha
    nova. O token vale por tempo limitado e só pode ser usado uma vez. Nenhuma
    operação revela se um e-mail está cadastrado.
    """

    def __init__(self):
        self.repository = PasswordResetRepository()
        self.user_repository = UserRepository()
        self.usuario_service = UsuarioService()

    def solicitar(self, email: str) -> None:
        """Emite e envia o link. Silencioso quando não há a quem enviar.

        Conta inexistente, conta desativada e excesso de pedidos seguem o
        mesmo caminho: registra em log e não faz nada. Quem chamou responde a
        mesma mensagem em todos os casos.
        """
        usuario = self.user_repository.find_by_email(email)
        if not usuario or not usuario.id:
            logger.info(f"Recuperação de senha pedida para e-mail sem conta: {email}")
            return
        if not usuario.status:
            logger.info(f"Recuperação de senha pedida para conta desativada: {email}")
            return

        janela = datetime.now() - timedelta(
            minutes=Config.PASSWORD_RESET_JANELA_MINUTES
        )
        token = secrets.token_urlsafe(32)
        with transaction():
            recentes = self.repository.contar_desde(usuario.id, janela)
            if recentes >= Config.PASSWORD_RESET_MAX_PEDIDOS:
                logger.warning(
                    f"Recuperação de senha barrada por excesso de pedidos: {email}"
                )
                return
            # Um pedido novo invalida os anteriores: só o último link funciona.
            self.repository.invalidate_for_user(usuario.id)
            self.repository.create(
                usuario.id,
                _hash(token),
                datetime.now()
                + timedelta(minutes=Config.PASSWORD_RESET_TOKEN_TTL_MINUTES),
            )

        # Fora da transação: um SMTP lento não pode segurar a conexão do banco.
        url = f"{Config.FRONTEND_URL}/redefinir-senha/{token}"
        enviar_link_recuperacao(usuario.email, usuario.nome, url)

    def validar(self, token: str) -> UserInfo:
        registro = self.repository.find_valid_by_hash(_hash(token))
        if not registro:
            raise ValidationException(MSG_LINK_INVALIDO)
        usuario = self.usuario_service.find_by_id(registro.usuario_id)
        if not usuario or not usuario.status:
            raise ValidationException(MSG_LINK_INVALIDO)
        return usuario

    def redefinir(self, token: str, nova_senha: str) -> None:
        if len(nova_senha or "") < Config.PASSWORD_MIN_LENGTH:
            raise ValidationException(
                f"A senha deve ter pelo menos {Config.PASSWORD_MIN_LENGTH} caracteres",
                field="password",
            )

        registro = self.repository.find_valid_by_hash(_hash(token))
        if not registro or not registro.id:
            raise ValidationException(MSG_LINK_INVALIDO)

        usuario = self.usuario_service.find_by_id(registro.usuario_id)
        if not usuario or not usuario.status:
            raise ValidationException(MSG_LINK_INVALIDO)

        with transaction():
            self.usuario_service.change_password(
                registro.usuario_id,
                current_password=None,
                new_password=nova_senha,
                is_admin_change=True,
            )
            self.repository.mark_used(registro.id)

        logger.info(f"Senha redefinida por link de recuperação: usuário {usuario.id}")
