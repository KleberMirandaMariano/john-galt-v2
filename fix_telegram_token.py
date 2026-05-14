#!/usr/bin/env python3
"""fix_token_v2.py - Encontra e corrige token Telegram em qualquer lugar"""
import os, glob, subprocess

OLD = "8257136195:AAH-1UP7_LzmKwoFUnF_-VK_A5cCX2zW4-g"
NEW = "8930603673:AAHHbMpUnsNq5KaAcJNsuuvZ1nSaeARHaP0"

print("=" * 60)
print("1. PROCURANDO TOKEN ANTIGO EM TODOS OS ARQUIVOS...")
print("=" * 60)

# Buscar em todos os arquivos de texto relevantes
extensions = ["*.toml", "*.env", "*.py", "*.sh", "*.conf", "*.cfg", "*.json", "*.yaml", "*.yml"]
search_dirs = ["/root", "/home", "/etc/zeroclaw", "/opt"]
found_files = []

for d in search_dirs:
    if not os.path.exists(d):
        continue
    for ext in extensions:
        for f in glob.glob(f"{d}/**/{ext}", recursive=True):
            try:
                content = open(f, errors='ignore').read()
                if OLD in content:
                    found_files.append(f)
            except:
                pass

if found_files:
    for f in found_files:
        content = open(f, errors='ignore').read()
        open(f, "w").write(content.replace(OLD, NEW))
        print(f"✅ Corrigido: {f}")
else:
    print("Token antigo não encontrado em arquivos.")
    print("Provável: token já atualizado ou em variável de ambiente.")

print()
print("=" * 60)
print("2. VERIFICANDO PROCESSO ZEROCLAW...")
print("=" * 60)

r = subprocess.run(["ps", "aux"], capture_output=True, text=True)
for line in r.stdout.splitlines():
    if "zeroclaw" in line.lower() and "grep" not in line:
        print(f"Processo: {line.strip()}")

print()
print("=" * 60)
print("3. CONTEUDO DO config.toml (secao telegram)...")
print("=" * 60)

config_path = "/root/.zeroclaw/config.toml"
if os.path.exists(config_path):
    content = open(config_path).read()
    # Mostrar só a seção telegram
    lines = content.splitlines()
    in_telegram = False
    for line in lines:
        if "telegram" in line.lower():
            in_telegram = True
        if in_telegram:
            print(line)
        if in_telegram and line.strip() == "" and "telegram" not in line.lower():
            in_telegram = False
else:
    print("config.toml não encontrado")

print()
print("=" * 60)
print("4. ARQUIVOS .env NO WORKSPACE...")
print("=" * 60)
for f in ["/root/.zeroclaw/workspace/.env", "/root/.zeroclaw/.env", "/root/.env"]:
    if os.path.exists(f):
        print(f"Encontrado: {f}")
        print(open(f).read())
    else:
        print(f"Não existe: {f}")
