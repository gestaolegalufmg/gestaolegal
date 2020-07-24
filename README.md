# gestaolegaldaj
Sistema desenvolvido para Divisão de Assistência Judiciária da Faculdade de Direito da UFMG no primeiro semestre de 2020. Esse sistema tem como objetivo auxiliar o gerenciamento e funcionamento da DAJ em seus dias de serviço.

# Guia de instalação
1. Instale o Python 3.7 (Recomenda-se também criar um ambievente virtual - Docker ou virtualenv)
2. Baixe as dependências: `pip install -r requirements.txt`
3. Na raiz do repositório, execute o comando `python app.py`
4. Em um navegador, acesse o `localhost:5000`

# Alteração do BD
String de conexão: mysql+pysql://username:password@host:port/database

```
flask db init
flask db migrate
flask db upgrade
```