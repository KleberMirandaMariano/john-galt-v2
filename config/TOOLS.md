# John Galt — Registry de Ferramentas e APIs

> ⚠️ `shell`, `python3`, `curl`, `import`, `localhost` são **BLOQUEADOS** pelo ZeroClaw.
> Use apenas `web_fetch` para buscar dados externos.

---

## APIs Disponíveis via web_fetch

### BRAPI — Cotações B3
```
web_fetch("https://brapi.dev/api/quote/TICKER?token=tP2QrzuthuXx4JjrnBqnkd")
→ results[0].regularMarketPrice         # preço atual
→ results[0].regularMarketChangePercent # variação %
→ results[0].priceEarnings              # P/L
→ results[0].earningsPerShare           # LPA
→ results[0].marketCap                  # market cap
```
Múltiplos tickers: `quote/PETR4,VALE3,COGN3?token=...`

### CoinGecko — Cripto Spot
```
web_fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,solana,ethereum&vs_currencies=usd,brl&include_24hr_change=true&include_market_cap=true")
→ bitcoin.usd, bitcoin.usd_24h_change, bitcoin.usd_market_cap

web_fetch("https://api.coingecko.com/api/v3/global")
→ data.market_cap_percentage.btc  # dominância BTC
```

### OKX v5 — Futuros e Opções Cripto
```
web_fetch("https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT")
→ data[0].last     # preço spot BTC

web_fetch("https://www.okx.com/api/v5/public/funding-rate?instId=BTC-USD-SWAP")
→ data[0].fundingRate  # funding rate atual

web_fetch("https://www.okx.com/api/v5/market/open-interest?instId=BTC-USD-SWAP")
→ data[0].oi           # Open Interest

web_fetch("https://www.okx.com/api/v5/public/opt-summary?instFamily=SOL-USD")
→ IV ATM, options chain
```

### Fear & Greed Index
```
web_fetch("https://api.alternative.me/fng/?limit=1")
→ data[0].value                  # 0-100
→ data[0].value_classification   # "Fear", "Greed", etc.
```

### Selic — Banco Central do Brasil
```
web_fetch("https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json")
→ [0]['valor']  # Selic % a.a.
→ [0]['data']   # data referência
```

### Câmbio USD/BRL
```
web_fetch("https://economia.awesomeapi.com.br/json/last/USD-BRL")
→ USDBRL.bid         # cotação compra
→ USDBRL.pctChange   # variação %
```

### Financial Datasets — Fundamentalistas (NYSE/NASDAQ, SEM API KEY)
```
web_fetch("https://api.financialdatasets.ai/financial-metrics/snapshot/?ticker=AAPL")
→ snapshot.price_to_earnings_ratio  # P/E
→ snapshot.price_to_book_ratio      # P/B
→ snapshot.return_on_equity         # ROE
→ snapshot.net_margin
→ snapshot.debt_to_equity

web_fetch("https://api.financialdatasets.ai/prices/snapshot/?ticker=AAPL")
→ snapshot.price
→ snapshot.day_change_percent
```
⚠️ Apenas NYSE/NASDAQ. B3 retorna 400. Não requer headers nem API key.

---

## Fórmulas — Calcular Inline na Resposta

### Black-Scholes
```
d1 = (ln(S/K) + (r + σ²/2) × T) / (σ × √T)
d2 = d1 - σ × √T
Call = S × N(d1) - K × e^(-rT) × N(d2)
Put  = K × e^(-rT) × N(-d2) - S × N(-d1)

N(x) ≈ 0.5 × (1 + erf(x / √2))

Greeks:
  Delta_call = N(d1)                    | Delta_put = N(d1) - 1
  Gamma      = N'(d1) / (S × σ × √T)   | N'(x) = e^(-x²/2) / √(2π)
  Vega       = S × N'(d1) × √T / 100
  Theta      = -(S × N'(d1) × σ) / (2 × √T) / 365

Parâmetros B3: r = Selic/252 (diária) | σ = HV30d/√252
Parâmetros cripto: r = 0 (sem risco) | T = DTE/365
```

### Kelly Criterion
```
f* = (p × b - q) / b
  p = P(ITM) ou taxa de acerto histórica
  b = Ganho_max / Perda_max
  q = 1 - p
f_conservador = f* / 4

Limites:
  Máx 2% capital — alto risco
  Máx 5% capital — risco limitado (RR > 2:1)
  Stop: drawdown mensal > 10% → parar e revisar
```

### Valor Graham
```
Valor_Graham = √(22.5 × LPA × VPA)
Upside = (Valor_Graham / Preço_atual - 1) × 100%
Válido apenas se LPA > 0 e VPA > 0
```

### DVR — Diferencial de Volatilidade de Rolagem
```
DVR = IV_vencimento_curto - IV_vencimento_longo
DVR > 0: term structure normal → favorável para Calendar Spread e THL
DVR < 0: invertida → rolar com cautela, custo maior
```

---

## Estratégias de Opções — Referência Rápida

| Cenário | Estratégia | Badge | IV/HV |
|---------|-----------|-------|-------|
| Neutro + IV alta | Iron Condor | ⭐ TOP PICK | > 1.2 |
| Alta moderada | Bull Call Spread | 🐂 ALTA | qualquer |
| Defensivo crédito | Bull Put Spread | 🛡️ DEFENSIVO | > 1.0 |
| Term invertida | Calendar Spread | 📅 AVANÇADO | DVR < 0 |
| Vol play compra | Long Straddle | ⚡ ALTO RISCO | < 0.8 |
| Vol play venda | Short Straddle | 🎯 NEUTRO | > 1.2 |
| Especulativo | OTM Call | 🚀 ASSIMÉTRICO | < 0.8 |

**Formato JSON para estratégias:**
```json
{
  "ticker": "SOL",
  "spot": 84.09,
  "iv_atm": 50.1,
  "dte": 25,
  "strategies": [
    {
      "emoji": "🦅",
      "name": "Iron Condor",
      "type_desc": "Neutro · Range-bound · Vende volatilidade",
      "badge_color": "orange",
      "badge_text": "⭐ TOP PICK",
      "metrics": [
        {"value": "+$2.73", "label": "Crédito Recebido", "color": "green"},
        {"value": "-$1.27", "label": "Perda Máxima", "color": "red"},
        {"value": "2.15:1", "label": "Risk/Reward", "color": "blue"},
        {"value": "$77-$95", "label": "Break-evens", "color": "yellow"}
      ],
      "legs": [
        {"action": "BUY",  "strike": 80, "type": "PUT",  "premium": 2.56},
        {"action": "SELL", "strike": 84, "type": "PUT",  "premium": 4.27},
        {"action": "SELL", "strike": 88, "type": "CALL", "premium": 2.79},
        {"action": "BUY",  "strike": 92, "type": "CALL", "premium": 1.77}
      ],
      "note": "Insight / contexto da estratégia"
    }
  ]
}
```

---

## Erros Históricos a Evitar

**SOL 02/05/2026 — dados de memória:**
- ❌ HV 38% usada (real: 49.8%) → estratégia invertida
- ❌ Corr BTC +0.92 (real: +0.41) → alpha subestimado
- **Solução:** sempre buscar dados frescos via web_fetch antes de qualquer análise
