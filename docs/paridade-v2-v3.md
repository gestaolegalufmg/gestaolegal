# Paridade 2.0 → 3.0: análise, plano e roteiro de testes

Documento de trabalho da migração de funcionalidades da versão 2.0 (tag `v2.0.2`,
Flask + Jinja) para a 3.0 (API Flask + SvelteKit). Atualizado em 02/09/2026.

## 1. Diferenças entre as versões

### 1.1 O que a 2.0 tem e a 3.0 não tem

Módulos inteiros removidos (as tabelas `arquivos` e `notificacao` continuam
existindo no banco com o esquema da 2.0; só o código foi removido):

| # | Funcionalidade 2.0 | Detalhes | Fase |
|---|---|---|---|
| 1 | **Notificações** (tabela `notificacao`) | Geradas em: cadastro de caso (avisa orientador, estagiário e colaborador), novo evento, novo lembrete e abertura do plantão (avisa todos orientadores e estagiários). Tela paginada com link para o destino. Orientadores e estagiários viam também as de broadcast (`id_usu_notificar` nulo). | 3 |
| 2 | **Arquivos gerais** (tabela `arquivos`) | Título, descrição e arquivo. Listar/cadastrar/editar/visualizar/excluir. Acesso: admin, professor, colab. projeto, colab. externo. | 2 |
| 3 | **Recuperação de senha por e-mail** | Token com expiração via Flask-Mail; rotas `esqueci-a-senha` e `resetar-a-senha/<token>`. `.env` da 3.0 tem `MAIL_*` comentado. Coluna `chave_recuperacao` já existe em `usuarios`. | 4 |
| 4 | **Termos de uso** | Página estática (termos, privacidade LGPD, cookies). | 1 ✅ |
| 5 | **Relatório de horários** | Presenças (`registro_entrada`) + plantões (`dias_marcados_plantao`) por período e usuários. Os outros 3 relatórios já existiam na 3.0. `relatorio_plantao`/`relatorio_casos` da 2.0 eram stubs quebrados. | 1 ✅ |

Ações pontuais ausentes em módulos existentes:

| # | Ação | Fase |
|---|---|---|
| 6 | Excluir evento (soft delete; admin ou criador; apaga anexo) | 1 ✅ |
| 7 | Substituir arquivo de caso (o de evento já existia via edição) | 1 ✅ |
| 8 | Filtro de eventos por tipo | 1 ✅ |
| 9 | "Meus Casos" no menu + filtro "Cadastrado por mim" | 1 ✅ |
| 10 | Atalhos da home (2.0: Meus Casos, Plantão, Notificações, Relatórios, Arquivos) | 5 |

A verificar: 2.0 tinha tabela `assistidos_pessoa_juridica`; a 3.0 absorveu em
`assistidos` (coluna `cnpj`). Não conferido campo a campo.

Já coberto pela 3.0: fila, busca geral, histórico, lembretes, processos,
roteiros, presença, escala, assistências judiciárias + encaminhar, atendidos,
orientações, usuários (inativar, senha), deferimento.

### 1.2 Presença (Registro e Confirmar) — comparação detalhada

Funcionalidades idênticas. Melhorias da 3.0: regra da segunda-feira corrigida
(2.0 testava `weekday() != 1`, terça); filtro "aberto" sempre aplicado; fuso de
Brasília consistente; fechamento de registro esquecido compara a data inteira;
após salvar permanece na data; exige seleção antes de salvar; seletor não aceita
datas futuras; só usuários e marcações ativos.

### 1.3 Wiki vs. código (resumo)

- **Manual de Instalação**: obsoleto por completo (script de instalação,
  `docker-compose.prod.yml`, containers `app_gl`/`db_gl`/Adminer, `make run`,
  `flask db`, `flask create-admin`). README está correto. README linka página
  "Arquitetura" inexistente.
- **Manual do Sistema**: §2.3 (associar OJ), §4.4 (excluir evento — agora existe
  de novo), §5 (notificações), §9 (arquivos) descrevem coisas ausentes.
  Rótulos: "Página do plantão"→"Escala do Plantão", "Excluir"→"Desativar",
  "Gerenciar Roteiros"→"Links de Roteiro". Faltam: fila, assistências
  judiciárias, relatórios, busca, processos, lembretes, histórico, setup-admin.
- **Permissões de Usuários** (detalhada): diverge do código em quase tudo. A
  página "(2025)" bate com o código, exceto "excluir evento". Tornar oficial.
- Código: roteiros e relatórios = admin, orient, colab_ext (wiki dizia prof).
  Só admin exclui. Só admin vê usuários.

## 2. Plano

1. **Fase 1** — ganhos rápidos sem migração (itens 5–9). **Concluída e aprovada em 03/09/2026 (PR #375).**
2. **Fase 2** — Arquivos gerais. **Implementada em 03/09/2026 na branch
   `feat/fase2-arquivos-gerais`; roteiro aprovado em 03/09/2026.**
3. **Fase 3** — Notificações, só dentro do sistema (decisão de 03/09/2026).
   **Implementada em 03/09/2026 na branch `feat/fase3-notificacoes` (a partir
   da fase 2); em teste (seção 8).**
4. **Fase 4** — Recuperação de senha: serviço de e-mail, token PyJWT com
   expiração, endpoints públicos em auth, páginas e link no login. SMTP:
   não há servidor do projeto; replicar a estrutura de `/opt/sanfili`
   (Mailpit em desenvolvimento, `boky/postfix` como relay em produção,
   configurado por `MAIL_HOST`/`MAIL_PORT`/`MAIL_FROM`). Decisão de 03/09/2026.
5. **Fase 5** — PJ, atalhos da home, atualizar a wiki.

Decisões tomadas em 03/09/2026: notificações só no sistema por enquanto (e-mail
fica para depois da fase 4); SMTP via container Postfix como em `/opt/sanfili`;
termos reaproveitados da 2.0.

## 3. Fase 1 — o que foi implementado (branch `feat/fase1-paridade-v2`)

Backend:
- `DELETE /api/caso/<id>/eventos/<evento_id>` — admin ou criador; 403 caso
  contrário; soft delete + remove anexo. Listagem esconde `status=False`.
- `GET /api/caso/<id>/eventos?tipo=` — filtro ("todos" = sem filtro).
  `ListEvento` ganhou `id_criado_por` e `descricao` (a descrição nunca era
  enviada — bug pré-existente).
- `PUT /api/caso/<id>/arquivos/<arquivo_id>` (multipart) — substitui PDF;
  validação extraída para `_validar_pdf`/`_salvar_pdf` em `caso_service`.
- `GET /api/caso/?criado_por=me|<id>` — combinável com `user=`.
- `GET /api/relatorio/horarios?data_inicio&data_final&usuarios=1,2` (papéis:
  admin, orient, colab_ext).
- `GET /api/user/opcoes` — usuários ativos (id, nome, urole) em ordem
  alfabética, para qualquer autenticado. Corrige bug pré-existente da 3.0
  encontrado no teste 4: novo caso, editar caso e diálogo de lembrete
  carregavam `GET /api/user` (só admin), então não-admins recebiam erro ao
  abrir essas telas. Também usado no relatório de horários.
- Mensagens de permissão padronizadas (03/09): o decorator `authorized`
  devolve JSON com "Você não tem permissão para executar esta ação. Contate o
  administrador." (antes era texto puro "Forbidden", que quebrava o parse no
  cliente). No web, `mensagemDeErro(err, padrão)` em `$lib/utils/erros.ts`
  mostra a mensagem do backend em todos os toasts de erro; páginas com
  bloqueio próprio (usuários, plantão, relatórios) terminam com "Contate o
  administrador.".
- Erros HTTP do Werkzeug traduzidos (404, 405, 413 "O arquivo excede o tamanho
  máximo de 10 MB", 415) em `utils/error_handlers.py`.

Frontend:
- Página do caso: seletor de tipo de evento, lixeira por evento (regra
  admin/criador), botão substituir arquivo por anexo, colunas da tabela de
  eventos com larguras ajustadas (`previewClass` novo no DataTable).
- `EventoDialog` com `bind:open` (botão Novo Evento não reabria após fechar).
- `TIPO_EVENTO_OPTIONS` em ordem alfabética ("Outros" por último).
- Detalhe do evento: botão Excluir.
- Lista de casos: checkbox "Cadastrados por mim"; título "Meus Casos" quando
  `user=me`. Sidebar: item "Meus Casos" (`/casos?user=me`), link "Termos de
  uso" no rodapé. Página `/termos-de-uso`. Breadcrumb.
- Relatórios: 4ª opção "Horário de chegada e saída dos usuários" com seleção de
  usuários, duas tabelas e CSV.

Testes: 216 passam (20 novos: `test_evento_api.py`, `test_caso_api.py`,
`test_relatorio_api.py`). `svelte-check`: 21 erros, todos pré-existentes em
arquivos não tocados. Build OK.

## 3b. Fase 2 — Arquivos gerais (branch `feat/fase2-arquivos-gerais`)

Regras iguais às da 2.0: todo usuário logado lista, visualiza e baixa; admin,
professor, colab. de projeto e colab. externo cadastram e editam; colab.
externo não exclui. Qualquer tipo de arquivo, até 10 MB.

Backend:
- A tabela `arquivos` da 2.0 (titulo, descricao, nome) nunca foi removida.
  Migração `4e1eb1a09578` acrescenta `caminho`, `data_criacao` e
  `id_criado_por` (nulos em registros herdados; o serviço resolve o caminho
  deles como `ARQUIVOS_DIR/nome`). `Config.ARQUIVOS_DIR = STATIC_ROOT_DIR/arquivos`.
- `gestaolegal/{models,repositories,services,controllers}/arquivo*.py`.
  Rotas em `/api/arquivo`: `GET /?search&page&per_page` (lista com
  `criado_por`, mais recentes primeiro), `GET /<id>`, `POST /` (multipart:
  titulo, descricao, arquivo), `PUT /<id>` (multipart; arquivo opcional,
  substitui e apaga o antigo), `DELETE /<id>` (apaga do disco),
  `GET /<id>/download` (nome original).
- 17 testes em `tests/api/test_arquivo_api.py` (236 no total).

Frontend:
- Sidebar: "Arquivos" (ícone pasta) com "Cadastrar Arquivo" (só papéis que
  editam) e "Ver Arquivos". Breadcrumbs.
- `/arquivos` lista com busca, colunas Título/Descrição/Arquivo/Cadastrado
  por/Data e ações Baixar, Visualizar, Editar, Excluir (com confirmação),
  conforme papel. `/arquivos/cadastrar-arquivo`, `/arquivos/[id]`,
  `/arquivos/[id]/editar` (gate de papel no `+page.ts`).
- `lib/forms/arquivo-form.svelte` (título, descrição, arquivo),
  `lib/utils/download.ts` (download autenticado reutilizável).

## 3c. Fase 3 — Notificações (branch `feat/fase3-notificacoes`)

Regras da 2.0 mantidas: cada usuário vê as suas; orientadores e estagiários
veem também os avisos gerais (destinatário nulo). Quem executa a ação não é
notificado da própria ação (a 2.0 notificava; era ruído).

Disparos (serviço único `NotificacaoService`, chamado dentro da transação da
ação de origem):
- Cadastro de caso: responsável, orientador, estagiário e colaborador
  ("Cadastrado no caso N"). Edição de caso: só quem passou a fazer parte.
- Novo evento com responsável: o responsável ("Cadastrado no evento N do
  caso M"). Novo lembrete: o usuário do lembrete.
- Configuração do plantão com data de abertura nova ou alterada: aviso geral
  "Abertura do plantão" (salvar sem mudar a abertura não repete).

Backend:
- A tabela `notificacao` da 2.0 nunca foi removida. Migração `2101e3af25b9`
  acrescenta `tipo` (caso|evento|lembrete|plantao), `id_caso`,
  `id_referencia` (id do evento/lembrete), `lida` e `data_criacao`. A 2.0
  descobria o destino interpretando o texto da ação; agora é estruturado.
- `/api/notificacao`: `GET /?page&per_page` (com nome do executor, mais
  recentes primeiro), `GET /nao-lidas` (`{total}`), `PATCH /<id>/lida`,
  `PATCH /lidas` (todas). 10 testes em `tests/api/test_notificacao_api.py`
  (246 no total).

Frontend:
- Sino no cabeçalho (`notificacao-bell.svelte`) com contador de não lidas,
  atualizado a cada 60 s e a cada navegação; leva a `/notificacoes`.
- Página `/notificacoes`: lista paginada, não lidas em destaque, botão
  "Abrir" (marca como lida e vai ao destino: caso, evento, caso do lembrete ou
  escala do plantão), "Marcar todas como lidas". Item "Notificações" na sidebar.

## 4. Seed local (banco em localhost)

Script: `scripts/seed_local.py` (cópia do usado). Usuários (senha `senha123`):
Olívia Orientadora `orientadora@gl.local` (orient, id 2), Eduardo Estagiário
`estagiario@gl.local` (estag_direito, id 3), Carla Colaboradora Externa
`colab.ext@gl.local` (colab_ext, id 4). Admin: `rvnovaes@gmail.com` / `admin`.

Casos: 1 (criado admin, resp. admin), 2 (admin → Eduardo), 3 (Eduardo →
Eduardo), 4 (Olívia → admin). Caso 1: 5 eventos (2 admin, 2 Eduardo, 1 Olívia)
e 2 PDFs. Presenças e plantões inseridos por SQL entre 18/08 e 02/09/2026
(7 presenças, 4 plantões ativos + 1 apagado), todas as situações de conferência.

## 5. Roteiro de testes — status (fase 1 aprovada em 03/09/2026)

| Item | Status |
|---|---|
| 1. Excluir evento (admin/criador, detalhe e lista) | ✅ OK |
| 2. Filtro de eventos por tipo | ✅ OK após correções (ordem alfabética, botão Novo Evento) |
| 3. Substituir arquivo (troca, download, não-PDF, >10 MB) | ✅ OK após tradução do 413 |
| 4. Meus Casos / Cadastrados por mim | ✅ OK; revelou bug pré-existente (novo caso por não-admin) corrigido com `user/opcoes` |
| 5. Termos de uso | ✅ OK |
| 6. Relatório de horários | ✅ OK após ajustes (largura do card, 403 traduzido, menu e página restritos por papel) |

### Passos pendentes

**4b. Novo caso / lembrete por não-admin (correção)**
1. Eduardo: Casos › Novo caso → formulário abre, seletores de orientador,
   estagiário e colaborador listam os 4 usuários em ordem alfabética.
2. Eduardo: editar caso 3 → abre normalmente.
3. Eduardo: novo lembrete em um caso → seletor de usuário preenchido.

**5. Termos de uso**
1. Link no rodapé da sidebar → página com 3 blocos e breadcrumb.
2. Sidebar recolhida → link some.

**6. Relatório de horários**
1. Admin: Relatórios → "Horário de chegada e saída" → lista de usuários no lugar
   das áreas.
2. 18/08/2026–02/09/2026 sem usuários → Presenças (7), Plantões (4); situações
   Confirmado/Divergência/Ausência/Não conferido; presença do admin de 15/08 e
   plantão apagado de 26/08 não aparecem.
3. Só Eduardo → 4 presenças, 2 plantões.
4. 01/09–02/09 → 1 presença (Eduardo 08:30–12:30), 1 plantão (Olívia 02/09).
5. Baixar CSV → duas seções, acentos OK.
6. "Casos por Situação" continua funcionando.
7. Olívia gera OK; Eduardo não vê "Relatórios" no menu e, acessando
   `/relatorios` pela URL, cai na página de erro "Acesso negado" com "Você não
   tem permissão para acessar os relatórios. Contate o administrador." (gate no
   `+page.ts`, mesmo padrão de configurar-abertura).

## 7. Roteiro de testes — fase 2 (Arquivos gerais) — aprovado em 03/09/2026

Seed: dois arquivos cadastrados pelo admin via API ("Regimento interno",
`.txt`, com descrição; "Planilha modelo de controle", `.csv`, sem descrição).

| Item | Status |
|---|---|
| 1. Menu e listagem (admin) | ✅ OK |
| 2. Cadastrar (admin): validações, sucesso, detalhe | ✅ OK |
| 3. Baixar (lista e detalhe) | ✅ OK |
| 4. Editar: só texto; substituir arquivo | ✅ OK |
| 5. Excluir com confirmação | ✅ OK após corrigir o refresh da lista |
| 6. Papéis: Eduardo (estagiário) e Carla (colab. externo) | ✅ OK |

## 8. Roteiro de testes — fase 3 (Notificações)

Seed: caso 5 (admin → responsável admin, orientadora Olívia, estagiário
Eduardo) criado pela API, gerando 1 notificação para Olívia e 1 para Eduardo.

| Item | Status |
|---|---|
| 1. Sino e página (Eduardo): contador 1, lista, Abrir → caso 5, contador 0 | ⏳ |
| 2. Evento com responsável e lembrete (admin → Eduardo) | ⏳ |
| 3. Editar caso incluindo Carla → só Carla é avisada | ⏳ |
| 4. Abertura do plantão → aviso geral para Olívia e Eduardo, não para Carla | ⏳ |
| 5. Marcar todas como lidas; paginação | ⏳ |

## 6. Pendências e ideias anotadas

- Lembrete novo: pré-selecionar o usuário logado no campo "Usuário
  responsável" (hoje começa vazio, como na 2.0).

- ~~Esconder "Relatórios" na sidebar para papéis sem acesso~~ — feito
  (03/09): item só para admin, orient e colab_ext; página mostra "Você não tem
  permissão para gerar relatórios" no 403.
- Wiki: reescrever Manual de Instalação a partir do README; arquivar
  "Permissões de Usuários" antiga; documentar módulos novos.
- Limitações já mapeadas (histórico de presença do plantão invisível após o
  encerramento, ausência de histórico de períodos, validação frouxa de
  `situacao_deferimento`) estão em `docs/known_issues.md`.
