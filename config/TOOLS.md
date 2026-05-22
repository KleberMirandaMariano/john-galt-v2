# John Galt — Registry de Ferramentas e APIs

> ⚠️ `shell`, `python3`, `curl`, `import` são **BLOQUEADOS** pelo ZeroClaw. Use `web_fetch`.

---

## APIs via web_fetch

### BRAPI — Cotações B3
```
web_fetch("https://brapi.dev/api/quote/TICKER?token={BRAPI_TOKEN}")
→ results[0].regularMarketPrice / regularMarketChangePercent / priceEarnings
→ results[0].earningsPerShare / marketCap / fiftyTwoWeekHigh / fiftyTwoWeekLow
```

### Fundamentus — Fundamentalistas B3 (sem auth)
```
web_fetch("https://www.fundamentus.com.br/detalhes.php?papel={TICKER}")
→ HTML com tabelas de indicadores — extrair por rótulo adjacente
Campos: P/L, P/VP, EV/EBITDA, Div.Yield, ROE, ROIC, Marg.Líquida,
        Marg.EBIT, Dív.Bruta/Patrim., Líq. Corr., Cresc. Rec.5a
```
Parsing: remover `.` (milhar) e substituir `,` por `.` antes de converter para float.
Ex: `"1.234,56%"` → `1234.56` → `/100` = `12.3456`

### BRAPI — Liquidez de Opções B3
```
web_fetch("https://brapi.dev/api/quote/PETR4/options?token={BRAPI_TOKEN}")
→ options[0].calls[].volume           # volume diário
→ options[0].calls[].openInterest     # OI — mínimo aceitável: 500
→ options[0].calls[].impliedVolatility # IV da série
```
Critério: `openInterest ≥ 500` e `volume ≥ 100/dia`.

### CoinGecko — Spot e Histórico
```
# Spot
web_fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd,brl&include_24hr_change=true&include_market_cap=true")

# Histórico para HV real
web_fetch("https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30&interval=daily")
→ prices: [[timestamp_ms, price], ...]

# Dominância
web_fetch("https://api.coingecko.com/api/v3/global")
→ data.market_cap_percentage.btc
```
Ids: `bitcoin`, `ethereum`, `solana`, `ripple`

### OKX v5 — Opções Cripto (sem auth)
```
web_fetch("https://www.okx.com/api/v5/public/opt-summary?instFamily=SOL-USD")
web_fetch("https://www.okx.com/api/v5/public/funding-rate?instId=BTC-USD-SWAP")
web_fetch("https://www.okx.com/api/v5/market/open-interest?instId=BTC-USD-SWAP")
```

### BCB — Selic + PTAX
```
# Selic
web_fetch("https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json")
→ [0]['valor']  # % a.a.

# USD/BRL PTAX (oficial, sem rate limit) — buscar 2 pontos para calcular variação
web_fetch("https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados/ultimos/2?formato=json")
→ [1]['valor']  # PTAX hoje (ou último dia útil)
→ variação = (float([1]['valor']) / float([0]['valor']) - 1) * 100

# Fallback USD/BRL (se BCB série 1 falhar)
web_fetch("https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=brl")
→ tether.brl    # proxy USDT/BRL
```
⚠️ **NÃO use AwesomeAPI** (`economia.awesomeapi.com.br`) — sofre rate limit constante em produção.

### Fear & Greed
```
web_fetch("https://api.alternative.me/fng/?limit=1")
→ data[0].value  /  data[0].value_classification
```

### Financial Datasets (NYSE/NASDAQ, sem auth)
```
web_fetch("https://api.financialdatasets.ai/financial-metrics/snapshot/?ticker=AAPL")
→ snapshot.price_to_earnings_ratio / return_on_equity / net_margin / debt_to_equity
```

### FRED — Macro EUA (requer FRED_API_KEY em SECRETS.md)
```
# Fed Funds Rate (diário)
web_fetch("https://api.stlouisfed.org/fred/series/observations?series_id=DFF&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=2")
→ observations[0].value   # % a.a. (use [1] se [0].value == ".")
→ observations[0].date    # data YYYY-MM-DD

# Treasury Yield 10 anos (diário)
web_fetch("https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=2")
→ observations[0].value

# Treasury Yield 2 anos (diário)
web_fetch("https://api.stlouisfed.org/fred/series/observations?series_id=DGS2&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=2")
→ observations[0].value

# Spread curva 10Y-2Y (diário)
web_fetch("https://api.stlouisfed.org/fred/series/observations?series_id=T10Y2Y&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=2")
→ observations[0].value   # pp (negativo = curva invertida)

# Índice do Dólar — broad (semanal, proxy DXY)
web_fetch("https://api.stlouisfed.org/fred/series/observations?series_id=DTWEXBGS&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=2")
→ observations[0].value   # base 2006=100
```
Obtenha FRED_API_KEY gratuita em: https://fred.stlouisfed.org/docs/api/api_key.html

---

## Fórmulas Inline

### HV 30d Real (via CoinGecko)
```
retornos = [ln(P[i]/P[i-1]) for i in 1..29]   # 30 preços diários
HV_30d   = std(retornos) × √252 × 100           # % anualizada
```

### Black-Scholes
```
d1 = (ln(S/K) + (r + σ²/2)×T) / (σ×√T)   |   d2 = d1 - σ×√T
Call = S×N(d1) - K×e^(-rT)×N(d2)           |   Put = K×e^(-rT)×N(-d2) - S×N(-d1)
Delta_call=N(d1) | Gamma=N'(d1)/(S×σ×√T) | Vega=S×N'(d1)×√T/100 | Theta=-(S×N'(d1)×σ)/(2×√T)/365
B3: r=Selic/100/252, σ=HV30d/100/√252, T=DTE/252
Cripto: r=0, T=DTE/365
```

### IV/HV Ratio
```
> 1.2 → vol CARA → venda (Iron Condor)
< 0.8 → vol BARATA → compra (Straddle)
```

### Kelly
```
f* = (p×b - q)/b  |  f_conservador = f*/4  |  Máx: 2% alto risco / 5% risco limitado
```

### Valor Graham
```
VG = √(22.5 × LPA × VPA)  |  válido só se LPA>0 e VPA>0
```

---

## Estratégias de Opções

| Cenário | Estratégia | IV/HV |
|---------|-----------|-------|
| Neutro + IV alta | Iron Condor ⭐ | > 1.2 |
| Alta moderada | Bull Call Spread 🐂 | qualquer |
| Defensivo crédito | Bull Put Spread 🛡️ | > 1.0 |
| Vol play compra | Long Straddle ⚡ | < 0.8 |
| Especulativo | OTM Call 🚀 | < 0.8 |

---

## Erros Históricos a Evitar

**SOL 02/05/2026 — dados de memória:**
- ❌ HV 38% usada → real: 49.8% → estratégia invertida
- ❌ Corr BTC +0.92 → real: +0.41

**Solução permanente:** sempre buscar dados frescos via web_fetch + calcular HV via CoinGecko market_chart.
