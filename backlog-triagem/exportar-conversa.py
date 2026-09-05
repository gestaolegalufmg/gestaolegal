#!/usr/bin/env python3
"""Converte o transcript .jsonl da sessão do Claude Code em Markdown legível."""

import json
import sys
from datetime import datetime

ENTRADA = sys.argv[1] if len(sys.argv) > 1 else (
    "/home/gladmin/.claude/projects/-opt/"
    "79a1a82c-1683-419c-a908-edfdc123be5d.jsonl"
)
SAIDA = sys.argv[2] if len(sys.argv) > 2 else "/home/gladmin/backlog-triagem/conversa.md"
LIMITE_SAIDA = 3000  # corta saídas de ferramenta muito longas


def hora(ts):
    if not ts:
        return ""
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%d/%m %H:%M")
    except ValueError:
        return ts[:16]


def texto_de(conteudo):
    """Normaliza o campo content, que pode ser str ou lista de blocos."""
    if isinstance(conteudo, str):
        return [("text", conteudo)]
    if not isinstance(conteudo, list):
        return []

    partes = []
    for bloco in conteudo:
        if not isinstance(bloco, dict):
            continue
        tipo = bloco.get("type")
        if tipo == "text":
            partes.append(("text", bloco.get("text", "")))
        elif tipo == "thinking":
            partes.append(("thinking", bloco.get("thinking", "")))
        elif tipo == "tool_use":
            entrada = bloco.get("input", {})
            desc = entrada.get("command") or entrada.get("file_path") or ""
            if not desc:
                desc = json.dumps(entrada, ensure_ascii=False)[:400]
            partes.append(("tool_use", f"{bloco.get('name', '?')}\n{desc}"))
        elif tipo == "tool_result":
            c = bloco.get("content")
            if isinstance(c, list):
                c = "\n".join(
                    b.get("text", "") for b in c if isinstance(b, dict)
                )
            partes.append(("tool_result", str(c or "")))
    return partes


def main():
    linhas = ["# Conversa — Claude Code", ""]
    with open(ENTRADA, encoding="utf-8") as f:
        primeiro = True
        for linha in f:
            try:
                d = json.loads(linha)
            except json.JSONDecodeError:
                continue

            tipo = d.get("type")
            if tipo not in ("user", "assistant"):
                continue
            if d.get("isSidechain"):
                continue

            msg = d.get("message", {})
            partes = texto_de(msg.get("content"))
            if not partes:
                continue

            if primeiro:
                linhas += [
                    f"Sessão `{d.get('sessionId', '')}`  ·  host `glap2`  ·  cwd `{d.get('cwd', '')}`",
                    "",
                    "---",
                    "",
                ]
                primeiro = False

            # Resultados de ferramenta chegam em mensagens de role "user";
            # são saída do comando, não fala do usuário.
            so_resultado = all(classe == "tool_result" for classe, _ in partes)
            autor = "Você" if tipo == "user" else "Claude"
            cabecalho = (
                "" if (tipo == "user" and so_resultado)
                else f"## {autor} — {hora(d.get('timestamp'))}"
            )
            corpo = []

            for classe, conteudo in partes:
                conteudo = conteudo.strip()
                if not conteudo:
                    continue
                if classe == "text":
                    corpo.append(conteudo)
                elif classe == "thinking":
                    continue  # raciocínio interno fica de fora
                elif classe == "tool_use":
                    nome, _, resto = conteudo.partition("\n")
                    corpo.append(f"**→ {nome}**\n\n```\n{resto[:LIMITE_SAIDA]}\n```")
                elif classe == "tool_result":
                    if len(conteudo) > LIMITE_SAIDA:
                        conteudo = (
                            conteudo[:LIMITE_SAIDA]
                            + f"\n… (+{len(conteudo) - LIMITE_SAIDA} caracteres omitidos)"
                        )
                    corpo.append(f"<details><summary>saída</summary>\n\n```\n{conteudo}\n```\n</details>")

            if corpo:
                if cabecalho:
                    linhas += [cabecalho, ""]
                linhas += ["\n\n".join(corpo), ""]

    with open(SAIDA, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    print(f"escrito: {SAIDA}")


if __name__ == "__main__":
    main()
