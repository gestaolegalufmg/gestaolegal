# Unidades de atendimento: modelagem e plano de unificação dos bancos

Documento de trabalho. Criado em 04/09/2026.

## 1. Contexto

A DAJ atende em dois locais, Belo Horizonte (BH) e Nova Lima (NL), e hoje cada um
roda uma instalação separada do Gestão Legal com banco próprio. A 3.0 não tem
nenhum conceito de tenant nem de filial. O objetivo é:

1. Criar a noção de **unidade** (filial) na 3.0.
2. Depois, unificar os dois bancos num só, mantendo cada registro marcado com a
   unidade de origem.

Não será modelado um nível de **tenant** (outra faculdade, com segregação
total). Para esse cenário a solução é uma instância/banco separado por
instituição, que é o que já existe hoje. Colocar `tenant_id` em todas as
tabelas traria risco de vazamento a cada query esquecida sem necessidade atual.

Ordem escolhida: estrutura primeiro, importação depois. Motivos:

- O script de importação vira "inserir com `unidade_id` = NL e remapear ids".
- A estrutura é validada com a base de BH sozinha antes de misturar dados.
- Os dumps continuam vivos; o import é repetível contra um dump novo no dia da
  virada.

## 2. Situação dos bancos (dumps de 04/09/2026)

| | BH | NL |
|---|---|---|
| usuários | 213 | 32 |
| atendidos | 3255 | 518 |
| casos | 606 | 297 |
| processos | 35 | 51 |
| eventos | 678 | 422 |
| orientações jurídicas | 1919 | 130 |
| fila de atendimento | 2825 | 741 |
| revisão Alembic | `060d870f00e1` (não existe no repositório) | `03085453841c` |

Colisões a tratar na importação:

- Todos os ids se sobrepõem (as duas bases começam do 1). São 35 FKs a remapear.
- 16 usuários existem nas duas bases com o mesmo e-mail (coluna `UNIQUE`).
- 3 atendidos existem nas duas bases com o mesmo CPF.
- Os arquivos físicos de casos e eventos não estão nos dumps; precisam ser
  copiados das duas instalações e os nomes podem colidir.
- O esquema de BH difere do de NL em detalhes: `processos.numero` é `bigint`
  em BH e `varchar(25)` em NL; BH tem FK `orientacao_juridica.id_usuario`;
  `registro_entrada` tem ordem de colunas e nulidade diferentes.

## 3. Decisões tomadas (04/09/2026)

| # | Questão | Decisão |
|---|---|---|
| 1 | Arquivos gerais (`arquivos`) | **Compartilhados** entre unidades, sem `unidade_id`. |
| 2 | Assistências judiciárias | **Por unidade**, recebem `unidade_id`. |
| 3 | Atendido vinculado a caso de outra unidade | **Permitido.** Atendido tem a unidade onde foi cadastrado e aparece só nessa listagem; o caso tem a dele e mostra o atendido normalmente. Os 3 CPFs repetidos viram um único cadastro. |
| 4 | Visão do admin | **Escolhe unidade ativa como todos.** Tem acesso a todas, navega com uma por vez. Uma única regra de filtro para todos os papéis. |

## 4. Modelagem

### 4.1 Tabela `unidades`

| coluna | tipo | obs |
|---|---|---|
| id | int PK autoincrement | |
| nome | varchar(60) unique | "Belo Horizonte", "Nova Lima" |
| sigla | varchar(10) unique | "BH", "NL"; usada em prefixo de arquivos e na UI |
| ativa | bool not null default true | permite desativar sem apagar |
| criado | datetime not null | |

Sem `unidade_pai_id`. Não há hierarquia entre unidades: a DAJ inteira é o
próprio banco. Se um dia for preciso agrupar unidades, a coluna entra depois
sem quebrar nada.

### 4.2 Tabela `usuarios_unidades`

| coluna | tipo |
|---|---|
| usuario_id | int FK usuarios.id |
| unidade_id | int FK unidades.id |

PK composta. Existe porque 16 pessoas já atuam nas duas unidades.

### 4.3 Entidades raiz: recebem `unidade_id` (int NOT NULL, FK unidades.id, indexada)

Critério: a entidade nasce num balcão físico e tem listagem própria no
sistema. Tudo que se lista "por unidade" precisa da coluna direto, para o
filtro não depender de JOIN.

| tabela | por que é raiz |
|---|---|
| atendidos | a pessoa é cadastrada no balcão de uma unidade |
| orientacao_juridica | atendimento feito na unidade, listado por unidade |
| casos | aberto na unidade, listado por unidade |
| eventos | tem agenda própria por unidade, além de pertencer ao caso |
| lembretes | listagem "meus lembretes" filtra por unidade ativa |
| fila_atendimentos | fila física do dia |
| registro_entrada | presença dos estagiários naquele local |
| plantao, dias_plantao, dias_marcados_plantao | escala é por local |
| assistencias_judiciarias | parceiros regionais (decisão 2) |

Eventos e lembretes têm caso pai, mas ganham a coluna mesmo assim porque são
listados fora do contexto do caso. Regra: `unidade_id` sempre igual ao do
caso, garantido pelo service; a migração de dados preenche a partir do caso.

### 4.4 Entidades filhas: herdam a unidade pelo pai (sem coluna)

| tabela filha | pai que define a unidade | caminho |
|---|---|---|
| assistidos | atendidos | `assistidos.id_atendido → atendidos.unidade_id` |
| assistidos_pessoa_juridica | assistidos → atendidos | dois saltos |
| enderecos | atendidos / usuarios / assistencias_judiciarias | endereço não tem dono fixo; herda de quem aponta para ele |
| atendido_xOrientacaoJuridica | orientacao_juridica | tabela de ligação |
| casos_atendidos | casos | tabela de ligação |
| processos | casos | sempre acessado via caso |
| arquivosCaso | casos | sempre via caso |
| arquivosEvento | eventos | sempre via evento |
| historicos | casos | sempre via caso |
| assistenciasJudiciarias_xOrientacao_juridica | orientacao_juridica | tabela de ligação |

Regra de integridade: o service nunca cria uma filha sem passar pelo pai, então
a filha nasce na unidade certa por construção. A checagem de acesso é feita no
pai: quem pode ver o caso pode ver seus processos, arquivos e histórico.

### 4.5 Entidades sem unidade

| tabela | motivo |
|---|---|
| usuarios | pertence a N unidades via `usuarios_unidades` |
| arquivos | biblioteca compartilhada (decisão 1) |
| notificacao | é da pessoa destinatária, não da unidade |
| password_reset_tokens | é da pessoa |
| documentos_roteiro | conteúdo institucional compartilhado |

### 4.6 Unidade ativa na sessão

A API é stateless (JWT + `RequestContext`). A unidade ativa vai em um header
`X-Unidade-Id` enviado pelo front em toda requisição:

1. O decorator de autenticação lê o header, confere em `usuarios_unidades` que
   o usuário tem acesso àquela unidade e grava em `RequestContext`. Header
   ausente ou unidade não permitida: 403.
2. Repositórios das raízes recebem a unidade ativa e aplicam o filtro
   obrigatoriamente. Não existe caminho de listagem sem unidade.
3. Criação de raízes usa a unidade ativa; criação de filhas copia do pai.
4. O login retorna a lista de unidades do usuário. O front guarda a escolhida
   (store + `localStorage`) e mostra um seletor no cabeçalho só para quem tem
   mais de uma. Trocar de unidade recarrega as listagens; não exige novo login.

## 5. Sequência de implementação

### Fase A: estrutura de unidades na 3.0 (base de BH) — **entregue em 04/09/2026**

1. Migração Alembic: cria `unidades`, insere BH e NL, cria `usuarios_unidades`,
   adiciona `unidade_id` nullable nas raízes com FK e índice.
2. Migração de dados no mesmo arquivo: `unidade_id` = BH em todas as raízes
   existentes; todos os usuários ganham linha em `usuarios_unidades` para BH.
   Depois altera `unidade_id` para NOT NULL.
3. `tables.py` e dataclasses em `models/`: `Unidade`, campo `unidade_id` nas
   raízes, `unidades` em `UserInfo`.
4. `RequestContext` + decorator de autenticação: header `X-Unidade-Id`,
   validação, 403.
5. Repositórios das raízes: filtro obrigatório por unidade em listagem, busca,
   contagem e relatórios. Services propagam unidade do caso para eventos e
   lembretes.
6. Endpoints: login devolve unidades; CRUD de unidades e de vínculo
   usuário-unidade para admin; formulário de usuário com as unidades.
7. Front: store de unidade ativa, header em `api-client.ts`, seletor no
   cabeçalho, campo de unidades no cadastro de usuário.
8. Testes: cada raiz filtrada; usuário em duas unidades; troca de unidade;
   header inválido; filha herdando do pai; atendido de BH em caso de NL.
9. Subir em QA e produção. Nada muda para o usuário de BH além do seletor
   (invisível para quem só tem uma unidade).

Os oito primeiros passos foram implementados na branch `helton/unidades`
(migration `b7c1d2e3f4a5_unidades`, API, front e 343 testes verdes). O passo 9
(subir em QA e produção) continua aberto: depende da pendência da revisão
`060d870f00e1` da base de BH. O que ficou diferente do planejado está em §5.1.

#### 5.1 Divergências em relação ao planejado

**Ordem.** A migration não foi escrita primeiro (passo 1), e sim depois de toda a
API (`f1-migration`, décima quarta story). O schema nasceu em
`gestaolegal/database/tables.py`, e os testes rodam em SQLite em memória via
`create_all`, sem Alembic — escrever a migration por último evitou reescrevê-la a
cada ajuste de coluna.

**`default` de unidade nas colunas.** O helper `coluna_unidade()` de `tables.py`
cria `unidade_id` NOT NULL indexada **com `default=UNIDADE_PADRAO_ID` (1)**. Isso
não estava no plano. Sem o default, 149 testes quebram enquanto os services ainda
não gravam a coluna, e todo `INSERT` cru (conftest, seed) precisaria da unidade.
Foi mantido depois da Fase 3 como rede de segurança; **não** substitui o filtro,
porque um registro criado na unidade 2 que caísse no default apareceria na
unidade 1 e os testes de isolamento acusariam.

**Onde mora o filtro.** O plano dizia "repositórios das raízes aplicam o filtro
obrigatoriamente" (§4.6, item 2). Na prática o filtro mora no **service**, que lê
`RequestContext.get_unidade_ativa()`; o repositório recebe um
`unidade_id: int | None = None` opcional. Motivo: o mesmo repositório serve a
vários services (`AtendidoRepository` é usado por caso e por orientação), e um
parâmetro obrigatório no repositório obrigaria a mudar todos de uma vez.
Exceção deliberada: **escrita destrutiva em massa** (`desativar_todos_dias`,
`desativar_todas_marcacoes`) recebe `unidade_id` **obrigatório** — parâmetro com
default aí faria a leitura da escala de uma unidade apagar a de outra.

**Header ausente responde 400, não 403.** O plano previa 403 para os dois casos
(§4.6, item 1). O decorator distingue: header ausente ou não numérico é
`ValidationException` → **400** ("Unidade ativa não informada"); unidade que o
usuário não possui é `ForbiddenException` → **403**. São erros diferentes — um é
cliente mal configurado, o outro é tentativa de acesso.

**Rotas isentas do header.** Três rotas usam `@authenticated(unidade=False)`
porque existem antes de haver unidade ativa: `GET /api/user/me`,
`GET /api/user/opcoes` e `GET /api/unidades/` (a que alimenta o seletor). As
rotas de `/api/auth/*` nunca passaram por `@authenticated`. Todo o resto exige o
header — inclusive as rotas `@authorized(...)`, que empilham `@authenticated`
internamente.

**Entidades filhas: guarda do pai.** Confirmado como no plano (§4.4), com um
detalhe: **evento e lembrete têm coluna própria e guarda do pai ao mesmo tempo**.
A unidade gravada é a do **caso** (`evento_data["unidade_id"] = caso.unidade_id`),
não a do header. A redundância é de propósito: o filtro segura registro herdado
da 2.0 que tenha caído no default errado, e a guarda do pai segura caso movido de
unidade no futuro.

**Tabela de ligação entre duas raízes.** `assistenciasJudiciarias_xOrientacao_juridica`
não está em nenhuma das listas do §4 e é o ponto cego do modelo: sem
`unidade_id`, ela seria caminho para ler dado de outra unidade. Regra adotada:
quem cria vínculo valida as **duas** pontas pela unidade ativa; quem lê vínculo
filtra pela entidade do outro lado do JOIN.

**Singletons que viraram por unidade.** O plantão deixou de ser configuração
global e virou **singleton por unidade**. A sequência de senhas da fila reinicia
por unidade (cada balcão começa em N01/P01/S01 no dia). O registro de entrada
também é por unidade: quem atende nos dois locais pode ter um ponto aberto em
cada um, e a saída em um não fecha o do outro.

**Vínculo usuário-unidade no cadastro.** `unidade_ids` é **obrigatório** no
`POST /api/user` (`min_length=1`) e opcional no `PUT` (ausente = não mexe; lista
vazia = recusado). `PUT /api/user/me` **descarta** o campo: o perfil próprio
compartilha o input model com a rota de admin, e sem o descarte qualquer usuário
se auto-vincularia a qualquer unidade. Admin não pode remover a própria última
unidade. O `create_admin` do setup inicial vincula o admin à unidade padrão se
ela existir — sem isso o primeiro admin nasceria sem unidade e o sistema ficaria
inutilizável logo após o setup.

**Front.** Como planejado (§4.6, item 4), mais uma tela não prevista: **`/unidades`,
CRUD de unidades só para admin**, necessária porque a `f4-unidade-controller`
criou os endpoints e não havia interface para eles. A store é
`web/src/lib/stores/unidade.ts` (localStorage `unidade_ativa`) e o `apiFetch`
manda o header a partir dela; trocar de unidade dispara `invalidateAll()`.

**O que ficou adiado.**

- **Verificação em navegador de todas as telas da Fase 5.** O plugin browser-use
  não rodou nesta máquina (`permission-blocked` e, depois, binário ausente). Em
  substituição, cada story exercitou o payload exato da tela contra a API da
  worktree e conferiu o bundle servido pelo nginx. Login → dashboard → seletor →
  formulário de usuário → tela de unidades ainda precisam de um olho humano.
- **Filtro por unidade na listagem de usuários.** `UsuarioService.search` não
  filtra por `usuarios_unidades`: o admin continua vendo todo mundo. É decisão de
  produto, não esquecimento.
- **Rota `/api/caso/<id>/processos`.** Chama `ProcessoService.search_by_caso` sem
  passar pelo `CasoService`, então não checa a unidade do caso pai. As demais
  filhas de caso (arquivos, histórico) passam pela guarda.
- **Reativar unidade pela interface.** `GET /api/unidades/` devolve só as ativas,
  então desativar pela tela faz a unidade sumir da lista; hoje só se reativa pelo
  banco. O caminho seria um `?incluir_inativas=1` no controller.
- **`notificacao` e `arquivos`** seguem sem filtro, conforme as decisões 1 e 5.

### Fase B: script de importação de Nova Lima

1. Restaurar o dump de NL num banco temporário e rodar as migrações da 3.0
   até a revisão da Fase A (o dump já está numa revisão conhecida).
2. Script Python (`scripts/importar_unidade.py`) que lê do banco temporário e
   escreve no banco final:
   - ordem topológica das tabelas (enderecos → usuarios → atendidos → ...);
   - tabela de remapeamento `{tabela: {id_antigo: id_novo}}` aplicada nas 35 FKs;
   - `unidade_id` = NL em todas as raízes;
   - usuários: se o e-mail já existe, não insere; remapeia o id para o
     existente e acrescenta linha em `usuarios_unidades` para NL;
   - atendidos: se o CPF já existe, não insere; remapeia para o existente
     (decisão 3);
   - `assistidos`, `enderecos` e demais filhas seguem o remapeamento do pai;
   - `notificacao` e `password_reset_tokens`: remapeia usuários e importa;
   - `alembic_version`: ignora.
3. Arquivos físicos: copiar de NL para o servidor final com prefixo `NL_` e
   ajustar `caminho`/`nome` nos registros de `arquivosCaso` e `arquivosEvento`.
4. Validação: contagem por tabela e por unidade contra o dump; amostra de
   casos de NL abertos no sistema; login de um usuário que existe nas duas
   unidades.
5. Ensaio completo em QA com o dump atual. Virada em produção com dump novo.

### Fase C: dump de BH

A base de BH será a própria base da 3.0 após a Fase A, então não há
importação de BH. Fica pendente apenas alinhar a revisão `060d870f00e1`
(desconhecida) com a cadeia do repositório antes de rodar a migração da Fase A
em produção.

## 6. Pendências

- [ ] Descobrir o que a revisão `060d870f00e1` do banco de BH alterou e
      registrar a migração correspondente (ou carimbar a revisão equivalente).
- [x] Confirmar se os relatórios (horários, casos, etc.) filtram por unidade
      ativa ou se algum precisa consolidar as duas. **Todos filtram pela unidade
      ativa** (as cinco consultas de `RelatorioRepository`). Não há relatório
      consolidado das duas unidades; se for preciso, é story nova.
- [ ] Conferir em navegador as telas da Fase 5 (seletor no cabeçalho, unidades no
      formulário de usuário, tela `/unidades`) — ver "O que ficou adiado" em §5.1.
- [ ] Decidir se a listagem de usuários do admin passa a filtrar por
      `usuarios_unidades`.
- [ ] Aplicar a guarda da unidade do caso em `/api/caso/<id>/processos`.
- [ ] Permitir reativar unidade pela interface (`?incluir_inativas=1` na listagem).
- [ ] Reavaliar o `default=UNIDADE_PADRAO_ID` de `coluna_unidade()` agora que todos
      os services gravam a unidade explicitamente.
