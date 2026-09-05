# Plano: unidades de atendimento (Fase A)

Plano para o loop Helton. Criado em 04/09/2026 a partir de `docs/unidades.md`,
que é a spec: contexto, decisões tomadas e modelagem. Este arquivo só diz **o
que construir, onde e como provar**. Em caso de dúvida sobre "por quê", leia a
spec.

Escopo desta fatia: **só a Fase A** da spec. A importação de Nova Lima (Fase B)
é outro plano, a ser escrito depois que esta fatia estiver no `master`, porque
depende do código que sai daqui.

## Resultado esperado

Com esta fatia mesclada, a base de Belo Horizonte continua funcionando
exatamente como hoje, mas:

1. existe a tabela `unidades` com BH e NL, e `usuarios_unidades` (N:N);
2. atendidos, casos, orientações, eventos, lembretes, fila, plantão, presença e
   assistências judiciárias têm `unidade_id` NOT NULL;
3. toda requisição autenticada declara a unidade ativa no header
   `X-Unidade-Id`; a API recusa header ausente ou unidade não permitida;
4. toda listagem, busca, contagem e relatório dessas entidades filtra pela
   unidade ativa;
5. o front guarda a unidade ativa, manda o header e mostra um seletor no
   cabeçalho só para quem tem mais de uma unidade;
6. o admin cadastra unidades e vincula usuários a elas.

## Decisões já tomadas (não reabrir)

Ver `docs/unidades.md`, seção 3. Resumo:

- `arquivos` (biblioteca geral) é compartilhado: **sem** `unidade_id`.
- `assistencias_judiciarias` é por unidade.
- Atendido tem a unidade onde foi cadastrado e aparece só nessa listagem, mas
  pode ser vinculado a caso de qualquer unidade.
- Admin escolhe unidade ativa como todo mundo. Não existe modo "todas".
- Sem hierarquia entre unidades (sem `unidade_pai_id`).
- Sem tenant. Uma instância por instituição.

## Premissas verificadas na base (04/09/2026)

- Tabelas definidas com `Table()` em `gestaolegal/database/tables.py`
  (`usuarios` na linha 31, `atendidos` 69, `orientacao_juridica` 129, `casos`
  154, `eventos` 205, `assistencias_judiciarias` 263, `lembretes` 294,
  `fila_atendimentos` 327, `dias_plantao` 343, `plantao` 352,
  `dias_marcados_plantao` 360, `registro_entrada` 372).
- Modelos são dataclasses em `gestaolegal/models/` (`Atendido`, `Caso`,
  `User`/`UserInfo` etc.), convertidos por `from_dict` em
  `gestaolegal/utils/dataclass_utils.py`.
- Repositórios herdam de `BaseRepository`
  (`gestaolegal/repositories/repository.py`), com `search`, `find_one`,
  `count` recebendo `where` em `WhereClause`/`ComplexWhereClause`. Exemplo:
  `gestaolegal/repositories/caso_repository.py`.
- Autenticação: `@authenticated` em `gestaolegal/utils/api_decorators.py:21`
  lê o JWT, carrega o usuário e grava em `RequestContext`
  (`gestaolegal/utils/request_context.py`). `@authorized(*roles)` checa papel.
- Login em `gestaolegal/controllers/auth_controller.py:24` devolve
  `{"token", "user"}`. Token em `gestaolegal/utils/jwt_auth.py`.
- Front: `web/src/lib/api-client.ts` monta todo request em `apiFetch`
  (header `Authorization` na linha ~48). Layout autenticado em
  `web/src/routes/(dashboard)/+layout.svelte`, com `+layout.ts` chamando
  `user/me`. Cabeçalho tem busca e `NotificacaoBell`.
- Testes: `tests/api/conftest.py` cria o schema com `metadata.create_all` em
  SQLite em memória (linha 85) e insere admin por SQL cru em
  `ensure_admin_user_exists` (linha 112) e `criar_usuario` (linha 311).
  Fixtures de headers: `auth_headers`, `non_admin_auth_headers`,
  `prof_auth_headers`, `estagiario_auth_headers`, `headers_para`.
- Última migration: `migrations/versions/99b46509b0e1_password_reset_tokens.py`
  (head atual: `99b46509b0e1`). Padrão do arquivo serve de molde.
- Alembic roda contra MySQL 8; os testes não rodam Alembic.

## Fases

### F1. Schema e migration

**F1.1 `tables.py`**: adicionar `unidades` (id, nome varchar(60) unique, sigla
varchar(10) unique, ativa bool not null default true, criado datetime not
null) e `usuarios_unidades` (usuario_id FK usuarios.id, unidade_id FK
unidades.id, PK composta). Adicionar `Column("unidade_id", Integer,
ForeignKey("unidades.id"), nullable=False, index=True)` em: `atendidos`,
`orientacao_juridica`, `casos`, `eventos`, `lembretes`, `fila_atendimentos`,
`dias_plantao`, `plantao`, `dias_marcados_plantao`, `registro_entrada`,
`assistencias_judiciarias`.

**F1.2 migration** `migrations/versions/<rev>_unidades.py`, `down_revision =
"99b46509b0e1"`, em quatro passos dentro do mesmo `upgrade()`:

1. `create_table unidades`; `op.bulk_insert` com `(1, "Belo Horizonte", "BH")`
   e `(2, "Nova Lima", "NL")`, `ativa=True`, `criado=now`.
2. `create_table usuarios_unidades`; `INSERT ... SELECT id, 1 FROM usuarios`
   (todo usuário existente pertence a BH).
3. Para cada tabela raiz: `add_column unidade_id nullable=True`; `UPDATE ...
   SET unidade_id = 1`; `alter_column nullable=False`; `create_foreign_key`;
   `create_index`.
4. `downgrade()` desfaz na ordem inversa. Deve rodar de ponta a ponta.

Aceite: `docker compose run --rm migrate` aplica sem erro num banco com dados
(o canteiro sobe com banco vazio; testar também `alembic downgrade -1` e
`upgrade head` de novo). `review_required` (migration).

**F1.3 conftest**: `ensure_admin_user_exists` e `criar_usuario` passam a
inserir também em `usuarios_unidades` (unidade 1). Adicionar fixture
`unidades` que garante as linhas 1 (BH) e 2 (NL) em `unidades` antes de
qualquer teste, e fixture `auth_headers_nl` (admin com header da unidade 2).
Os headers de todas as fixtures existentes passam a incluir `X-Unidade-Id: 1`.
Aceite: `make test` continua verde **antes** de F2 (o filtro ainda não existe,
mas as colunas NOT NULL já existem no SQLite, então todo `INSERT` de teste
precisa de `unidade_id`; os services de F2 é que vão preencher).

> Ordem sugerida: F1.1 → F1.3 → F2 → F1.2 por último, porque a migration é o
> que mais pode divergir do `tables.py` e é melhor escrevê-la com o modelo
> fechado.

### F2. Unidade ativa na requisição

**F2.1 `RequestContext`**: novo `ContextVar` `_unidade_ativa: int | None`,
com `set_unidade_ativa`, `get_unidade_ativa` (levanta `RuntimeError` se
ausente, como `get_current_user`) e `clear` zerando os dois.

**F2.2 modelo e repositório de unidade**: `gestaolegal/models/unidade.py`
(dataclass `Unidade`), `gestaolegal/repositories/unidade_repository.py`
(`find_by_id`, `list_ativas`, `create`, `update`, `unidades_do_usuario(usuario_id)
-> list[Unidade]`, `vincular(usuario_id, unidade_ids)` que apaga e reinsere,
`usuario_pertence(usuario_id, unidade_id) -> bool`).

**F2.3 `UserInfo.unidades`**: `UserInfo` ganha `unidades: list[Unidade]`
(default `[]`), preenchida em `UsuarioService.find_by_id` e `find_by_email`.
`User.to_info` continua funcionando. O `user/me` e o `auth/login` passam a
devolver `unidades` no `user`.

**F2.4 decorator**: em `@authenticated`, depois de `set_current_user`: ler
`X-Unidade-Id`; ausente ou não numérico → 400 com mensagem "Unidade ativa não
informada"; número que não está em `user.unidades` → 403. Caso ok,
`set_unidade_ativa`. Rotas que **não** exigem unidade: `auth/*`,
`user/me` (GET), `user/opcoes`, `unidades` (listagem para o seletor). Fazer
isso com um parâmetro do decorator (`@authenticated(unidade=False)`) ou um
decorator irmão, sem duplicar a leitura do token.

**F2.5 testes**: `tests/api/test_unidade_auth.py`: sem header → 400; header
de unidade a que o usuário não pertence → 403; header válido → 200; `user/me`
sem header → 200 e traz `unidades`.

### F3. Filtro por unidade nas raízes

Para cada service/repositório abaixo, **toda** consulta que devolve lista,
página, contagem, opções ou item por id passa a exigir a unidade ativa
(`RequestContext.get_unidade_ativa()`), e toda criação grava `unidade_id`.
Item por id de outra unidade → 404 (não vazar existência).

| service | o que muda | teste |
|---|---|---|
| `atendido_service.py` (`search` 54, `create` 120, `create_assistido` 157) | filtro + gravação; assistido herda (não tem coluna) | `test_atendido_api.py` |
| `caso_service.py` (`search` 71, `create` 160) | filtro + gravação; `link_atendidos` **não** filtra por unidade (decisão 3) | `test_caso_api.py` |
| `orientacao_juridica_service.py` (`search` 87, `create` 209) | filtro + gravação | `test_orientacao_api.py` |
| `evento_service.py` (`create` 110) | `unidade_id` copiado do caso, não do header; listagem de agenda filtra | `test_evento_api.py` |
| `lembrete_service.py` (`create` 71) | idem evento | novo `test_lembrete_api.py` se não houver |
| `fila_atendimento_service.py` | filtro + gravação | `test_fila_atendimento_api.py` |
| `plantao_service.py` | `plantao`, `dias_plantao`, `dias_marcados_plantao` por unidade; o encerramento automático (`_encerrar_se_expirado`) só encerra a unidade ativa | `test_plantao_api.py` |
| `presenca_service.py` (`listar_para_confirmacao` 99) | `registro_entrada` por unidade | `test_presenca_api.py` |
| `assistencia_judiciaria_service.py` (`search` 86, `create` 163) | filtro + gravação | novo teste |
| `relatorio_service.py` / `relatorio_repository.py` | as cinco consultas recebem `unidade_id` | `test_relatorio_api.py` |
| `controllers/search_controller.py` (`global_search` 20) | herda o filtro dos services; confirmar com teste | `test_search` novo |
| `notificacao_service.py` | **sem** filtro (é da pessoa) | nenhum |
| `arquivo_service.py` | **sem** filtro (decisão 1) | nenhum |

Padrão de teste para cada tabela: criar um registro com header da unidade 1 e
outro com header da unidade 2 (fixture `auth_headers_nl`); listar com cada
header e ver só o seu; buscar por id o da outra unidade e receber 404.

Caso especial (decisão 3), em `test_caso_api.py`: atendido criado na unidade 1
pode ser vinculado a caso criado na unidade 2; o caso da unidade 2 lista o
atendido; a listagem de atendidos da unidade 2 **não** o mostra.

`review_required` em toda story desta fase (filtro por unidade, ver `CLAUDE.md`).

### F4. Endpoints de unidade e vínculo

**F4.1** `gestaolegal/controllers/unidade_controller.py`, blueprint
`/api/unidades`:

- `GET /` (autenticado, sem exigir header): unidades ativas. É o que o seletor
  usa.
- `POST /`, `PUT /<id>` (admin): nome, sigla, ativa.
- Registrar no `gestaolegal/controllers/__init__.py` como os demais.

**F4.2** usuário: `UserCreateInput`/`UserUpdateInput`
(`gestaolegal/models/user_input.py`) ganham `unidade_ids: list[int]`
(obrigatório, mínimo 1 no create). `UsuarioService.create` (138) e `update`
(175) chamam `vincular`. `GET /user/<id>` devolve `unidades`. Admin não pode
remover a própria última unidade.

**F4.3** testes em `test_user_api.py` e novo `test_unidade_api.py`.

### F5. Front

**F5.1** `web/src/lib/types/unidade.ts` (`Unidade`), `User.unidades` em
`web/src/lib/types/user.ts`, export em `index.ts`.

**F5.2** store `web/src/lib/stores/unidade.ts`: unidade ativa (id) com
persistência em `localStorage` (chave `unidade_ativa`), inicializada a partir
de `user.unidades` no `+layout.ts`: se a guardada não está na lista, usa a
primeira. `apiFetch` em `api-client.ts` manda `X-Unidade-Id` sempre que houver
valor.

**F5.3** login (`web/src/routes/login/+page.svelte`, após gravar o cookie):
define a unidade ativa como a primeira de `user.unidades`.

**F5.4** seletor no cabeçalho de `(dashboard)/+layout.svelte`, entre a busca e
o sino: componente `web/src/lib/components/unidade-selector.svelte`. Aparece
só se `user.unidades.length > 1`; com uma só, mostra a sigla como texto.
Trocar → atualiza a store e `invalidateAll()`.

**F5.5** formulário de usuário (`web/src/lib/forms/user-form.svelte`; o schema
zod dele não está em `forms/schemas/`, procurar no próprio componente ou na
rota): campo de múltipla escolha "Unidades",
obrigatório. Tela de detalhe do usuário mostra as unidades.

**F5.6** tela de unidades para admin: `web/src/routes/(dashboard)/unidades/`
(listar, criar, editar). Item de menu "Unidades" em `app-sidebar.svelte`,
`roles: ['admin']`.

Aceite de F5: `cd web && npm run check && npm run lint` verdes, e verificação
no browser na porta desta worktree: login com admin (que pertence a BH e NL
pelo seed), trocar de unidade, criar um atendido em cada, ver cada listagem
mostrar só o seu.

### F6. Seed e fechamento

**F6.1** `scripts/seed_local.py`: ler `APP_PORT` do ambiente (padrão 5000),
enviar `X-Unidade-Id`, vincular o admin às duas unidades, criar pelo menos um
atendido e um caso em cada unidade. Tornar idempotente para atendidos (buscar
por CPF antes de criar). Depois disso, preencher `SEED_CMD` no
`scripts/helton/obra/obra.conf` — **não** nesta fatia: `scripts/helton/` é
gate; deixar a instrução no `progress.txt`.

**F6.2** `docs/unidades.md`: marcar a Fase A como entregue e anotar o que
ficou diferente do planejado.

## Verificação

- Backend: `make test`.
- Front: `cd web && npm run check && npm run lint`.
- Migration: `docker compose run --rm migrate` no canteiro, e depois
  `docker compose run --rm migrate alembic -c migrations/alembic.ini downgrade -1`
  seguido de `upgrade head`.
- Browser: porta do front desta worktree (ver `.env` gerado, `WEB_PORT`).

## Armadilhas desta fatia

- SQLite dos testes cria o schema pelo `metadata`, então toda coluna nova NOT
  NULL quebra os `INSERT`s crus do `conftest.py` até serem atualizados. Fazer
  F1.3 junto com F1.1.
- `from_dict` ignora chaves que a dataclass não tem, mas **não** tolera campo
  obrigatório ausente. `unidade_id` novo nas dataclasses precisa de default
  `None` ou de ser preenchido em todo `create`.
- `JWTAuth.get_user_from_token` recarrega o usuário a cada request via
  `UsuarioService.find_by_id`. Carregar `unidades` ali é uma query a mais por
  request; aceitável, mas fazer em uma consulta (JOIN), não N.
- O front em modo `prod` no canteiro é servido pelo nginx e só reflete mudança
  após `docker compose build web`.
- `page.url`/`invalidateAll` no SvelteKit: trocar de unidade sem invalidar
  deixa listagens da unidade anterior na tela.
- Não tocar em `docs/known_issues.md` nem nos problemas que ele descreve
  (plantão encerrado some do relatório etc.).

## Human gates

- Nenhuma story desta fatia é `human_gate: true`: tudo acontece dentro do
  canteiro.
- `review_required: true` em: migration (F1.2), todo filtro por unidade (F3),
  decorator de autenticação (F2.4), contrato de API que o front consome (F2.3,
  F4).
- Editar `scripts/helton/obra/obra.conf` é gate por regra do `CLAUDE.md`.
  F6.1 só deixa a instrução.

## Fora desta fatia

- Importação de Nova Lima (Fase B da spec): plano próprio, depois do merge.
- Alinhar a revisão Alembic `060d870f00e1` do banco de BH (Fase C da spec):
  tarefa humana antes do deploy, fora do loop.
- Relatórios consolidados entre unidades (pendência da spec, seção 6).
- `unidade_id` em `arquivos`, `notificacao`, `documentos_roteiro`.
