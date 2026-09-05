# Revalidação das issues abertas — 05/09/2026

Foram consultadas as **28 issues abertas** de `gestaolegalufmg/gestaolegal`, seus corpos e os comentários relevantes. A análise foi confrontada com o checkout e com o `master` remoto, incluindo o merge de unidades, PR #406.

- Base remota: [`c7cd60bb5def8522fdd98fbdb3a5d799aaadce28`](https://github.com/gestaolegalufmg/gestaolegal/commit/c7cd60bb5def8522fdd98fbdb3a5d799aaadce28).
- Checkout: `6d1a2194cf4823305642c2fcc8c88e1e4ec5d9de`, 31 commits atrás após atualizar a referência remota. Nenhum checkout, merge ou alteração de código foi feito.
- Método: leitura de implementação, requisitos, testes existentes e documentação. **Não executei testes nem reproduzi os fluxos no navegador; não consultei produção.** Testes citados abaixo são cobertura encontrada, não resultados desta execução.
- A triagem anterior em `analise-issues-abertas.md` foi preservada. Este relatório corrige e complementa aquele documento.
- Nenhuma issue foi fechada, editada ou comentada nesta análise. “Resolvido no código” não comprova implantação nem correção de dados legados.

## Conclusão

**#213 é a candidata mais forte a fechamento por fluxo substituído/atendido na 3.0.** #114, #179 e #316 merecem reformulação ou encerramento por escopo obsoleto, com as ressalvas abaixo. Não há evidência para fechar em lote as outras issues.

A limpeza anterior já ocorreu no GitHub: por exemplo, #73, #124, #136, #137, #157, #169, #175, #177, #194 e #322 estão fechadas. As propostas de multiempresa #267, #272, #273 e #274 também estão fechadas; `docs/unidades.md` registra a escolha por unidades dentro da instituição e instâncias separadas para outras instituições. Não são novos fechamentos a realizar.

## Candidatas a fechamento ou reformulação

| Issue | Conclusão | Evidência e recomendação |
|---|---|---|
| [#213 — Erro ao editar caso para trocar arquivo](https://github.com/gestaolegalufmg/gestaolegal/issues/213) | Forte candidata a encerramento na 3.0 | A troca ocorre diretamente na ficha, com ação **Substituir** e `PUT /caso/{id}/arquivos/{id}`. Há testes de substituição, rejeição de não-PDF e arquivo inexistente. A edição carrega `user/opcoes`, sem depender da listagem administrativa. O próprio comentário de 2022 diz que o erro não foi reproduzido. Recomendo encerrar como fluxo antigo substituído, deixando explícita a versão; não como causa original diagnosticada. [Interface][caso-page], [service][caso-service], [testes][caso-tests]. |
| [#114 — Sócios e enquadramento de PJ](https://github.com/gestaolegalufmg/gestaolegal/issues/114) | Especificação de tela obsoleta; necessidade de negócio não resolvida | Não há campos `enquadramento`/`socios` no frontend atual. O modelo `AssistidoPessoaJuridica` permanece como legado. A documentação de paridade registra que esse módulo não foi migrado porque estava inativo na versão examinada. Os comentários históricos mostram que ele existiu em versões anteriores: não é correto concluir que nunca existiu. Recomendo substituir o pedido de reorganização por uma decisão explícita sobre voltar a coletar esses dados; se descartado, encerrar como obsoleto. Os dados básicos de PJ e representante continuam no cadastro de atendido. [Paridade][paridade], [formulário][atendido-form]. |
| [#179 — Permissões na página de casos](https://github.com/gestaolegalufmg/gestaolegal/issues/179) | Relato genérico desatualizado; candidata a consolidação | O corpo já afirma que o erro 500 foi resolvido; o restante remete a uma matriz de permissões em imagem, sem cenários textuais atuais. #159 e #203 já cobrem problemas concretos de arquivos e deferimento. Recomendo confrontar a matriz histórica com as regras desejadas e consolidar apenas as pendências equivalentes. Não há evidência suficiente para declarar toda a matriz atendida. |
| [#316 — Implementar komodo](https://github.com/gestaolegalufmg/gestaolegal/issues/316) | Escopo ambíguo e premissa arquitetural a revisar | O título fala em **Komodo**, mas o corpo descreve **Komodor para Kubernetes**. São nomes distintos. Não encontrei integração correspondente; a infraestrutura versionada é Docker Compose. Se o pedido realmente depende de Kubernetes, é candidato a obsolescência; se pretendia Komodo para administrar a stack atual, precisa ser reescrito. Ausência de implementação, por si só, não justifica fechar. |

## Funcionalidade existente, mas decisão ou validação ainda necessária

| Issue | Conclusão | Evidência e próximo passo |
|---|---|---|
| [#310 — Cor do login de Nova Lima](https://github.com/gestaolegalufmg/gestaolegal/issues/310) | Premissa mudou; identidade visual específica não foi implementada | A Fase A de unidades já está integrada. O login continua usando um gradiente comum e `/logo-gestao-legal.png`; só sincroniza unidades depois de autenticar. Decidir se o sistema unificado terá identidade comum ou identidade por unidade/entrada. O merge de unidades não resolveu a cor solicitada. [Login][login], [unidades][unidades]. |
| [#315 — Lançar plantão](https://github.com/gestaolegalufmg/gestaolegal/issues/315) | Implementação existe; issue é de homologação e lançamento | Há escala, abertura, fila e presença, agora por unidade; existem testes de API nos módulos correspondentes. A issue pede conferir regras e colocar em uso. Só código existente não comprova esses critérios. Reescrever como checklist de homologação, incluindo BH e NL. |
| [#403 — Painel lateral de diligências](https://github.com/gestaolegalufmg/gestaolegal/issues/403) | Parcialmente atendida | A tabela mostra preview da descrição, mas o painel lateral sequencial não existe. O preview é truncado; não equivale automaticamente à leitura integral em sequência. Validar com quem usa se atende a necessidade antes de dispensar o painel. [Ficha do caso][caso-page], `web/src/lib/components/data-table.svelte:252`. |

## Relatos que ainda exigem reprodução

| Issue | O que o código permite concluir | Recomendação |
|---|---|---|
| [#311 — Botões/texto na listagem](https://github.com/gestaolegalufmg/gestaolegal/issues/311) | O próprio autor não conseguiu repetir o defeito. A interface foi reescrita. | Pedir um cenário atual com tela, perfil, largura e dados. Candidata a encerramento por não reproduzível se a conferência na 3.0 não mostrar o problema; não declarar corrigida só pela reescrita. |
| [#363 — Endereço apagado ao cadastrar atendido](https://github.com/gestaolegalufmg/gestaolegal/issues/363) | O preenchimento de CEP ainda desabilita campos, mas o POST usa `form.data` em modo SPA. Isso não sustenta a explicação automática de que campos HTML desabilitados somem do envio. | Manter aberta até reproduzir o cadastro, inspecionando estado do formulário, validação e payload. [Formulário][atendido-form]. |
| [#326 — Orientação jurídica perde dados](https://github.com/gestaolegalufmg/gestaolegal/issues/326) | O formulário atual tem `resetForm: false` e tratamento de erro. Não encontrei persistência de rascunho nesse fluxo. JWT dura 12 horas e cookie de login 8 horas, mas isso não prova nem descarta expiração de uma sessão já antiga. | Manter aberta; reproduzir após inatividade, falha de rede e sessão expirada. Não afirmar que nada foi implementado, nem que autosave já resolveria a causa. [Formulário de orientação][oj-form], `gestaolegal/utils/jwt_auth.py:19`. |

## Pendências confirmadas na implementação ou no esquema versionado

| Issue | Diagnóstico atualizado |
|---|---|
| [#159 — Arquivos sem restrição por papel](https://github.com/gestaolegalufmg/gestaolegal/issues/159) | Continua aberta. Listar, subir, baixar e substituir exigem autenticação, sem distinção de papel nessas rotas. **Agora há guarda da unidade do caso no service**; portanto, a frase “qualquer autenticado em qualquer caso” ficou ampla demais. O problema de papel permanece dentro dos casos acessíveis na unidade. [Controller][caso-controller], [service][caso-service]. |
| [#183 — Múltiplos arquivos em evento](https://github.com/gestaolegalufmg/gestaolegal/issues/183) | `Evento.arquivo` continua singular e o diálogo recebe um arquivo. O upload múltiplo de arquivos do caso não atende a anexos múltiplos do evento. `gestaolegal/models/evento.py`, `web/src/lib/components/evento-dialog.svelte`. |
| [#190 — Arquivos em pasta pública](https://github.com/gestaolegalufmg/gestaolegal/issues/190) | A configuração continua derivando `UPLOADS` e `ARQUIVOS_DIR` de `STATIC_ROOT_DIR`, e o Flask mantém a rota estática padrão. As rotas autenticadas não eliminam o caminho estático no arranjo padrão. Há base concreta para manter a issue prioritária; não foi testada exposição em produção nesta análise. [Configuração][config], `gestaolegal/__init__.py:11`. |
| [#191 — Caracteres fora de latin1](https://github.com/gestaolegalufmg/gestaolegal/issues/191) | A migration inicial contém `latin1_general_ci`; não encontrei migration de conversão geral para UTF-8. Manter aberta e conferir as collations efetivas antes de corrigir dados. A contagem de 106 colunas da triagem anterior não foi revalidada nos bancos. `migrations/versions/ed1b0a0a61a6_.py`. |
| [#203 — Deferimento e permissões](https://github.com/gestaolegalufmg/gestaolegal/issues/203) | O deferimento **existe no formulário de edição**, inclusive justificativa de indeferimento. Faltam restrições por papel no caminho de edição e nas rotas dedicadas; a guarda por unidade não substitui isso. O diálogo dedicado permanece sem uso pelas rotas do frontend. A issue atual já reconhece o formulário; o relatório antigo é que ficou incorreto. [Formulário][caso-form], [controller][caso-controller], [service][caso-service]. |
| [#205 — Número de processo longo](https://github.com/gestaolegalufmg/gestaolegal/issues/205) | `processos.numero` continua `BigInteger` e o frontend usa `z.number()`. Além do limite do banco para números de 20 dígitos, números acima de `Number.MAX_SAFE_INTEGER` podem perder precisão no JavaScript. É necessário tratar o identificador como texto de ponta a ponta. Isso identifica um defeito atual, mas não prova a causa de todos os erros históricos de visualização/link. [Tabela][tables], `web/src/lib/forms/schemas/processo-schema.ts:5`. |
| [#309 — Dashboard Superset](https://github.com/gestaolegalufmg/gestaolegal/issues/309) | Existem relatórios próprios, mas não encontrei Superset nem a entrega do dashboard e dos filtros pedidos. Continua sendo funcionalidade pendente; não está obsoleta só porque existem relatórios. |
| [#324 — Pessoas do caso clicáveis](https://github.com/gestaolegalufmg/gestaolegal/issues/324) | Os quatro responsáveis são valores textuais em `responsiblesData`, renderizados pelo `InfoCard`. **Não basta inserir links:** o `+page.ts` do perfil recusa a visualização de terceiros para não-admins, e `GET /api/user/<id>` exige admin. A solução precisa definir a exposição dos contatos para os perfis atendidos pela issue. [Ficha][caso-page], [acesso ao perfil][perfil], [API de usuários][user-controller]. |
| [#325 — Painel de notificações](https://github.com/gestaolegalufmg/gestaolegal/issues/325) | Sino, contador e ações existem, mas o sino leva a `/notificacoes`; não há painel com abas Lidas/Não lidas. **Ressalva ao histórico da issue:** `caso_editado` só avisa novos integrantes; `evento_criado` só avisa o responsável do evento. Isso não equivale a avisar todos os envolvidos sobre qualquer edição/evento. Se essa expectativa original permanece, ainda precisa entrar no escopo. [Sino][sino], [gatilhos][notificacoes]. |
| [#364 — Questionário de assistido](https://github.com/gestaolegalufmg/gestaolegal/issues/364) | Persistem diferenças de ordem, títulos e condições: renda familiar vem antes de benefício; “Qual benefício?” aparece para benefícios além de “Outro”; saúde não oferece “Não informou”. **Correção da triagem anterior:** já existem checkboxes “Possui outros imóveis?” e “Possui veículos?”, com campos condicionais; não faltam por completo. [Formulário][assistido-form]. |
| [#365 — Cadastro de atendido](https://github.com/gestaolegalufmg/gestaolegal/issues/365) | CPF e e-mail continuam obrigatórios. Há outras divergências: número e bairro obrigatórios no frontend; CNPJ exigido quando PJ constituída; vários dados do representante exigidos em bloco além do nome. A issue já absorve a necessidade das fechadas #176/#244, mas ainda menciona essas duas como abertas. Corrigir esse texto ao tratar a especificação. [Schema][atendido-schema], `gestaolegal/models/atendido_input.py:23`. |
| [#366 — Plantão dá 404](https://github.com/gestaolegalufmg/gestaolegal/issues/366) | O atalho da home aponta para a escala, mas o breadcrumb ainda gera `href="/plantao"`; não existe página correspondente. Portanto, o problema não foi eliminado em toda a navegação. [Breadcrumb][breadcrumb]. |
| [#401 — Aviso de caso desatualizado](https://github.com/gestaolegalufmg/gestaolegal/issues/401) | Não encontrei regra de X dias sem evento nem banner de desatualização. Datas de criação/modificação exibidas na ficha não atendem ao pedido. [Ficha][caso-page]. |
| [#402 — Aviso dos meus casos parados](https://github.com/gestaolegalufmg/gestaolegal/issues/402) | Não encontrei cálculo/lista de casos parados para o usuário. O sistema de notificações existente pode ser reutilizado, mas seus gatilhos atuais não fazem essa detecção. [Gatilhos][notificacoes]. |
| [#404 — E-mail de casos parados](https://github.com/gestaolegalufmg/gestaolegal/issues/404) | A infraestrutura de e-mail existe, mas não encontrei seleção periódica de casos inativos nem envio dessa mensagem. SMTP e recuperação de senha não entregam essa funcionalidade. `gestaolegal/utils/mail_service.py`, `gestaolegal/services/password_reset_service.py`. |
| [#405 — Modelos de texto de diligência](https://github.com/gestaolegalufmg/gestaolegal/issues/405) | O diálogo mantém descrição livre, sem catálogo/seleção de modelos. A lista de tipos de evento não equivale a textos prontos. `web/src/lib/components/evento-dialog.svelte`, `web/src/lib/constants/tipo_evento.ts`. |

## Issues agregadoras

| Issue | Situação |
|---|---|
| [#312 — Adoção de diligências](https://github.com/gestaolegalufmg/gestaolegal/issues/312) | Manter como agregadora de #401–#405. O preview já existente está corretamente separado do trabalho restante. |
| [#337 — Bugs do frontend](https://github.com/gestaolegalufmg/gestaolegal/issues/337) | Manter como agregadora: #363–#366 continuam abertas. Fechar outras sub-issues não encerra esse escopo. |

## Ordem sugerida

1. Segurança: #190, #159 e #203. Atualizar as descrições para considerar a unidade ativa.
2. Fluxo de atendimento: #363, #365 e #364; investigar #326 por risco de perda de texto.
3. Integridade dos dados: #205 e #191, considerando as migrations e a importação de Nova Lima.
4. Navegação: #366 e #324; a segunda também exige uma decisão de acesso aos contatos.
5. Limpeza do backlog: avaliar encerramento de #213 e reformulação de #114/#179/#316; registrar homologação em #315.

## Fontes de código fixadas na revisão analisada

[caso-page]: https://github.com/gestaolegalufmg/gestaolegal/blob/c7cd60bb5def8522fdd98fbdb3a5d799aaadce28/web/src/routes/%28dashboard%29/casos/%5Bid%5D/%2Bpage.svelte
[caso-service]: https://github.com/gestaolegalufmg/gestaolegal/blob/c7cd60bb5def8522fdd98fbdb3a5d799aaadce28/gestaolegal/services/caso_service.py
[caso-tests]: https://github.com/gestaolegalufmg/gestaolegal/blob/c7cd60bb5def8522fdd98fbdb3a5d799aaadce28/tests/api/test_caso_api.py#L1169
[caso-controller]: https://github.com/gestaolegalufmg/gestaolegal/blob/c7cd60bb5def8522fdd98fbdb3a5d799aaadce28/gestaolegal/controllers/caso_controller.py
[caso-form]: https://github.com/gestaolegalufmg/gestaolegal/blob/c7cd60bb5def8522fdd98fbdb3a5d799aaadce28/web/src/lib/forms/caso-form.svelte#L209
[paridade]: https://github.com/gestaolegalufmg/gestaolegal/blob/c7cd60bb5def8522fdd98fbdb3a5d799aaadce28/docs/paridade-v2-v3.md
[unidades]: https://github.com/gestaolegalufmg/gestaolegal/blob/c7cd60bb5def8522fdd98fbdb3a5d799aaadce28/docs/unidades.md
[login]: https://github.com/gestaolegalufmg/gestaolegal/blob/c7cd60bb5def8522fdd98fbdb3a5d799aaadce28/web/src/routes/login/%2Bpage.svelte
[atendido-form]: https://github.com/gestaolegalufmg/gestaolegal/blob/c7cd60bb5def8522fdd98fbdb3a5d799aaadce28/web/src/lib/forms/atendido-form.svelte
[atendido-schema]: https://github.com/gestaolegalufmg/gestaolegal/blob/c7cd60bb5def8522fdd98fbdb3a5d799aaadce28/web/src/lib/forms/schemas/atendido-schema.ts
[assistido-form]: https://github.com/gestaolegalufmg/gestaolegal/blob/c7cd60bb5def8522fdd98fbdb3a5d799aaadce28/web/src/lib/forms/assistido-form.svelte
[oj-form]: https://github.com/gestaolegalufmg/gestaolegal/blob/c7cd60bb5def8522fdd98fbdb3a5d799aaadce28/web/src/lib/forms/orientacao-juridica-form.svelte
[config]: https://github.com/gestaolegalufmg/gestaolegal/blob/c7cd60bb5def8522fdd98fbdb3a5d799aaadce28/gestaolegal/config.py#L117
[tables]: https://github.com/gestaolegalufmg/gestaolegal/blob/c7cd60bb5def8522fdd98fbdb3a5d799aaadce28/gestaolegal/database/tables.py#L210
[perfil]: https://github.com/gestaolegalufmg/gestaolegal/blob/c7cd60bb5def8522fdd98fbdb3a5d799aaadce28/web/src/routes/%28dashboard%29/usuarios/%5Bid%5D/%2Bpage.ts
[user-controller]: https://github.com/gestaolegalufmg/gestaolegal/blob/c7cd60bb5def8522fdd98fbdb3a5d799aaadce28/gestaolegal/controllers/user_controller.py#L61
[sino]: https://github.com/gestaolegalufmg/gestaolegal/blob/c7cd60bb5def8522fdd98fbdb3a5d799aaadce28/web/src/lib/components/notificacao-bell.svelte
[notificacoes]: https://github.com/gestaolegalufmg/gestaolegal/blob/c7cd60bb5def8522fdd98fbdb3a5d799aaadce28/gestaolegal/services/notificacao_service.py#L140
[breadcrumb]: https://github.com/gestaolegalufmg/gestaolegal/blob/c7cd60bb5def8522fdd98fbdb3a5d799aaadce28/web/src/lib/components/dynamic-breadcrumb.svelte#L19
