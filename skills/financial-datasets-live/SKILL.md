# Financial Datasets — Análise Fundamentalista Global

## Quando usar
Análise fundamentalista de ações NYSE/NASDAQ: AAPL, MSFT, NVDA, GOOGL, META, XOM, etc.
NÃO usar para B3 — B3 retorna 400. Para COGN3, PETR4 → usar BRAPI.

## ✅ COMO BUSCAR — User-Agent obrigatório

### 1. Múltiplos e Fundamentalistas
```
web_fetch(
  url="https://api.financialdatasets.ai/financial-metrics/snapshot/?ticker=AAPL",
  headers={"User-Agent": "Mozilla/5.0"}
)
```

Campos em `snapshot`:
- `price_to_earnings_ratio` → P/L
- `price_to_book_ratio`     → P/VP
- `return_on_equity`        → ROE (×100 = %)
- `return_on_assets`        → ROA (×100 = %)
- `net_margin`              → Margem Líquida (×100 = %)
- `gross_margin`            → Margem Bruta (×100 = %)
- `operating_margin`        → Margem Operacional (×100 = %)
- `debt_to_equity`          → Dívida/PL
- `current_ratio`           → Liquidez Corrente
- `revenue_growth`          → Crescimento Receita (×100 = %)
- `dividend_yield`          → Dividend Yield (×100 = %)

### 2. Preço Atual
```
web_fetch(
  url="https://api.financialdatasets.ai/prices/snapshot/?ticker=AAPL",
  headers={"User-Agent": "Mozilla/5.0"}
)
```

Campos em `snapshot`:
- `price`              → Preço atual USD
- `day_change_percent` → Variação %

## 📊 Scoring Inline (calcular sem Python)

**Value Score:**
- P/L:  <10→10 | 10-15→8 | 15-25→6 | 25-40→4 | >40→2
- P/VP: <1.5→10 | 1.5-3→7 | 3-6→4 | >6→2
- Value = média(P/L pts, P/VP pts)

**Quality Score:**
- ROE×100:    >25%→10 | 15-25%→8 | 10-15%→6 | <10%→4
- Margem×100: >20%→10 | 10-20%→7 | 5-10%→5 | <5%→3
- Quality = média(ROE pts, Margem pts)

**Growth Score:**
- revenue_growth×100: >20%→10 | 10-20%→7 | 5-10%→5 | 0-5%→3 | <0%→1

**Risk Score:**
- debt_to_equity: <0.5→10 | 0.5-1→7 | 1-2→5 | >2→3
- current_ratio:  >2→10 | 1.5-2→7 | 1-1.5→5 | <1→2
- Risk = média(D/E pts, CR pts)

**FINAL = Value×0.30 + Quality×0.30 + Growth×0.25 + Risk×0.15**

| Score | Recomendação | Confiança |
|-------|-------------|-----------|
| ≥7.5  | STRONG BUY  | 90% |
| ≥6.5  | BUY         | 75% |
| ≥5.5  | HOLD        | 60% |
| ≥4.0  | SELL        | 70% |
| <4.0  | STRONG SELL | 85% |

## Formato de Output
```
📊 ANÁLISE FUNDAMENTALISTA — {TICKER}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 PREÇO

${price:.2f} ({change:+.2f}%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 MÚLTIPLOS

P/L:         {pe:.1f}x
P/VP:        {pb:.1f}x
ROE:         {roe:.1f}%
Marg. Líq:  {margin:.1f}%
Dívida/PL:  {de:.2f}
Rev. Growth: {growth:+.1f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 SCORES (0-10)

Value:    {v:.1f} {emoji}
Quality:  {q:.1f} {emoji}
Growth:   {g:.1f} {emoji}
Risk:     {r:.1f} {emoji}
FINAL:    {final:.1f} ⭐

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 {action} ({confidence}% confiança)
Fonte: Financial Datasets API
```
