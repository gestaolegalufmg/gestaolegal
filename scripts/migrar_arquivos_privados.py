"""Migrador dos anexos legados para a raiz privada (#190): três fases.

O procedimento inteiro, na ordem, é:

    1. `inventario`  — levanta e classifica as referências; grava o manifesto.
       Não escreve mais nada, nem no banco nem no volume.
    2. `aplicacao`   — copia cada origem para o destino do manifesto, confere
       tamanho e SHA-256 e só então atualiza a referência no banco. É
       reexecutável: a retomada é validada contra o estado real do banco.
    3. `verificacao` — relê as referências FINAIS do banco e confere que cada
       uma resolve dentro da raiz privada e tem o conteúdo do manifesto. Não
       escreve nada; sai com a contagem de erros.

**Rodar qualquer fase contra o banco de QA ou de produção é decisão humana.**
Nenhuma delas é acionada pela esteira automatizada: ela só escreve e testa o
script. A aplicação ainda exige `--backup-conferido`, que é a afirmação de
quem executa.

Uso:
    uv run python scripts/migrar_arquivos_privados.py inventario \
        --origem /code/gestaolegal/static/casos=/mnt/legado/casos \
        --origem /code/gestaolegal/static/eventos=/mnt/legado/eventos \
        --origem /code/gestaolegal/static/arquivos=/mnt/legado/arquivos \
        --arquivos-legado /mnt/legado/arquivos \
        --manifesto /data/gestaolegal/migracao/manifesto.json

    uv run python scripts/migrar_arquivos_privados.py aplicacao \
        --manifesto /data/gestaolegal/migracao/manifesto.json \
        --raiz-privada /data/gestaolegal/uploads \
        --backup-conferido

    uv run python scripts/migrar_arquivos_privados.py verificacao \
        --manifesto /data/gestaolegal/migracao/manifesto.json \
        --raiz-privada /data/gestaolegal/uploads

Lê o `.env` do diretório atual (raiz do checkout ou da worktree) e usa
`Config.SQLALCHEMY_DATABASE_URI`, como `migrations/env.py`. `--database-url`
substitui essa URL (é o que os testes usam).

Fase de inventário: NÃO ESCREVE NADA além do manifesto. Percorre as três
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

Fase de aplicação: pressupõe a **escrita da API suspensa** e o **backup do
banco e das origens já feito e conferido** — o script não faz backup nenhum e
recusa rodar sem `--backup-conferido`, que é a afirmação de quem executa.

A ordem de cada item é sempre a mesma, e é ela que torna a fase recuperável:

    1. copia a origem para o destino ÚNICO do registro, dentro do volume;
    2. confere tamanho e SHA-256 da cópia contra o manifesto;
    3. só então atualiza a referência no banco, e só se o valor anterior ainda
       for exatamente o que o manifesto registrou.

Origem cujo tamanho ou SHA-256 divergiu do manifesto não é migrada: o
arquivo mudou depois do inventário, e o certo é refazer o inventário, não
copiar às cegas. Referência que já mudou no banco desde o inventário também é
recusada — outra coisa mexeu ali.

O progresso não mora em arquivo de progresso à parte: a retomada é validada
contra o **estado real do banco**. Registro cuja coluna já contém o destino do
manifesto conta como aplicado e é apenas conferido no disco. Por isso a fase é
reexecutável e idempotente: rodar duas vezes não copia duas vezes nem produz
efeito duplicado.

Nenhuma origem é removida. A quarentena das origens públicas é decisão humana,
fora deste script.

Fase de verificação: NÃO ESCREVE NADA. Para cada item do manifesto ela relê a
coluna do banco — a referência FINAL, não a do manifesto — e confere que ela
resolve dentro da raiz privada pela mesma regra do `private_file_storage`, que
o arquivo está lá e que tamanho e SHA-256 continuam sendo os do manifesto.

O resumo separa quatro grupos:

    migrado     referência final resolve, existe no volume e o conteúdo bate
    ausente     erro: a referência não resolve, sumiu do volume ou continua
                no formato legado (a aplicação não chegou nela)
    divergente  erro: o arquivo está lá, mas o conteúdo mudou desde o manifesto
    excecao     nada a conferir por desenho — externo, sem anexo, ou registro
                que não existe mais no banco

E conta à parte a **quarentena**: as origens públicas que continuam de pé no
lugar antigo. Nenhuma fase as remove; a quarentena é decisão humana.

O código de saída é a contagem de erros (ausentes + divergentes), como em
`scripts/seed_local.py`.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from dotenv import load_dotenv
from sqlalchemy import create_engine, select, update
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

APLICADO = "aplicado"
JA_APLICADO = "ja_aplicado"
IGNORADO = "ignorado"
ERRO = "erro"

RESULTADOS = (APLICADO, JA_APLICADO, IGNORADO, ERRO)

MIGRADO = "migrado"
DIVERGENTE = "divergente"
EXCECAO = "excecao"

VERIFICACOES = (MIGRADO, AUSENTE, DIVERGENTE, EXCECAO)
"""Grupos do resumo da verificação. `AUSENTE` e `DIVERGENTE` são os erros."""

TABELAS = {
    "arquivosCaso": (arquivos_caso, "link_arquivo"),
    "eventos": (eventos, "arquivo"),
    "arquivos": (arquivos, "caminho"),
}
"""Tabela e coluna de anexo de cada origem do manifesto."""

CATEGORIAS = ("casos", "eventos", "arquivos")
"""Subdiretórios da raiz privada — os mesmos de `PRIVATE_FILE_CATEGORIES`."""


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


# --------------------------------------------------------------------------
# Fase 2: aplicação
# --------------------------------------------------------------------------


class FalhaDeItem(Exception):
    """O item não pôde ser migrado — contabilizado, sem abortar a fase."""


def carregar_manifesto(caminho: str) -> dict:
    """Lê o manifesto gerado pelo inventário e confere o formato mínimo."""
    origem = _normalizar_dir(caminho)
    try:
        with open(origem, encoding="utf-8") as entrada:
            conteudo = json.load(entrada)
    except FileNotFoundError:
        raise ErroDeUso(f"Manifesto não encontrado: {origem}") from None
    except json.JSONDecodeError as e:
        raise ErroDeUso(f"Manifesto ilegível ({origem}): {e}") from None
    if not isinstance(conteudo, dict) or conteudo.get("versao") != 1:
        raise ErroDeUso(f"Manifesto em versão desconhecida: {origem}")
    if not isinstance(conteudo.get("itens"), list):
        raise ErroDeUso(f"Manifesto sem lista de itens: {origem}")
    return conteudo


def caminho_destino(raiz: str, categoria: str, destino: str | None) -> str:
    """Caminho absoluto do destino, confinado ao diretório da categoria.

    Mesma regra do `private_file_storage.resolve`, escrita aqui porque o
    script roda fora do app Flask (não há `current_app` para consultar).
    """
    if categoria not in CATEGORIAS:
        raise FalhaDeItem(f"categoria desconhecida: {categoria!r}")
    if not destino or not destino.strip():
        raise FalhaDeItem("item do manifesto sem destino")
    destino = destino.strip()
    if os.path.isabs(destino) or "/" in destino or "\\" in destino or destino in (".", ".."):
        raise FalhaDeItem(f"destino inválido no manifesto: {destino!r}")
    base = os.path.realpath(os.path.join(raiz, categoria))
    confinado = _confinar(base, os.path.join(base, destino))
    if confinado is None:
        raise FalhaDeItem(f"destino escapa da raiz privada: {destino!r}")
    return confinado


def _conferir_contra_manifesto(caminho: str, tamanho: int | None, sha: str | None, rotulo: str) -> None:
    real_tamanho = os.path.getsize(caminho)
    if tamanho is not None and real_tamanho != tamanho:
        raise FalhaDeItem(
            f"tamanho de {rotulo} divergiu do manifesto ({real_tamanho} != {tamanho})"
        )
    real_sha = sha256_de(caminho)
    if sha is not None and real_sha != sha:
        raise FalhaDeItem(f"SHA-256 de {rotulo} divergiu do manifesto")


def copiar_verificado(origem: str, destino: str, tamanho: int | None, sha: str | None) -> bool:
    """Copia origem -> destino conferindo tamanho e SHA-256. True se copiou.

    Destino já presente e conferido não é recopiado (reexecução idempotente);
    destino presente com conteúdo diferente é falha, nunca sobrescrita. A
    cópia passa por um temporário no próprio diretório e é publicada com
    `os.replace`, para que ninguém veja destino pela metade.
    """
    if os.path.exists(destino):
        _conferir_contra_manifesto(destino, tamanho, sha, "destino já existente")
        return False

    if not os.path.isfile(origem):
        raise FalhaDeItem(f"origem não encontrada: {origem}")
    _conferir_contra_manifesto(origem, tamanho, sha, "origem")

    diretorio = os.path.dirname(destino)
    os.makedirs(diretorio, exist_ok=True)
    temporario = os.path.join(diretorio, f".tmp_{uuid.uuid4().hex}")
    try:
        with open(origem, "rb") as entrada, open(temporario, "wb") as saida:
            for bloco in iter(lambda: entrada.read(CHUNK), b""):
                saida.write(bloco)
            saida.flush()
            os.fsync(saida.fileno())
        os.chmod(temporario, 0o600)
        _conferir_contra_manifesto(temporario, tamanho, sha, "cópia")
        os.replace(temporario, destino)
    except Exception:
        _remover(temporario)
        raise
    return True


def _remover(caminho: str) -> None:
    try:
        os.remove(caminho)
    except OSError:
        pass


def _valor_atual(conn, tabela: str, registro_id: int) -> str | None:
    if tabela not in TABELAS:
        raise FalhaDeItem(f"tabela desconhecida no manifesto: {tabela!r}")
    objeto, coluna = TABELAS[tabela]
    linha = conn.execute(
        select(objeto.c[coluna]).where(objeto.c.id == registro_id)
    ).fetchone()
    if linha is None:
        raise FalhaDeItem("registro não existe mais no banco")
    return linha[0]


def _mesma_referencia(a: str | None, b: str | None) -> bool:
    return (a or "").strip() == (b or "").strip()


def atualizar_referencia(conn, tabela: str, registro_id: int, anterior: str | None, destino: str) -> None:
    """Aponta a coluna para o destino, só se o valor anterior ainda bater.

    O `WHERE` repete a condição do `SELECT`: entre a leitura e a escrita
    ninguém pode ter mexido na coluna. `rowcount` zero é falha do item.
    """
    objeto, coluna = TABELAS[tabela]
    condicao = (
        objeto.c[coluna].is_(None)
        if anterior is None or not anterior.strip()
        else objeto.c[coluna] == anterior
    )
    resultado = conn.execute(
        update(objeto)
        .where(objeto.c.id == registro_id, condicao)
        .values({coluna: destino})
    )
    if resultado.rowcount != 1:
        raise FalhaDeItem("a referência mudou no banco durante a aplicação")


def aplicar_item(engine, item: dict, raiz: str) -> str:
    """Aplica um item do manifesto e devolve o resultado.

    Copia primeiro, atualiza o banco depois: interromper entre as duas deixa
    um arquivo a mais no volume e o banco intacto — a retomada recopia (ou
    reconhece a cópia boa) e conclui. O inverso deixaria referência apontando
    para o nada.
    """
    tabela = item.get("tabela")
    registro_id = item.get("registro_id")
    destino_ref = item.get("destino")
    destino_abs = caminho_destino(raiz, item.get("categoria", ""), destino_ref)

    with engine.begin() as conn:
        atual = _valor_atual(conn, tabela, registro_id)

    ja_aplicado = _mesma_referencia(atual, destino_ref)
    if not ja_aplicado and not _mesma_referencia(atual, item.get("referencia_anterior")):
        raise FalhaDeItem(
            "a referência anterior não bate com o manifesto — refaça o inventário"
        )

    copiar_verificado(item.get("origem") or "", destino_abs, item.get("tamanho"), item.get("sha256"))
    if ja_aplicado:
        return JA_APLICADO

    with engine.begin() as conn:
        atualizar_referencia(conn, tabela, registro_id, item.get("referencia_anterior"), destino_ref)
    return APLICADO


def aplicar(engine, manifesto: dict, raiz: str) -> dict:
    """Percorre o manifesto item a item. Nenhuma origem é removida."""
    contagem = {resultado: 0 for resultado in RESULTADOS}
    erros: list[str] = []
    for item in manifesto["itens"]:
        if item.get("classificacao") != MIGRAVEL:
            contagem[IGNORADO] += 1
            continue
        rotulo = f"{item.get('tabela')}#{item.get('registro_id')}"
        try:
            contagem[aplicar_item(engine, item, raiz)] += 1
        except FalhaDeItem as e:
            contagem[ERRO] += 1
            erros.append(f"{rotulo}: {e}")
        except OSError as e:
            contagem[ERRO] += 1
            erros.append(f"{rotulo}: falha de filesystem: {e}")
    return {"contagem": contagem, "erros": erros}


def _raiz_privada(argumento: str | None) -> str:
    if argumento:
        raiz = _normalizar_dir(argumento)
    else:
        from gestaolegal.config import Config

        raiz = _normalizar_dir(str(Config.PRIVATE_FILES_ROOT))
    if not os.path.isdir(raiz):
        raise ErroDeUso(f"Raiz privada não existe ou não é diretório: {raiz!r}")
    return raiz


def executar_aplicacao(args) -> int:
    if not args.backup_conferido:
        raise ErroDeUso(
            "a aplicação escreve no banco: rode com --backup-conferido só depois de"
            " suspender a escrita da API e conferir o backup do banco e das origens"
        )
    manifesto = carregar_manifesto(args.manifesto)
    raiz = _raiz_privada(args.raiz_privada)

    engine = create_engine(_database_url(args.database_url))
    try:
        relatorio = aplicar(engine, manifesto, raiz)
    finally:
        engine.dispose()

    contagem = relatorio["contagem"]
    print(f"aplicação: {len(manifesto['itens'])} item(ns) no manifesto")
    for chave in RESULTADOS:
        print(f"  {chave}: {contagem[chave]}")
    for erro in relatorio["erros"]:
        print(f"  ! {erro}", file=sys.stderr)
    print("nenhuma origem foi removida — a quarentena é decisão humana")
    return contagem[ERRO]


# --------------------------------------------------------------------------
# Fase 3: verificação
# --------------------------------------------------------------------------


def verificar_item(conn, item: dict, raiz: str) -> tuple[str, str | None]:
    """Confere a referência FINAL de um item. Devolve `(grupo, motivo)`.

    A referência conferida é a que está no banco AGORA, não a do manifesto: é
    ela que o app vai resolver. O manifesto entra só como padrão de conteúdo,
    quando a referência final é o destino que ele previu.
    """
    if item.get("classificacao") in (EXTERNO, SEM_REFERENCIA):
        return EXCECAO, "sem anexo migrável no inventário"

    try:
        atual = _valor_atual(conn, item.get("tabela"), item.get("registro_id"))
    except FalhaDeItem as e:
        return EXCECAO, str(e)

    if not (atual or "").strip():
        return EXCECAO, "registro sem anexo"
    atual = atual.strip()

    if not _e_referencia_relativa(atual):
        return AUSENTE, "referência ainda no formato legado — não foi migrada"

    try:
        caminho = caminho_destino(raiz, item.get("categoria", ""), atual)
    except FalhaDeItem as e:
        return AUSENTE, str(e)

    if not os.path.isfile(caminho):
        return AUSENTE, f"arquivo não está na raiz privada: {item.get('categoria')}/{atual}"

    if _mesma_referencia(atual, item.get("destino")):
        try:
            _conferir_contra_manifesto(
                caminho, item.get("tamanho"), item.get("sha256"), "referência final"
            )
        except FalhaDeItem as e:
            return DIVERGENTE, str(e)

    return MIGRADO, None


def verificar(engine, manifesto: dict, raiz: str) -> dict:
    """Percorre o manifesto conferindo o estado final. Não escreve nada."""
    contagem = {grupo: 0 for grupo in VERIFICACOES}
    erros: list[str] = []
    quarentena = 0
    with engine.connect() as conn:
        for item in manifesto["itens"]:
            rotulo = f"{item.get('tabela')}#{item.get('registro_id')}"
            try:
                grupo, motivo = verificar_item(conn, item, raiz)
            except OSError as e:
                grupo, motivo = AUSENTE, f"falha de filesystem: {e}"
            contagem[grupo] += 1
            if grupo in (AUSENTE, DIVERGENTE):
                erros.append(f"{rotulo}: {motivo}")
            origem = item.get("origem")
            if origem and os.path.isfile(origem):
                quarentena += 1
    return {"contagem": contagem, "erros": erros, "quarentena": quarentena}


def executar_verificacao(args) -> int:
    manifesto = carregar_manifesto(args.manifesto)
    raiz = _raiz_privada(args.raiz_privada)

    engine = create_engine(_database_url(args.database_url))
    try:
        relatorio = verificar(engine, manifesto, raiz)
    finally:
        engine.dispose()

    contagem = relatorio["contagem"]
    print(f"verificação: {len(manifesto['itens'])} item(ns) no manifesto")
    for chave in VERIFICACOES:
        print(f"  {chave}: {contagem[chave]}")
    print(f"  quarentena (origens ainda no lugar antigo): {relatorio['quarentena']}")
    for erro in relatorio["erros"]:
        print(f"  ! {erro}", file=sys.stderr)
    print("nenhuma origem foi removida — a quarentena é decisão humana")
    return contagem[AUSENTE] + contagem[DIVERGENTE]


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

    aplicacao = sub.add_parser(
        "aplicacao",
        help="Fase 2: copia para o volume e só então atualiza as referências.",
    )
    aplicacao.add_argument(
        "--manifesto",
        required=True,
        metavar="ARQUIVO",
        help="Manifesto gerado pela fase de inventário.",
    )
    aplicacao.add_argument(
        "--raiz-privada",
        metavar="DIR",
        help="Raiz privada de destino. Padrão: Config.PRIVATE_FILES_ROOT.",
    )
    aplicacao.add_argument(
        "--backup-conferido",
        action="store_true",
        help="Afirma que a escrita da API está suspensa e o backup do banco e das"
        " origens foi feito e conferido. Sem isto o script não escreve nada.",
    )
    aplicacao.add_argument("--database-url", help="Substitui Config.SQLALCHEMY_DATABASE_URI.")

    verificacao = sub.add_parser(
        "verificacao",
        help="Fase 3: confere as referências finais e resume. Não escreve nada.",
    )
    verificacao.add_argument(
        "--manifesto",
        required=True,
        metavar="ARQUIVO",
        help="Manifesto gerado pela fase de inventário.",
    )
    verificacao.add_argument(
        "--raiz-privada",
        metavar="DIR",
        help="Raiz privada a conferir. Padrão: Config.PRIVATE_FILES_ROOT.",
    )
    verificacao.add_argument("--database-url", help="Substitui Config.SQLALCHEMY_DATABASE_URI.")
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
        if args.fase == "aplicacao":
            return executar_aplicacao(args)
        if args.fase == "verificacao":
            return executar_verificacao(args)
    except ErroDeUso as e:
        print(f"migrador: {e}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
