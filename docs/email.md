# E-mail

Hoje o sistema envia um único e-mail: o link de recuperação de senha. Esta
página descreve como o envio está montado e o que precisa existir em produção.

## Desenho

```
API (Flask-Mail)  ──SMTP──▶  mailpit   (desenvolvimento: captura, não entrega)
                  ──SMTP──▶  mail      (produção: Postfix + OpenDKIM)  ──▶  MX do destinatário
                                                                       └──▶  relay autenticado (opcional)
```

A aplicação só fala SMTP em texto simples com um MTA da própria stack, pela
rede interna do Docker — quem assina com DKIM e entrega é o MTA, não a API.
Falha de envio nunca derruba a requisição: `gestaolegal/utils/mail_service.py`
registra o erro no log e devolve `False`.

## Desenvolvimento

O `docker-compose.override.yml` sobe o **Mailpit**, que aceita qualquer
mensagem e não entrega nada para fora — testar recuperação de senha não manda
e-mail para ninguém. As mensagens capturadas ficam em
<http://localhost:8025> (porta ajustável por `MAILPIT_UI_PORT`).

Variáveis relevantes no `.env`:

```
MAIL_SERVER=mailpit
MAIL_DEFAULT_SENDER=nao-responda@gestaolegal.direito.ufmg.br
FRONTEND_URL=http://localhost:5001   # a porta em que você publica o web
```

`FRONTEND_URL` é o que monta o link do e-mail. Quem publica o `web` em outra
porta no override (5002, por exemplo) precisa ajustá-la, ou o link do e-mail
aponta para uma porta onde não há nada.

## Produção

O serviço `mail` (`boky/postfix`, Postfix com OpenDKIM embutido) está no
`docker-compose.yml` sob o profile `mail`, para não subir em desenvolvimento:

```bash
docker compose --profile mail up -d
```

Sem o profile a API sobe normalmente, mas nenhum e-mail sai — as tentativas
ficam registradas como erro no log.

Variáveis obrigatórias:

| Variável | Para quê |
|---|---|
| `MAIL_HOSTNAME` | FQDN do MTA; vira o HELO e o `myhostname` do Postfix |
| `MAIL_ALLOWED_SENDER_DOMAINS` | domínios aceitos como remetente |
| `MAIL_DEFAULT_SENDER` | endereço que assina as mensagens |
| `FRONTEND_URL` | endereço público do sistema, para o link do e-mail |

Opcionais, para repassar a um relay autenticado em vez de entregar direto:
`MAIL_RELAYHOST` (formato `[smtp.provedor.com]:587`),
`MAIL_RELAYHOST_USERNAME`, `MAIL_RELAYHOST_PASSWORD`. Vazios = entrega direta.

### Checklist de DNS (entrega direta)

Sem isto os e-mails saem, mas caem em spam ou são recusados. Recomenda-se um
**subdomínio dedicado ao envio** (ex.: `envio.gestaolegal.direito.ufmg.br`),
para que um problema de reputação não afete o e-mail institucional.

1. **A** do subdomínio → IP do servidor.
2. **SPF**: `TXT` no subdomínio → `v=spf1 ip4:<IP> -all`.
3. **DKIM**: o contêiner gera o par de chaves na primeira subida; a chave
   pública sai em `/etc/opendkim/keys/<domínio>.txt`, para publicar como `TXT`
   em `mail._domainkey.<subdomínio>` (selector `mail`).
4. **DMARC**: `TXT` em `_dmarc.<subdomínio>` → `v=DMARC1; p=none; rua=mailto:...`
   (começar monitorando, subir para `quarantine` depois).
5. **PTR reverso** do IP apontando para exatamente o valor de `MAIL_HOSTNAME`.
6. **Porta 25 de saída** liberada pelo provedor do servidor — vários bloqueiam
   por padrão. Se estiver bloqueada, use o relay autenticado.

### Duas armadilhas conhecidas

- **Permissão da chave DKIM**: o diretório montado em `/etc/opendkim/keys`
  precisa pertencer a `uid:gid 101:104` (o usuário `opendkim` da imagem). Com
  a permissão errada o Postfix **entrega sem assinar**, em silêncio; a única
  pista está em `docker compose logs mail | grep -i opendkim`, procurando a
  linha `DKIM-Signature field added`.
- **HELO genérico**: se `MAIL_HOSTNAME` não resolver ou não bater com o PTR,
  Gmail e Outlook recusam ou marcam como spam.

O volume `mail_dkim` guarda a chave privada e precisa sobreviver a
`docker compose down -v`: perdê-la obriga a gerar outra e republicar o TXT.

## Recuperação de senha

- Pedido em `/esqueci-a-senha`, redefinição em `/redefinir-senha/<token>`.
- O token é opaco (`secrets.token_urlsafe`), guardado no banco apenas como
  hash SHA-256, válido por `PASSWORD_RESET_TOKEN_TTL_MINUTES` (60) e de uso
  único. Um pedido novo invalida os anteriores.
- Conta inexistente, conta desativada e excesso de pedidos (3 em 15 minutos)
  recebem a mesma resposta de quem tem conta, para não revelar quem está
  cadastrado.
