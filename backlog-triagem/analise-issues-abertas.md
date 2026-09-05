# Triagem das 41 issues abertas contra o código do `master` (3.0)

Data: 04/09/2026. Base: checkout `/opt/gestaolegal`, branch `master`.

Contexto que vale para tudo: produção roda a imagem `2.0.0-alpha.2` (Flask+Jinja).
O `master` é a 3.0 (API Flask + SvelteKit). "Resolvido no código" só chega ao
usuário no deploy da 3.0. Boa parte das issues de 2021–2022 descreve a 2.0 e foi
resolvida por consequência da reescrita, não por correção deliberada.

---

## A. Resolvidas na 3.0 — FECHADAS em 04/09/2026 (10)

| # | Título | Evidência |
|---|--------|-----------|
| 73 | Eventos não podem ser um quadrinho à parte | Eventos são tabela própria na página do caso, com filtro por tipo e colunas Nº/Tipo/Descrição/Data/Responsável (`casos/[id]/+page.svelte:134-138`). O "quadrinho" da 2.0 não existe mais. |
| 124 | Acrescentar tipo de alteração e horário em Ver Histórico | `Historico` ganhou `acao` e `descricao`; `data` é `DateTime` (`tables.py:308-317`). O front renderiza rótulo da ação, descrição e `formatDateTime` (`casos/[id]/+page.svelte:591-605`). |
| 136 | Escala de Plantão não se atualiza após selecionar dias | O POST devolve a página inteira e o estado é reatribuído, sem reload (`plantao/escala/+page.svelte:66`). |
| 137 | Apenas Estagiário/Orientador podem selecionar datas | Marcar plantão exige só `@authenticated` (`plantao_controller.py:21-23`). Quota existe apenas para `orient` e `estag_direito`; os demais papéis recebem vagas ilimitadas (`plantao_service.py:75-77`). É exatamente o pedido da issue. |
| 157 | Último lembrete não mostra o mais recente | Não há mais card "último lembrete". Os lembretes vêm ordenados por `data_criacao` decrescente (`lembrete_repository.py:28`) e são listados inteiros. |
| 169 | Navegação do cadastro de atendidos | Após criar, redireciona para a ficha (`atendido-form.svelte:61`), e a ficha tem botão Editar (`atendidos-assistidos/[id]/+page.svelte:151`). |
| 175 | Coluna "Lembrete" na listagem de eventos | A coluna não existe mais. A coluna de data se chama "Data" e usa `data_evento` (`casos/[id]/+page.svelte:137`). |
| 177 | Forma de associar atendidos | Virou seletor múltiplo com chips removíveis (`orientacao-juridica-form.svelte:89-109`), que é o modelo pedido na issue. |
| 194 | Arquivo obrigatório só testado no servidor | A premissa caiu: `arquivo` é opcional no schema de evento (`evento-schema.ts:6,15`). |
| 322 | Erro 404 ao abrir arquivo dentro de um caso | O front não usa mais `/static/casos/...`. Baixa por rota autenticada `caso/{id}/arquivos/{id}/download` (`casos/[id]/+page.svelte:283`). |

---

## B. Parcialmente resolvidas — TRATADAS em 04/09/2026 (7)

Desfecho: #208, #314 e #319 fechadas. #159 e #203 reescritas com o escopo trocado.
#325 reduzida ao que falta. #312 convertida em guarda-chuva, com as sub-issues
#401 a #405.

**#159 — Arquivos dos Casos.** A queixa original era que estagiário e colaborador
externo não conseguiam subir arquivo. Resolvido, mas por excesso: as quatro rotas
de arquivo do caso (listar, subir, baixar, substituir) exigem apenas
`@authenticated`, sem distinção de papel (`caso_controller.py:420-462`). A
planilha de permissões pede colaborador de projeto sem acesso e exclusão restrita
a admin/orientador/professor. Compare com `arquivo_controller.py:15-16`, que
declara `PAPEIS_EDITAM` e `PAPEIS_EXCLUEM` para os arquivos gerais. Os arquivos do
caso ficaram mais frouxos que os gerais.

**#203 — Deferir/Indeferir: permissão do administrador.** As rotas `deferir` e
`indeferir` exigem só `@authenticated` (`caso_controller.py:129-143`), então o
admin passa. Mas o componente `indeferir-caso-dialog.svelte` não é importado por
nenhuma rota: **não há interface de deferimento no front da 3.0**. A issue não
pode ser fechada; o que falta agora é a tela, e a permissão está aberta demais.

**#208 — Campos do questionário não admitem 0.** `salario` e `renda_familiar`
aceitam 0 (`assistido-schema.ts:42,69`), assim como `quantos_imoveis`,
`quantos_veiculos` e `gastos_medicacao`. Resta `qtd_pessoas_moradia: min(1)`
(`assistido-schema.ts:67`). A especificação de #364 chama esse campo de "Quantas
pessoas moram com você?", e quem mora sozinho responde 0. É preciso decidir se o
campo conta a pessoa ou os coabitantes.

**#312 — Adoção e retenção de diligências.** Diligência é um tipo de evento
(`tipo_evento.ts:5`). Das ideias listadas, só o preview de texto na tabela existe
(coluna Descrição com `type: 'preview'`). Faltam banner de caso desatualizado,
pop-up de pendências, sidebar de diligências e e-mail de lembrete.

**#314 — Ajustes de layout gerais.** O exemplo citado na issue, a listagem de
orientação jurídica sem data, foi resolvido junto com #307. O resto é subjetivo e
não dá para verificar por código. Vale reescrever a issue apontando as telas que
ainda incomodam, ou fechá-la em favor de issues específicas.

**#319 — Todo controller com service correspondente.** Faltam dois:
`auth_controller` e `search_controller`. O `user_controller` tem service com nome
divergente (`usuario_service.py`).

**#325 — Melhorar notificações.** Bem mais adiantado do que a issue supõe. Existe
sino com contador de não lidas (`notificacao-bell.svelte`), marcar lida, marcar
todas, arquivar, e cinco gatilhos implementados: caso cadastrado, caso editado,
evento criado, lembrete criado e plantão aberto (`notificacao_service.py:125-194`).
Falta o formato pedido: o sino navega para a página `/notificacoes` em vez de abrir
uma sidebar com as abas Lidas e Não lidas.

---

## C. Continuam abertas, com diagnóstico (13)

**#190 — Arquivos privados em pasta pública. Prioridade máxima.** Confirmado
explorável em produção em 04/09/2026, e a 3.0 não corrige: `UPLOADS` e
`ARQUIVOS_DIR` continuam dentro de `STATIC_ROOT_DIR` (`config.py:117-121`), que o
Flask publica em `/static`. A rota autenticada de download foi adicionada, mas não
impede o acesso pelo caminho direto. Correção: mover os dois diretórios para fora
de `STATIC_ROOT_DIR` e servir só pelas rotas autenticadas. É exposição de dado
pessoal sensível sob a LGPD.

**#191 — Encoding latin1.** As tabelas são utf8mb4, mas 106 colunas seguem
`latin1_general_ci` nos dois bancos de produção, e quem manda é a coluna. Precisa
de `CONVERT TO CHARACTER SET utf8mb4` por tabela. Vale fazer junto da unificação
descrita em `docs/unidades.md`.

**#205 — Erro ao ver processo com número longo.** `Processo.numero` é `int` no
modelo e `BigInteger` no banco (`tables.py:189`), com `unique=True`. O número CNJ
tem 20 dígitos e o `bigint` com sinal comporta 19. Correção: `varchar`, que guarda
a máscara e não tem teto.

**#183 — Upload de mais de um arquivo em Eventos.** `Evento.arquivo` é `str |
None` singular (`evento.py`), e o input do dialog não tem `multiple`
(`evento-dialog.svelte:153-157`). Nada mudou.

**#114 — Ordem das perguntas de PJ em Tornar Assistido.** Mais grave que a issue
descreve: o modelo `AssistidoPessoaJuridica` existe no backend, mas **não há
nenhum formulário de pessoa jurídica no front da 3.0**. Nenhuma ocorrência de
`enquadramento` ou `socios` em `web/src`. Bate com a fase 5 pendente de
`docs/paridade-v2-v3.md`.

**#364 — Questionário de tornar assistido.** Confirmado. A ordem atual é Salário,
Renda Familiar, Benefício, Qual benefício, Contribui com INSS, Participação na
Renda, Quantidade de Pessoas na Moradia. A especificação pede Salário, Benefício,
Qual benefício, Previdência, Quantas pessoas moram com você, Renda familiar,
Posição na renda. Títulos divergem, e faltam as perguntas condicionais "A família
possui outros imóveis?", "A família possui veículos?" e "Qual é o veículo?".

**#365 — Formulário de cadastro de atendido.** Continua a especificação de
referência. Absorveu #176 e #244, fechadas hoje. O defeito permanece:
`AtendidoCreateInput` declara `cpf: str` e `email: str` sem valor padrão
(`atendido_input.py:26,30`), então a API segue exigindo ambos, contra a
especificação.

**#366 — Botão Plantão leva a 404.** O item da barra lateral não navega mais, mas
o breadcrumb sim: `dynamic-breadcrumb.svelte:19` mapeia `'/plantao'` com `href:
'/plantao'`, e não existe `plantao/+page.svelte`. O mesmo mapa ainda tem rotas
inexistentes: `/atendidos`, `/atendidos/cadastrar`, `/casos/meus-casos`,
`/casos/gestao-casos`, `/casos/gerenciar-roteiros`.

**#363 — Campos de endereço apagados ao criar atendido.** Não reproduzi. O
suspeito continua sendo `addressFieldsDisabled` em `atendido-form.svelte:80-122`,
que mantém logradouro, bairro, cidade e estado desabilitados após o CEP ser
resolvido. Descartei a hipótese de campos `disabled` não irem no submit: o form usa
`SPA: true`, então o superforms serializa `$formData`, não o FormData nativo.
Precisa de reprodução com a stack no ar.

**#324 — Pessoas do caso devem ser clicáveis.** Confirmado. Em
`casos/[id]/+page.svelte:103-108` as quatro pessoas são texto puro. Falta envolver
em link para `/usuarios/{id}`.

**#326 — Orientação jurídica perde dados.** Nada implementado: nenhuma ocorrência
de `localStorage`, rascunho ou autosave em `web/src`. O JWT dura 12 horas
(`jwt_auth.py:19`), então expiração de sessão dificilmente é a causa em um
atendimento de 10 minutos. Investigar o erro real antes de escolher a mitigação.

**#309 (Superset), #316 (Komodor).** Nenhuma implementação no repositório. Abertas
como sempre estiveram.

**#310 — Cor do login para Nova Lima.** Não há nenhuma noção de unidade ou tema no
`login/+page.svelte`. Depende da modelagem de unidades (`docs/unidades.md`).

**#311 — Botões quebrando na listagem de casos.** Quem relatou não conseguiu
reproduzir. Não é verificável por leitura de código. Precisa de reprodução ou
fechamento por falta de evidência.

**#315 — Lançar plantão.** O código existe: escala, configurar abertura, fila de
atendimento, registro e confirmação de presença. A issue é operacional, testar e
lançar, não um defeito de código.

---

## D. Premissa revista — FECHADAS em 04/09/2026 (5)

**#267, #272, #273, #274 — Multiempresa/multitenant.** O `docs/unidades.md`
(04/09/2026) decidiu modelar unidade/filial e descartou explicitamente o
`tenant_id`: "colocar tenant_id em todas as tabelas traria risco de vazamento a
cada query esquecida sem necessidade atual". Para outra instituição, a solução
continua sendo instância e banco separados. As quatro issues descreviam a abordagem
descartada e foram fechadas com esse comentário.

**#275 — Demonstração de como cadastrar um novo caso.** O corpo era só o texto do
template de abertura de issue, sem conteúdo. Fechada por falta de relato.

---

## E. Guarda-chuva

**#337 — Bugs da refatoração do frontend.** Das seis sub-issues, duas fecharam
(#367 e #368). Seguem abertas #363, #364, #365 e #366. A issue diz que pode ser
fechada quando as seis estiverem resolvidas, então continua aberta.

---

## Ordem sugerida de ataque

1. **#190** — exposição de arquivos sem autenticação, explorável hoje em produção.
2. **#365 + #363 + #364** — o fluxo de entrada do sistema. Resolver junto, porque
   #365 carrega a especificação que muda a obrigatoriedade de CPF e e-mail.
3. **#366** — um `href` a remover no breadcrumb, mais a limpeza das rotas mortas.
4. **#324** — envolver quatro nomes em link.
5. **#205** — trocar `numero` para `varchar`, com migration.
6. **#203** — decidir se deferimento entra no front e restringir a rota por papel.
7. **#191** — converter as 106 colunas, junto da unificação dos bancos.
