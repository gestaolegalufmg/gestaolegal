---
name: compatibilizar
description: Compatibiliza os planos de desenvolvimento de plans/ antes de mandá-los para worktrees paralelas — varre os arquivos que cada plano reivindica, detecta choques entre eles, resolve as ambiguidades com o usuário e grava scripts/helton/projects/plans/manifest.json dizendo quais podem rodar em paralelo e quais precisam esperar. Use quando o usuário pedir para "compatibilizar os planos", "verificar choque entre planos", "analisar a interseção dos planos", "ver se dá para rodar em paralelo", "preparar a esteira" ou antes de montar mais de um canteiro de obra ao mesmo tempo.
---

# Compatibilizar planos

"Compatibilização" é o termo da engenharia civil para a conferência que cruza os
projetos de disciplinas diferentes — elétrico, hidráulico, estrutural — procurando
onde um passa por dentro do outro. É exatamente o que esta skill faz com os planos
de desenvolvimento antes de eles virarem empreitadas paralelas.

## Quando roda

Depois que os planos existem em `scripts/helton/projects/plans/<nome>.md` e antes de qualquer
`montar-canteiro.sh`. Um choque descoberto aqui custa uma conversa; descoberto
depois, custa duas branches que não fazem merge.

## O que produz

`scripts/helton/projects/plans/manifest.json`. É o único artefato, e é ele que o `/cronograma` e o
`/mobilizar-obras` leem depois.

```json
{
  "generated_at": "2026-08-09T14:00:00-03:00",
  "plans": [
    {
      "name": "onda-2",
      "file": "scripts/helton/projects/plans/onda-2.md",
      "hash": "sha256:2b1e...",
      "claims": ["app/domain/stock/**", "web/src/routes/(app)/estoque/**"],
      "creates_migration": false,
      "status": "parallel",
      "resolved_questions": [
        {"q": "O acerto de estoque zera a reserva?", "a": "Não — reserva é outra fatia."}
      ]
    },
    {
      "name": "pedido-desconto",
      "file": "scripts/helton/projects/plans/pedido-desconto.md",
      "hash": "sha256:9fa0...",
      "claims": ["app/domain/sales/**", "app/api/contracts/sales.py"],
      "creates_migration": true,
      "status": "serialized_after:schema-zero",
      "conflicts_with": ["schema-zero"],
      "resolved_questions": []
    }
  ]
}
```

`status` só assume três valores:

- `parallel` — pode montar canteiro agora.
- `serialized_after:<plano>` — espera o predecessor mergear no `develop`.
- `needs_reslicing` — o plano precisa ser reescrito antes de qualquer coisa; o
  choque não se resolve com ordem.

## Procedimento

### 1. Ler os planos

Todo `scripts/helton/projects/plans/*.md` que não seja o `manifest.json`. Se `scripts/helton/projects/plans/` não existir ou
estiver vazio, diga isso e pare — não há o que compatibilizar.

### 2. Extrair os claims de cada plano

Claim é **arquivo ou glob que o plano vai escrever**, não que vai ler. Um plano
que lê `app/domain/sales/pricing.py` para entender o markup não reivindica
esse arquivo; um plano que muda a fórmula do markup, sim.

Prefira o glob mais estreito que ainda cubra o trabalho. `app/**` como claim
não informa nada — se um plano precisa mesmo disso, ele é grande demais e o
diagnóstico é `needs_reslicing`.

Registre também `creates_migration`: o plano acrescenta arquivo em
`migrations/versions/`?

### 3. Cruzar

Dois planos chocam quando os claims se intersectam. Casos que a interseção
literal não pega e você precisa procurar à mão:

- **Migrations.** Dois planos criando migration partem do mesmo head do Alembic
  e produzem heads múltiplos no merge. Se mais de um plano tem
  `creates_migration: true`, a saída é extrair um **plano-zero de schema**: uma
  fatia só de migration, executada primeiro e de forma interativa, mergeada no
  `develop`; os demais viram `serialized_after:<plano-zero>` e partem do
  develop já migrado, tocando só código. Proponha isso ao usuário, não decida
  sozinho — o plano-zero é um plano novo, e escrevê-lo é dele.
- **Contrato de API.** Dois planos mexendo em `app/api/contracts/` ou em
  endpoints do mesmo controller colidem no `openapi_schema.json`, que é
  versionado, mesmo que os arquivos Python sejam diferentes.
- **Tipos TS gerados.** Mesma raiz do item acima: `web/src/lib/gen/schema.ts` é
  gerado e não versionado, então o choque não aparece no diff — aparece no
  `make ready` da segunda branch a mergear.
- **Catálogo de menu e permissões.** Dois planos acrescentando item de menu
  disputam `tests/test_menu_catalog_parity.py` e o catálogo que ele valida.
- **Mapa de ícones.** `web/src/lib/icons/lucide-map.ts` é lista única e
  ordenada: dois planos acrescentando ícone conflitam em linhas vizinhas.

### 4. Interrogar o usuário

Esta é a fase que a skill absorveu do `/cronograma` — a intenção é que nenhum
prd seja gravado depois com pergunta pendente, e que a rodada AFK não pare para
perguntar nada.

Pergunte **uma coisa por vez**, com uma resposta recomendada junto. Duas
famílias de pergunta:

1. **Choque entre planos** — "os dois mexem no cálculo do preço; o
   `pedido-desconto` depende do markup novo do `precificacao`, ou são
   independentes?" A resposta vira `status`.
2. **Ambiguidade dentro de um plano** — qualquer coisa que, se ficasse sem
   resposta, faria o loop autônomo escolher no escuro. A resposta vai para
   `resolved_questions` do plano, e é dali que o `/cronograma` tira o contexto
   das stories sem ter que perguntar de novo.

Não invente resposta. Se o usuário não decidir, o plano fica `needs_reslicing` —
é melhor do que uma empreitada de dez horas construída sobre um chute.

### 5. Gravar o manifesto

`hash` é o sha256 do arquivo do plano no momento da compatibilização. É o
detector de deriva: se o plano for editado depois, o `/cronograma` percebe que a
decisão registrada aqui já não corresponde ao texto e volta a perguntar.

Calcule com `sha256sum scripts/helton/projects/plans/<nome>.md`.

### 6. Relatar

Termine com o quadro: quantos planos, quais em paralelo, quais serializados e
atrás de quem, quais precisam ser refatiados, e a ordem de merge que o desenho
implica. É esse quadro que o usuário usa para decidir quantos canteiros montar.

## Fronteiras

- Não monte canteiro, não gere prd, não crie branch. Esta skill só lê planos,
  conversa e grava um JSON.
- Não edite os arquivos de plano. Se um plano precisa mudar, o diagnóstico é
  `needs_reslicing` e quem reescreve é o usuário, em sessão própria.
- Não trate como choque o fato de dois planos tocarem o mesmo *diretório* se os
  arquivos são distintos e independentes. Falso positivo serializa trabalho que
  podia ser paralelo, que é o custo que esta esteira existe para evitar.
