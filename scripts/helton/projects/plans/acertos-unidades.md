# Plano: acertos de unidades

Plano para o loop Helton. Criado em 05/09/2026, base `670aec8`. A spec é
`docs/unidades.md` — modelagem (§4), o que a Fase A entregou e o que ficou
adiado (§5.1) e as pendências (§6). Este arquivo só diz **o que construir, onde
e como provar**.

Escopo: as quatro pendências de código que sobraram da Fase A. **Fora de
escopo** a Fase B (importação de Nova Lima, já entregue em
`scripts/importar_unidade.py`), a execução de qualquer coisa contra QA ou
produção, e a conferência das telas em navegador — que é trabalho de humano,
não de loop.

Nenhum item aqui mexe em schema. **Este canteiro não cria migration**, portanto
não disputa o head do Alembic com nenhum outro.

## Resultado esperado

Com esta fatia mesclada:

1. as seis rotas de processo de um caso recusam caso de outra unidade, como já
   fazem eventos, arquivos e histórico;
2. o admin consegue reativar pela interface uma unidade que desativou;
3. a listagem de usuários do admin sabe filtrar por unidade quando pedirem, e
   segue mostrando todos por padrão;
4. `coluna_unidade()` não depende mais do `default=UNIDADE_PADRAO_ID` para os
   caminhos de produção — ou, se depender, está documentado por quê.

## Estado atual (levantado em 05/09/2026)

- **`gestaolegal/controllers/caso_controller.py:159-250`**: as seis rotas de
  processo (`GET`/`POST` da coleção, `GET`/`PUT`/`DELETE` do item) chamam o
  `ProcessoService` direto, sem passar pelo `CasoService`. `docs/unidades.md`
  registra só a listagem, mas **o furo é maior**: `validate_processo_for_caso`
  (`processo_service.py:83`) confere que o processo pertence ao caso e nada
  mais, e `create` (`:105`) grava sem olhar o caso. Com o id de um caso de
  outra unidade, dá para listar, ler, criar, editar e inativar processo.
- O padrão da casa está em `caso_service.py:596` e `evento_service.py:36`, os
  dois `_caso_da_unidade_ativa`: buscam o caso por
  `find_by_id(caso_id, unidade_id=RequestContext.get_unidade_ativa())` e
  devolvem `None`/`False` quando o caso não é da unidade. `ProcessoService` não
  tem nada disso — nem importa `RequestContext`.
- **`unidade_repository.py:26` (`list_ativas`)** filtra `unidades.c.ativa` sem
  alternativa, e é a única leitura de lista que existe: `UnidadeService.list_ativas`
  (`unidade_service.py:20`) e `GET /api/unidades/`
  (`unidade_controller.py:14`) só repassam. Desativar pela tela `/unidades`
  faz a unidade sumir da própria tela que a desativou.
- **`usuario_service.py:69` (`search`)** monta as cláusulas sobre a tabela
  `usuarios` e nunca toca em `usuarios_unidades`.
- **`tables.py:24` (`coluna_unidade`)**: o `default=UNIDADE_PADRAO_ID` é
  *client-side* do SQLAlchemy, não DDL — mexer nele **não** pede migration. Ele
  entrou porque 149 testes quebravam enquanto os services ainda não gravavam a
  coluna (§5.1 da spec).

## Decisões já tomadas (não reabrir)

- Listagem de usuários: **filtro opcional, padrão todos**. O admin continua
  vendo todo mundo quando não pede nada; só filtra quem pedir. Filtrar sempre
  esconderia de um admin de BH justamente quem ele precisa achar para vincular
  a uma unidade.
- Reativar unidade é `?incluir_inativas=1` na listagem, como a spec previu —
  não uma rota nova.
- O filtro por unidade continua morando no **service**, não no repositório
  (§5.1 da spec). O repositório ganha parâmetro opcional; quem decide é o
  service, lendo o `RequestContext`.

## O que construir

### 1. Guarda da unidade nas rotas de processo

`ProcessoService` ganha o `_caso_da_unidade_ativa` que os outros dois services
já têm, e o aplica em `search_by_caso`, `validate_processo_for_caso` e
`create`. Caso que não é da unidade ativa se comporta como caso inexistente —
`NotFoundException`, não 403: dizer "existe, mas não é sua" já vaza a
existência do caso.

Reusar `CasoRepository.find_by_id(caso_id, unidade_id=…)`; não escrever
consulta nova. As rotas do controller não mudam de assinatura — quem passa a
recusar é o service.

Atenção ao `DELETE` (`caso_controller.py:236`): é `@authorized("admin")`, e
admin tem todas as unidades. A guarda vale para ele igual — ele navega com uma
unidade por vez (decisão 4 da spec).

### 2. `?incluir_inativas=1` na listagem de unidades

- `UnidadeRepository.list_ativas` → `listar(incluir_inativas: bool = False)`,
  mantendo a ordenação por nome. Sem parâmetro, comportamento de hoje.
- `UnidadeService` repassa.
- `unidade_controller.listar` lê o parâmetro com `StringBool`, como o
  `show_inactive` das outras listagens (ver `caso_controller.py:166`), e **só
  aceita `incluir_inativas=1` de admin** — a rota é `@authenticated(unidade=False)`
  porque alimenta o seletor do cabeçalho de todo mundo, e o seletor não pode
  passar a oferecer unidade desativada. Usuário comum pedindo inativas recebe
  a lista de ativas, sem erro.
- Front: a tela `/unidades` (`web/src/routes/(dashboard)/unidades/+page.ts`)
  passa a pedir com o parâmetro e a marcar visualmente a unidade inativa, com o
  botão de reativar. O seletor do cabeçalho continua pedindo **sem** o
  parâmetro. Conferir `web/src/lib/stores/unidade.ts`: se a unidade guardada no
  `localStorage` foi desativada, a store precisa cair para a primeira ativa em
  vez de mandar um `X-Unidade-Id` que o back recusa.

### 3. Filtro opcional por unidade na listagem de usuários

`GET /api/user` aceita `unidade` com dois valores: ausente (todos, como hoje) e
`ativa` (só quem tem vínculo com a unidade do header). `UsuarioService.search`
ganha o parâmetro e, quando pedido, restringe pelos ids de
`usuarios_unidades` — `UnidadeRepository` já tem o JOIN pronto em
`unidades_do_usuario`; o caminho inverso (usuários de uma unidade) é o método
que falta.

Não mexer na paginação por fora: o filtro entra na consulta, não em pós-
processamento da página, senão a contagem mente.

Front: a tela de usuários ganha o filtro só se couber sem reforma — se não
couber, deixar a API pronta e registrar. O que **não** pode é a tela passar a
filtrar sozinha sem o usuário pedir.

### 4. Reavaliar o `default=UNIDADE_PADRAO_ID`

Tirar o `default` de `coluna_unidade()` (`tables.py:24-33`) e rodar `make test`.
Cada quebra é uma pergunta a responder, não um teste a consertar no automático:

- quebrou um `INSERT` de fixture/`conftest`/seed? Corrigir o teste, passando a
  unidade — é o teste que dependia da rede de segurança.
- quebrou um caminho de **produção** (service ou repositório inserindo sem
  unidade)? É bug real de isolamento: consertar o código e escrever o teste que
  o denuncia.

Se sobrar caminho legítimo sem unidade — algum `INSERT` cru que só o
`migrations/` ou o `create_admin` faz —, **manter o default e trocar o
comentário** por um que diga qual é esse caminho, em vez de repetir a
justificativa da Fase 3 que já não vale. Decidir e registrar é o entregável;
remover a todo custo não é.

## Como provar

Testes novos, em `tests/api/`:

- `test_processo_api.py`: para cada uma das seis rotas, caso de outra unidade
  responde 404; caso da unidade ativa segue funcionando. O teste do `DELETE`
  com admin é o que fecha o buraco — admin tem as duas unidades e é o caso em
  que um filtro mal escrito passa despercebido.
- `test_unidade_api.py`: listagem sem parâmetro não traz inativa; admin com
  `incluir_inativas=1` traz; não-admin com o parâmetro recebe só as ativas;
  reativar por `PUT` devolve a unidade ao seletor.
- `test_user_api.py`: sem `unidade`, o admin vê usuário das duas unidades; com
  `unidade=ativa`, só os da unidade do header, e o **total da paginação**
  acompanha.
- A remoção do `default` não ganha teste próprio: quem prova é a suíte inteira
  passando sem ele.

Comandos: `make test`. Mexeu em `web/`:
`cd web && npm run check && npm run lint`.

Manual, na stack do canteiro: desativar uma unidade pela tela `/unidades`,
confirmar que ela some do seletor do cabeçalho e continua visível na tela de
unidades, e reativá-la.

## Travas

- `review_required`: a guarda das rotas de processo e o filtro opcional de
  usuários — são regra de acesso por unidade, e a spec pede olho humano nisso
  no merge. A mudança em `coluna_unidade()` também: ela decide se uma linha sem
  unidade explícita ainda tem para onde cair.
- `human_gate`: nada. Nenhum item toca `.env*`, workflow, banco de QA ou de
  produção, nem enfraquece a verificação — os quatro **acrescentam** teste.
- Sem migration, portanto sem `creates_migration` no manifesto.
