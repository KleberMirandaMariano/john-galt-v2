# Cripto Live — Preços em Tempo Real

## Quando usar
Sempre que mencionar preços de BTC, SOL, ETH, dominância ou market cap.
NUNCA mencione preços de cripto sem executar os curls abaixo.

## Fonte Principal — CoinStats API

### Preços BTC, ETH, SOL
shell: curl -s "https://openapiv1.coinstats.app/coins?limit=10" \
  -H "X-API-KEY: c0u1/Hf2JHZPdEJ1/wepZ1GVtKf1/Hdmj85Lfsfj1jQ=" | python3 -c "
import json,sys
d=json.load(sys.stdin)
coins=['BTC','ETH','SOL']
for c in d.get('result',[]):
    if c['symbol'].upper() in coins:
        print(f\"{c['symbol'].upper()}: USD \${c['price']:,.2f} | 24h: {c.get('priceChange1d',0):.2f}% | Cap: \${c.get('marketCap',0)/1e9:.1f}B\")
"

### Market Cap Global e Dominância
shell: curl -s "https://openapiv1.coinstats.app/coins?limit=3" \
  -H "X-API-KEY: c0u1/Hf2JHZPdEJ1/wepZ1GVtKf1/Hdmj85Lfsfj1jQ=" | python3 -c "
import json,sys
d=json.load(sys.stdin)
total=sum(c.get('marketCap',0) for c in d.get('result',[]))
print(f'Top 3 Market Cap: \${total/1e9:.1f}B')
for c in d.get('result',[]):
    print(f\"{c['symbol'].upper()}: \${c['price']:,.2f} ({c.get('priceChange1d',0):+.2f}%)\")
"

## Fallback — CoinGecko (se CoinStats falhar)
shell: curl -s "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,solana,ethereum&vs_currencies=usd&include_24hr_change=true" | python3 -c "
import json,sys
d=json.load(sys.stdin)
map={'bitcoin':'BTC','ethereum':'ETH','solana':'SOL'}
for k,v in d.items():
    print(f\"{map[k]}: USD \${v['usd']:,.2f} | 24h: {v.get('usd_24h_change',0):.2f}%\")
"

## Interpretação Dominância BTC
- >60%: Bitcoin dominante — risk-off cripto
- 50-60%: Equilíbrio
- <45%: Altseason em curso

## REGRA CRÍTICA
Execute SEMPRE os curls antes de citar preços de cripto.
Se ambas as APIs falharem: "Preços indisponíveis. Consulte coingecko.com"
JAMAIS invente ou estime preços.
