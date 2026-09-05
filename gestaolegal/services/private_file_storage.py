"""Único ponto de contato com o filesystem dos anexos privados (#190).

Todo anexo — de caso, de evento ou geral — mora na raiz privada
(`PRIVATE_FILES_ROOT`), dentro de uma das categorias declaradas em
`PRIVATE_FILE_CATEGORIES`. O banco guarda a **referência** (o nome gerado,
relativo à categoria), nunca o caminho absoluto: assim a raiz pode mudar de
lugar sem reescrever registro nenhum.

A raiz é lida de `current_app.config` a cada chamada. Constante capturada no
import congelaria a config e impediria `monkeypatch` por teste.
"""

import logging
import os
import uuid
from typing import Final

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from gestaolegal.exceptions import ValidationException

logger = logging.getLogger(__name__)

REF_MAX = 300
"""Teto da referência gravada no banco (as colunas são String(300))."""

NAME_MAX = 255
"""Teto de um componente de nome no filesystem (ext4, xfs, overlayfs).

Menor que `REF_MAX`: a coluna aceita 300, o disco não. O nome gerado respeita
os dois, e o excedente é cortado do nome original, nunca da extensão.
"""

DOWNLOAD_HEADERS: Final[dict[str, str]] = {
    "Content-Disposition": "attachment",
    "Cache-Control": "private, no-store",
}
"""Cabeçalhos exigidos em todo download de anexo privado."""


class PrivateFileError(ValidationException):
    """Referência ou categoria inaceitável para a raiz privada."""

    def __init__(self, message: str):
        super().__init__(message, field="arquivo")


def _root() -> str:
    root = current_app.config.get("PRIVATE_FILES_ROOT")
    if not root:
        raise PrivateFileError("Raiz privada dos anexos não configurada")
    return os.path.realpath(str(root))


def categoria_dir(categoria: str) -> str:
    """Diretório da categoria, criado se ainda não existir."""
    categorias = current_app.config.get("PRIVATE_FILE_CATEGORIES", ())
    if categoria not in categorias:
        raise PrivateFileError(f"Categoria de arquivo desconhecida: {categoria!r}")
    caminho = os.path.join(_root(), categoria)
    os.makedirs(caminho, exist_ok=True)
    return os.path.realpath(caminho)


def _validar_ref(ref: str | None) -> str:
    if not ref or not ref.strip():
        raise PrivateFileError("Referência de arquivo vazia")
    ref = ref.strip()
    if len(ref) > REF_MAX:
        raise PrivateFileError(
            f"Referência de arquivo excede {REF_MAX} caracteres"
        )
    if os.path.isabs(ref) or ref.startswith("\\") or ":" in ref:
        raise PrivateFileError("Referência de arquivo não pode ser caminho absoluto")
    normalizada = ref.replace("\\", "/")
    partes = normalizada.split("/")
    if any(parte in ("", ".", "..") for parte in partes):
        raise PrivateFileError("Referência de arquivo inválida")
    return normalizada


def _confinar(base: str, caminho: str) -> str:
    """Realpath de `caminho` só é aceito se ficar dentro de `base`.

    Cobre o symlink que aponta para fora: o realpath segue o link, e o
    prefixo denuncia a fuga.
    """
    real = os.path.realpath(caminho)
    if real != base and not real.startswith(base + os.sep):
        raise PrivateFileError("Referência de arquivo fora da raiz privada")
    return real


def gerar_ref(filename: str | None) -> str:
    """`<uuid4>_<secure_filename>`, com a extensão preservada.

    O UUID substitui o timestamp de segundos usado até aqui, que colidia
    quando dois uploads caíam no mesmo segundo.
    """
    seguro = secure_filename(filename or "") or "arquivo"
    prefixo = f"{uuid.uuid4().hex}_"
    disponivel = min(REF_MAX, NAME_MAX) - len(prefixo)
    if len(seguro) > disponivel:
        raiz, extensao = os.path.splitext(seguro)
        extensao = extensao[:disponivel]
        seguro = raiz[: disponivel - len(extensao)] + extensao
    return prefixo + seguro


def resolve(categoria: str, ref: str | None) -> str:
    """Caminho absoluto da referência, confinado à categoria.

    Não exige que o arquivo exista — quem lê é que decide o que fazer com a
    ausência.
    """
    base = categoria_dir(categoria)
    return _confinar(base, os.path.join(base, _validar_ref(ref)))


def save(categoria: str, file: FileStorage) -> str:
    """Grava o upload e devolve a referência a guardar no banco.

    Escreve num temporário dentro do próprio volume e publica com
    `os.replace` (atômico no mesmo filesystem). O destino é criado com
    `O_EXCL`: nunca sobrescreve um arquivo já existente. Em qualquer falha o
    temporário é removido.
    """
    base = categoria_dir(categoria)
    ref = gerar_ref(file.filename)
    destino = _confinar(base, os.path.join(base, ref))

    temporario = os.path.join(base, f".tmp_{uuid.uuid4().hex}")
    try:
        with open(temporario, "wb") as saida:
            file.save(saida)
        fd = os.open(destino, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        os.replace(temporario, destino)
    except Exception:
        _remover_temporario(temporario)
        raise
    logger.info(f"Anexo gravado em {categoria}/{ref}")
    return ref


def remove(categoria: str, ref: str | None) -> None:
    """Apaga o anexo. Ausência não é erro; referência inválida é."""
    caminho = resolve(categoria, ref)
    try:
        os.remove(caminho)
    except FileNotFoundError:
        logger.info(f"Anexo já ausente ao remover: {categoria}/{ref}")
    except OSError as e:
        logger.warning(f"Não foi possível remover {caminho}: {e}")


def _remover_temporario(caminho: str) -> None:
    try:
        os.remove(caminho)
    except OSError:
        pass
