# Problemas conhecidos

Registro de limitações já identificadas e ainda não corrigidas. Cada item
diz o que acontece hoje, por que acontece e o que seria preciso para
resolver.

## Plantão: histórico de presença fica invisível após o encerramento

**O que acontece.** Quando a data de fechamento do plantão passa, o
encerramento automático (`PlantaoService._encerrar_se_expirado`) desativa
todos os dias e todas as marcações (`status=False`) e zera a janela. Os
registros continuam no banco, mas somem de todas as telas: escala, fila de
atendimento e confirmação de presença filtram por `status=True`.

**O relatório de horários também perde o histórico.** Em
`RelatorioRepository`, a consulta de horários de plantão filtra
`dias_marcados_plantao.status IS TRUE`, então o relatório enxerga apenas o
período vigente — pedir um intervalo de datas já encerrado devolve nada,
mesmo com os dados gravados.

**Por que não basta remover o filtro.** A coluna `status` de
`dias_marcados_plantao` acumula dois significados: marcação apagada pelo
próprio usuário e marcação desativada pelo encerramento do período. Sem
separá-los, tirar o filtro faria o relatório contar como presença o que o
usuário desmarcou.

**Como resolver.** Distinguir os dois casos — uma coluna própria para o
encerramento, ou vincular a marcação ao período de plantão — e então expor
o histórico: relatório de horários sobre períodos anteriores e listagem
dos plantões já realizados.

**Nada se perde no banco.** `dias_marcados_plantao` guarda a data literal
(`data_marcada`) e a confirmação (`aberto`, `confirmar`, `divergencia`,
`ausencia`), sem vínculo com a janela do plantão. Reconfigurar o período
não apaga marcação nenhuma. A v2 apagava os dias fisicamente ao encerrar,
deixando marcações órfãs; a 3.0 desativa em vez de apagar.

## Plantão: não há histórico de períodos configurados

A tabela `plantao` guarda um único registro, sobrescrito a cada nova
configuração (comportamento herdado da v2). Não existe listagem de
"plantões configurados": ao abrir um período novo, o anterior deixa de
existir como registro próprio. Um histórico exigiria transformar `plantao`
em vários registros e ligar `dias_plantao` a cada um, com migração dos
dados existentes.

## Casos: a API aceita qualquer valor em `situacao_deferimento`

`CasoCreateInput.situacao_deferimento` é `str`, sem conjunto fechado de
valores. Foi assim que registros com o valor legado `deferido` entraram no
banco — e eles não podiam ser editados, porque o formulário não tem essa
opção (corrigido pela migração `9b4a1c7e30df` e pela normalização na carga
do formulário). Fechar o conjunto no input evitaria a recorrência, mas
alguns testes usam `deferido` de propósito e precisariam ser revistos
junto.

## Recuperação de senha: limite de pedidos só por usuário

**O que acontece.** `PasswordResetService.solicitar` conta os pedidos de cada
usuário nos últimos 15 minutos e para de enviar acima de três, o que protege
uma caixa de entrada de ser inundada.

**O que fica de fora.** Nada limita a quantidade de tentativas por origem: um
script pode chamar `POST /api/auth/forgot-password` com milhares de endereços
diferentes. A resposta é sempre a mesma, então isso não revela quem tem conta,
mas consome recursos do servidor e do MTA.

**Como resolver.** Limitar por IP exige estado compartilhado entre os workers
do gunicorn — Flask-Limiter com Redis, ou `limit_req` no nginx à frente da
API. A segunda opção não acrescenta dependência à aplicação.
