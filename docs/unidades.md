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

### Fase A: estrutura de unidades na 3.0 (base de BH)

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
- [ ] Confirmar se os relatórios (horários, casos, etc.) filtram por unidade
      ativa ou se algum precisa consolidar as duas.
