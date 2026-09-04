"""Seed de dados de desenvolvimento, via API, idempotente.

Uso: uv run python scripts/seed_local.py [ids.json]

Lê o `.env` do diretório atual (a raiz do checkout ou da worktree) e fala com a
API em http://localhost:$APP_PORT (padrão 5000). Serve tanto para o checkout
principal quanto para um canteiro da esteira helton, que tem porta própria.

Variáveis (todas opcionais):
  SEED_API_URL        substitui a URL montada a partir de APP_PORT
  SEED_ADMIN_EMAIL    admin usado para semear (padrão rvnovaes@gmail.com)
  SEED_ADMIN_PASSWORD senha desse admin (padrão admin)
  ADMIN_SETUP_TOKEN   se o banco não tem usuários, cria o admin acima por
                      auth/setup-admin com este token (o mesmo do .env)
  SEED_UNIDADE_ID     manda o header X-Unidade-Id (só faz sentido depois da
                      Fase A de docs/unidades.md; antes dela é ignorado pela API)

Idempotência: usuários por e-mail, atendidos por CPF, casos por descrição,
eventos e arquivos por descrição/nome dentro do caso. Rodar duas vezes não
duplica nada. Presenças e plantões de datas passadas continuam sendo inseridos
por SQL (ver docs/paridade-v2-v3.md, seção 4).
"""

import io
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

from dotenv import load_dotenv

load_dotenv()

API = os.environ.get("SEED_API_URL") or f"http://localhost:{os.environ.get('APP_PORT', '5000')}"
API = API.rstrip("/") + "/api"
ADMIN_EMAIL = os.environ.get("SEED_ADMIN_EMAIL", "rvnovaes@gmail.com")
ADMIN_PASSWORD = os.environ.get("SEED_ADMIN_PASSWORD", "admin")
SETUP_TOKEN = os.environ.get("ADMIN_SETUP_TOKEN")
UNIDADE_ID = os.environ.get("SEED_UNIDADE_ID")
SENHA_PADRAO = "senha123"

falhas = 0


def call(method, path, token=None, body=None, files=None):
    """Chama a API e devolve o JSON decodificado, ou None em erro HTTP."""
    global falhas
    url = f"{API}/{path}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if UNIDADE_ID:
        headers["X-Unidade-Id"] = UNIDADE_ID
    data = None
    if files is not None:
        boundary = "----seedboundary"
        buf = io.BytesIO()
        for k, v in (body or {}).items():
            buf.write(
                f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
            )
        for k, (fname, content, ctype) in files.items():
            buf.write(
                f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{fname}"\r\nContent-Type: {ctype}\r\n\r\n'.encode()
            )
            buf.write(content)
            buf.write(b"\r\n")
        buf.write(f"--{boundary}--\r\n".encode())
        data = buf.getvalue()
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    elif body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        falhas += 1
        print(f"ERRO {method} {path}: {e.code} {e.read().decode()[:300]}")
        return None
    except urllib.error.URLError as e:
        sys.exit(f"seed: API inacessível em {API}: {e.reason}")


def itens(r):
    """Extrai a lista de uma resposta paginada ou de envelope {chave: [...]}."""
    d = (r or {}).get("data") or {}
    if isinstance(d, list):
        return d
    for k in ("items", "eventos", "arquivos"):
        if isinstance(d.get(k), list):
            return d[k]
    return []


def login(email, senha):
    r = call("POST", "auth/login", body={"email": email, "password": senha})
    if not r:
        sys.exit(f"seed: login falhou para {email}")
    return r["data"]["token"]


def garantir_admin():
    """Cria o admin pelo setup inicial se o banco estiver vazio."""
    r = call("GET", "auth/needs-setup")
    if r and r["data"]["needs_setup"]:
        if not SETUP_TOKEN:
            sys.exit("seed: banco sem usuários e ADMIN_SETUP_TOKEN não definido")
        r = call(
            "POST",
            "auth/setup-admin",
            body={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD, "setup_token": SETUP_TOKEN},
        )
        if not r:
            sys.exit("seed: setup-admin falhou")
        print("admin criado:", ADMIN_EMAIL)
    return login(ADMIN_EMAIL, ADMIN_PASSWORD)


admin = garantir_admin()
ADMIN_ID = call("GET", "user/me", admin)["data"]["id"]


def user(nome, email, urole, matricula):
    existente = next(
        (u for u in itens(call("GET", "user/?per_page=100&show_inactive=true", admin)) if u["email"] == email),
        None,
    )
    if existente:
        uid = existente["id"]
    else:
        base = {
            "email": email, "nome": nome, "urole": urole, "sexo": "F", "rg": "11.222.333-4",
            "cpf": "000.000.000-00", "profissao": urole, "estado_civil": "solteiro",
            "nascimento": "1995-05-15", "telefone": None, "celular": "(31) 99999-0000", "oab": None,
            "obs": "seed", "data_entrada": "2024-01-15", "data_saida": None, "matricula": matricula,
            "bolsista": False, "tipo_bolsa": None, "horario_atendimento": None, "suplente": None,
            "ferias": None, "cert_atuacao_DAJ": "sim", "inicio_bolsa": None, "fim_bolsa": None,
            "logradouro": "Rua Seed", "numero": "1", "bairro": "Centro", "cep": "30000-000",
            "cidade": "Belo Horizonte", "estado": "MG", "complemento": None,
        }
        r = call("POST", "user/", admin, base)
        if not r:
            sys.exit(f"seed: não criou o usuário {email}")
        uid = r["data"]["id"]
    # Senha conhecida sempre, para os logins abaixo funcionarem.
    call("PUT", f"user/{uid}/password", admin, {"newPassword": SENHA_PADRAO, "fromAdmin": True})
    return uid


orient = user("Olívia Orientadora", "orientadora@gl.local", "orient", "OR001")
estag = user("Eduardo Estagiário", "estagiario@gl.local", "estag_direito", "EST001")
colab = user("Carla Colaboradora Externa", "colab.ext@gl.local", "colab_ext", "CE001")
print("usuarios:", orient, estag, colab)

tok_estag = login("estagiario@gl.local", SENHA_PADRAO)
tok_orient = login("orientadora@gl.local", SENHA_PADRAO)


def atendido(nome, cpf):
    # A busca da API é por nome; o CPF confirma que é o mesmo registro.
    q = urllib.parse.quote(nome)
    for a in itens(call("GET", f"atendido/?search={q}&per_page=50", admin)):
        if a.get("cpf") == cpf:
            return a["id"]
    r = call("POST", "atendido/", admin, {
        "nome": nome, "data_nascimento": "1990-01-15", "cpf": cpf, "telefone": None,
        "celular": "(31) 98888-0000", "email": f"{cpf[:3]}@seed.local", "estado_civil": "solteiro",
        "logradouro": "Rua A", "numero": "10", "bairro": "Centro", "cep": "30000-000",
        "cidade": "Belo Horizonte", "estado": "MG", "como_conheceu": "assist",
        "procurou_outro_local": "nao", "pj_constituida": "nao", "status": 1,
    })
    return r["data"]["id"] if r else None


a1 = atendido("Maria Aparecida Seed", "111.111.111-11")
a2 = atendido("José Ribeiro Seed", "222.222.222-22")
print("atendidos:", a1, a2)


def caso(token, resp, area, desc, clientes):
    q = urllib.parse.quote(desc)
    for c in itens(call("GET", f"caso/?search={q}&per_page=50&show_inactive=true", admin)):
        if c.get("descricao") == desc:
            return c["id"]
    r = call("POST", "caso/", token, {
        "id_usuario_responsavel": resp, "area_direito": area, "situacao_deferimento": "ativo",
        "descricao": desc, "ids_clientes": [c for c in clientes if c],
    })
    if not r:
        sys.exit(f"seed: não criou o caso '{desc}'")
    return r["data"]["id"]


c_admin = caso(admin, ADMIN_ID, "civel", "Caso criado pelo ADMIN, responsável admin (seed)", [a1])
c_admin2 = caso(admin, estag, "penal", "Caso criado pelo ADMIN, responsável estagiário (seed)", [a2])
c_estag = caso(tok_estag, estag, "trabalhista", "Caso criado pelo ESTAGIÁRIO, responsável estagiário (seed)", [a1, a2])
c_orient = caso(tok_orient, ADMIN_ID, "civel", "Caso criado pela ORIENTADORA, responsável admin (seed)", [])
print("casos:", c_admin, c_admin2, c_estag, c_orient)


def evento(token, cid, tipo, desc, data):
    if any(e.get("descricao") == desc for e in itens(call("GET", f"caso/{cid}/eventos?per_page=100", admin))):
        return
    call("POST", f"caso/{cid}/eventos", token,
         {"tipo": tipo, "data_evento": data, "descricao": desc, "status": "true"}, files={})


evento(admin, c_admin, "reuniao", "Reunião inicial (criado pelo admin)", "2026-08-01")
evento(admin, c_admin, "audencia", "Audiência de conciliação (criado pelo admin)", "2026-08-10")
evento(tok_estag, c_admin, "contato", "Contato telefônico (criado pelo estagiário)", "2026-08-12")
evento(tok_estag, c_admin, "documentos", "Juntada de documentos (criado pelo estagiário)", "2026-08-20")
evento(tok_orient, c_admin, "reuniao", "Reunião de orientação (criado pela orientadora)", "2026-08-25")


def arquivo(cid, nome):
    # ArquivoCaso guarda o caminho em link_arquivo; o nome enviado faz parte dele.
    if any(nome in str(a.get("link_arquivo") or "") for a in itens(call("GET", f"caso/{cid}/arquivos", admin))):
        return
    pdf = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n"
    call("POST", f"caso/{cid}/arquivos", admin, {}, files={"arquivo": (nome, pdf, "application/pdf")})


arquivo(c_admin, "procuracao_v1.pdf")
arquivo(c_admin, "contrato_v1.pdf")
print("eventos e arquivos conferidos no caso", c_admin)

if len(sys.argv) > 1:
    with open(sys.argv[1], "w") as f:
        json.dump({"orient": orient, "estag": estag, "colab": colab, "caso_admin": c_admin}, f)

if falhas:
    sys.exit(f"seed: terminou com {falhas} erro(s)")
print("seed ok em", API)
