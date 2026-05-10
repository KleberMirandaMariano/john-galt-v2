# Financial Datasets — Análise Fundamentalista

## Quando usar
Sempre que o usuário pedir análise fundamentalista, múltiplos (P/L, ROE, margem), comparação de ações globais (NYSE/NASDAQ) ou score de qualidade de empresa.

## API Key
A variável de ambiente está disponível no workspace:
`FINANCIAL_DATASETS_API_KEY`

## Como buscar dados

### 1. Preço atual de uma ação

```
web_fetch(
  url="https://api.financialdatasets.ai/prices/snapshot/?ticker=AAPL",
  headers={"Authorization": "Bearer {FINANCIAL_DATASETS_API_KEY}"}
)
```

**Response:**
```json
{
  "snapshot": {
    "ticker": "AAPL",
    "price": 293.50,
    "day_change": 6.10,
    "day_change_percent": 2.11
  }
}
```

### 2. Fundamentalistas / Múltiplos

```
web_fetch(
  url="https://api.financialdatasets.ai/financial-metrics/snapshot/?ticker=AAPL",
  headers={"Authorization": "Bearer {FINANCIAL_DATASETS_API_KEY}"}
)
```

**Response:**
```json
{
  "snapshot": {
    "ticker": "AAPL",
    "report_period": "2024-12-28",
    "pe_ratio": 36.0,
    "price_to_book_ratio": 40.4,
    "return_on_equity": 1.126,
    "return_on_assets": 0.323,
    "net_margin": 0.270,
    "debt_to_equity": 1.97,
    "current_ratio": 0.87,
    "revenue_growth": 0.082,
    "earnings_growth": null,
    "dividend_yield": 0.0043
  }
}
```

### 3. Earnings / Resultados

```
web_fetch(
  url="https://api.financialdatasets.ai/stocks/{TICKER}/earnings?limit=4",
  headers={"Authorization": "Bearer {FINANCIAL_DATASETS_API_KEY}"}
)
```

## Como calcular Scores (fazer inline, sem Python)

Com os dados acima, calcule mentalmente:

**Value Score (0-10):**
- P/E < 10 → 10 pts | P/E 10-15 → 8 pts | P/E 15-25 → 6 pts | P/E 25-40 → 4 pts | P/E > 40 → 2 pts
- P/B < 1.5 → 10 pts | P/B 1.5-3 → 7 pts | P/B 3-6 → 4 pts | P/B > 6 → 2 pts
- Dividend Yield > 5% → 10 pts | 3-5% → 7 pts | 1-3% → 4 pts | <1% → 1 pt
- **Value = média dos 3**

**Quality Score (0-10):**
- ROE > 25% → 10 pts | 15-25% → 8 pts | 10-15% → 6 pts | 5-10% → 4 pts | <5% → 2 pts
- Net Margin > 20% → 10 pts | 10-20% → 7 pts | 5-10% → 5 pts | <5% → 3 pts
- **Quality = média dos 2**

**Growth Score (0-10):**
- Revenue Growth > 20% → 10 pts | 10-20% → 7 pts | 5-10% → 5 pts | 0-5% → 3 pts | <0% → 1 pt

**Risk Score (0-10):**
- Debt/Equity < 0.5 → 10 pts | 0.5-1 → 7 pts | 1-2 → 5 pts | >2 → 3 pts
- Current Ratio > 2 → 10 pts | 1.5-2 → 7 pts | 1-1.5 → 5 pts | <1 → 2 pts
- **Risk = média dos 2**

**Score Final = Value×0.30 + Quality×0.30 + Growth×0.25 + Risk×0.15**

**Recomendação:**
- ≥ 7.5 → STRONG BUY (90%)
- ≥ 6.5 → BUY (75%)
- ≥ 5.5 → HOLD (60%)
- ≥ 4.0 → SELL (70%)
- < 4.0 → STRONG SELL (85%)

## Formato de Output

```
📊 ANÁLISE FUNDAMENTALISTA — {TICKER}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 PREÇO

Preço: ${price} ({change:+.2f}%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 MÚLTIPLOS

P/L:         {pe_ratio}
P/VP:        {pb_ratio}
ROE:         {roe*100:.1f}%
Marg. Líq:  {net_margin*100:.1f}%
Dívida/PL:  {debt_to_equity}
Div. Yield: {dividend_yield*100:.1f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 SCORES (0-10)

Value:    {value_score}/10 {emoji}
Quality:  {quality_score}/10 {emoji}
Growth:   {growth_score}/10 {emoji}
Risk:     {risk_score}/10 {emoji}

FINAL:    {final_score}/10 ⭐

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 RECOMENDAÇÃO

{action} ({confidence}% confiança)
```

## Tickers suportados
- NYSE/NASDAQ: AAPL, MSFT, GOOGL, META, NVDA, XOM, etc.
- B3 via sufixo .SA: PETR4.SA, VALE3.SA, ITUB4.SA — **mas API retorna 400, não disponível**
- Cripto: BTC-USD, SOL-USD, ETH-USD (endpoint diferente)

## REGRA CRÍTICA
- NUNCA invente múltiplos ou scores
- Se API retornar 400 para ticker B3 → avisar que Financial Datasets não cobre B3
- Para ações brasileiras, usar análise qualitativa via web_fetch para notícias + BRAPI para preços
- SEMPRE mostrar a fonte: "Fonte: Financial Datasets API"
