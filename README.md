# Gestão Legal UFMG
## Sistema de Gestão de Assistências Judiciárias e Escritórios de Advocacia Modelo

Sistema desenvolvido pelo projeto de extensão da Faculdade de Direito da UFMG [Gestão Legal](https://gestaolegal.direito.ufmg.br/).

Este sistema tem como objetivo auxiliar o gerenciamento e funcionamento da [Divisão de Assistência Judiciária - DAJ](https://daj.direito.ufmg.br/) da Faculdade de Direito da UFMG.

## Requisitos

- Python 3.11 ou superior
- Docker e Docker Compose

## Instalação

### Usando Docker (Recomendado)

1. Clone o repositório:
```bash
git clone https://github.com/gestaolegalufmg/gestaolegal.git
cd gestaolegal
```

2. Copie e configure o arquivo de ambiente:
```bash
cp .env.example .env
# Edite o .env com suas credenciais de desenvolvimento
```

3. Inicie o ambiente de desenvolvimento:
```bash
make up
```

**Pronto!** O ambiente será automaticamente inicializado com:
- ✓ Banco de dados criado e configurado
- ✓ Todas as migrações aplicadas
- ✓ Usuário administrador criado

O sistema estará disponível em:
- **Frontend**: http://localhost:5001
- **Backend API**: http://localhost:5000

**Credenciais padrão**:
- Email: `admin@gl.com`
- Senha: `123456`

### Configuração de Segurança

⚠️ **IMPORTANTE**: Antes de executar o sistema, configure as credenciais de segurança.

#### Para Desenvolvimento
1. Copie o arquivo de configuração de exemplo:
```bash
cp docker-compose.override.example.yml docker-compose.override.yml
```

2. Edite o arquivo `docker-compose.override.yml` e atualize as credenciais:
   - `JWT_SECRET_KEY`: Chave secreta para sessões Flask
   - `DB_PASSWORD`: Senha do banco de dados
   - `MYSQL_ROOT_PASSWORD`: Senha root do MySQL

#### Para Produção
1. Configure as variáveis de ambiente no seu servidor:
   - `JWT_SECRET_KEY`: Chave secreta para sessões Flask
   - `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_NAME`: Configurações do banco de dados
   - `MYSQL_ROOT_PASSWORD`: Senha root do MySQL

2. **Nunca** commite credenciais de produção no repositório

### Instalação Manual

1. Clone o repositório:
```bash
git clone https://github.com/gestaolegalufmg/gestaolegal.git
cd gestaolegal
```

2. Configure as credenciais (veja seção "Configuração de Segurança" acima):
```bash
cp docker-compose.override.example.yml docker-compose.override.yml
# Edite o arquivo docker-compose.override.yml com suas credenciais
```

3. Crie e ative um ambiente virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

4. Instale as dependências:
```bash
pip install -e ".[dev]"
```

5. Execute as migrações:
```bash
flask db upgrade
```

6. Inicie o servidor:
```bash
flask run
```

## Desenvolvimento

### Comandos Úteis

O projeto possui diversos comandos no Makefile para facilitar o desenvolvimento:

```bash
# Ver todos os comandos disponíveis
make help

# Gerenciamento de containers
make up          # Inicia o ambiente (auto-inicializa o banco de dados)
make down        # Para os containers
make restart     # Reinicia os containers
make build       # Reconstrói as imagens
make clean       # Remove containers e volumes
make reset       # Limpa tudo e reinicia do zero

# Logs e debugging
make logs        # Ver logs de todos os containers
make logs-api    # Ver logs apenas da API
make logs-db     # Ver logs do banco de dados
make shell-api   # Abrir shell no container da API
make shell-db    # Abrir MySQL shell no banco

# Testes
make test        # Executar testes
make test-cov    # Executar testes com relatório de cobertura
make test-watch  # Executar testes em modo watch
```

### Executando Testes

```bash
# Testes com pytest
make test

# Testes com cobertura
make test-cov

# Modo watch (re-executa ao salvar arquivos)
make test-watch
```

Os testes são executados com o pytest e incluem testes de interface usando Playwright.

### Contribuindo

Por favor, leia o [guia de contribuição](CONTRIBUTING.md) antes de enviar pull requests.

## Suporte

Para reportar erros ou sugerir melhorias, consulte o [guia de issues](https://github.com/gestaolegalufmg/gestaolegal/wiki/Como-reportar-erros-ou-sugerir-melhorias).

## Licença

Leia [LICENSE](LICENSE)
