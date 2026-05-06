#!/bin/bash

echo "🔧 Configurando Cron Job..."
echo ""

# Cron job para segundas 12:00
CRON_CMD="0 12 * * 1 cd /root/.zeroclaw/workspace && python3 deribit_btc_options.py >> /tmp/deribit.log 2>&1 && python3 yfinance_indices.py >> /tmp/yfinance.log 2>&1"

# Verificar se já existe
if crontab -l 2>/dev/null | grep -q "deribit_btc_options.py"; then
    echo "⚠️  Cron job já existe!"
    echo ""
    echo "Cron atual:"
    crontab -l | grep deribit
else
    echo "✅ Adicionando novo cron job..."
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo "✅ Cron job adicionado com sucesso!"
fi

echo ""
echo "📋 Listando todos os cron jobs:"
crontab -l
