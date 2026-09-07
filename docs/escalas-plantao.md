# Escalas de plantão por unidade

A página Plantão → Escalas de Plantão lista os períodos da unidade ativa.
Cada escala tem nome, dias de atendimento, início e fim das inscrições.
Todos os horários de configuração são interpretados no fuso de Brasília.

Usuários escolhem seus dias somente entre o início (inclusive) e o fim
(exclusive) das inscrições. A consulta nunca encerra ou apaga registros.
Depois do prazo, escala e confirmações continuam acessíveis.

Administradores e colaboradores do projeto criam/configuram escalas e podem
ajustar suas inscrições fora do prazo. Criação, configuração, inscrições,
retiradas e cancelamento registram autor, horário e detalhes no histórico.
O limite de dias por pessoa e as vagas por papel são contados por escala.
Permanece a regra anterior que libera excedentes quando todos os dias estão
lotados para o papel. A criação de novas escalas não altera as anteriores.

Dias com inscrições ativas não podem ser retirados da configuração.
Cancelar uma escala é uma ação explícita: bloqueia novas inscrições e edição,
preserva os registros e retira a escala das pendências e do relatório de
plantões válidos. Não altera os registros de entrada/saída efetivamente feitos.

## Dados e atualização

Migration `d1e2f3a4b5c6`, após `c0d1e2f3a4b5`:

- `plantao` passa a representar escalas, com nome, legado, cancelado e histórico.
- `dias_plantao.plantao_id` e `dias_marcados_plantao.plantao_id` são FKs obrigatórias.
- Registros antigos são agrupados por unidade e identificados como legado,
  somente para consulta, incluindo registros inativos e datas ausentes.
- Datas, usuários, confirmações e status anteriores são preservados. Havendo
  várias configurações antigas na unidade, elas são mantidas, e os dias e
  marcações ficam no agrupamento de menor ID. O esquema antigo não permite
  inferir a configuração original de cada marcação.

Antes de atualizar uma instalação, faça backup do banco. Execute a migration
antes de iniciar a nova aplicação. Crie uma nova escala para abrir inscrições;
os agrupamentos de legado não são reabertos automaticamente.

Downgrade é bloqueado quando há escalas novas, pois o modelo anterior não
consegue representá-las. Nesse caso, o retorno à versão anterior exige backup.

## API

- `GET /api/plantao/escalas`: listagem da unidade ativa.
- `POST /api/plantao/escalas`: nova escala.
- `GET /api/plantao?escala_id=ID`: escala, inscrições e situação calculada.
- `GET/PUT /api/plantao/configuracao?escala_id=ID`: consultar/alterar configuração.
- `POST/DELETE /api/plantao/marcacoes?escala_id=ID`: inscrever/retirar inscrições próprias.
- `POST /api/plantao/escalas/ID/cancelar`: cancelamento administrativo.

Todo acesso valida unidade ativa e permissão. IDs de outra unidade retornam
404. Escritas de inscrições e configuração bloqueiam a linha da escala na
transação para serializar validações de limites e duplicidade.
