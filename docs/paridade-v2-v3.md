# Paridade 2.0 → 3.0: análise, plano e roteiro de testes

Documento de trabalho da migração de funcionalidades da versão 2.0 (tag `v2.0.2`,
Flask + Jinja) para a 3.0 (API Flask + SvelteKit). Atualizado em 02/09/2026.

## 1. Diferenças entre as versões

### 1.1 O que a 2.0 tem e a 3.0 não tem

Módulos inteiros removidos (tabelas dropadas nas migrações da 3.0):

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

1. **Fase 1** — ganhos rápidos sem migração (itens 5–9). **Concluída; em teste.**
2. **Fase 2** — Arquivos gerais: migração recriando `arquivos`, repo/service/
   controller no padrão de `arquivosCaso`, páginas `/arquivos`, item na sidebar
   restrito aos 4 papéis, testes.
3. **Fase 3** — Notificações: migração recriando `notificacao` com coluna `lida`
   e destino estruturado (tipo + ids); serviço único de disparo chamado por
   caso, evento, lembrete e configuração do plantão; endpoint paginado; página +
   ícone com contador no cabeçalho.
4. **Fase 4** — Recuperação de senha: SMTP no `.env`, serviço de e-mail, token
   PyJWT com expiração, endpoints públicos em auth, páginas e link no login.
5. **Fase 5** — PJ, atalhos da home, atualizar a wiki.

Decisões pendentes do usuário: notificações só in-app ou também e-mail; há SMTP
disponível; reaproveitar texto dos termos (feito com o texto da 2.0).

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

## 4. Seed local (banco em localhost)

Script: `scripts/seed_local.py` (cópia do usado). Usuários (senha `senha123`):
Olívia Orientadora `orientadora@gl.local` (orient, id 2), Eduardo Estagiário
`estagiario@gl.local` (estag_direito, id 3), Carla Colaboradora Externa
`colab.ext@gl.local` (colab_ext, id 4). Admin: `rvnovaes@gmail.com` / `admin`.

Casos: 1 (criado admin, resp. admin), 2 (admin → Eduardo), 3 (Eduardo →
Eduardo), 4 (Olívia → admin). Caso 1: 5 eventos (2 admin, 2 Eduardo, 1 Olívia)
e 2 PDFs. Presenças e plantões inseridos por SQL entre 18/08 e 02/09/2026
(7 presenças, 4 plantões ativos + 1 apagado), todas as situações de conferência.

## 5. Roteiro de testes — status

| Item | Status |
|---|---|
| 1. Excluir evento (admin/criador, detalhe e lista) | ✅ OK |
| 2. Filtro de eventos por tipo | ✅ OK após correções (ordem alfabética, botão Novo Evento) |
| 3. Substituir arquivo (troca, download, não-PDF, >10 MB) | ✅ OK após tradução do 413 |
| 4. Meus Casos / Cadastrados por mim | ✅ OK; revelou bug pré-existente (novo caso por não-admin) corrigido com `user/opcoes` |
| 5. Termos de uso | ⏳ pendente |
| 6. Relatório de horários | ⏳ pendente |

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
7. Olívia gera OK; Eduardo recebe "Erro ao gerar relatório" (backend nega
   estagiário — pré-existente; melhoria de UX: esconder Relatórios no menu).

## 6. Pendências e ideias anotadas

- Esconder "Relatórios" na sidebar para papéis sem acesso (estag_direito,
  colab_proj, prof) e/ou gate no `+page.ts`.
- Wiki: reescrever Manual de Instalação a partir do README; arquivar
  "Permissões de Usuários" antiga; documentar módulos novos.
