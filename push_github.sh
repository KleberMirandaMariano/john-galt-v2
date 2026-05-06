#!/bin/bash

echo "🚀 Push para GitHub..."
cd /root/.zeroclaw/workspace

# Configurar remote para SSH (se ainda não estiver)
git remote set-url origin git@github.com:KleberMirandaMariano/john-galt-v2.git

# Ver logs
echo "📋 Commits a enviar:"
git log --oneline origin/main..HEAD

# Push
echo ""
echo "Enviando para GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Push concluído!"
    echo "🔗 Verifique: https://github.com/KleberMirandaMariano/john-galt-v2/actions"
else
    echo "⚠️ Push falhou (esperado em container sem internet)"
    echo "✅ Mas os commits estão salvos localmente!"
    echo "✅ GitHub Actions vai fazer o deploy quando você fizer push do seu PC"
fi
