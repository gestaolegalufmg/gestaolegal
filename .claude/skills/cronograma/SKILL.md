---
name: cronograma
description: Transforma o plano aprovado desta worktree em scripts/helton/projects/prds/prd.json — o cronograma de user stories que o loop Helton executa, com prioridade, dependências, esforço e as travas de revisão humana já marcadas. Use quando o usuário pedir "gera o cronograma", "vira o plano em prd", "monta as tarefas do Helton", "prepara a empreitada" ou logo depois de montar um canteiro com montar-canteiro.sh.
---

# Cronograma (plano → prd.json)

Converte `scripts/helton/projects/plans/<plano>.md` no `scripts/helton/projects/prds/prd.json` desta worktree. É o passo
entre montar o canteiro e soltar a empreitada.

## Antes de qualquer coisa

**Rode de dentro da worktree do plano**, nunca do checkout principal. O
`prd.json` tem nome fixo, e é a raiz-por-worktree que permite N planos
coexistirem. Confira:

```bash
git rev-parse --show-toplevel   # tem de ser .../<projeto>-<plano>
git branch --show-current       # tem de ser helton/<plano>
```

Se estiver no checkout principal, pare e diga ao usuário para montar o canteiro
primeiro (`./scripts/helton/obra/montar-canteiro.sh <plano>`).

## Entrada

1. `scripts/helton/projects/plans/<plano>.md` — o plano aprovado. O `<plano>` sai do nome da branch
   (`helton/onda-2` → `onda-2`).
2. `scripts/helton/projects/plans/manifest.json` — a compatibilização. Dele saem:
   - `status`: se não for `parallel` nem o predecessor já mergeado de um
     `serialized_after`, **pare** e avise — gerar cronograma para um plano
     serializado é construir sobre um develop que ainda vai mudar.
   - `resolved_questions`: as ambiguidades já decididas. **Use-as como contexto
     das stories e não pergunte de novo.**
   - `hash`: confira contra `sha256sum scripts/helton/projects/plans/<plano>.md`.

**Deriva de hash é a única razão para reabrir perguntas.** Se o hash bate, o
plano é o mesmo que foi compatibilizado e todas as decisões já estão tomadas;
gere o prd calado. Se não bate, o plano foi editado depois — mostre o que mudou,
pergunte o que a mudança implica, e sugira rodar `/compatibilizar` de novo se a
edição mexeu nos arquivos reivindicados.

Sem `scripts/helton/projects/plans/manifest.json`, ofereça rodar `/compatibilizar` antes. Se o usuário
recusar (plano único, sem paralelismo), siga — mas então a fase de perguntas
desta skill é bloqueante: **nenhum prd é gravado com pergunta pendente.**

## O que do plano vira story

**Nem todo plano é só escopo futuro.** O formato "o que sobrou" — plano escrito
depois de uma empreitada parcial — carrega metade do documento em `## Já feito`,
com fases marcadas `FEITO` ou `✅`, e só depois o `## O que falta`. Converta
**exclusivamente a parte pendente**.

Story criada para trabalho já entregue manda o loop refazer o que já está no
`develop`, e nada pega isso: o `make ready` passa, o diff parece
plausível, e o resultado pode desfazer decisão deliberada de quem entregou.
Antes de escrever qualquer story, delimite o escopo e **diga ao usuário de onde
até onde você vai converter**.

O que nunca vira story, mesmo estando no arquivo:

- `## Já feito`, `## Estado por fase`, e qualquer fase marcada `FEITO`/`✅`.
- `## Fora desta rodada`, `## Fora de escopo`, `## Pendências que não são código`.
- `## Verificação` e `## Armadilhas` — são insumo do campo `verify` das stories,
  não trabalho por si.
- `## Human gates` — é insumo do `human_gate`/`gate_reason`, não uma story.

**Confira a premissa antes de converter.** Um plano "resto" pressupõe que a base
já contém as fases dadas como feitas — e o `hash` do manifesto detecta deriva do
*plano*, nunca da *base*. Escolha dois ou três itens concretos do `## Já feito`
(um arquivo, um método, uma coluna) e confirme que existem em
`origin/develop`. Se o que está declarado como entregue não estiver lá,
**pare e pergunte**: o plano está construindo sobre chão que não existe, seja
porque a branch anterior não mergeou, seja porque o texto envelheceu.

**Gate já anotado no plano é para respeitar.** Quando o texto marca uma tarefa
com algo como "Human gate — contrato de API publicado (gate 5)", isso é
julgamento de quem escreveu somado à categoria do `CLAUDE.md`: leve para o
`human_gate` e aproveite a frase no `gate_reason`. Você pode acrescentar gates
que o plano não viu; não remova os que ele marcou.

## Saída: o schema

Este repositório usa `userStories`, não `tasks` (o `tasks` do upstream nunca
valeu aqui). Envelope:

```json
{
  "project": "meuprojeto",
  "branchName": "helton/onda-2",
  "description": "uma frase sobre a fatia",
  "execution": "sandboxed",
  "userStories": [ ... ]
}
```

`execution` é `sandboxed` quando o loop roda numa worktree com stack própria (o
caso desta esteira) e `gated` quando roda em ambiente compartilhado. Ele muda o
que é gate — ver adiante.

Cada story:

```json
{
  "id": "f1-estoque-acerto-api",
  "title": "frase de uma linha, no imperativo",
  "context": "por que esta story existe e o que o agente precisa saber antes de abrir o editor; cite arquivo e linha",
  "files": ["app/domain/stock/services/stock_service.py"],
  "acceptance": "o que tem de ser verdade no fim, em termos observáveis",
  "verify": "make ready",
  "effort_label": "low",
  "human_gate": false,
  "gate_reason": null,
  "review_required": false,
  "blocked_by_gate": false,
  "depends_on": [],
  "priority": 1,
  "passes": false,
  "notes": ""
}
```

Regras de preenchimento:

- **`id`** — kebab-case, estável, prefixado pela fase (`f1-`, `f2-`). É a chave
  de `depends_on` e o que aparece na mensagem de commit.
- **`context`** — é o que sobrevive ao reset de contexto entre iterações. Uma
  story cujo `context` não permite começar sem reler o plano inteiro está mal
  escrita. Cite caminho e número de linha.
- **`files`** — os que a story escreve. Serve de mapa de colisão dentro da
  própria fatia.
- **`verify`** — comando real que prova o `acceptance`, dos **Comandos** do
  `CLAUDE.md` da raiz. `make ready` é o piso; story de UI pede verificação no
  browser (ver **Automação de browser** no `CLAUDE.md`); story de backend com
  regra nova pede teste próprio.
- **`effort_label`** — `low` / `medium` / `high`. Roteia modelo. `high` é sinal
  de que a story **precisa ser quebrada** — fatia grande demais para o loop não é
  fatia, é plano. Quebre-a; se realmente não der, marque `review_required: true`.
  `high` **não** implica mais `human_gate` (mudou em 22/08/2026): tamanho é
  problema de fatiamento, não de irreversibilidade, e barrar por tamanho era mais
  uma fonte de empreitada travada cedo.
- **`priority`** — inteiro, menor executa antes. Não repita número: a ordem é o
  cronograma.
- **`passes`** — sempre `false` num prd novo.

## Human gates

O `CLAUDE.md` da raiz tem a seção `## Human gates` com as instâncias deste
projeto. **Leia-a e aplique-a.** Se ela não existir, ofereça criá-la e não
prossiga sem — nunca invente gates em silêncio.

**A régua é o canteiro, não o arquivo** (revista em 22/08/2026). A pergunta não é
"este arquivo é sensível?", é **"o efeito escapa da worktree?"**. Cada empreitada
roda em worktree própria, com stack e volume de Postgres próprios: o que acontece
lá dentro se desfaz com `git` e com `desmontar-canteiro.sh --volumes`.

O teste concreto, antes de marcar qualquer gate: *o estrago sobrevive a
`desmontar-canteiro.sh --volumes` e a um `git revert`?*

- **Não sobrevive** → `review_required: true`. A story **executa**, e entra no
  índice de revisão do desmonte. **Na dúvida, é aqui.**
- **Sobrevive** → `human_gate: true`.

Gate barra a story e, por `blocked_by_gate`, tudo que depende dela. Marcar gate
por precaução não deixa a fatia mais segura — deixa a empreitada parada, e o
humano revisa no merge de qualquer jeito.

Continuam `human_gate: true`, e só estes:

- **Efeito que escapa do canteiro**: chamada a API externa real, webhook, e-mail
  que sai da máquina, emissão fiscal fora de homologação, numeração de série.
- **Segredos e o que roda fora daqui**: `.env*`, vaults, `ansible/`, DNS,
  `.github/workflows/`.
- **Enfraquecer a maquinaria de verificação**: o loop nunca mexe na própria
  guarda — testes, asserções, `make ready`, hooks, `scripts/helton/`,
  `scripts/helton/obra/`, estas skills. Ampliar a verificação (teste novo, check
  a mais) **não** é gate: é o resultado desejado.

**Não** são gate, e sim `review_required`: migration, aritmética de dinheiro e
imposto, permissões e escopo de tenant, contrato de API, `docker-compose*.yml`, e
o fiscal que não emite (DTO, parser, tabela, tela, regra tributária).

`gate_reason` é obrigatório quando `human_gate: true`, em uma frase, dizendo qual
categoria disparou.

`blocked_by_gate` é **derivado, não julgado**: é o fechamento transitivo de
`depends_on` sobre stories com `human_gate: true`. Se A é gate e B depende de A,
B é `blocked_by_gate: true`; se C depende de B, C também. `review_required` **não**
propaga bloqueio — quem revisa é o humano no merge, não o loop.

### Migration destravada tem um preço, e ele é pago no manifesto

Dois canteiros criando migration em paralelo produzem dois heads de Alembic, e
dois heads derrubam produção sem que o portão de testes perceba. Quem resolve é o
`/compatibilizar`, pelo `creates_migration` do manifesto. Ao gerar cronograma para
um plano com migration, **confira que o manifesto existe e que este plano não
divide schema com outro em voo**; se dividir e não houver plano-zero, pare e
avise.

## Documentação obrigatória

O `CLAUDE.md` da raiz manda: se **qualquer** story tocar `app/api/` ou
`web/src/routes/` (fora de `(backoffice)/`) **e mudar o que o usuário vê ou
faz**, a fatia precisa de uma story de atualização do `docs/manual.md`. Para
`app/api/platform/` e `web/src/routes/(backoffice)/`, do `docs/SAAS_manual.md`.
Uma story por documento distinto, não uma por story tocada, e ela depende
(`depends_on`) das stories que mudam o comportamento.

Refactor, infra e migration sem efeito visível não disparam a regra.

## Preservação de estado

Se já existir `scripts/helton/projects/prds/prd.json`:

- **Mesmo `branchName`** — é a mesma empreitada, retomada. **Não sobrescreva
  `passes`, `notes` nem `priority`** das stories que já existem: elas carregam o
  que o loop já fez. Mostre o diff (stories novas, removidas, alteradas) e peça
  confirmação antes de gravar.
- **`branchName` diferente** — é outra empreitada. Arquive a anterior em
  `scripts/helton/projects/prds/implemented/AAAA-MM-DD-<fase>/` (prd.json e progress.txt juntos)
  antes de escrever o novo. O `helton.sh` também arquiva sozinho ao detectar
  troca de branch, mas não conte com isso: arquive você.

## Depois de gravar

1. Valide: `jq -e '.userStories | length' scripts/helton/projects/prds/prd.json`.
2. Confira que todo `depends_on` aponta para um `id` que existe.
3. Confira que `blocked_by_gate` está coerente com o fechamento transitivo.
4. Relate ao usuário: quantas stories, quantas barradas por gate (e por quê),
   quantas marcadas para revisão, e qual a primeira que o loop vai pegar.
5. Lembre que o próximo passo é o **ensaio de uma iteração vigiada**
   (`./scripts/helton/helton.sh --tool claude 1`) antes de liberar o cap real.

## Fronteiras

- Não implemente nenhuma story. Esta skill escreve JSON.
- Não dispare o `helton.sh`.
- Não commite o prd — quem commita é o loop, junto do código da primeira story.
