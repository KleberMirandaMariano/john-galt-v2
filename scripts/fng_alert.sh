#!/bin/bash

set -euo pipefail

TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:?Erro: TELEGRAM_BOT_TOKEN nao definido. Exporte a variavel antes de executar.}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-1808474055}"
WORKSPACE_DIR="/root/.zeroclaw/workspace"
LOG_FILE="${WORKSPACE_DIR}/fng_alert.log"
FNG_THRESHOLD="${FNG_THRESHOLD:-25}"
TIMEOUT_SEC=10

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

send_telegram() {
    local msg="$1"
    curl -s --max-time 10 \
        -X POST \
        "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT_ID}" \
        -d "text=${msg}" \
        -d "parse_mode=Markdown" > /dev/null 2>&1 || log "⚠️  Falha ao enviar Telegram"
}

log "🔍 Verificando Fear & Greed Index..."

FNG_URL="https://api.alternative.me/fng/"

FNG_RESPONSE=$(timeout "$TIMEOUT_SEC" curl -s "$FNG_URL" 2>/dev/null) || {
    log "❌ Timeout ao buscar FNG"
    exit 1
}

FNG_VALUE=$(echo "$FNG_RESPONSE" | jq -r '.data[0].value // "N/A"' 2>/dev/null)
FNG_LABEL=$(echo "$FNG_RESPONSE" | jq -r '.data[0].value_classification // "N/A"' 2>/dev/null)

if ! [[ "$FNG_VALUE" =~ ^[0-9]+\.?[0-9]*$ ]]; then
    log "⚠️  FNG value não numérico: $FNG_VALUE — pulando"
    exit 0
fi

log "✅ FNG atual: $FNG_VALUE ($FNG_LABEL)"

if (( $(echo "$FNG_VALUE <= $FNG_THRESHOLD" | bc -l) )); then
    ALERT_MSG=$(cat << EOF
🚨 *EXTREME FEAR DETECTED*

Fear & Greed Index: \`$FNG_VALUE\` (*$FNG_LABEL*)
Threshold: \`≤ $FNG_THRESHOLD\`

⏰ $(date '+%d/%m %H:%M:%S BRT')

💡 *Ação:* Verificar análise quantitativa. Possível compra de puts/calls OTM em alta volatilidade.

John Galt | ZMI — ZeroClaw Market Intelligence
EOF
)
    
    log "🚨 ALERTA DISPARADO: FNG ≤ $FNG_THRESHOLD"
    send_telegram "$ALERT_MSG"
else
    log "✅ FNG $FNG_VALUE > $FNG_THRESHOLD — sem alerta"
fi

log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

