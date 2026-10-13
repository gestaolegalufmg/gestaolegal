# Guia de contribuição

## Ambiente de desenvolvimento

Siga a [instalação no README](README.md#instalação) para configurar o `.env`
e iniciar a stack. Para usar os dados de demonstração, configure
`FLASK_ENV=development` ou `testing`; o seed e o reset recusam produção.

Após aplicar as migrations, execute:

```bash
make seed ARGS="--dry-run"
make seed
```

O comando usa `scripts/seed_database.py`. Ele cria `admin@ufmg.br`,
`orient@ufmg.br`, `estag_direito@ufmg.br` e `colab_ext@ufmg.br`, com senha
inicial `123456` (substituível por `SEED_PASSWORD`). Reexecutar preserva
as senhas e os registros existentes. O script `scripts/seed_local.py` é uma
alternativa via API, com contas próprias, para testar endpoints e uploads.

## Reset periódico da demo

Para restaurar uma demo descartável, use `scripts/reset_demo.sh` no host Docker.
Ele para a API, apaga e recria o banco, aplica migrations, roda o seed e inicia
a API. Configure `DEMO_DB_NAME` no `.env` com o mesmo nome de `DB_NAME` e
atualize a imagem da API para incluir os scripts antes da primeira execução.
O usuário MySQL precisa de permissões de `DROP` e `CREATE` nesse banco.

O agendamento a cada seis horas, as variáveis para a stack de QA e os requisitos
do host estão em [Reset automático do banco de demo](README.md#reset-automático-do-banco-de-demo).
O cron deve usar o caminho absoluto do script e um usuário com acesso ao Docker.
Não configure esse agendamento em bancos com dados que devam ser preservados.

Se o reset falhar após a parada, a API permanece parada. Corrija a causa e rode
novamente o script; não há rollback da exclusão do banco. Os anexos no volume
não são removidos, embora seus registros sejam apagados.

## Verificação das alterações

```bash
uv run pytest tests/
uv run pytest tests/scripts/test_seed_database.py tests/scripts/test_reset_demo_database.py -q
cd web && npm run check && npm run lint
```

Os testes dos scripts verificam o seed em SQLite e simulam a orquestração do
reset, sem apagar um banco MySQL real. Alterações em migrations também exigem
conferir que há um único head (`uv run alembic -c migrations/alembic.ini heads`)
e validar a execução em um MySQL descartável antes de usar o reset na demo.

## Relatar problemas

Oi, pessoal!

Siga as orientações abaixo para reportar os bugs encontrados no sistema ou sugerir melhorias.

## Instruções de Postagem

1. Pense bem. Ao escrever um relatório de um problema, tente se colocar na posição do desenvolvedor e se perguntar: "O que eu gostaria de saber para ser capaz de investigar e consertar esse problema?"
2. Exclusividade. Cada problema encontrado deve ser reportado em uma mensagem própria. Diferentes problemas, diferentes mensagens.
3. Título. Insira um título objetivo e claro: ao invés de "problema no cadastro de assistidos", experimente "não consigo cadastrar um assistido PJ como administrador";
4. Numeração. Inclua um passo a passo detalhado de como você chegou no erro, de preferência numerados.
5. Descrição. Descreva o (i) problema em si, (ii) o tipo de login utilizado (administrador, estagiário, etc.), (iii) o navegador utilizado, (iv) e tudo mais que for ajudar a quem for resolver o problema.
6. Imagens. Use e abuse de capturas de tela, legendas para elas, highlights na captura e etc.

Como postar um erro?

Cada erro deverá ser postados como uma Issue separada, para facilitar o acompanhamento:

![](https://user-images.githubusercontent.com/55855366/110985390-2dda5000-834b-11eb-82d3-d8061da082e7.png)

Depois de clicar em 'New Issue', basta preencher os campos seguindo as instruções acima.
![](https://user-images.githubusercontent.com/55855366/110985770-99bcb880-834b-11eb-9f63-75a9fdc1b366.png)
