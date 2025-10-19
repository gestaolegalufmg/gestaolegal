# Gestão Legal UFMG

Sistema de Gestão de Assistências Judiciárias e Escritórios de Advocacia Modelo

---

## Sobre

Sistema desenvolvido pelo projeto de extensão da Faculdade de Direito da UFMG [Gestão Legal](https://gestaolegal.direito.ufmg.br/) para auxiliar o gerenciamento e funcionamento da [Divisão de Assistência Judiciária - DAJ](https://daj.direito.ufmg.br/).

### Funcionalidades

- Gestão de casos jurídicos e processos
- Cadastro e acompanhamento de clientes
- Controle de orientações jurídicas
- Gerenciamento de equipe (orientadores, estagiários, colaboradores)
- Acompanhamento de eventos e prazos processuais
- Upload e gerenciamento de documentos

---

## Requisitos

- **Python 3.11+**
- **Docker** e **Docker Compose** (recomendado)
- **Node.js 18+** (apenas para desenvolvimento do frontend)

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

## Documentação

- 📖 [Wiki do Projeto](https://github.com/gestaolegalufmg/gestaolegal/wiki) - Documentação completa
- 🏗️ [Arquitetura](https://github.com/gestaolegalufmg/gestaolegal/wiki/Arquitetura) - Detalhes técnicos e stack
- 🔧 [Guia de Contribuição](CONTRIBUTING.md) - Como contribuir
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

**Status:** 🚧 Em desenvolvimento ativo - v0.1.0

Desenvolvido pelo projeto de extensão [Gestão Legal](https://gestaolegal.direito.ufmg.br/) da Faculdade de Direito da UFMG.
