#!/usr/bin/env bash
# Triagem do backlog do gestaolegal — 04/09/2026
#
# Rode na SUA máquina local, onde o gh já está autenticado:
#     bash fechar-issues.sh
#
# REVISE ANTES DE RODAR: comente com "#" a linha de qualquer issue
# que você não queira fechar ou comentar.
#
# Contexto que vale para tudo: produção roda a imagem 2.0.0-alpha.2
# (Flask+Jinja); o master é a 3.0 (API Flask + SvelteKit). "Resolvido
# no código" só chega ao usuário no deploy da 3.0.

set -uo pipefail
R=gestaolegalufmg/gestaolegal

fechar()   { echo "→ fechando  #$1"; gh issue close   "$1" --repo "$R" --comment "$2"; }
comentar() { echo "→ comentando #$1"; gh issue comment "$1" --repo "$R" --body    "$2"; }

NOTA_DEPLOY='

_Verificado no código do `master` (3.0). A produção ainda roda a imagem `2.0.0-alpha.2`, então a correção chega aos usuários no deploy da 3.0._'

# ══════════════════════════════════════════════════════════════
# 1. FECHAR — resolvido e verificado no código
# ══════════════════════════════════════════════════════════════

fechar 241 "Resolvido na 3.0. A busca de casos agora casa pelo nome das partes envolvidas (\`caso_service.search\`, via \`find_ids_by_atendido_nome\`), e a página do atendido/assistido ganhou uma seção **Casos** listando os casos vinculados, com link para cada um.${NOTA_DEPLOY}"

fechar 265 "Resolvido na 3.0. O redirecionamento após criar usuário usa o id devolvido pela API — \`web/src/lib/forms/user-form.svelte:62\`, \`goto(\\\`/usuarios/\\\${response.id}\\\`)\`. Não há mais id fixo.${NOTA_DEPLOY}"

fechar 266 "Resolvido na 3.0. A listagem de Atendidos e Assistidos ganhou a coluna **Tipo**, com badge \`Assistido\` ou \`Atendido\` — o espaço não fica mais em branco.

O rótulo ficou \"Assistido\" em vez de \"Já é Assistido\" e o badge não é amarelo; se a redação ou a cor importarem, abra uma issue de ajuste.${NOTA_DEPLOY}"

fechar 269 "Resolvido na 3.0. A página de usuários tem searchbar, coluna **Status**, filtro por função e alternância de inativos. A ordenação alfabética vem do backend (\`user_repository.py\`, \`order_by(usuarios.c.nome)\`).${NOTA_DEPLOY}"

fechar 271 "Resolvido. O repositório tem 19 arquivos de teste em \`tests/\` (\`api\` e \`database\`) e, desde 03/09/2026, o CI roda \`pytest tests/\` no job \`test\`, do qual o \`build\` depende (\`needs: test\`) — nenhuma imagem é publicada com teste vermelho."

fechar 283 "Resolvido. O servidor (\`glap2\`, 150.164.104.57) roda **Ubuntu 24.04.4 LTS**, com a aplicação em containers Docker. A migração do CentOS está concluída."

fechar 306 "Resolvido na 3.0. A tela do usuário mostra **Data de Inclusão** e **Data de Exclusão**.${NOTA_DEPLOY}"

fechar 307 "Resolvido na 3.0. A listagem de orientações jurídicas tem a coluna **Data de Criação** (com hora) e é ordenada por ela — \`orientacao_juridica_repository.py\`, \`order_by(data_criacao.desc())\`.${NOTA_DEPLOY}"

fechar 313 "Resolvido. O envio de e-mail deixou de depender do servidor da Setter: a stack própria tem Postfix + OpenDKIM em produção e mailpit em desenvolvimento, com a aplicação falando SMTP apenas pela rede interna do Docker. Desenho e operação em \`docs/email.md\`."

fechar 367 "Resolvido na 3.0. A home tem o atalho **Meus Casos** (\`/casos?user=me\`), a listagem unificada troca o título para \"Meus Casos\" quando filtrada, e há também o filtro \"Cadastrado por mim\". Cobre os quatro papéis pedidos.${NOTA_DEPLOY}"

# ══════════════════════════════════════════════════════════════
# 2. FECHAR — duplicatas absorvidas por #365
#    Atenção: o defeito NÃO está corrigido; #365 carrega a
#    especificação completa dos campos do formulário.
# ══════════════════════════════════════════════════════════════

fechar 176 "Fechando como duplicata de #365, que traz a especificação completa do formulário de cadastro de atendido — nela CPF e CNPJ aparecem sem asterisco, ou seja, não obrigatórios.

⚠️ O defeito **continua**: \`AtendidoCreateInput\` (\`gestaolegal/models/atendido_input.py\`) declara \`cpf: str\` sem valor padrão, então a API segue exigindo o campo. A correção deve sair junto com #365."

fechar 244 "Fechando como duplicata de #365, que traz a especificação completa do formulário de cadastro de atendido — nela \"Endereço de e-mail\" aparece sem asterisco, ou seja, não obrigatório.

⚠️ O defeito **continua**: \`AtendidoCreateInput\` declara \`email: str\` sem valor padrão. A migração \`03085453841c\` apenas removeu o índice único da coluna, não a obrigatoriedade. A correção deve sair junto com #365."

# ══════════════════════════════════════════════════════════════
# 3. NÃO FECHAR — registrar o que a verificação encontrou
# ══════════════════════════════════════════════════════════════

comentar 190 "**Confirmado em produção em 04/09/2026 — segue explorável.**

Requisição sem nenhuma autenticação contra a instância NL devolveu um despacho judicial de um caso:

\`\`\`
GET /static/casos/<arquivo>.pdf
→ HTTP 200, application/pdf, 98.932 bytes
\`\`\`

**A 3.0 não corrige.** \`gestaolegal/config.py\` mantém \`UPLOADS = os.path.join(STATIC_ROOT_DIR, \"casos\")\` — os uploads continuam dentro da pasta que o Flask publica em \`/static\`. A rota autenticada de download (\`caso_controller.py:453\`, \`@authenticated\`) foi adicionada, mas não impede o acesso pelo caminho direto.

**Correção:** mover \`UPLOADS\` e \`ARQUIVOS_DIR\` para fora de \`STATIC_ROOT_DIR\` (volume próprio) e servir exclusivamente pelas rotas autenticadas. Pelo conteúdo — documentos de assistidos — é exposição de dado pessoal sensível sob a LGPD e sigilo profissional."

comentar 191 "**Continua aberto.** Verificado nos dumps dos dois bancos de produção (04/09/2026): as *tabelas* são \`utf8mb4 / utf8mb4_0900_ai_ci\`, mas **106 colunas ainda são \`CHARACTER SET latin1 COLLATE latin1_general_ci\`** — e quem manda é a coluna.

Tabelas afetadas: \`arquivos\`, \`arquivosCaso\`, \`arquivosEvento\`, \`assistencias_judiciarias\`, \`assistidos\`, \`assistidos_pessoa_juridica\`, \`atendidos\`, \`casos\`, \`dias_marcados_plantao\`, \`documentos_roteiro\`, \`enderecos\`, \`eventos\`, \`fila_atendimentos\`, \`lembretes\`, \`notificacao\`, \`orientacao_juridica\`, \`processos\`, \`registro_entrada\`, \`usuarios\`.

Precisa de migração \`CONVERT TO CHARACTER SET utf8mb4\` por tabela. Vale fazer junto da unificação dos bancos descrita em \`docs/unidades.md\`."

comentar 205 "**Continua aberto, com causa provável identificada.** \`Processo.numero\` é \`int\` no modelo e \`bigint\` no banco. O número CNJ tem **20 dígitos** (NNNNNNN-DD.AAAA.J.TR.OOOO) e o \`bigint\` com sinal comporta no máximo 19 (9.223.372.036.854.775.807) — acima disso estoura.

**Correção:** o número do processo deve ser \`varchar\` (guarda a máscara e não tem teto numérico), não inteiro."

comentar 319 "**Parcialmente resolvido.** Dos 14 controllers, só dois seguem sem service correspondente: \`auth_controller\` e \`search_controller\`. O \`user_controller\` tem service, com nome diferente (\`usuario_service.py\`) — vale padronizar o nome ou registrar a exceção."

comentar 324 "**Continua aberto** na 3.0. Em \`web/src/routes/(dashboard)/casos/[id]/+page.svelte:105-106\` as pessoas do caso são renderizadas como texto puro:

\`\`\`
{ label: 'Orientador', value: caso.orientador?.nome || '--' },
{ label: 'Estagiário', value: caso.estagiario?.nome || '--' },
\`\`\`

Falta envolver em link para \`/usuarios/{id}\`."

comentar 363 "**Pista para investigação.** Em \`web/src/lib/forms/atendido-form.svelte:80\`:

\`\`\`
let addressFieldsDisabled = \$state(!\$formData.logradouro);
\`\`\`

Os campos de endereço nascem desabilitados até a consulta de CEP preencher \`logradouro\`. Vale checar se esse estado é reavaliado no submit e no erro de validação — é o candidato mais provável para os campos aparecerem apagados após clicar em Criar Atendido."

comentar 366 "**Parcialmente resolvido.** O item Plantão da barra lateral não navega mais: em \`nav-main.svelte\`, itens com submenu viram \`Collapsible.Trigger\` (botão que expande) e só as folhas viram \`<a href>\`. O \`url: '/plantao'\` em \`app-sidebar.svelte:32\` virou dado morto.

**Mas o 404 persiste pelo breadcrumb.** \`dynamic-breadcrumb.svelte:19\` mapeia \`'/plantao': { label: 'Plantão', href: '/plantao' }\`, e \`generateBreadcrumbs\` empilha um crumb por segmento — então toda página \`/plantao/*\` mostra \"Plantão\" clicável apontando para \`/plantao\`, que não tem \`+page.svelte\`.

**Correção:** remover o \`href\` desse mapa, ou criar \`/plantao/+page.svelte\` redirecionando (a sugestão original era mandar para Casos).

De quebra, o mesmo mapa ainda tem rotas que não existem: \`/atendidos\`, \`/atendidos/cadastrar\`, \`/casos/meus-casos\`, \`/casos/gestao-casos\`, \`/casos/gerenciar-roteiros\`."

comentar 267 "**Premissa revista.** O \`docs/unidades.md\` (04/09/2026) decidiu modelar **unidade/filial** em vez de multiempresa/multitenant, e descartou explicitamente o \`tenant_id\`: _\"colocar tenant_id em todas as tabelas traria risco de vazamento a cada query esquecida sem necessidade atual\"_. Para outra instituição, a solução continua sendo instância e banco separados.

Esta issue e as sub-issues #272, #273 e #274 descrevem a abordagem descartada: precisam ser reescritas conforme o documento, ou fechadas em favor de issues novas de \"unidades\"."

echo
echo "✔ Concluído."
