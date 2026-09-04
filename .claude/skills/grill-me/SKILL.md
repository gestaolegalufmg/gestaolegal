---
name: grill-me
description: Relentlessly interviews you in rounds to extract what's in your head into a durable, searchable capture file. Activates on "grill me", "grill me about <X>", "stress-test this plan", "pressure-test my thinking on <X>", "interview me about <X>", "drill me on <X>", "get this out of my head", "discovery session on <X>", "I need to think through <X> properly", or any request to externalize a process, plan, decision, or mental model. Walks each branch of the decision tree, gives a recommended answer with every question, and CHECKPOINTS every answer to a markdown file on disk so nothing is lost as the context window fills. NOT a content generator — it extracts, it doesn't write deliverables.
argument-hint: "[topic, plan, or decision to be grilled on]"
---

# Grill Me

You want something out of your head and into a durable system. Interview the user relentlessly about every branch of the topic until you reach genuine shared understanding. The real job is **extraction** — turning what only lives in someone's head into durable, reusable, retrievable context. A five-minute brain-dump is never enough; the questions are how you get the rest.

## The capture file is the whole point

A long interview fills the context window. If answers live only in your head, you will eventually misremember, conflate, or drop one. So you **checkpoint to disk after every single answer**. The file on disk — not your conversation memory — is the source of truth. Never make the user ask you to save progress; it's automatic and constant.

There are TWO distinct "checkpoints" in this skill. Do not conflate them:

1. **Capture-file write** — appending each answer to the markdown file. A cheap local write. Happens after **EVERY single answer**, always. This is the anti-context-loss guarantee.
2. **Ingest / indexing** — making the file searchable in whatever retrieval layer you use (a vector DB, a notes index, etc.). Heavier. Happens **once at session close**, or when the user explicitly says "ingest what we have." Never on a timer, never on a self-counted cadence (you are unreliable at both). The on-disk file is the safety net the whole time; searchability just lands at the end.

## When this runs

The user says one of: "grill me", "grill me about <X>", "stress-test this plan", "pressure-test my thinking on <X>", "interview me about <X>", "drill me on <X>", "get this out of my head", "discovery session on <X>", "I need to think through <X> properly". Or any moment they clearly want to externalize a process / plan / decision / mental model rather than have you produce a deliverable.

## When NOT to run this skill

- **A single thing to save right now.** If the user just wants to persist one paste or insight, that's a quick capture, not a whole interview.
- **They want a deliverable written** (copy, a doc, a post). This skill extracts thinking; it does not produce finished artifacts. Hand off to whatever writing workflow you use.

grill-me is for when there's a body of knowledge in someone's head and the way to get it out is sustained, structured questioning.

## Setup — do this BEFORE the first question

### 1. Resolve the capture path

Write to `scripts/helton/projects/specs/<tema>.md` — a spec é a entrada da sessão de plan mode que vem depois, e essa sessão lê o ARQUIVO, não esta conversa. Fora de um projeto com essa convenção, `notes/YYYY-MM-DD-<topic>-grill.md` serve. Data com `date +%F`.

### 2. Create the file immediately

Write the header before asking anything (see structure below): title, date, the one-line goal of the session, and empty "Summary" + "Open flags" sections. Tell the user the path in ONE line ("Capturing to `<path>` as we go."). Then ask Q1.

## The checkpoint rule (non-negotiable)

After EVERY round of answers, BEFORE you ask the next round:

- Append a structured entry to the capture file: the question topic, the key facts and decisions from their answer (**in their own words where the wording matters** — don't paraphrase their exact phrasing into something cleaner), and any flags (things they couldn't answer + who owns them).
- Update or correct earlier entries if a later answer changes them. Keep the running "Summary / key decisions" synthesis current.
- ONLY then ask the next round.

Never carry a round in your head into the next one. One round, one write. The point is that if context is lost at any moment, the file already holds everything said so far.

## Interview method

Map the problem as a **design tree**: every decision branches into the decisions
that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose
prerequisites are already settled — the questions you can ask *now* without
guessing at answers you haven't heard yet. Ask the whole frontier in one round,
then wait for the answers before the next. A question whose answer depends on
another question still open in this round belongs to a *later* round, not this
one.

Format each question like this:

```
❓ **Q1** — **<título da pergunta>**: <o corpo, que pode ter vários parágrafos e
alternativas>

➡️ <sua resposta recomendada>
```

The recommended answer is not optional: it is what lets the user confirm,
correct, or redirect in a word, and it surfaces where your model of the problem
is wrong.

**Finding _facts_ is your job, never the user's.** When a frontier question needs
something from the environment — o código, um arquivo, a saída de um comando —
go get it, or dispatch a sub-agent. Don't block the round on it: a running
exploration is an unsettled prerequisite, so only the questions downstream of it
wait. Ask the rest of the frontier now. The **decisions** are the user's; put
each to them and wait.

When the user **can't answer** something, capture it as a flag with the right
owner (a teammate, a system to check, a doc to pull) and move on. Don't stall on
a gap.

The session is done when the frontier is empty: every branch visited, nothing
left silently assumed. Near the end, offer a completeness backstop: "Ficou algo
de fora que deveria estar aqui?" **Do not act on the result** until the user
confirms you reached a shared understanding — a spec é o produto, não o começo
da implementação.

## Capture file structure

```markdown
# {Topic}: Grill / Discovery Notes
Date: {YYYY-MM-DD} · Goal: {one line}

## Summary / key decisions
(running synthesis, updated as you go — the TL;DR of everything settled so far)

## Q&A log

### Q1 — {topic}
- Asked: {the question}
- Captured: {facts, decisions, the user's words verbatim where it matters}
- Flags: {open item -> owner}

### Q2 — {topic}
...

## Open flags (pending input)
- {item} -> {who/what can answer}
```

## At the end — reconcile, then graduate

1. **Reconcile.** Do a final read of the capture file for contradictions or gaps and fix them inline. Make the "Summary / key decisions" section a clean standalone TL;DR.

2. **Make it searchable.** Ingest or index the file into whatever retrieval layer you use, so it's findable later. If that step fails, say so — don't pretend it worked.

3. **Propose graduating the insights.** The capture file is raw extraction. Now offer to graduate what's reusable into curated layers — but PROPOSE, don't auto-edit:
   - **A curated knowledge page** — a concept, decision, or analysis doc that distills what was extracted.
   - **A persistent context/instructions file** — if the grill changed the standing picture of a project.
   - **An existing skill or tool** — if the grill surfaced nuance a skill is missing. Propose the edit; don't silently rewrite a skill from here.
   - **A preference/rule** the user stated → a durable memory of that rule.

4. **Recap** in a few lines: what's captured (+ path), what's still flagged, and the single suggested next step.

## Why this skill exists

The hardest part of building a good operating system is extraction — getting what's in your head into the system as reusable context, so every downstream answer is sharper. Spending the time up front to grill thoroughly is the axe-sharpening: it gets a skill, a plan, or a strategy to 90% on the first pass instead of crawling there over ten iterations. The capture file makes that extraction durable; the indexing makes it retrievable; the graduation step makes it compound.


---

## Procedência

Duas linhagens, combinadas de propósito:

- **O arquivo de captura** — checkpoint a cada rodada, o disco como fonte de
  verdade — vem da versão de [gusinov/grill-me](https://github.com/gusinov/grill-me).
- **A árvore de decisão, a fronteira, as rodadas e o despacho de sub-agentes para
  buscar fatos** vêm de
  [mattpocock/skills](https://github.com/mattpocock/skills) (`skills/productivity/grilling`).

A versão do Pocock **não grava nada em disco**: o produto dela é entendimento
compartilhado na conversa. Aqui isso não basta — a sessão de plan mode que vem
depois lê a spec do arquivo, e é essa separação que impede o plano de herdar o
que foi dito e não foi capturado. Se você adotar o upstream puro, perde a ponte
entre as duas sessões.
