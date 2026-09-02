"""Seed de dados de teste para o ambiente local (API em localhost:5000).

Uso: uv run python scripts/seed_local.py ids.json
Requer o admin rvnovaes@gmail.com / admin. Idempotente para usuários; duplica
casos, atendidos e eventos se rodado de novo. Presenças e plantões de datas
passadas foram inseridos por SQL (ver docs/paridade-v2-v3.md, seção 4).
"""
import io, json, sys, urllib.request

API = "http://localhost:5000/api"

def call(method, path, token=None, body=None, files=None):
    url = f"{API}/{path}"
    headers = {}
    if token: headers["Authorization"] = f"Bearer {token}"
    data = None
    if files is not None:
        boundary = "----seedboundary"
        buf = io.BytesIO()
        for k, v in (body or {}).items():
            buf.write(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
        for k, (fname, content, ctype) in files.items():
            buf.write(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{fname}\"\r\nContent-Type: {ctype}\r\n\r\n".encode())
            buf.write(content); buf.write(b"\r\n")
        buf.write(f"--{boundary}--\r\n".encode())
        data = buf.getvalue()
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    elif body is not None:
        data = json.dumps(body).encode(); headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        print(f"ERRO {method} {path}: {e.code} {e.read().decode()[:300]}"); return None

def login(email, senha):
    return call("POST", "auth/login", body={"email": email, "password": senha})["data"]["token"]

admin = login("rvnovaes@gmail.com", "admin")

def user(nome, email, urole, matricula):
    base = {"email": email, "nome": nome, "urole": urole, "sexo": "F", "rg": "11.222.333-4",
            "cpf": "000.000.000-00", "profissao": urole, "estado_civil": "solteiro", "nascimento": "1995-05-15",
            "telefone": None, "celular": "(31) 99999-0000", "oab": None, "obs": "seed", "data_entrada": "2024-01-15",
            "data_saida": None, "matricula": matricula, "bolsista": False, "tipo_bolsa": None,
            "horario_atendimento": None, "suplente": None, "ferias": None, "cert_atuacao_DAJ": "sim",
            "inicio_bolsa": None, "fim_bolsa": None, "logradouro": "Rua Seed", "numero": "1", "bairro": "Centro",
            "cep": "30000-000", "cidade": "Belo Horizonte", "estado": "MG", "complemento": None}
    r = call("POST", "user/", admin, base)
    if r is None:  # já existe: procura
        lst = call("GET", "user/?per_page=100", admin)["data"]["items"]
        uid = next(u["id"] for u in lst if u["email"] == email)
    else:
        uid = r["data"]["id"]
    call("PUT", f"user/{uid}/password", admin, {"newPassword": "senha123", "fromAdmin": True})
    return uid

orient = user("Olívia Orientadora", "orientadora@gl.local", "orient", "OR001")
estag  = user("Eduardo Estagiário", "estagiario@gl.local", "estag_direito", "EST001")
colab  = user("Carla Colaboradora Externa", "colab.ext@gl.local", "colab_ext", "CE001")
print("usuarios:", orient, estag, colab)

tok_estag = login("estagiario@gl.local", "senha123")
tok_orient = login("orientadora@gl.local", "senha123")

def atendido(nome, cpf):
    r = call("POST", "atendido/", admin, {"nome": nome, "data_nascimento": "1990-01-15", "cpf": cpf,
        "telefone": None, "celular": "(31) 98888-0000", "email": f"{cpf[:3]}@seed.local", "estado_civil": "solteiro",
        "logradouro": "Rua A", "numero": "10", "bairro": "Centro", "cep": "30000-000", "cidade": "Belo Horizonte",
        "estado": "MG", "como_conheceu": "assist", "procurou_outro_local": "nao", "pj_constituida": "nao", "status": 1})
    return r["data"]["id"] if r else None

a1 = atendido("Maria Aparecida Seed", "111.111.111-11")
a2 = atendido("José Ribeiro Seed", "222.222.222-22")

def caso(token, resp, area, desc, clientes):
    r = call("POST", "caso/", token, {"id_usuario_responsavel": resp, "area_direito": area,
        "situacao_deferimento": "ativo", "descricao": desc, "ids_clientes": clientes})
    return r["data"]["id"]

c_admin = caso(admin, 1, "civel", "Caso criado pelo ADMIN, responsável admin (seed)", [a1])
c_admin2 = caso(admin, estag, "penal", "Caso criado pelo ADMIN, responsável estagiário (seed)", [a2])
c_estag = caso(tok_estag, estag, "trabalhista", "Caso criado pelo ESTAGIÁRIO, responsável estagiário (seed)", [a1, a2])
c_orient = caso(tok_orient, 1, "civel", "Caso criado pela ORIENTADORA, responsável admin (seed)", [])
print("casos:", c_admin, c_admin2, c_estag, c_orient)

def evento(token, cid, tipo, desc, data):
    r = call("POST", f"caso/{cid}/eventos", token, {"tipo": tipo, "data_evento": data, "descricao": desc, "status": "true"}, files={})
    return r["data"]["id"]

evento(admin, c_admin, "reuniao", "Reunião inicial (criado pelo admin)", "2026-08-01")
evento(admin, c_admin, "audencia", "Audiência de conciliação (criado pelo admin)", "2026-08-10")
evento(tok_estag, c_admin, "contato", "Contato telefônico (criado pelo estagiário)", "2026-08-12")
evento(tok_estag, c_admin, "documentos", "Juntada de documentos (criado pelo estagiário)", "2026-08-20")
evento(tok_orient, c_admin, "reuniao", "Reunião de orientação (criado pela orientadora)", "2026-08-25")

pdf = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n"
call("POST", f"caso/{c_admin}/arquivos", admin, {}, files={"arquivo": ("procuracao_v1.pdf", pdf, "application/pdf")})
call("POST", f"caso/{c_admin}/arquivos", admin, {}, files={"arquivo": ("contrato_v1.pdf", pdf, "application/pdf")})
print("eventos e arquivos criados no caso", c_admin)
json.dump({"orient": orient, "estag": estag, "colab": colab, "caso_admin": c_admin}, open(sys.argv[1], "w"))
