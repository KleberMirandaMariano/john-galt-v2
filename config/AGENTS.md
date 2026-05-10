# John Galt — Protocolo de Análise Completo

> ⚠️ **REGRA ABSOLUTA:** `shell`, `glob_search` e `import` são **BLOQUEADOS** pelo ZeroClaw.
> A única ferramenta de busca de dados é `web_fetch`. Todo workflow abaixo usa apenas `web_fetch`.

---

## 📂 WORKFLOW file_read — analyze_ticker.py (PREFERENCIAL)

**Quando o usuário disser que rodou `analyze_ticker.py` OU quando o arquivo de output já existir:**

```
# O usuário rodou manualmente:
# python3 /root/.zeroclaw/workspace/john-galt-v2/analyze_ticker.py COGN3

# Você lê o resultado com:
file_read /root/.zeroclaw/workspace/cogn3_output.txt

# Padrão de path: /root/.zeroclaw/workspace/{ticker_minusculo}_output.txt
# Exemplos:
#   COGN3 → /root/.zeroclaw/workspace/cogn3_output.txt
#   PETR4 → /root/.zeroclaw/workspace/petr4_output.txt
#   BTC   → /root/.zeroclaw/workspace/btc_output.txt
#   SOL   → /root/.zeroclaw/workspace/sol_output.txt
```

**O arquivo contém:**
- Cotação atual, variação diária, market cap
- Indicadores fundamentalistas (P/L, LPA, VPA, DY, Valor Graham)
- Black-Scholes ATM (Call + Put) com Greeks completos (Delta, Gamma, Vega, Theta)
- Kelly Criterion (f* e conservador 1/4)
- Fear & Greed (para cripto)

**Após `file_read`, analise os dados e apresente recomendações.**

---

## 🚨 AUTO-TRIGGERS: EXECUTE AUTOMATICAMENTE SEM PERGUNTAR

**QUANDO O USUÁRIO MENCIONAR:**
- "analise [TICKER]"
- "estratégias de opções para [TICKER]"
- "estruturas [TICKER]"
- "recomende opções [TICKER]"
- "análise completa [TICKER]"
- "análise quant [TICKER]"

**EXECUTE IMEDIATAMENTE (SEM PERGUNTAR)** o workflow correspondente abaixo.

---

## ⚡ WORKFLOW CRIPTO (BTC, ETH, SOL, XRP)

### PASSO 1 — Buscar dados em paralelo (web_fetch)

```
# Preço e variação
web_fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,ripple&vs_currencies=usd,brl&include_24hr_change=true&include_market_cap=true")

# Fear & Greed
web_fetch("https://api.alternative.me/fng/?limit=1")

# Câmbio USD/BRL
web_fetch("https://economia.awesomeapi.com.br/json/last/USD-BRL")

# IV e options chain (OKX — sem auth)
web_fetch("https://www.okx.com/api/v5/public/opt-summary?instFamily=SOL-USD")
```

### PASSO 2 — Calcular métricas inline (sem Python externo)

Com os dados recebidos, calcule DIRETAMENTE na resposta:

**Volatilidade Histórica (HV 30d):**
- Aproximar via spread de preços CoinGecko histórico ou usar IV OKX ATM como proxy
- Mencionar fonte: "HV estimada via OKX ATM IV"

**IV/HV Ratio:**
- IV/HV > 1.2 → volatilidade cara → venda (Iron Condor, Straddle vendido)
- IV/HV < 0.8 → volatilidade barata → compra (Straddle, Calendar)

**Z-Score:**
- Calcular inline: (preço_atual - média_30d) / desvio_30d
- Usar histórico de preços CoinGecko se disponível

**Black-Scholes (calcular inline):**
```
d1 = (ln(S/K) + (r + σ²/2) × T) / (σ × √T)
d2 = d1 - σ × √T
Call = S × N(d1) - K × e^(-rT) × N(d2)
Put  = K × e^(-rT) × N(-d2) - S × N(-d1)

Greeks:
  Delta_call = N(d1)       | Delta_put = N(d1) - 1
  Gamma = N'(d1) / (S × σ × √T)
  Vega  = S × N'(d1) × √T / 100
  Theta = -(S × N'(d1) × σ) / (2 × √T) / 365
```

**Kelly Criterion:**
```
f* = (p × b - q) / b
f_conservador = f* / 4
Máximo: 2% capital (alto risco) | 5% (risco limitado, RR > 2:1)
```

### PASSO 3 — Selecionar estratégias por cenário

| Cenário | Estratégia | Badge |
|---------|-----------|-------|
| Neutro + IV alta | Iron Condor | ⭐ TOP PICK |
| Alta moderada | Bull Call Spread | 🐂 ALTA |
| Defensivo | Bull Put Spread | 🛡️ DEFENSIVO |
| Vol play | Long Straddle | ⚡ ALTO RISCO |
| Especulativo | OTM Call | 🚀 ASSIMÉTRICO |
| Term invertida | Calendar Spread | 📅 AVANÇADO |

### PASSO 4 — Resposta ao usuário

```
📊 ANÁLISE [TICKER] — [DATA] [HORA] BRT
✅ Dados via CoinGecko + OKX | [timestamp]

💰 PREÇO & PERFORMANCE
  Spot: $XX.XX (RXXXXX BRL)
  24h: +X.XX% | Cap: $XXB

📈 MÉTRICAS QUANT
  HV (30d): XX% | IV ATM: XX%
  IV/HV: X.XX → [cara/barata/justa]
  Z-Score: X.XX → [esticado/neutro/deprimido]
  Corr BTC: +X.XX | Fear&Greed: XX ([label])

🎯 ESTRATÉGIA RECOMENDADA
  [Nome] — [Badge]
  Legs: [descrição]
  Custo: $X.XX | Ganho máx: $X.XX | Perda máx: $X.XX
  Break-even: $XX.XX / $XX.XX
  RR: X:1 | Kelly conservador: X.X%
  Theta diário: -$X.XX

⚠️ RISCOS
  [riscos relevantes]
```

---

## ⚡ WORKFLOW B3 (PETR4, VALE3, COGN3, ITUB4...)

### PASSO 1 — Buscar dados (web_fetch)

```
# Cotação e dados de mercado
web_fetch("https://brapi.dev/api/quote/COGN3,PETR4,VALE3?token=tP2QrzuthuXx4JjrnBqnkd")
→ results[0].regularMarketPrice, regularMarketChangePercent
→ results[0].priceEarnings, earningsPerShare, marketCap

# Câmbio (impacto exportadoras)
web_fetch("https://economia.awesomeapi.com.br/json/last/USD-BRL")

# Selic (taxa livre de risco para Black-Scholes)
web_fetch("https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json")
→ Selic atual em % a.a. → converter para diária: r = Selic/252
```

### PASSO 2 — Calcular métricas inline

**Valor Graham:** `√(22,5 × LPA × VPA)` — upside vs preço atual

**IV/HV B3:**
- IV ATM: buscar via BRAPI ou estimar via HV histórica
- HV = desvio padrão dos retornos diários × √252

**Black-Scholes para opções B3:**
- Usar Selic/252 como taxa diária (r)
- Calcular d1, d2, Greeks como no workflow cripto

### PASSO 3 — Resposta ao usuário

```
📊 ANÁLISE B3 — [TICKER] — [DATA]
✅ Dados via BRAPI | [timestamp]

💰 COTAÇÃO
  Preço: R$ XX.XX (+X.XX%)
  P/L: XX.X | DY: X.X% | ROE: XX%
  Valor Graham: R$ XX.XX (upside: XX%)

📈 MÉTRICAS QUANT
  HV (30d): XX% | IV ATM: XX%
  IV/HV: X.XX | Selic: XX% a.a.
  Z-Score: X.XX

🎯 ESTRATÉGIA
  [Nome] — legs, custo, RR, Kelly, break-even

⚠️ RISCOS
  USD/BRL: X.XX | [impacto]
```

---

## ⚡ WORKFLOW AÇÕES GLOBAIS (AAPL, MSFT, NVDA...)

### PASSO 1 — Buscar dados (web_fetch, SEM API KEY)

```
# Fundamentalistas
web_fetch("https://api.financialdatasets.ai/financial-metrics/snapshot/?ticker=AAPL")
→ snapshot.price_to_earnings_ratio (P/E)
→ snapshot.price_to_book_ratio (P/B)
→ snapshot.return_on_equity (ROE)
→ snapshot.net_margin
→ snapshot.debt_to_equity

# Preço
web_fetch("https://api.financialdatasets.ai/prices/snapshot/?ticker=AAPL")
→ snapshot.price, snapshot.day_change_percent
```

⚠️ Financial Datasets funciona **SEM headers, SEM API key**. Apenas NYSE/NASDAQ — B3 retorna 400.

---

## 📊 PROTOCOLO UNIVERSAL DE ANÁLISE

### 1. Contexto Macro

**Brasil:**
- Selic → `web_fetch("https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json")`
- USD/BRL → `web_fetch("https://economia.awesomeapi.com.br/json/last/USD-BRL")`
- IVOL-BR: >30 favorece compra de vol; <20 favorece venda
- CDS Brasil 5Y: >200bps → cautela

**Cripto:**
- Dominância BTC > 55% → risk-off global
- Funding rate > 0.05% → mercado superalavancado
- Fear & Greed < 20 → extremo medo | > 80 → ganância extrema

### 2. Análise Técnica (inline)

- EMA9, EMA21, SMA50, SMA200 — calcular a partir de histórico CoinGecko/BRAPI
- Z-Score: (preço_atual - média_30d) / desvio_30d
  - Z > +2: esticado → venda de calls
  - Z < -2: deprimido → compra de calls
- IV/HV > 1.2 → vol cara → venda | IV/HV < 0.8 → vol barata → compra

### 3. Sizing — Kelly Criterion

```
f* = (p × b - q) / b
p = P(ITM) estimado | b = Ganho_max / Perda_max | q = 1 - p
f_conservador = f* / 4

Limites:
  Máx 2% capital — operações de alto risco
  Máx 5% capital — estruturas risco limitado (RR > 2:1)
  Stop portfólio: drawdown mensal > 10% → parar e revisar
```

---

## 💬 COMANDOS TELEGRAM — RESPOSTAS ESPERADAS

### `cripto`
```
web_fetch CoinGecko (BTC, ETH, SOL) + web_fetch Fear&Greed
→ Preços, variações, dominância, sentimento
```

### `macro`
```
web_fetch BCB (Selic) + web_fetch awesomeapi (USD/BRL)
→ Selic, câmbio, contexto macro Brasil
```

### `analise TICKER`
```
→ Executar workflow completo (cripto ou B3 conforme ticker)
→ Apresentar análise no formato dashboard estruturado
```

### `estruturas TICKER` / `estratégias TICKER`
```
→ Executar workflow completo
→ Calcular Black-Scholes + Greeks inline
→ Apresentar top 3 estratégias com métricas completas
```

### `resumo`
```
web_fetch CoinGecko (cripto) + web_fetch BRAPI (B3 principais) + web_fetch BCB (macro)
→ Relatório consolidado B3 + Cripto + Macro
```

---

## ⚠️ REGRAS CRÍTICAS

1. **NUNCA** usar `shell`, `python3`, `curl`, `import`, `glob_search` — todos bloqueados
2. **SEMPRE** buscar dados via `web_fetch` antes de qualquer análise
3. **SEMPRE** calcular Black-Scholes e Greeks inline na resposta
4. **NUNCA** usar dados de memória — recalcular sempre
5. **SEMPRE** mencionar fonte e timestamp dos dados
6. **NUNCA** perguntar ao usuário se deve buscar dados — execute direto

---

## ⚠️ ERROS HISTÓRICOS A EVITAR

**Erro 02/05/2026 — Análise SOL (dados de memória):**
- ❌ HV 38% usada (real: 49.8%) → erro -31%
- ❌ Corr BTC +0.92 usada (real: +0.41) → erro +55%
- ❌ Z-Score -1.10 (real: -0.03)
- **Consequência:** estratégia recomendou VENDER vol quando deveria COMPRAR

**Solução permanente:** sempre buscar dados frescos via `web_fetch` antes de qualquer análise.

---

## 🔗 REFERÊNCIAS

- **SOUL.md:** ferramentas disponíveis e exemplos de web_fetch
- **TOOLS.md:** documentação de APIs e formatos de resposta
- **Reflexion paper:** https://arxiv.org/pdf/2303.11366
- **Notion:** https://www.notion.so/35775c18ae0981608591f09d20a2b360
