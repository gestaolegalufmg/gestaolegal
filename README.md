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

2. Copie o arquivo de configuração de exemplo:
```bash
cp docker-compose.override.example.yml docker-compose.override.yml
```

3. Inicie os containers:
```bash
docker-compose up -d
```

O sistema estará disponível em:
- Aplicação: http://localhost:5000
- Adminer (gerenciador de banco de dados): http://localhost:8080
- Mailpit (servidor de email para desenvolvimento): http://localhost:8025

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

### Executando Testes

O projeto possui comandos especializados no Makefile para execução dos testes:

```bash
# Executa os testes localmente
# Obs.: Para isso, é necessário estar em um ambiente Python com as dependências [dev] instaladas
make tests

# Executa os testes em um ambiente dockerizado
make tests_dockerized
```

Os testes são executados com o pytest e incluem testes de interface usando Playwright. O comando `make tests` irá:
1. Iniciar os containers necessários
2. Inicializar o ambiente de teste
3. Executar os testes com o pytest

### Comandos Úteis do Makefile

```bash
# Inicia os containers
make up

# Limpa os volumes (apenas em ambiente de desenvolvimento)
make clean

# Inicializa o ambiente (apenas em ambiente de desenvolvimento)
make initialize_environment
```

### Contribuindo

Por favor, leia o [guia de contribuição](CONTRIBUTING.md) antes de enviar pull requests.

## Suporte

Para reportar erros ou sugerir melhorias, consulte o [guia de issues](https://github.com/gestaolegalufmg/gestaolegal/wiki/Como-reportar-erros-ou-sugerir-melhorias).

## Licença

Leia [LICENSE](LICENSE)
