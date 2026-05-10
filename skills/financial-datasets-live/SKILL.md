# Financial Datasets — Análise Fundamentalista Global

## Quando usar
Sempre que pedir análise fundamentalista de ação global (NYSE/NASDAQ): AAPL, MSFT, NVDA, GOOGL, META, XOM, etc.
NÃO usar para B3 — para ações brasileiras usar BRAPI + análise qualitativa.

## ✅ COMO BUSCAR — SEM API KEY, SEM HEADERS

### 1. Múltiplos e Fundamentalistas

web_fetch("https://api.financialdatasets.ai/financial-metrics/snapshot/?ticker=AAPL")

Campos disponíveis em snapshot:
- price_to_earnings_ratio   → P/L
- price_to_book_ratio       → P/VP
- gross_margin              → Margem Bruta (×100 = %)
- operating_margin          → Margem Operacional
- net_margin                → Margem Líquida
- return_on_equity          → ROE (×100 = %)
- return_on_assets          → ROA (×100 = %)
- debt_to_equity            → Dívida/PL
- revenue_growth            → Crescimento Receita
- dividend_yield            → Dividend Yield
- current_ratio             → Liquidez Corrente

### 2. Preço Atual

web_fetch("https://api.financialdatasets.ai/prices/snapshot/?ticker=AAPL")

Campos em snapshot:
- price                 → Preço atual
- day_change_percent    → Variação %

## Como calcular Scores (inline, sem Python)

Value Score (P/L):  <10→10pts | 10-15→8 | 15-25→6 | 25-40→4 | >40→2
Value Score (P/VP): <1.5→10  | 1.5-3→7 | 3-6→4   | >6→2
Value = média dos dois

Quality Score (ROE):    >25%→10 | 15-25%→8 | 10-15%→6 | <5%→2
Quality Score (Margem): >20%→10 | 10-20%→7 | 5-10%→5  | <5%→3
Quality = média dos dois

Growth Score: >20%→10 | 10-20%→7 | 5-10%→5 | 0-5%→3 | <0%→1

Risk Score (D/E):    <0.5→10 | 0.5-1→7 | 1-2→5 | >2→3
Risk Score (Curr.R): >2→10   | 1.5-2→7 | 1-1.5→5 | <1→2
Risk = média dos dois

FINAL = Value×0.30 + Quality×0.30 + Growth×0.25 + Risk×0.15

Recomendação: ≥7.5→STRONG BUY | ≥6.5→BUY | ≥5.5→HOLD | ≥4.0→SELL | <4.0→STRONG SELL

## Para B3 (COGN3, PETR4, VALE3, etc.)

web_fetch("https://brapi.dev/api/quote/COGN3?token=tP2QrzuthuXx4JjrnBqnkd")

Campos disponíveis no plano atual:
- regularMarketPrice         → Preço
- regularMarketChangePercent → Variação %
- marketCap                  → Market Cap (BRL)
- priceEarnings              → P/L
- earningsPerShare           → EPS
- fiftyTwoWeekHigh/Low       → Máx/Mín 52 semanas

Scores com dados B3: calcular Value(P/L) + análise qualitativa para demais.

## REGRA CRÍTICA
- Financial Datasets: NYSE/NASDAQ apenas — ZERO autenticação necessária
- BRAPI: B3 apenas — token tP2QrzuthuXx4JjrnBqnkd
- NUNCA inventar múltiplos
- SEMPRE indicar: "Fonte: Financial Datasets" ou "Fonte: BRAPI"
