#!/bin/bash

# ============================================================================
# cripto_daily.sh v2 — Relatório Criptográfico Robusto (Cron-Ready)
# ============================================================================

set -euo pipefail

TELEGRAM_BOT_TOKEN="8257136195:AAH-1UP7_LzmKwoFUnF_-VK_A5cCX2zW4-g"
TELEGRAM_CHAT_ID="1808474055"
WORKSPACE_DIR="/root/.zeroclaw/workspace"
LOG_FILE="${WORKSPACE_DIR}/cripto_daily.log"
CACHE_FILE="${WORKSPACE_DIR}/.cripto_cache.json"
TIMEOUT_SEC=30

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

fetch_json() {
    local url="$1"
    local name="$2"
    
    timeout "$TIMEOUT_SEC" curl -s "$url" 2>/dev/null || {
        log "❌ Timeout em $name"
        return 1
    }
}

log "🚀 Iniciando coleta de dados..."

COINGECKO_URL="https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_change=true&include_market_cap=true"

BTC_DATA=$(fetch_json "$COINGECKO_URL" "CoinGecko") || BTC_DATA="{}"
BTC_PRICE=$(echo "$BTC_DATA" | jq -r '.bitcoin.usd // "N/A"' 2>/dev/null || echo "N/A")
BTC_24H=$(echo "$BTC_DATA" | jq -r '.bitcoin.usd_24h_change // "N/A"' 2>/dev/null || echo "N/A")

ETH_PRICE=$(echo "$BTC_DATA" | jq -r '.ethereum.usd // "N/A"' 2>/dev/null || echo "N/A")
ETH_24H=$(echo "$BTC_DATA" | jq -r '.ethereum.usd_24h_change // "N/A"' 2>/dev/null || echo "N/A")

SOL_PRICE=$(echo "$BTC_DATA" | jq -r '.solana.usd // "N/A"' 2>/dev/null || echo "N/A")
SOL_24H=$(echo "$BTC_DATA" | jq -r '.solana.usd_24h_change // "N/A"' 2>/dev/null || echo "N/A")

FNG_URL="https://api.alternative.me/fng/"
FNG_DATA=$(fetch_json "$FNG_URL" "Alternative.me") || FNG_DATA="{}"
FNG_VALUE=$(echo "$FNG_DATA" | jq -r '.data[0].value // "N/A"' 2>/dev/null || echo "N/A")
FNG_LABEL=$(echo "$FNG_DATA" | jq -r '.data[0].value_classification // "N/A"' 2>/dev/null || echo "N/A")

OKX_URL="https://www.okx.com/api/v5/public/funding-rate?instId=BTC-USD-SWAP"
OKX_DATA=$(fetch_json "$OKX_URL" "OKX Funding") || OKX_DATA="{}"
FUNDING_RATE=$(echo "$OKX_DATA" | jq -r '.data[0].fundingRate // "N/A"' 2>/dev/null || echo "N/A")

TIMESTAMP=$(date '+%d/%m %H:%M BRT')

MESSAGE=$(cat << EOF
📊 *Cripto Daily Report* — $TIMESTAMP

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 *PREÇOS*

🔵 *BTC* \`\$$BTC_PRICE\` ($BTC_24H%)
⚪ *ETH* \`\$$ETH_PRICE\` ($ETH_24H%)
🟡 *SOL* \`\$$SOL_PRICE\` ($SOL_24H%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
😨 *SENTIMENTO*

Fear & Greed: \`$FNG_VALUE\` (*$FNG_LABEL*)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 *DERIVATIVES*

BTC Funding Rate: \`$FUNDING_RATE%\`
(Positivo = Bulls pagam, Negativo = Bears pagam)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
John Galt | ZMI — ZeroClaw Market Intelligence
EOF
)

log "✅ Dados coletados com sucesso"
log "$MESSAGE"

send_telegram "$MESSAGE"

echo "$BTC_DATA" > "$CACHE_FILE"
log "💾 Cache atualizado: $CACHE_FILE"

log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

