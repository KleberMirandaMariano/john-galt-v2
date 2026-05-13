#!/usr/bin/env python3
"""
update_telegram.py — Atualiza send_telegram no daily_report.py
Rodar em: /root/.zeroclaw/workspace/
"""

import os

DAILY_REPORT = os.path.join(os.path.dirname(__file__), "daily_report.py")

OLD = """def send_telegram(report: str):
    \"\"\"
    Enviar relatório via Telegram (placeholder)
    
    TODO: Integrar com bot Telegram do John Galt
    \"\"\"
    print(\"📱 TODO: Implementar envio Telegram\")
    print(f\"   Tamanho do relatório: {len(report)} chars\")"""

NEW = """def send_telegram(report: str):
    \"\"\"
    Enviar relatório via Telegram.
    Token/chat_id via env vars ou fallback hardcoded.
    Divide automaticamente mensagens > 4096 chars (limite Telegram).
    \"\"\"
    import requests as _req

    TOKEN = os.getenv("TELEGRAM_TOKEN", "8930603673:AAHHbMpUnsNq5KaAcJNsuuvZ1nSaeARHaP0")
    CHAT  = os.getenv("TELEGRAM_CHAT_ID", "1808474055")
    URL   = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    chunks = [report[i:i+4096] for i in range(0, len(report), 4096)]
    success = True

    for i, chunk in enumerate(chunks, 1):
        try:
            # Tentar com Markdown primeiro
            r = _req.post(URL, json={"chat_id": CHAT, "text": chunk, "parse_mode": "Markdown"}, timeout=15)
            if r.status_code == 200:
                print(f"   ✅ Parte {i}/{len(chunks)} enviada")
            else:
                # Fallback sem Markdown
                r2 = _req.post(URL, json={"chat_id": CHAT, "text": chunk}, timeout=15)
                if r2.status_code == 200:
                    print(f"   ✅ Parte {i}/{len(chunks)} enviada (sem markdown)")
                else:
                    print(f"   ❌ Erro parte {i}: {r2.text[:120]}")
                    success = False
        except Exception as e:
            print(f"   ❌ Exceção parte {i}: {e}")
            success = False

    if success:
        print(f"📱 Telegram: ✅ Relatório enviado ({len(chunks)} parte(s))")
    else:
        print("📱 Telegram: ⚠️ Falha em alguns chunks")"""


def main():
    print("=" * 60)
    print("🔧 UPDATE TELEGRAM — daily_report.py")
    print("=" * 60)

    if not os.path.exists(DAILY_REPORT):
        print(f"❌ Arquivo não encontrado: {DAILY_REPORT}")
        return

    content = open(DAILY_REPORT, encoding="utf-8").read()

    if OLD not in content:
        if "8930603673" in content:
            print("✅ Token novo já aplicado — nada a fazer.")
        else:
            print("⚠️  Trecho antigo não encontrado. Verifique o arquivo manualmente.")
        return

    new_content = content.replace(OLD, NEW)
    open(DAILY_REPORT, "w", encoding="utf-8").write(new_content)
    print("✅ daily_report.py atualizado com sucesso!")

    # Teste rápido de importação
    import subprocess
    result = subprocess.run(
        ["python3", "-c", "from daily_report import send_telegram; print('✅ Import OK')"],
        cwd=os.path.dirname(DAILY_REPORT),
        capture_output=True, text=True
    )
    print(result.stdout.strip() or result.stderr.strip())


if __name__ == "__main__":
    main()
