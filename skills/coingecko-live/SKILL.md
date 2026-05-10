# Cripto Live — Preços em Tempo Real

## Quando usar
Sempre que mencionar preços de BTC, SOL, ETH, dominância ou market cap.
NUNCA mencione preços de cripto sem executar os web_fetch abaixo.

## Fonte Principal — CoinGecko (sem API key)

### Preços BTC, ETH, SOL + variação 24h
```
web_fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd,brl&include_24hr_change=true&include_market_cap=true")
→ bitcoin.usd              # preço em USD
→ bitcoin.brl              # preço em BRL
→ bitcoin.usd_24h_change   # variação 24h %
→ bitcoin.usd_market_cap   # market cap USD
```

### Dominância BTC e Market Cap Global
```
web_fetch("https://api.coingecko.com/api/v3/global")
→ data.market_cap_percentage.btc   # dominância BTC %
→ data.total_market_cap.usd        # market cap total USD
```

## Interpretação Dominância BTC
- >60%: Bitcoin dominante — risk-off cripto
- 50-60%: Equilíbrio
- <45%: Altseason em curso

## Formato de resposta esperado
```
🪙 CRIPTO — [DATA] [HORA] BRT

₿ BTC: $XX,XXX (+X.XX%) | R$ XXX,XXX
◎ ETH: $X,XXX (+X.XX%)
◉ SOL: $XXX (+X.XX%)

🌐 Dominância BTC: XX.X%
💹 Market Cap Total: $X.XXt
```

## REGRA CRÍTICA
Execute SEMPRE os web_fetch antes de citar preços de cripto.
Se a API falhar: "Preços indisponíveis. Consulte coingecko.com"
JAMAIS invente ou estime preços.
