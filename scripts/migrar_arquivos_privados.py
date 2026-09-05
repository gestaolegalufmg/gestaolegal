"""Migrador dos anexos legados para a raiz privada (#190), fase 1: inventário.

Uso:
    uv run python scripts/migrar_arquivos_privados.py inventario \
        --origem /code/gestaolegal/static/casos=/mnt/legado/casos \
        --origem /code/gestaolegal/static/eventos=/mnt/legado/eventos \
        --origem /code/gestaolegal/static/arquivos=/mnt/legado/arquivos \
        --arquivos-legado /mnt/legado/arquivos \
        --manifesto /data/gestaolegal/migracao/manifesto.json

Lê o `.env` do diretório atual (raiz do checkout ou da worktree) e usa
`Config.SQLALCHEMY_DATABASE_URI`, como `migrations/env.py`. `--database-url`
substitui essa URL (é o que os testes usam).

**Rodar isto contra o banco de QA ou de produção é decisão humana.** O script
existe para ser lido e conferido antes de qualquer execução com dados reais; a
esteira automatizada só o escreve e o testa.

Fase de inventário (esta): NÃO ESCREVE NADA além do manifesto. Percorre as três
colunas de anexo — `arquivosCaso.link_arquivo`, `eventos.arquivo` e
`arquivos.caminho` —, registros ativos e inativos, traduz cada referência
legada pelo mapa `prefixo antigo=mount de leitura` e classifica o que achou. Os
`arquivos` herdados da v2 não têm `caminho`: para eles o candidato é
`--arquivos-legado/<nome>`, que era onde o `ARQUIVOS_DIR` da 2.0 guardava.

O disco NÃO é varrido e o caminho gravado NÃO é seguido: só o que o mapa
traduzir, e apenas dentro do mount correspondente, é considerado. Caminho que
escapa do mount (via `..` ou symlink) é classificado como externo.

Classificações de cada item:
    migravel      origem encontrada no mount, com tamanho e SHA-256 apurados
    ja_migrado    referência já é relativa (formato novo); nada a fazer
    ausente       o caminho traduziu, mas o arquivo não está no mount
    externo       nenhum prefixo do mapa cobre a referência, ou ela foge do mount
    sem_referencia  registro sem anexo a migrar

Cada item ganha destino PRÓPRIO, derivado de `<tabela>:<id>` — dois registros
que apontam para o mesmo arquivo de origem (referência compartilhada) recebem
destinos distintos, para que excluir um não apague o anexo do outro.

O manifesto é privado (nomes de arquivos de pessoas) e é gravado com modo 0600
FORA da árvore do git; o script recusa gravá-lo dentro do repositório.

As fases de aplicação e de verificação são das stories seguintes (f11, f12).
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from werkzeug.utils import secure_filename

from gestaolegal.database.tables import arquivos, arquivos_caso, casos, eventos

load_dotenv()

REF_MAX = 300
"""Teto da referência gravada no banco (as colunas são String(300))."""

NAME_MAX = 255
"""Teto de um componente de nome no filesystem — menor que `REF_MAX`."""

CHUNK = 1024 * 1024

MIGRAVEL = "migravel"
JA_MIGRADO = "ja_migrado"
AUSENTE = "ausente"
EXTERNO = "externo"
SEM_REFERENCIA = "sem_referencia"

CLASSIFICACOES = (MIGRAVEL, JA_MIGRADO, AUSENTE, EXTERNO, SEM_REFERENCIA)


class ErroDeUso(Exception):
    """Parâmetro inaceitável — o script para antes de tocar no banco."""


@dataclass
class ItemInventario:
    """Uma linha do manifesto: um registro do banco e seu anexo."""

    tabela: str
    registro_id: int
    coluna: str
    categoria: str
    referencia_anterior: str | None
    origem: str | None
    destino: str | None
    tamanho: int | None
    sha256: str | None
    classificacao: str
    orfao: bool = False
    compartilhado: bool = False
    nome_repetido: bool = False
    observacao: str | None = None
    motivos: list[str] = field(default_factory=list)


def _normalizar_dir(caminho: str) -> str:
    return os.path.normpath(os.path.abspath(os.path.expanduser(caminho)))


def carregar_mapa_origens(pares: list[str]) -> dict[str, str]:
    """`PREFIXO=MOUNT` -> dicionário, com os dois lados normalizados.

    O prefixo é o caminho como está gravado no banco (a máquina antiga); o
    mount é onde esse diretório está montado para leitura AQUI.
    """
    mapa: dict[str, str] = {}
    for par in pares:
        prefixo, separador, mount = par.partition("=")
        if not separador or not prefixo.strip() or not mount.strip():
            raise ErroDeUso(f"Origem inválida (esperado PREFIXO=MOUNT): {par!r}")
        prefixo = os.path.normpath(prefixo.strip())
        if not os.path.isabs(prefixo):
            raise ErroDeUso(f"Prefixo de origem precisa ser absoluto: {prefixo!r}")
        mount = _normalizar_dir(mount)
        if not os.path.isdir(mount):
            raise ErroDeUso(f"Mount de leitura não existe ou não é diretório: {mount!r}")
        if prefixo in mapa:
            raise ErroDeUso(f"Prefixo de origem repetido: {prefixo!r}")
        mapa[prefixo] = mount
    return mapa


def _confinar(base: str, caminho: str) -> str | None:
    """Realpath de `caminho`, aceito só se ficar dentro de `base`.

    Cobre `..` na referência gravada e symlink que aponta para fora do mount.
    """
    base_real = os.path.realpath(base)
    real = os.path.realpath(caminho)
    if real != base_real and not real.startswith(base_real + os.sep):
        return None
    return real


def traduzir(caminho: str, mapa: dict[str, str]) -> str | None:
    """Caminho legado -> caminho de leitura local, ou None se não couber.

    O prefixo mais longo ganha: mounts aninhados não se atrapalham.
    """
    alvo = os.path.normpath(caminho.replace("\\", "/"))
    for prefixo in sorted(mapa, key=len, reverse=True):
        if alvo == prefixo:
            return None  # é o diretório, não um arquivo dentro dele
        if alvo.startswith(prefixo + os.sep):
            resto = alvo[len(prefixo) + 1 :]
            return _confinar(mapa[prefixo], os.path.join(mapa[prefixo], resto))
    return None


def destino_para(tabela: str, registro_id: int, nome: str | None) -> str:
    """`<32 hex>_<nome>`, derivado de `<tabela>:<id>`.

    Mesmo formato que `private_file_storage.gerar_ref` produz — e que
    `nome_original` sabe desmontar —, mas determinístico: reexecutar o
    inventário devolve o mesmo destino, e cada registro tem o seu, mesmo
    quando dois registros compartilham a origem.
    """
    digest = hashlib.sha256(f"{tabela}:{registro_id}".encode()).hexdigest()[:32]
    seguro = secure_filename(os.path.basename(nome or "")) or "arquivo"
    prefixo = f"{digest}_"
    disponivel = min(REF_MAX, NAME_MAX) - len(prefixo)
    if len(seguro) > disponivel:
        raiz, extensao = os.path.splitext(seguro)
        extensao = extensao[:disponivel]
        seguro = raiz[: disponivel - len(extensao)] + extensao
    return prefixo + seguro


def sha256_de(caminho: str) -> str:
    digest = hashlib.sha256()
    with open(caminho, "rb") as entrada:
        for bloco in iter(lambda: entrada.read(CHUNK), b""):
            digest.update(bloco)
    return digest.hexdigest()


def _e_referencia_relativa(referencia: str) -> bool:
    """A referência já está no formato novo (relativa à categoria)?"""
    return not os.path.isabs(referencia) and "\\" not in referencia and ":" not in referencia


def _classificar(
    tabela: str,
    registro_id: int,
    coluna: str,
    categoria: str,
    referencia: str | None,
    mapa: dict[str, str],
    orfao: bool = False,
    candidato_legado: str | None = None,
    observacao: str | None = None,
) -> ItemInventario:
    item = ItemInventario(
        tabela=tabela,
        registro_id=registro_id,
        coluna=coluna,
        categoria=categoria,
        referencia_anterior=referencia,
        origem=None,
        destino=None,
        tamanho=None,
        sha256=None,
        classificacao=SEM_REFERENCIA,
        orfao=orfao,
        observacao=observacao,
    )

    origem: str | None = None
    if referencia and referencia.strip():
        referencia = referencia.strip()
        item.referencia_anterior = referencia
        if _e_referencia_relativa(referencia):
            item.classificacao = JA_MIGRADO
            return item
        origem = traduzir(referencia, mapa)
        if origem is None:
            item.classificacao = EXTERNO
            item.motivos.append("nenhum mount de leitura cobre esta referência")
            return item
    elif candidato_legado is not None:
        origem = candidato_legado
    else:
        return item

    item.origem = origem
    item.destino = destino_para(tabela, registro_id, os.path.basename(origem))
    if not os.path.isfile(origem):
        item.classificacao = AUSENTE
        item.motivos.append("origem não encontrada no mount de leitura")
        return item

    item.classificacao = MIGRAVEL
    item.tamanho = os.path.getsize(origem)
    item.sha256 = sha256_de(origem)
    return item


def _candidato_legado(nome: str | None, arquivos_legado: str | None) -> tuple[str | None, str | None]:
    """Caminho do `arquivos` herdado da v2 (`ARQUIVOS_DIR/nome`), ou o motivo."""
    if not arquivos_legado:
        return None, "sem --arquivos-legado, registro herdado da v2 não pôde ser localizado"
    nome = (nome or "").strip()
    if not nome:
        return None, "registro sem `caminho` e sem `nome`"
    if "/" in nome or "\\" in nome or nome in (".", ".."):
        return None, "o `nome` do registro não é um nome de arquivo simples"
    candidato = _confinar(arquivos_legado, os.path.join(arquivos_legado, nome))
    if candidato is None:
        return None, "o `nome` do registro escapa do diretório legado"
    return candidato, None


def inventariar(conn, mapa: dict[str, str], arquivos_legado: str | None = None) -> list[ItemInventario]:
    """Percorre as três colunas de anexo e devolve o inventário completo.

    Nada é escrito: só `SELECT`. Registros ativos e inativos entram — o
    `status` falso de um evento não faz o anexo dele sumir do disco.
    """
    itens: list[ItemInventario] = []

    consulta = select(
        arquivos_caso.c.id, arquivos_caso.c.link_arquivo, arquivos_caso.c.id_caso, casos.c.id
    ).select_from(arquivos_caso.outerjoin(casos, arquivos_caso.c.id_caso == casos.c.id))
    for registro_id, referencia, id_caso, caso_existente in conn.execute(consulta):
        itens.append(
            _classificar(
                "arquivosCaso",
                registro_id,
                "link_arquivo",
                "casos",
                referencia,
                mapa,
                orfao=caso_existente is None,
                observacao="registro sem caso" if id_caso is None else None,
            )
        )

    consulta = select(
        eventos.c.id, eventos.c.arquivo, eventos.c.id_caso, casos.c.id
    ).select_from(eventos.outerjoin(casos, eventos.c.id_caso == casos.c.id))
    for registro_id, referencia, _id_caso, caso_existente in conn.execute(consulta):
        itens.append(
            _classificar(
                "eventos",
                registro_id,
                "arquivo",
                "eventos",
                referencia,
                mapa,
                orfao=caso_existente is None,
            )
        )

    consulta = select(arquivos.c.id, arquivos.c.caminho, arquivos.c.nome)
    for registro_id, referencia, nome in conn.execute(consulta):
        candidato, motivo = (None, None)
        if not (referencia or "").strip():
            candidato, motivo = _candidato_legado(nome, arquivos_legado)
        item = _classificar(
            "arquivos",
            registro_id,
            "caminho",
            "arquivos",
            referencia,
            mapa,
            candidato_legado=candidato,
            observacao="registro herdado da v2, sem `caminho`"
            if not (referencia or "").strip()
            else None,
        )
        if motivo:
            item.classificacao = EXTERNO
            item.motivos.append(motivo)
        itens.append(item)

    _marcar_repetidos(itens)
    return itens


def _marcar_repetidos(itens: list[ItemInventario]) -> None:
    """Marca referência compartilhada (mesma origem) e nome repetido.

    Compartilhada: mais de um registro aponta para o MESMO arquivo. Repetido:
    origens diferentes com o mesmo nome de arquivo — inofensivo, porque cada
    destino leva o prefixo do registro, mas vale no resumo.
    """
    por_origem: dict[str, list[ItemInventario]] = {}
    por_nome: dict[str, set[str]] = {}
    for item in itens:
        if not item.origem:
            continue
        por_origem.setdefault(item.origem, []).append(item)
        por_nome.setdefault(os.path.basename(item.origem), set()).add(item.origem)
    for grupo in por_origem.values():
        if len(grupo) > 1:
            for item in grupo:
                item.compartilhado = True
    for item in itens:
        if item.origem and len(por_nome[os.path.basename(item.origem)]) > 1:
            item.nome_repetido = True


def resumir(itens: list[ItemInventario]) -> dict[str, int]:
    contagem = {classificacao: 0 for classificacao in CLASSIFICACOES}
    for item in itens:
        contagem[item.classificacao] = contagem.get(item.classificacao, 0) + 1
    contagem["compartilhados"] = sum(1 for item in itens if item.compartilhado)
    contagem["nomes_repetidos"] = sum(1 for item in itens if item.nome_repetido)
    contagem["orfaos"] = sum(1 for item in itens if item.orfao)
    contagem["total"] = len(itens)
    return contagem


def _raiz_do_git() -> str | None:
    try:
        saida = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if saida.returncode != 0:
        return None
    return os.path.realpath(saida.stdout.strip())


def validar_manifesto_fora_do_git(caminho: str) -> str:
    """Recusa manifesto dentro do repositório — ele é privado, não versionável."""
    destino = _normalizar_dir(caminho)
    raiz = _raiz_do_git()
    if raiz and (destino == raiz or destino.startswith(raiz + os.sep)):
        raise ErroDeUso(
            f"O manifesto é privado e não pode ficar dentro do repositório ({raiz}): {destino}"
        )
    return destino


def escrever_manifesto(caminho: str, itens: list[ItemInventario], mapa: dict[str, str]) -> str:
    """Grava o manifesto com modo 0600 e devolve o caminho final."""
    destino = validar_manifesto_fora_do_git(caminho)
    os.makedirs(os.path.dirname(destino) or ".", exist_ok=True)
    conteudo = {
        "versao": 1,
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "origens": mapa,
        "resumo": resumir(itens),
        "itens": [asdict(item) for item in itens],
    }
    fd = os.open(destino, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as saida:
        json.dump(conteudo, saida, ensure_ascii=False, indent=2)
    os.chmod(destino, 0o600)
    return destino


def _database_url(argumento: str | None) -> str:
    if argumento:
        return argumento
    from gestaolegal.config import Config

    return Config.SQLALCHEMY_DATABASE_URI


def _montar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="migrar_arquivos_privados.py",
        description="Migra os anexos legados para a raiz privada (#190).",
    )
    sub = parser.add_subparsers(dest="fase", required=True)

    inventario = sub.add_parser("inventario", help="Fase 1: levanta e classifica, sem escrever.")
    inventario.add_argument(
        "--origem",
        action="append",
        default=[],
        metavar="PREFIXO=MOUNT",
        help="Prefixo gravado no banco e onde ele está montado para leitura. Repetível.",
    )
    inventario.add_argument(
        "--arquivos-legado",
        metavar="DIR",
        help="ARQUIVOS_DIR da v2, onde ficam os `arquivos` sem `caminho`.",
    )
    inventario.add_argument(
        "--manifesto",
        required=True,
        metavar="ARQUIVO",
        help="Onde gravar o manifesto (fora do repositório).",
    )
    inventario.add_argument("--database-url", help="Substitui Config.SQLALCHEMY_DATABASE_URI.")
    return parser


def executar_inventario(args) -> int:
    mapa = carregar_mapa_origens(args.origem)
    arquivos_legado = None
    if args.arquivos_legado:
        arquivos_legado = _normalizar_dir(args.arquivos_legado)
        if not os.path.isdir(arquivos_legado):
            raise ErroDeUso(f"Diretório legado não existe: {arquivos_legado!r}")
    caminho_manifesto = validar_manifesto_fora_do_git(args.manifesto)

    engine = create_engine(_database_url(args.database_url))
    with engine.connect() as conn:
        itens = inventariar(conn, mapa, arquivos_legado)

    destino = escrever_manifesto(caminho_manifesto, itens, mapa)
    contagem = resumir(itens)
    print(f"inventário: {contagem['total']} registro(s) de anexo")
    for chave in CLASSIFICACOES:
        print(f"  {chave}: {contagem[chave]}")
    print(
        f"  compartilhados: {contagem['compartilhados']}"
        f" | nomes repetidos: {contagem['nomes_repetidos']}"
        f" | órfãos: {contagem['orfaos']}"
    )
    print(f"manifesto em {destino}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _montar_parser().parse_args(argv)
    try:
        if args.fase == "inventario":
            return executar_inventario(args)
    except ErroDeUso as e:
        print(f"migrador: {e}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
