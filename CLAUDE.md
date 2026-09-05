# Gestão Legal 3.0

Sistema da Divisão de Assistência Judiciária (DAJ) da Faculdade de Direito da
UFMG. API Flask (`gestaolegal/`) + front SvelteKit (`web/`) + MySQL, tudo em
Docker Compose. Conversa e documentação em português; nomes de tabelas e campos
legados ficam como estão.

## Verificação

- API: `make test` (equivale a `uv run pytest tests/api/ -v`). Roda no host, com
  banco SQLite em memória; não precisa da stack Docker.
- Front: `cd web && npm run check && npm run lint` (svelte-check + prettier).
- CI (`.github/workflows/build_image.yml`) roda `uv run pytest tests/` e só
  então publica as imagens. O que quebra no `make test` quebra o deploy.

## Armadilhas que quebram em silêncio

- `docker-compose.override.yml` é ignorado pelo git. Num checkout que não o
  tenha, a stack sobe com os alvos `prod` dos Dockerfiles: sem hot reload, e o
  front é servido pelo nginx, que faz proxy de `/api/` para o serviço `api`.
  Alteração no código só aparece depois de `docker compose build`.
- O Mailpit só existe no override. Sem ele, envio de e-mail falha em silêncio
  (é melhor esforço por desenho) e a recuperação de senha não tem como ser
  testada pela interface.
- Migrations: `alembic -c migrations/alembic.ini`. O serviço `migrate` do
  compose aplica `upgrade head` antes da API subir. Duas migrations criadas em
  paralelo geram dois heads; ver "Mudanças que exigem revisão humana".
- `Config` lê variáveis obrigatórias no import (`DB_USER`, `DB_HOST`,
  `JWT_SECRET_KEY`...). Sem `.env`, a API nem importa. Os testes preenchem via
  `tests/api/conftest.py`.
- `coluna_unidade()` (`gestaolegal/database/tables.py`) não tem `default`. Todo INSERT
  numa tabela com `unidade_id` precisa passar a unidade explicitamente — em service,
  em script e em fixture de teste —, senão estoura o NOT NULL. O default existiu na
  Fase A e foi removido para que o esquecimento apareça, em vez de gravar calado em
  Belo Horizonte um registro de outra unidade.
- Uploads vão para o volume privado `PRIVATE_FILES_ROOT` (padrão
  `/data/gestaolegal/uploads`), nas categorias `casos`, `eventos` e `arquivos`.
  A raiz é validada na subida do app: se estiver dentro de `app.static_folder`
  (ou contendo ela), a API não sobe. Registros herdados da 2.0 não têm
  `caminho`; o service resolve para a raiz da categoria + `nome`.
- Portas publicadas vêm de `APP_PORT`, `DB_PORT`, `WEB_PORT` e
  `MAILPIT_UI_PORT` (padrões 5000, 3306, 5001, 8025). Script que aponte para
  `localhost:5000` fixo fala com o checkout principal e não com um checkout
  paralelo; `scripts/seed_local.py` lê `APP_PORT` do `.env` do diretório atual
  por isso.
- Limitações já conhecidas e ainda abertas estão em `docs/known_issues.md`.
  Não são bugs a corrigir de passagem.

## Glossário

- **Atendido**: pessoa que procura a DAJ (cliente). **Assistido**: atendido que
  passou pela triagem socioeconômica e recebe assistência; `assistidos` estende
  `atendidos`.
- **Caso**: a demanda jurídica, com orientador, estagiário e colaborador.
  **Processo**: ação judicial vinculada a um caso. **Evento**: prazo, audiência
  ou compromisso do caso. **Histórico**: log de alterações do caso.
- **Orientação jurídica**: atendimento pontual, sem abrir caso.
- **Plantão**: período de atendimento com escala (`dias_plantao`,
  `dias_marcados_plantao`). **Fila de atendimento**: senha do dia.
  **Registro de entrada**: presença do estagiário.
- **Assistência judiciária**: parceiro externo (defensoria, núcleo conveniado).
- **Unidade**: local de atendimento da DAJ (Belo Horizonte, Nova Lima). Em
  implantação; modelagem em `docs/unidades.md`.
- Papéis (`urole`): `admin`, `prof` (professor), `orient` (orientador),
  `estag_direito` (estagiário), `colab_proj` (colaborador do projeto),
  `colab_ext` (colaborador externo).

## Mudanças que exigem revisão humana

A régua é o alcance do efeito: **uma mudança que só afeta este checkout se
desfaz com `git`; uma que sai daqui, não.** As duas listas abaixo separam o que
não deve ser alterado sem decisão explícita do que merece o olho de um revisor
antes de entrar no `master`.

### Não altere sem decisão explícita

1. **Efeito sobre terceiro, irreversível**: envio de e-mail real a atendidos ou
   usuários (o serviço `mail`/Postfix e qualquer `MAIL_RELAYHOST`), e qualquer
   script que leia ou escreva no banco de **produção** ou de **QA**
   (`docker-compose.qa.yml`, os dumps em `dumps/`). A importação dos bancos de
   Belo Horizonte e Nova Lima (`docs/unidades.md`, Fase B) roda contra dados
   reais de pessoas.
2. **Segredos e o que roda fora daqui**: `.env*` (exceto `.env.example` e
   `.env.worktree`), `.github/workflows/` (executa no push), credenciais do
   MySQL e do GHCR. `docker-compose*.yml` não entra: molda só a stack local.
3. **Enfraquecer a verificação**: remover ou afrouxar asserção em `tests/`,
   tirar passo do `make test` ou do workflow, mexer em hook. Tarefa cujo
   caminho mais curto é apagar asserção cai sempre aqui. **Estender** a
   verificação (teste novo, check a mais) não é o caso. Boa parte disto está
   travada mecanicamente no `deny` do `.claude/settings.json`.

### Revisar antes do merge

Migration em `migrations/versions/`, regras de permissão por `urole`, filtro por
unidade (`unidade_id`), contrato da API consumido pelo front
(`web/src/lib/types`, `api-client.ts`), `docker-compose*.yml`, e o que toca
dados pessoais de atendidos (CPF, endereço, renda).

Atenção especial a migrations: duas criadas em paralelo produzem dois heads de
Alembic, e dois heads derrubam produção sem que o portão de testes perceba —
os testes usam SQLite em memória e não rodam Alembic. Confira
`alembic -c migrations/alembic.ini heads` antes de abrir o PR.
