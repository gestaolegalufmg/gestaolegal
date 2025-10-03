from gestaolegal.common.constants import situacao_deferimento
from gestaolegal.models.user import User


def formatarTipoDeEvento(string):
    """
    Format event type string to human-readable format.

    Args:
        string (str): Event type string

    Returns:
        str: Formatted event type
    """
    return {
        "contato": "Contato",
        "reuniao": "Reunião",
        "protocolo_peticao": "Protocolo de Petição",
        "diligencia_externa": "Diligência Externa",
        "audiencia": "Audiência",
        "conciliacao": "Conciliação",
        "decisao_judicial": "Decisão Judicial",
        "redist_caso": "Redistribuição do Caso",
        "encerramento_caso": "Encerramento do Caso",
        "outros": "Outros",
        "documentos": "Documentos",
    }.get(string, "outros")


def formatarNomeDoUsuario(id_usuario, db):
    """
    Format user ID to user name.

    Args:
        id_usuario: User ID

    Returns:
        str: User name or "Não Há" if not found
    """
    if id_usuario:
        entidade_usuario = db.session.get(User, int(id_usuario))
        return entidade_usuario.nome if entidade_usuario else "Não Há"
    else:
        return "Não Há"


def formatarSituacaoDeferimento(situacao):
    """
    Format deferral status to human-readable format.

    Args:
        situacao (str): Deferral status

    Returns:
        str: Formatted deferral status
    """
    for key in situacao_deferimento:
        if situacao_deferimento[key][0] == situacao:
            return situacao_deferimento[key][1]
    return situacao
