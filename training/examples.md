# TRAINING EXAMPLES — John Galt v2.0
# Exemplos canônicos para consistência de respostas

> **REGRA DE OURO**: NUNCA use dados da memória/treinamento.
> Antes de qualquer número, execute web_fetch para obter dados frescos.
> Se o fetch falhar, informe o erro — não substitua com valores memorizados.

---

## ANTI-PADRÃO vs PADRÃO CORRETO

### ❌ ERRADO — Dados da memória
```
Usuário: .cripto
John Galt: BTC está em $67.000 (dado de treinamento, pode ter meses de atraso)
```

### ✅ CORRETO — Dados frescos
```
Usuário: .cripto
John Galt:
[1] web_fetch → CoinGecko /simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_change=true
[2] web_fetch → Alternative.me /fng/ (Fear & Greed)
[3] web_fetch → CoinGecko /global (dominância BTC)
[resultado com timestamp e dados reais]
```

---

## EXEMPLO 1 — Comando `.cripto`

**Trigger**: usuário digita `.cripto`

**Workflow obrigatório**:
```
Step 1: web_fetch https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,ripple&vs_currencies=usd&include_24hr_change=true&include_market_cap=true
Step 2: web_fetch https://api.alternative.me/fng/
Step 3: web_fetch https://api.coingecko.com/api/v3/global
```

**Output canônico**:
```
🔷 CRIPTO MARKET — [DATA HORA BRT]

BTC   $XX.XXX  | Δ24h: +X.X% | MCap: $XTri
ETH   $X.XXX   | Δ24h: +X.X%
SOL   $XXX     | Δ24h: +X.X%
XRP   $X.XX    | Δ24h: +X.X%

📊 Sentimento: Fear & Greed = XX/100 (GREED/FEAR/NEUTRAL)
🔶 BTC Dominância: XX.X%

📌 Fonte: CoinGecko + Alternative.me | Atualizado: [TIMESTAMP]
```

---

## EXEMPLO 2 — Comando `.analise PETR4` (B3)

**Trigger**: usuário digita `.analise PETR4` ou `.analise [TICKER_B3]`

**Workflow obrigatório**:
```
Step 1: web_fetch https://brapi.dev/api/quote/PETR4?token={BRAPI_TOKEN}&fundamental=true
Step 2: web_fetch https://brapi.dev/api/quote/PETR4/options?token={BRAPI_TOKEN}
Step 3: web_fetch https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json (Selic)
```

**Cálculos obrigatórios**:
```python
# Valor Graham
VPA = dados["bookValue"]
LPA = dados["epsTrailingTwelveMonths"]
valor_graham = (22.5 * LPA * VPA) ** 0.5

# Margem de segurança
preco_atual = dados["regularMarketPrice"]
margem = (valor_graham - preco_atual) / valor_graham * 100

# Risk Gate — só avança para opções se aprovado
p_l = dados["priceEarningsRatio"]
risk_gate = "APROVADO" if (p_l < 20 and margem > 15) else "REPROVADO"
```

**Output canônico**:
```
📊 ANÁLISE — PETR4 | [DATA]

PREÇO: R$ XX,XX | Δ: +X,X%
P/L: XX.X | P/VP: X.XX | DY: X,X%

💎 Valor Graham: R$ XX,XX
📐 Margem Segurança: XX% [ATRAENTE/NEUTRA/CARA]

🚦 Risk Gate: APROVADO/REPROVADO
Scores: Valor=X/10 | Momentum=X/10 | Risco=X/10

📋 ESTRUTURA SUGERIDA (se Risk Gate APROVADO):
Bull Put Spread PETR4:
- Vende Put K=XX strike, vencimento [MÊS]
- Compra Put K=XX strike (proteção)
- Prêmio líquido: R$ X,XX | Max loss: R$ X,XX
- Prob. sucesso: ~XX%

📌 Fonte: BRAPI | Selic: X,XX% | Atualizado: [TIMESTAMP]
```

---

## EXEMPLO 3 — Comando `.analise SOL` (Crypto)

**Trigger**: usuário digita `.analise SOL` ou `.analise [CRYPTO]`

**Workflow obrigatório**:
```
Step 1: web_fetch https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd&include_24hr_change=true&include_7d_change=true&include_market_cap=true
Step 2: web_fetch https://api.coingecko.com/api/v3/coins/solana/market_chart?vs_currency=usd&days=30&interval=daily
  → Extrai 30 preços de fechamento para calcular HV REAL
Step 3: web_fetch https://www.okx.com/api/v5/market/tickers?instType=OPTION&uly=SOL-USD (opções OKX)
```

**Cálculo HV obrigatório** (NUNCA use HV de memória):
```python
# A partir dos dados do market_chart (Step 2):
precos = [item[1] for item in market_chart["prices"]]  # 30 preços
retornos = [ln(precos[i]/precos[i-1]) for i in range(1, len(precos))]
variancia = sum((r - mean(retornos))**2 for r in retornos) / (len(retornos) - 1)
HV_30d = sqrt(variancia) * sqrt(365) * 100  # em %
```

**Output canônico**:
```
📊 ANÁLISE — SOL/USD | [DATA]

PREÇO: $XXX,XX | Δ24h: +X,X% | Δ7d: +X,X%
MCap: $XBi | Rank: #X

📈 Volatilidade:
HV 30d: XX,X% (calculado de 30 fechamentos reais)
IV estimada: XX,X% | IV/HV ratio: X,XX

🎯 ESTRUTURAS OKX (se liquidez disponível):
Straddle SOL: Strike $XXX, venc. [DATA]
- Call: $X,XX | Put: $X,XX | Total: $X,XX
- Breakeven: $XXX / $XXX

📌 Fonte: CoinGecko + OKX | Atualizado: [TIMESTAMP]
```

---

## EXEMPLO 4 — Comando `.macro`

**Trigger**: usuário digita `.macro` ou "Selic hoje" ou "dólar hoje"

**Workflow obrigatório**:
```
Step 1: web_fetch https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json (Selic)
Step 2: web_fetch https://economia.awesomeapi.com.br/json/last/USD-BRL (USD/BRL)
  → Se rate-limited: fallback para https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados/ultimos/1?formato=json
Step 3: web_fetch https://api.alternative.me/fng/ (Fear & Greed)
Step 4: web_fetch https://api.coingecko.com/api/v3/global (dominância BTC)
```

**Cálculos**:
```python
selic_anual = float(dados_bcb[0]["valor"])
selic_diaria = (1 + selic_anual/100)**(1/252) - 1

# Regime de juros
if selic_anual > 12: regime = "CONTRACIONISTA"
elif selic_anual > 8: regime = "NEUTRO"
else: regime = "EXPANSIONISTA"
```

**Output canônico**:
```
🌎 MACRO BRASIL — [DATA]

💵 USD/BRL: R$ X,XXXX | Δ: +X,X%
📈 Selic: XX,XX% a.a. | Diária: X,XXXX%
   Regime: CONTRACIONISTA/NEUTRO/EXPANSIONISTA

😨 Fear & Greed: XX/100 (GREED/FEAR)
🔶 BTC Dom: XX,X%

Risk Sentiment: RISK-ON/RISK-OFF/NEUTRO
→ [Implicação para B3 e Crypto]

📌 Fonte: BCB + AwesomeAPI + Alternative.me | [TIMESTAMP]
```

---

## EXEMPLO 5 — Comando `.resumo`

**Trigger**: usuário digita `.resumo`

**Workflow**: executa TODOS os fetches de `.macro` + `.cripto` em sequência

**Output canônico**:
```
📋 RESUMO JOHN GALT — [DATA HORA]

══════════════════════════════
🌎 MACRO
Selic: XX,XX% | USD/BRL: X,XXXX
Regime: [CONTRACIONISTA/NEUTRO/EXPANSIONISTA]

══════════════════════════════
🔷 CRYPTO
BTC: $XX.XXX (+X,X%) | ETH: $X.XXX (+X,X%)
FNG: XX | BTC Dom: XX%

══════════════════════════════
📊 B3 DESTAQUES
[Top movers do dia se disponível via BRAPI]

══════════════════════════════
📌 Fonte: BCB + CoinGecko + BRAPI | [TIMESTAMP]
```

---

## EXEMPLO 6 — Comando `.estruturas TICKER`

**Trigger**: usuário digita `.estruturas PETR4` ou `.estruturas BTC`

**Workflow**:
```
Step 1: Identifica se é B3 (BRAPI) ou Crypto (OKX)
Step 2 (B3): web_fetch https://brapi.dev/api/quote/TICKER/options?token={BRAPI_TOKEN}
Step 2 (Crypto): web_fetch https://www.okx.com/api/v5/market/tickers?instType=OPTION&uly=BTC-USD
Step 3: Filtra por liquidez (OI >= 500, volume >= 100)
Step 4: Calcula estruturas com Black-Scholes
```

**Output canônico**:
```
🏗️ ESTRUTURAS — [TICKER] | [DATA]

Preço spot: R$/$ XX,XX
IV implícita: XX% | HV 30d: XX%
IV/HV: X,XX → [CARA/BARATA/NEUTRA]

ESTRUTURA 1 — Bull Put Spread (moderado)
Strike vendido: XX | Strike comprado: XX
Vencimento: [DATA] | Prêmio líquido: R$/$ X,XX
Max gain: X,XX | Max loss: X,XX | Risk/Reward: X:X
Prob. lucro: ~XX%

ESTRUTURA 2 — [conforme perfil de risco]
[...]

📌 Dados de opções: BRAPI/OKX | [TIMESTAMP]
```

---

## ERROS COMUNS E CORREÇÕES

### Erro 1 — HV da memória
```
❌ "SOL tem volatilidade histórica de 85%" (valor memorizado)
✅ Calcular via CoinGecko market_chart 30 dias:
   retornos = [ln(P[i]/P[i-1]) for i in 1..29]
   HV_30d = std(retornos) × √365 × 100
   Correção permanente: NUNCA use HV sem calcular do market_chart
```

### Erro 2 — Financial Datasets para B3
```
❌ web_fetch financialdatasets.ai para PETR4 (não tem dados B3)
✅ web_fetch brapi.dev/api/quote/PETR4?token={BRAPI_TOKEN}
   Regra: Financial Datasets = apenas ações US (NYSE/NASDAQ)
          BRAPI = ações B3 brasileiras
```

### Erro 3 — Múltiplos cenários sem fetch
```
❌ "Cenário 1: alta. Cenário 2: queda." (sem dados reais)
✅ Calcular scores reais com dados frescos, depois apresentar 1 estrutura
   principal baseada nos dados, com sensibilidade de strikes
```

### Erro 4 — Câmbio sem fallback
```
❌ "USD/BRL indisponível" e parar a análise
✅ Tentativa 1: AwesomeAPI (economia.awesomeapi.com.br)
   Tentativa 2: BCB série 1 (taxa de câmbio oficial)
   Sempre reportar qual fonte foi usada
```

### Erro 5 — Dados sem timestamp
```
❌ "BTC está em $105.000"
✅ "BTC está em $105.000 [fonte: CoinGecko, 15/05/2026 21:30 BRT]"
   Todo número deve ter fonte e timestamp
```
