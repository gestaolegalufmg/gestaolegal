# Plano da #190 — anexos em volume privado

Base: `master` em `c7cd60b`. Planejamento solicitado após escolha por volume privado, sem Garage/S3. Nenhuma implementação ou migração foi executada nesta etapa.

## Resultado esperado

Arquivos de casos, eventos e biblioteca geral ficam em armazenamento persistente fora dos diretórios públicos. A aplicação entrega os anexos pelas rotas autenticadas existentes. URLs estáticas antigas deixam de entregar documentos, inclusive quando sobram arquivos legados no disco.

Escopo: armazenamento, migração, proteção do acesso estático e preservação das verificações atuais de acesso. A definição de novas permissões por papel continua na #159; arquivos gerais continuam compartilhados entre unidades, conforme a modelagem atual.

## 1. Configuração e infraestrutura

- Criar `PRIVATE_FILES_ROOT`, com padrão `/data/gestaolegal/uploads` no container. Subpastas: `casos`, `eventos` e `arquivos`.
- Montar um volume Docker nomeado `private_uploads` nesse caminho para a API. Usar o isolamento padrão por projeto Compose, sem nome global que misture desenvolvimento, QA e produção.
- O processo de migração de anexos será um comando operacional da mesma imagem, com o volume privado montado e as origens legadas montadas somente para leitura. Não executar cópia de arquivos dentro de uma migration Alembic nem automaticamente no startup.
- Ajustar `docker-compose.yml`, `docker-compose.qa.yml` e conferir a composição com os overrides de desenvolvimento. QA hoje monta `/opt/gestaolegal/arquivos` em `/code/gestaolegal/static/arquivos`: esse destino precisa sair da configuração final.
- Atualizar `.env.example`, README e instruções de backup. Validar na inicialização que a raiz resolvida não está dentro de nenhum diretório público, incluindo o `app.static_folder` real; `STATIC_ROOT_DIR` sozinho não define a pasta estática do Flask.
- A configuração incorreta deve falhar explicitamente; nunca voltar silenciosamente a gravar em `static`. Validar escrita na raiz privada e limitar as permissões ao usuário/grupo do serviço.
- Excluir diretórios de uploads legados, privados e manifestos de migração do contexto de build em `.dockerignore`. O Dockerfile usa `COPY . /code`; documentos não devem entrar em imagens novas.

## 2. Camada pequena de armazenamento local

Criar `gestaolegal/services/private_file_storage.py`, com operações de salvar, resolver para leitura e remover. A raiz vem da configuração da aplicação em execução, evitando constantes de caminho capturadas no import.

- Guardar referências relativas, por exemplo `casos/<uuid>_<nome-seguro>.pdf`, e nunca caminhos absolutos do servidor.
- Gerar nomes únicos com UUID, preservando um nome seguro reconhecível. Definir limite para o nome e para a referência completa compatível com as colunas de 300 caracteres; preservar a extensão. Não permitir que o cliente forneça o caminho de destino.
- Aceitar apenas as três categorias conhecidas; validar a categoria esperada para cada operação.
- Recusar caminhos absolutos, `..`, referências inválidas e arquivos/symlinks que escapem da raiz/categoria. Diretórios sob controle exclusivo da aplicação; criação exclusiva para impedir sobrescrita por colisão.
- Gravar em temporário dentro do volume, finalizar a gravação e publicar o arquivo apenas quando completo. Remover temporários em caso de falha.
- Não haverá fallback de leitura/exclusão para caminhos arbitrários ou pastas públicas. Compatibilidade de caminhos antigos pertence ao migrador, não ao download em produção.
- Usar headers de download com `Content-Disposition: attachment` e `Cache-Control: private, no-store` nas respostas de anexos.

Arquivos principais: `config.py`, `__init__.py`, novo storage, `arquivo_service.py`, `caso_service.py`, `evento_service.py` e controllers de arquivos/casos.

## 3. Integrar os três fluxos e preservar consistência

**Casos e arquivos gerais:** substituir `file.save`, `os.path.exists` e `os.remove` diretos pelo storage. Preservar regras atuais de tipos/tamanho e autorização. Arquivos gerais legados que hoje resolvem `ARQUIVOS_DIR/nome` serão normalizados pela migração.

**Eventos:** retirar dos handlers `create_evento` e `update_evento` a montagem de `STATIC_ROOT_DIR/eventos` e a gravação direta. O service recebe o upload e valida caso, unidade e dados antes de escrever. Hoje a criação grava antes da checagem do caso; isso pode deixar arquivo órfão após um erro de acesso.

Aplicar o ciclo de vida a todos os grupos:

1. Validar dados e autorização antes da gravação.
2. Criar arquivo novo, sem sobrescrever o anterior.
3. Confirmar a transação de banco que aponta para o novo arquivo.
4. Se a transação falhar, remover o novo e manter o antigo.
5. Após commit bem-sucedido, remover o anterior quando não houver outras referências a ele. Na exclusão, confirmar a alteração no banco antes de apagar o conteúdo.
6. Falha de limpeza após commit gera registro para reconciliação; não simular rollback de uma operação já confirmada. Não existe transação atômica conjunta de banco e filesystem.

O inventário deve identificar referências compartilhadas. Evitar apagar arquivos ainda referenciados por outro registro; o migrador produzirá destinos separados por registro quando necessário.

As URLs e as verificações de unidade do caso permanecem. Download de evento excluído/inativo deve ser recusado, mesmo se uma falha de limpeza deixou bytes no volume. Isso exige teste específico, pois a validação atual de evento não verifica `status` em todos os caminhos.

## 4. Banco e frontend

Manter as colunas existentes para referências relativas:

| Grupo | Referência |
|---|---|
| Arquivo de caso | `arquivosCaso.link_arquivo` |
| Anexo de evento | `eventos.arquivo` |
| Arquivo geral | `arquivos.caminho`; `nome` continua sendo o nome original |

- Migration Alembic para ampliar `eventos.arquivo` de 100 para 300 caracteres, alinhando às outras referências. Não truncar dados num downgrade: verificar tamanho antes e recusar a redução se houver valores incompatíveis.
- A migration de esquema não move nem reescreve arquivos. O script operacional faz a conversão de referências.
- Manter os campos JSON atuais, agora com caminhos relativos; não expor a raiz privada.
- Conferir as telas de caso e de detalhe/edição de evento, que extraem nomes com `split('/')`. A ficha de caso também faz `split('_').pop()`, o que mutila nomes: ajustar para retirar apenas o prefixo gerado conhecido, preservando os demais underscores.
- Preservar o nome original quando disponível. Para registros históricos que guardam só nome sanitizado/caminho, usar esse nome e registrar que o original exato não pode ser reconstruído.
- Frontend continua baixando pelas rotas autenticadas; não criar links estáticos para as referências relativas.

## 5. Bloquear acesso público, inclusive durante a transição

- Acrescentar bloqueio explícito no Flask para `/static/casos`, `/static/eventos` e `/static/arquivos`, incluindo descendentes e variantes normalizadas; retornar 404 em GET/HEAD. Manter os assets públicos legítimos.
- Conferir o proxy efetivamente usado em cada ambiente e bloquear os mesmos diretórios caso ele entregue estáticos diretamente. Bloqueio somente no nginx do frontend não protege acesso direto à porta da API.
- Levantar eventuais aliases públicos adicionais durante o inventário operacional e incluí-los na verificação.
- Colocar a aplicação em manutenção durante a virada, impedindo também escrita direta na API. Bloquear o acesso público antigo antes de iniciar o serviço novo.
- Ao final, mover todas as sobras das pastas públicas de uploads para quarentena privada, inclusive órfãos que não constam no banco. Não excluir definitivamente arquivos no mesmo passo da migração.

## 6. Migrador de anexos existentes

Criar `scripts/migrar_arquivos_privados.py` com fases explícitas de inventário/simulação, aplicação e verificação. Executável novamente sem duplicar arquivos ou refazer alterações já concluídas.

**Inventário, sem alterações:**

- Receber origens legadas e mapeamentos explícitos dos prefixos antigos para seus mounts de leitura. Não confiar no caminho armazenado no banco nem procurar pelo disco inteiro.
- Consultar registros ativos e inativos dos três grupos, incluindo arquivos gerais sem `caminho`; conferir tabelas legadas adicionais contra o esquema real de BH/NL antes de declarar o inventário completo.
- Identificar ausentes, links inválidos, caminhos externos, nomes repetidos, referências compartilhadas, órfãos e diferenças entre bancos e checkout.
- Gerar manifesto privado com origem, categoria, tabela/ID, referência anterior, destino, tamanho, SHA-256 e estado. Não versionar dados de assistidos nem manifestos reais.
- Ausentes e referências ambíguas impedem marcar a migração como integralmente validada; preservar a referência para diagnóstico e exigir tratamento explícito de cada exceção.

**Aplicação, com escrita da aplicação suspensa:**

1. Fazer backup consistente do banco e das origens e confirmar que o backup não é público.
2. Copiar os arquivos para destinos únicos no volume privado; verificar tamanho e SHA-256.
3. Atualizar a referência de cada registro somente após a cópia verificada. Conferir que o valor anterior ainda corresponde ao manifesto.
4. Registrar progresso recuperável. Ao retomar, validar o destino já existente e o estado real do banco; não confiar apenas num marcador de sucesso no manifesto.
5. Verificar todas as referências finais e produzir resumo de migrados, ausentes, exceções e quarentena. Não remover origens automaticamente nesse script.

As origens físicas e o banco efetivamente implantados precisam ser inventariados antes da execução. O repositório descreve bases BH/NL e versões legadas; não presumir que uma mudança na 3.0 já corrige a instância antiga.

## 7. Testes e verificações

### Automáticos

- Storage: gravação/leitura/remoção, nomes repetidos, nomes longos, caracteres especiais, categoria errada, caminho absoluto, `..`, symlink de escape e falha de gravação.
- API dos três grupos: upload/download/substituição/exclusão; download anônimo recusado; caso/unidade incorretos recusados; arquivo inexistente; evento excluído não baixável; resposta não expõe raiz absoluta.
- Simular rollback do banco e falha na limpeza: o arquivo anterior deve continuar disponível se a alteração não foi confirmada; o novo não pode ficar referenciado sem ter sido gravado.
- Testar o bloqueio público com arquivo de fato existente na pasta estática real da aplicação. **Não basta um 404 porque a fixture usa outra pasta.** Manter asset público sintético acessível para evitar bloqueio excessivo.
- Migrador: caminhos absolutos legados, geral sem `caminho`, nomes iguais em origens diferentes, referências compartilhadas, arquivo ausente, interrupção/retomada, reexecução e checksum divergente.
- Fixtures usam diretório temporário privado, separado de `app.static_folder`, em vez de redefinir apenas `STATIC_ROOT_DIR` como hoje.
- Rodar a suíte de API (`rtk make test`) após os testes focados. Verificar migration em MySQL, porque SQLite não verifica o limite real de `varchar`; validar os comandos de frontend existentes se as telas forem alteradas.

### Em QA

- Validar configuração Compose efetiva, mounts e permissão de escrita.
- Ensaio da migração em base isolada; dados reais, se necessários, permanecem privados.
- Conferir download com sessão, sem sessão e pela unidade errada, em casos e eventos; arquivo geral segue a regra atual de compartilhamento.
- Conferir URLs públicas antigas pelo domínio e pelo acesso direto à API. Nenhuma deve entregar bytes de anexos.
- Recriar o container da API e verificar a persistência dos anexos.
- Restaurar banco e volume de um backup em ambiente separado e comparar hashes/downloads.

## 8. Sequência de entrega e reversão

1. Implementar proteção estática, storage, configuração e testes básicos.
2. Integrar casos, eventos e arquivos gerais; ampliar coluna; ajustar nomes nas telas.
3. Implementar e testar migrador; documentar backup, limpeza e retomada.
4. Ensaiar integralmente em QA e reunir evidências de aceitação.
5. Na implantação: manutenção/bloqueio público → backup → schema → cópia e atualização de referências → verificação → quarentena das origens públicas → aplicação nova → conferência externa → reabrir escrita.

Reversão antes de reabrir escrita: restaurar o banco e a configuração compatíveis com o snapshot; manter o bloqueio público ativo. Se a aplicação antiga não funcionar com esse bloqueio, continuar em manutenção até corrigir, sem reexpor os documentos.

Reversão depois de novas escritas requer reconciliar uploads/alterações posteriores; restaurar simplesmente o banco anterior perderia essas operações. Preservar volume, manifesto e origens privadas até concluir a validação. Não remover o volume com `down -v`; manter backup externo com retenção documentada.

## Critérios para fechar a #190

- [ ] Novos uploads dos três grupos existem somente na raiz privada persistente.
- [ ] Downloads passam pelas rotas autenticadas e pelas verificações atuais de acesso.
- [ ] URLs públicas antigas não entregam documentos, pelo proxy nem diretamente pela API.
- [ ] Anexos históricos foram migrados e verificados; exceções foram reconciliadas explicitamente.
- [ ] Não restam cópias de uploads em diretórios públicos ou nas novas imagens.
- [ ] Substituição, exclusão e rollback não quebram referências válidas.
- [ ] Recriação de container mantém os anexos; restauração de backup foi testada.
- [ ] A configuração foi implantada e verificada no ambiente afetado. PR integrado sozinho não fecha a exposição em produção.
