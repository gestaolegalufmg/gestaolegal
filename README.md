# Gestão Legal UFMG

<p align="center">
  <img src="docs/images/gestao-legal-capivara.png" alt="Gestão Legal — capivara advogada" width="560">
</p>

Sistema de Gestão de Assistências Judiciárias e Escritórios de Advocacia Modelo

---

## Sobre

Sistema desenvolvido pelo projeto de extensão da Faculdade de Direito da UFMG [Gestão Legal](https://gestaolegal.direito.ufmg.br/) para auxiliar o gerenciamento e funcionamento da [Divisão de Assistência Judiciária - DAJ](https://daj.direito.ufmg.br/).

O **Gestão Legal é uma iniciativa do LAB P² — Laboratório de Tecnologias Públicas para o Setor Público**, da Faculdade de Direito da UFMG.

O laboratório desenvolve e integra tecnologias livres e abertas para atender às necessidades das instituições públicas. Reúne estudantes, professores e servidores em projetos que articulam ensino, pesquisa, extensão e gestão, promovendo formação interdisciplinar, compartilhamento de soluções e autonomia tecnológica. [Conheça o LAB P²](https://labp2.direito.ufmg.br/o-projeto/).

<table>
  <tr>
    <td align="center"><a href="https://labp2.direito.ufmg.br/"><img src="docs/images/labp2.png" alt="LAB P²" width="220"></a></td>
    <td align="center"><a href="https://www.direito.ufmg.br/"><img src="docs/images/fdufmg.png" alt="Faculdade de Direito da UFMG" width="100"></a></td>
    <td align="center"><a href="https://ufmg.br/"><img src="docs/images/ufmg.png" alt="Universidade Federal de Minas Gerais" width="220"></a></td>
  </tr>
  <tr>
    <td align="center">LAB P²</td>
    <td align="center">Faculdade de Direito</td>
    <td align="center">UFMG</td>
  </tr>
</table>

### Funcionalidades

- Gestão de casos jurídicos e processos
- Cadastro e acompanhamento de clientes
- Controle de orientações jurídicas
- Gerenciamento de equipe (orientadores, estagiários, colaboradores)
- Acompanhamento de eventos e prazos processuais
- Upload e gerenciamento de documentos
- Organização dos atendimentos por unidade
- Escalas de plantão, fila de atendimento e registro de presença

---

## Requisitos

- **Python 3.11+**
- **Docker** e **Docker Compose** (recomendado)
- **Node.js 24** (apenas para desenvolvimento do frontend, como nas imagens Docker)

---

## Instalação

### Usando Docker (Recomendado)

1. **Clone o repositório**
   ```bash
   git clone https://github.com/gestaolegalufmg/gestaolegal.git
   cd gestaolegal
   ```

2. **Configure as variáveis de ambiente**
   ```bash
   cp .env.example .env
   ```

   Edite o arquivo `.env` e configure as credenciais necessárias.

3. **(Opcional) Configure override para desenvolvimento**

   Para customizar o ambiente de desenvolvimento (portas, volumes, variáveis extras):
   ```bash
   cp docker-compose.override.example.yml docker-compose.override.yml
   ```

   Edite o `docker-compose.override.yml` conforme necessário.

4. **Inicie o ambiente**
   ```bash
   make up
   ```

5. **Acesse o sistema**
   - Frontend: http://localhost:5001
   - API Backend: http://localhost:5000

6. **Crie o administrador inicial**

   Acesse http://localhost:5001/setup-admin e use o token configurado em `ADMIN_SETUP_TOKEN`.

---

## Dados de demonstração (seed)

Após aplicar as migrations, execute o seed direto no banco, sem precisar da API:

```bash
make seed ARGS="--dry-run"  # simula a carga e faz rollback
make seed                 # grava os dados
make seed ARGS="--unidade BH"  # opcional: apenas uma unidade ativa
```

O comando usa `uv` e lê `DB_HOST`, `DB_PORT` (padrão `3306`), `DB_NAME`,
`DB_USER` e `DB_PASSWORD` do ambiente ou do `.env` da pasta atual. Para executar
no host com MySQL no Docker, use `DB_HOST=127.0.0.1 make seed` e a porta publicada.
Para executar dentro do container, após `make up` (que aplica as migrations):

```bash
docker compose exec -e DB_PORT=3306 api python scripts/seed_database.py --dry-run
docker compose exec -e DB_PORT=3306 api python scripts/seed_database.py
```

O script `scripts/seed_database.py` cria quatro usuários compartilhados e,
por unidade ativa, dois atendidos, dois casos com processos, quatro eventos,
duas orientações jurídicas, dois lembretes e uma escala com duas marcações.
Os dados são fictícios; CPFs são placeholders e processos não têm número real.
Não são criados anexos nem enviados e-mails. As unidades vêm das migrations.

Contas: `admin@ufmg.br`, `orient@ufmg.br`,
`estag_direito@ufmg.br` e `colab_ext@ufmg.br`.
A senha inicial é `123456`, configurável por `SEED_PASSWORD`.
Reexecutar preserva senhas e registros existentes, sem duplicá-los. Datas de
novos registros são relativas à execução; reexecutar não renova a agenda.
Não altere os identificadores do seed (e-mails, descrições e nome da escala)
se quiser preservar a deduplicação. Execute apenas uma instância por vez.

A carga é transacional: uma falha desfaz todas as inserções daquela execução.
`--dry-run` também pode consumir valores de auto incremento no MySQL, embora
não persista registros. Use apenas em desenvolvimento/testes; a execução é
bloqueada com `FLASK_ENV=production`. O script não cria nem altera o schema.
O seed via API existente, `scripts/seed_local.py`, continua disponível para
cenários que precisam exercitar endpoints e uploads.


### Reset automático do banco de demo

`scripts/reset_demo.sh` para a API, **apaga e recria o banco inteiro**, aplica
as migrations e executa `seed_database.py`. As contas e senhas voltam aos valores
do seed a cada execução. O usuário MySQL precisa de permissão para `DROP` e
`CREATE` no banco configurado.

No `.env` exclusivo da demo, configure `FLASK_ENV=development` ou `testing` e
`DEMO_DB_NAME` com o mesmo valor de `DB_NAME`. Essa confirmação é obrigatória.
O script recusa ambientes de produção e bancos de sistema. Dentro do Docker,
`DB_PORT` deve ser a porta interna do MySQL (`3306`), mesmo que a porta publicada
no host seja outra.

Com a stack já iniciada e a imagem da API atualizada com os scripts, execute no
host (requer Bash, Docker Compose e `flock`):

```bash
/opt/gestaolegal/scripts/reset_demo.sh
```

Para agendar às 00h, 06h, 12h e 18h, no fuso do servidor, adicione ao `crontab`
de um usuário com acesso ao Docker e escrita no checkout/log:

```cron
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
0 */6 * * * /opt/gestaolegal/scripts/reset_demo.sh >> /opt/gestaolegal/reset-demo.log 2>&1
```

Ajuste o caminho ao checkout da demo. Para a stack de QA, cujo serviço se chama
`qa_backend`, use `RESET_API_SERVICE=qa_backend` antes do comando. Se o arquivo
Compose tiver outro nome, informe também `COMPOSE_FILE` com seu caminho absoluto.
O script usa o `.env` e o Compose do checkout, independentemente da pasta atual.

Há bloqueios contra resets simultâneos no host e no MySQL. A API fica indisponível
durante o reset; se ele falhar, permanece parada. Corrija a causa e execute o
script novamente. A exclusão do banco não tem rollback. Os arquivos de anexos
no volume permanecem no disco, mas seus registros no banco são apagados.
O script não instala o cron automaticamente.

---

## Documentação

- 📖 [Wiki do Projeto](https://github.com/gestaolegalufmg/gestaolegal/wiki) - Documentação completa
- 🏗️ [Arquitetura](https://github.com/gestaolegalufmg/gestaolegal/wiki/Arquitetura) - Detalhes técnicos e stack
- 🔧 [Guia de Contribuição](CONTRIBUTING.md) - Como contribuir
- [Problemas conhecidos](docs/known_issues.md) - Limitações atuais e correções já entregues
- 🐛 [Reportar Issues](https://github.com/gestaolegalufmg/gestaolegal/issues) - Bugs e melhorias

---

## Contribuindo

Contribuições são bem-vindas! Por favor:

1. Leia o [guia de contribuição](CONTRIBUTING.md)
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Abra um Pull Request

---

## Licença

Este projeto está licenciado sob os termos especificados no arquivo [LICENSE](LICENSE).

---

## Suporte

- **Issues:** [GitHub Issues](https://github.com/gestaolegalufmg/gestaolegal/issues)
- **Wiki:** [Documentação](https://github.com/gestaolegalufmg/gestaolegal/wiki)
- **Site:** [gestaolegal.direito.ufmg.br](https://gestaolegal.direito.ufmg.br/)

---

**Status:** Em desenvolvimento ativo — versão 3.0

Uma iniciativa do [LAB P²](https://labp2.direito.ufmg.br/), da [Faculdade de Direito da UFMG](https://www.direito.ufmg.br/).
