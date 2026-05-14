#!/usr/bin/env python3
"""fix_config_links.py - Copia config/ para raiz do workspace"""
import os, shutil

WORKSPACE = "/root/.zeroclaw/workspace"
CONFIG_DIR = os.path.join(WORKSPACE, "config")

files = ["SOUL.md", "AGENTS.md", "TOOLS.md"]

print("=" * 50)
print("Copiando arquivos config/ para raiz do workspace...")
print("=" * 50)

for f in files:
    src = os.path.join(CONFIG_DIR, f)
    dst = os.path.join(WORKSPACE, f)
    
    if not os.path.exists(src):
        print(f"❌ Não encontrado: {src}")
        continue
    
    shutil.copy2(src, dst)
    print(f"✅ Copiado: config/{f} → {f}")

print()
print("Arquivos na raiz do workspace:")
for f in sorted(os.listdir(WORKSPACE)):
    if f.endswith(".md") or f.endswith(".toml") or f.endswith(".py"):
        size = os.path.getsize(os.path.join(WORKSPACE, f))
        print(f"  {f} ({size:,} bytes)")
