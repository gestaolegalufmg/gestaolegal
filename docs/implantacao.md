# Implantação e desenvolvimento

Há dois arquivos independentes. Use `docker-compose.yml` para instalar imagens
publicadas em produção ou QA; use `docker-compose.dev.yml` para desenvolver.
Não combine os dois e não mantenha um `docker-compose.override.yml` automático.
O Compose da fusão pertence ao repositório `gestaolegal-fusao`.

## Implantação nova

1. Copie `.env.example` para `.env` e configure credenciais e tokens próprios.
2. Defina `COMPOSE_PROJECT_NAME`, `IMAGE_TAG`, `MYSQL_VOLUME_NAME` e
   `UPLOADS_VOLUME_NAME`. Cada instalação deve usar nomes próprios de volumes.
   API, frontend e migração usam a mesma tag; escolha um SHA ou versão que tenha
   sido publicado com sucesso nas duas imagens do GHCR.
3. Apenas para uma instalação vazia, crie os dois volumes com `docker volume
   create NOME`. Um volume existente deve ser reutilizado, nunca substituído por
   um vazio. O Compose não cria os volumes de implantação automaticamente.
4. Execute `docker compose -f docker-compose.yml config --quiet`, depois
   `docker compose -f docker-compose.yml pull` e
   `docker compose -f docker-compose.yml up -d`.
5. Configure o proxy HTTPS do servidor para `127.0.0.1:WEB_PORT` (padrão 5001).
   Confira `FRONTEND_URL` e `CORS_ORIGINS` com o domínio público.

As migrações terminam antes de a API iniciar. `migrate` com saída 0 é normal;
os outros serviços principais devem permanecer ativos. O banco e os anexos
ficam em volumes externos, preservados inclusive por `down -v`; não use
`docker volume rm` nesses volumes. Backup continua sendo necessário.

`DB_USER`, `DB_PASSWORD` e `DB_NAME` são usados tanto pela API quanto pela
inicialização do MySQL. Em volumes já inicializados, trocar as variáveis não
altera usuários ou senhas do banco. Dentro da rede, a API sempre usa `db:3306`,
mesmo que `DB_PORT` publique outra porta no host. A raiz interna dos uploads é
sempre `/data/gestaolegal/uploads`.

## QA e serviços opcionais

QA usa o mesmo arquivo de implantação. Para capturar mensagens e disponibilizar
Adminer, defina no `.env`:

```dotenv
COMPOSE_PROFILES=mailpit,adminer
MAIL_SERVER=mailpit
MAIL_PORT=1025
MAIL_USE_SSL=false
MAIL_USE_TLS=false
```

Mailpit e Adminer ficam acessíveis apenas pelo host ou por túnel SSH, nas portas
8025 e 8080 (configuráveis). Habilitar o profile não modifica as variáveis SMTP.
Produção pode usar SMTP externo, com `COMPOSE_PROFILES` vazio, ou Postfix via
profile `mail` e volume externo de DKIM. Veja [E-mail](email.md).
Não ative o reset ou o seed no acervo real restaurado da fusão.

## Transição de glteste

Referência conferida por SSH em 24/10/2026:

- Arquivo instalado: `/opt/gestaolegal/docker-compose.yml` (pasta sem Git).
- Volumes: `gestaolegal_mysql_data` e `gestaolegal_uploads`.
- Serviços antigos: `qa_front`, `qa_backend`, `qa_db`, `qa_migrate`, `qa_mailpit`
  e `qa_adminer`. Rede antiga: `qa_network`, com alias `api` para o backend.
- Nginx vem da imagem; Caddy acessa o frontend em `127.0.0.1:5001`.

A nova configuração preserva os volumes, mas troca os serviços pelos nomes
`web`, `api`, `db`, `migrate`, `mailpit` e `adminer`, sem nomes globais de
containers e sem uma rede global. O Nginx encontra o serviço `api` diretamente.

**Faça a transição somente depois da fusão/carga em andamento e em janela
combinada. Não execute estes passos enquanto outro operador estiver atuando.**

1. Registre as imagens/digests, faça backup do banco e dos anexos e guarde o
   Compose e `.env` atuais em local protegido. Confira os mounts com
   `docker inspect qa_db qa_backend`; os nomes acima devem corresponder aos
   dados carregados. Não recrie os volumes.
2. Prepare uma cópia do novo Compose e do `.env` fora da instalação ativa.
   Configure `MYSQL_VOLUME_NAME=gestaolegal_mysql_data`,
   `UPLOADS_VOLUME_NAME=gestaolegal_uploads`, `COMPOSE_PROJECT_NAME=gestaolegal`
   e a tag aprovada. Confira que `DB_USER/DB_PASSWORD/DB_NAME` correspondem às
   credenciais existentes: o Compose antigo usava `MYSQL_USER/MYSQL_PASSWORD/
   MYSQL_DATABASE` para o banco. Troque `MAIL_SERVER=qa_mailpit` por `mailpit`
   se aplicável e habilite os profiles de QA. Não exponha senhas em logs.
3. Valide a cópia com `docker compose --project-directory PASTA_PREPARADA
   --env-file PASTA_PREPARADA/.env -f PASTA_PREPARADA/docker-compose.yml
   config --quiet` e baixe suas imagens com os mesmos argumentos e `pull`.
4. Ainda com o arquivo antigo em `/opt/gestaolegal`, execute nessa pasta
   `docker compose -f docker-compose.yml down` **sem `-v`**. Isso remove os
   containers `qa_*`, evitando dois MySQL acessando o mesmo volume.
5. Instale os arquivos preparados, mantendo os backups protegidos. Suba com
   `docker compose -f docker-compose.yml up -d`.
6. Confira a saída de `migrate`, saúde do banco, acesso pelo domínio, login,
   contagens de dados e download de anexos. Ajuste automações que usavam nomes
   `qa_*` para os serviços novos. Prefira `docker compose ... exec api/db`.

Se precisar reverter, pare primeiro a nova stack e restaure a configuração e
as imagens anteriores. Migrações podem mudar o banco: voltar apenas a imagem
não reverte o schema; use o backup compatível quando necessário.

## Desenvolvimento

`make up` executa `docker compose -f docker-compose.dev.yml up -d --build`.
Não requer `IMAGE_TAG` nem volumes externos. Para executar `make seed` pelo
host, configure `FLASK_ENV=development` no `.env` local. O Mailpit é obrigatório nessa
stack e a API força `FLASK_ENV=development` e `MAIL_SERVER=mailpit`.

Use projetos e portas diferentes de produção/QA. O volume MySQL é isolado
pelo nome do projeto; os anexos ficam em `DEV_UPLOADS_PATH` (padrão `./uploads`).
As fontes, configurações do frontend e migrations vêm do checkout. Alterações
nas dependências precisam de rebuild. A esteira de worktrees seleciona esse
arquivo por `COMPOSE_FILE` no `.env.worktree`.

Para usar uma instalação local antiga, confira os volumes e a pasta de uploads
antes da primeira subida. Arquive o override antigo e transfira suas portas
para as variáveis equivalentes. Neste checkout, o antigo override publicava o
frontend em 5002: `WEB_PORT=5002 make up` mantém essa porta. Nenhuma dessas
alterações exige apagar bancos ou executar seed automaticamente.
