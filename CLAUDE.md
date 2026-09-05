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

- `docker-compose.override.yml` é ignorado pelo git. Na worktree de um canteiro
  ele não existe, então a stack sobe com os alvos `prod` dos Dockerfiles: sem
  hot reload, e o front é servido pelo nginx, que faz proxy de `/api/` para o
  serviço `api`. Alteração no código só aparece depois de `docker compose
  build`.
- O Mailpit só existe no override. Sem ele, envio de e-mail falha em silêncio
  (é melhor esforço por desenho) e a recuperação de senha não tem como ser
  testada pela interface.
- Migrations: `alembic -c migrations/alembic.ini`. O serviço `migrate` do
  compose aplica `upgrade head` antes da API subir. Dois canteiros criando
  migration em paralelo geram dois heads; ver "Human gates".
- `Config` lê variáveis obrigatórias no import (`DB_USER`, `DB_HOST`,
  `JWT_SECRET_KEY`...). Sem `.env`, a API nem importa. Os testes preenchem via
  `tests/api/conftest.py`.
- Uploads vão para `gestaolegal/static/casos` e `gestaolegal/static/arquivos`,
  fora do git. Registros herdados da 2.0 não têm `caminho`; o service resolve
  para `ARQUIVOS_DIR/nome`.
- Portas publicadas vêm de `APP_PORT`, `DB_PORT`, `WEB_PORT` e
  `MAILPIT_UI_PORT` (padrões 5000, 3306, 5001, 8025). Script que aponte para
  `localhost:5000` fixo fala com o checkout principal e não com a worktree;
  `scripts/seed_local.py` lê `APP_PORT` do `.env` do diretório atual por isso.
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

## Human gates

**A régua é o canteiro, não o arquivo.** A pergunta não é "este arquivo é
sensível?", é **"o efeito escapa da worktree?"**. Cada agente roda numa worktree
própria, com stack Compose e volume de banco próprios; o que acontece lá dentro
se desfaz com `git` e com `desmontar-canteiro.sh --volumes`. Barrar o que o
canteiro contém não protege nada: trava a empreitada cedo, e o `blocked_by_gate`
transitivo leva as dependentes junto.

Os campos do `prd.json` são dois:

- **`human_gate: true`**: o loop **não executa**. Só para o efeito que escapa.
- **`review_required: true`**: o loop **executa**, e a story aparece no índice
  do `desmontar-canteiro.sh` para o humano conferir antes do merge.

Teste concreto: *o estrago sobrevive a `desmontar-canteiro.sh --volumes` e a um
`git revert`?* Não sobrevive: `review_required`. **Na dúvida, é aí.**

### O que é gate (o efeito escapa)

1. **Efeito sobre terceiro, irreversível**: envio de e-mail real a atendidos ou
   usuários (o serviço `mail`/Postfix e qualquer `MAIL_RELAYHOST`), e qualquer
   script que leia ou escreva no banco de **produção** ou de **QA**
   (`docker-compose.qa.yml`, os dumps em `dumps/`). A importação dos bancos de
   Belo Horizonte e Nova Lima (`docs/unidades.md`, Fase B) é gate: roda contra
   dados reais de pessoas.
2. **Segredos e o que roda fora daqui**: `.env*` (exceto `.env.example` e
   `.env.worktree`), `.github/workflows/` (executa no push), credenciais do
   MySQL e do GHCR. `docker-compose*.yml` **não** entra: só molda a stack do
   próprio canteiro.
3. **Enfraquecer a maquinaria de verificação**: remover ou afrouxar asserção em
   `tests/`, tirar passo do `make test` ou do workflow, mexer em hook, em skill
   do loop ou em `scripts/helton/`. Tarefa cujo caminho mais curto é apagar
   asserção é sempre gate. **Estender** a verificação (teste novo, check a mais)
   não é gate. Boa parte disto está travada mecanicamente no `deny` do
   `.claude/settings.json`.

### O que NÃO é gate, e sim `review_required`

Migration em `migrations/versions/` (aplica-se ao banco do próprio canteiro, e o
arquivo é revertível), regras de permissão por `urole`, filtro por unidade
(`unidade_id`), contrato da API consumido pelo front (`web/src/lib/types`,
`api-client.ts`), `docker-compose*.yml`, e o que toca dados pessoais de
atendidos (CPF, endereço, renda) sem sair do canteiro. Tudo isso merece o olho
de um humano **no merge**, não merece parar a empreitada.

### O preço de destravar migration

Dois canteiros criando migration em paralelo produzem dois heads de Alembic, e
dois heads derrubam produção sem que o portão de testes perceba (os testes usam
SQLite em memória e não rodam Alembic). Quem resolve é o `/compatibilizar`,
pelo `creates_migration` do manifesto (plano-zero de schema, e os demais
`serialized_after`). **Sem manifesto, não monte dois canteiros que mexam em
schema.**

O outro preço é retrabalho: o loop constrói em cima do schema que ele mesmo
escreveu. Mitigação barata: manter a story de migration cedo no cronograma e
olhar só ela depois da primeira iteração vigiada.

Fora dessas listas, o padrão é `human_gate: false`.
