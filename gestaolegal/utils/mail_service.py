import logging

from flask_mail import Message

from gestaolegal.config import Config

logger = logging.getLogger(__name__)

ASSUNTO_RECUPERACAO = "Recuperação de senha Gestão Legal"


def enviar_email(destinatario: str, assunto: str, corpo: str) -> bool:
    """Entrega uma mensagem ao SMTP configurado.

    Nunca levanta exceção: falha de envio vira log e `False`. Quem chama trata
    o envio como melhor esforço — indisponibilidade do servidor de e-mail não
    pode derrubar a requisição do usuário.
    """
    # Import local: o objeto é criado em gestaolegal/__init__.py, que importa
    # utils; importar no topo daria ciclo.
    from gestaolegal import mail

    mensagem = Message(
        subject=assunto,
        recipients=[destinatario],
        body=corpo,
        sender=Config.MAIL_DEFAULT_SENDER,
    )
    try:
        mail.send(mensagem)
    except Exception:
        logger.exception(f"Falha ao enviar e-mail para {destinatario}: {assunto}")
        return False

    logger.info(f"E-mail enviado para {destinatario}: {assunto}")
    return True


def enviar_link_recuperacao(destinatario: str, nome: str, url: str) -> bool:
    validade = Config.PASSWORD_RESET_TOKEN_TTL_MINUTES
    corpo = f"""Olá, {nome}.

Recebemos um pedido para redefinir a sua senha no Gestão Legal.

Para escolher uma senha nova, acesse o endereço abaixo:
{url}

O link vale por {validade} minutos e pode ser usado uma única vez.

Se não foi você que pediu, ignore esta mensagem: sua senha continua a mesma.
"""
    return enviar_email(destinatario, ASSUNTO_RECUPERACAO, corpo)
