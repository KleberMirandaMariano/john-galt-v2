---
name: financial-datasets-live
description: >
  Análise fundamentalista NYSE/NASDAQ via Financial Datasets API (sem auth). Disparar com
  ticker NYSE/NASDAQ (AAPL, MSFT, NVDA, GOOGL, etc) ou ADR brasileiro (VALE, PBR, ITUB, BBD).
  NÃO usar para B3 nativa — B3 retorna 400; para PETR4/COGN3 usar BRAPI.
---

# Financial Datasets — NYSE/NASDAQ + ADRs

## Endpoints

```
# Múltiplos e fundamentalistas
web_fetch(
  url="https://api.financialdatasets.ai/financial-metrics/snapshot/?ticker=AAPL",
  headers={"User-Agent": "Mozilla/5.0"}
)

# Preço atual
web_fetch(
  url="https://api.financialdatasets.ai/prices/snapshot/?ticker=AAPL",
  headers={"User-Agent": "Mozilla/5.0"}
)
```

## Campos `snapshot.*`
- `price_to_earnings_ratio` → P/L
- `price_to_book_ratio` → P/VP
- `return_on_equity` → ROE (×100 = %)
- `return_on_assets` → ROA (×100 = %)
- `net_margin`, `gross_margin`, `operating_margin` (×100 = %)
- `debt_to_equity`, `current_ratio`
- `revenue_growth` (×100 = %)
- `dividend_yield` (×100 = %)
- `price`, `day_change_percent`

## Scoring inline (0-10)

**Value:** P/L (<10→10, 15-25→6, >40→2) + P/VP (<1.5→10, 3-6→4, >6→2) → média
**Quality:** ROE (>25%→10, 15-25%→8, <10%→4) + Margem líquida + ROA → média
**Growth:** revenue_growth (>20%→10, 10-20%→7, 0-10%→5, <0→2)
**Risk:** debt_to_equity (<0.5→10, 0.5-1→7, 1-2→5, >2→2)

**Score final:** 0.30·Value + 0.30·Quality + 0.20·Growth + 0.20·Risk

## ADRs brasileiros disponíveis
- VALE (Vale)
- PBR (Petrobras)
- ITUB (Itaú)
- BBD (Bradesco)
- ABEV (Ambev)

## Regra crítica
- B3 nativa (PETR4, COGN3, etc) → BRAPI, NÃO essa API
- Sempre incluir `User-Agent` no header
- Para análise completa, preferir `daily_report.py` + `file_read`
