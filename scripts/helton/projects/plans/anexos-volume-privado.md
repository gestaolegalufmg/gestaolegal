# Plano: anexos em volume privado (#190)

Plano para o loop Helton. Criado em 05/09/2026 a partir de
`docs/plano-190-volume-privado.md`, que é a spec: contexto, decisões e o
procedimento operacional completo. Este arquivo só diz **o que construir, onde
e como provar**. Em caso de dúvida sobre "por quê", leia a spec.

Escopo: todo o código da #190, incluindo o migrador. **Fora de escopo a
execução** do migrador contra QA ou produção — isso é `human_gate` e não é
tarefa do loop.

## Resultado esperado

Com esta fatia mesclada:

1. anexos dos três fluxos ficam num volume privado persistente, fora de
   qualquer diretório publicado pelo Flask;
2. o banco guarda **referência relativa** à raiz privada, não caminho absoluto;
3. `/static/casos`, `/static/eventos` e `/static/arquivos` devolvem 404, pelo
   proxy e pela porta da API;
4. existe `scripts/migrar_arquivos_privados.py` capaz de inventariar, migrar e
   verificar os anexos legados, com testes;
5. recriar o container da API não perde mais os anexos — o que hoje acontece.

## Estado atual (levantado em 05/09/2026, base `b619317`)

O que a spec ainda não registrava e o loop precisa saber:

- **Não existe volume para uploads na stack padrão.** `docker-compose.yml` só
  declara `mysql_data` e `mail_dkim`. Anexos vivem dentro do container.
- O único bind de anexos do projeto está em `docker-compose.qa.yml`:
  `/opt/gestaolegal/arquivos:/code/gestaolegal/static/arquivos` — o próprio
  diretório público que a issue quer eliminar.
- `gestaolegal/__init__.py:11` cria `Flask(__name__, ...)` sem `static_folder`
  próprio; o default `gestaolegal/static` é servido em `/static/<path>` sem
  autenticação, em paralelo às rotas `/download`.
- `eventos.arquivo` é `String(100)` (`gestaolegal/database/tables.py:234`) e
  guarda caminho absoluto. `arquivosCaso.link_arquivo` e `arquivos.caminho` são
  `String(300)` (`:247`, `:259`).
- O upload de evento mora **dentro das rotas**, duplicado em
  `gestaolegal/controllers/caso_controller.py:274-287` e `:361-374`.
- `.dockerignore` não exclui os diretórios de upload, e o Dockerfile faz
  `COPY . /code`.

## Decisões já tomadas (não reabrir)

- Referência no banco é relativa a `PRIVATE_FILES_ROOT`
  (`casos/<uuid>_<nome>.pdf`). Leitura é `join(root, ref)` com `realpath`
  confinado à raiz.
- **Sem fallback de leitura para caminho absoluto no código de produção.** A
  compatibilidade com o legado é responsabilidade exclusiva do migrador.
- Sem Garage/S3. Volume Docker nomeado, isolado por `COMPOSE_PROJECT_NAME`.
- Permissões por papel continuam como estão (é a #159). `arquivos` segue
  compartilhada entre unidades (`docs/unidades.md:271`).

## O que construir

### 1. Configuração e volume

`gestaolegal/config.py:117-122`: trocar `STATIC_ROOT_DIR`, `UPLOADS` e
`ARQUIVOS_DIR` por `PRIVATE_FILES_ROOT` (env, padrão
`/data/gestaolegal/uploads`), com as categorias fixas `casos`, `eventos` e
`arquivos`. `MAX_CONTENT_LENGTH` passa a ser a fonte única de tamanho — remover
o `MAX_ARQUIVO_BYTES = 10 * 1024 * 1024` hardcoded em
`gestaolegal/services/caso_service.py:42`.

Em `configure_app` (`gestaolegal/__init__.py:38`), validar na subida: o
`realpath` da raiz não pode estar dentro de `app.static_folder`, e precisa ser
gravável. Falha explícita — nunca voltar a gravar em `static`.

- `docker-compose.yml`: volume nomeado `private_uploads` montado em
  `/data/gestaolegal/uploads` no serviço `api`.
- `docker-compose.qa.yml`: remover o bind do `static/arquivos` e montar o volume
  privado.
- `.env.example`: documentar `PRIVATE_FILES_ROOT` (hoje nem `STATIC_ROOT_DIR`
  está lá).
- `.dockerignore`: acrescentar `gestaolegal/static/casos`,
  `gestaolegal/static/eventos`, `gestaolegal/static/arquivos` e `dumps/`.

### 2. `gestaolegal/services/private_file_storage.py`

Módulo novo. A raiz vem de `current_app.config` — **não** capturar constante de
caminho no import, como fazem hoje `caso_service.py:41` e
`arquivo_service.py:18` (é o que obriga os testes a monkeypatch de módulo).

API: `save(categoria, file) -> ref`, `resolve(categoria, ref) -> path`,
`remove(categoria, ref)`.

- Nome gerado `<uuid4>_<secure_filename>`, extensão preservada, referência
  limitada a 300 caracteres. O UUID substitui o timestamp de segundos usado
  hoje em casos e eventos, que colide dentro do mesmo segundo.
- Recusa: categoria desconhecida, caminho absoluto, `..`, symlink que escapa,
  referência vazia. `realpath` confinado à raiz/categoria em toda leitura.
- Escrita em temporário dentro do volume + `os.replace` para publicar; criação
  exclusiva (`O_EXCL`), nunca sobrescrever; temporário removido em falha.
- Download responde com `Content-Disposition: attachment` e
  `Cache-Control: private, no-store`.

### 3. Os três fluxos

Nenhum `file.save`, `os.remove`, `os.makedirs` ou `os.path.exists` direto pode
sobrar em services e controllers.

**Arquivos de caso** — `caso_service.py:399-573`. Mantém a validação de PDF e a
checagem de unidade em `:417-419`. Corrigir `find_arquivo_by_id` (`:336`), hoje
sem validação de caso nem de unidade.

**Anexo de evento** — tirar o bloco de gravação de `caso_controller.py:274-287`
e `:361-374` e movê-lo para `EventoService`. O service valida caso, unidade e
dados **antes** de gravar (hoje grava e só depois checa, deixando órfão quando
o acesso é negado). Acrescentar validação de tipo e tamanho, que não existe. O
`PUT` passa a remover o anexo substituído — hoje ele vaza.
`EventoService.get_evento_file_for_download` (`evento_service.py:223-241`)
recusa evento com `status` falso.

**Arquivos gerais** — `arquivo_service.py:46-177`. Remover o fallback
`arquivo.caminho or os.path.join(ARQUIVOS_DIR, arquivo.nome)` (`:126`), que
concatena a coluna `Text` `nome`, sem `secure_filename`, num caminho de
filesystem. Os registros v2 sem `caminho` passam a ser resolvidos pelo migrador.

Ciclo de vida nos três: validar → gravar novo → confirmar transação → em falha,
remover o novo e manter o antigo → após commit, remover o anterior. Falha de
limpeza pós-commit vira log de reconciliação, não rollback simulado.

### 4. Migration e frontend

Migration com `down_revision = 'b7c1d2e3f4a5'` (head atual,
`migrations/versions/b7c1d2e3f4a5_unidades.py`): `eventos.arquivo` de
`String(100)` para `String(300)`. O `downgrade` confere o comprimento dos
valores e recusa a redução se houver incompatível. **A migration não move nem
reescreve arquivos.**

Front: `evento.arquivo.split('/').pop()` segue funcionando com a referência
relativa. Corrigir
`web/src/routes/(dashboard)/casos/[id]/+page.svelte:476`, que faz
`.split('_').pop()` e mutila nomes com underscore — retirar só o prefixo
gerado.

### 5. Bloqueio do caminho estático

`before_request` (ou blueprint dedicado) devolvendo 404 em GET/HEAD para
`/static/casos`, `/static/eventos`, `/static/arquivos` e descendentes, incluindo
formas normalizadas (`//`, `%2e%2e`, barra final). `static/imgs_daj` continua
servido.

`web/nginx.conf` não tem `location /static/`: os estáticos saem do próprio
Flask, na porta da API. Bloquear no nginx é complemento, não substituto.

### 6. `scripts/migrar_arquivos_privados.py`

Molde: `scripts/seed_local.py` (docstring de uso, `load_dotenv()`, config por
env, idempotência declarada, `sys.exit` com contagem de erros). Diferença: este
precisa de sessão SQLAlchemy — reusar `Config.SQLALCHEMY_DATABASE_URI` como faz
`migrations/env.py`. Três fases explícitas, reexecutável:

**Inventário (sem escrita).** Origens legadas e o mapeamento prefixo antigo →
mount de leitura vêm por parâmetro; não varrer disco nem confiar no caminho
gravado. Cobre registros ativos e inativos dos três grupos, inclusive `arquivos`
sem `caminho`. Classifica ausentes, caminhos externos, nomes repetidos,
referências compartilhadas e órfãos. Gera manifesto privado (origem, tabela/id,
referência anterior, destino, tamanho, SHA-256), **fora do git**.

**Aplicação (com escrita da API suspensa).** Backup do banco e das origens →
cópia para destino único no volume, conferindo tamanho e SHA-256 → atualização
da referência só depois da cópia verificada, checando que o valor anterior ainda
bate com o manifesto → progresso recuperável, validado contra o estado real do
banco na retomada.

**Verificação.** Confere todas as referências finais e resume migrados,
ausentes, exceções e quarentena. Não remove origens.

Referência compartilhada ganha destino separado por registro, para que excluir
um não apague o arquivo do outro.

## Como provar

Testes novos em `tests/api/`:

- `test_private_file_storage.py`: gravação/leitura/remoção, nome repetido, nome
  longo, caracteres especiais, categoria errada, caminho absoluto, `..`,
  symlink de escape, falha de gravação.
- Nos três fluxos: upload/download/substituição/exclusão; anônimo recusado;
  unidade errada recusada; arquivo inexistente; evento excluído não baixável; a
  resposta não expõe a raiz absoluta.
- Rollback do banco: o arquivo anterior segue disponível quando a transação não
  confirma; o novo nunca fica referenciado sem ter sido gravado.
- Bloqueio estático: criar um arquivo **de fato dentro de `app.static_folder`**
  e confirmar 404. Um 404 obtido porque a fixture usa outra pasta não prova
  nada. Manter um asset público sintético acessível, para detectar bloqueio
  excessivo.
- Migrador: caminho absoluto legado, `arquivos` sem `caminho`, nomes iguais em
  origens diferentes, referência compartilhada, arquivo ausente,
  interrupção/retomada, reexecução, checksum divergente.
- `tests/api/conftest.py:5,15` passa a definir `PRIVATE_FILES_ROOT` num tmpdir
  **separado** de `app.static_folder`; `tests/api/test_arquivo_api.py:13-18`
  deixa de precisar do `monkeypatch.setattr(arquivo_service, "ARQUIVOS_DIR", …)`.

Comandos: `make test`; se as telas mudarem,
`cd web && npm run check && npm run lint`.

Manual, na stack do canteiro: subir com o volume, enviar anexo nos três fluxos,
baixar autenticado, tentar a URL estática antiga (404), e rodar
`docker compose build && docker compose up -d` confirmando que os anexos
sobreviveram.

## Travas

- `review_required`: a migration de `eventos.arquivo`; as mudanças em
  `docker-compose.yml` e `docker-compose.qa.yml`; o bloqueio do caminho
  estático; o migrador.
- `human_gate`: qualquer execução do migrador contra banco de QA ou de
  produção, e o passo de quarentena das origens públicas. O loop escreve o
  script e seus testes; não roda contra dado real.
- `.dockerignore` e `.env.example` não são segredo e não são gate.
