#!/usr/bin/env python3
"""fix_telegram_token.py - Atualiza token do Telegram no config.toml"""
import os, glob, subprocess

OLD = "8257136195:AAH-1UP7_LzmKwoFUnF_-VK_A5cCX2zW4-g"
NEW = "8930603673:AAHHbMpUnsNq5KaAcJNsuuvZ1nSaeARHaP0"

# 1. Encontrar config.toml
candidates = [
    os.path.expanduser("~/.zeroclaw/config.toml"),
    "/root/.zeroclaw/config.toml",
    "/etc/zeroclaw/config.toml",
]
candidates += glob.glob("/root/**/*.toml", recursive=True)
candidates += glob.glob("/home/**/*.toml", recursive=True)

found = [p for p in candidates if os.path.exists(p)]
print(f"Arquivos .toml encontrados: {found}")

for path in found:
    content = open(path).read()
    if OLD in content:
        open(path, "w").write(content.replace(OLD, NEW))
        print(f"✅ Token atualizado em: {path}")
    elif NEW in content:
        print(f"✅ Token novo já presente em: {path}")
    else:
        print(f"   Token antigo não encontrado em: {path}")

# 2. Encontrar servico zeroclaw
print()
print("Procurando servico zeroclaw...")
r = subprocess.run(["systemctl", "list-units", "--type=service", "--all"], capture_output=True, text=True)
for line in r.stdout.splitlines():
    if "zero" in line.lower() or "claw" in line.lower() or "galt" in line.lower() or "bot" in line.lower():
        print(f"  {line.strip()}")

# Tentar docker
r2 = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True)
if r2.stdout:
    print("Containers Docker ativos:")
    for line in r2.stdout.splitlines():
        print(f"  {line}")
