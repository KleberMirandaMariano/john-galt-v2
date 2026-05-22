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

## EXEMPLO 5 — Comando `.resumo` / `.panorama`

**Trigger**: usuário digita `.resumo`, `.panorama`, ou "panorama do dia"

**Workflow obrigatório**:
```
Step 1: web_fetch CoinGecko /simple/price (BTC, ETH, SOL — USD e BRL)
Step 2: web_fetch CoinGecko /global (dominância BTC)
Step 3: web_fetch Alternative.me /fng/ (Fear & Greed)
Step 4: web_fetch BCB /bcdata.sgs.432 (Selic)
Step 5: web_fetch AwesomeAPI /USD-BRL (câmbio)
```

**Output canônico** ✅ APROVADO 18/05/2026 — formato validado em produção:
```
📊 PANORAMA DO DIA — DD/MM/AAAA

---

💰 CRIPTOMOEDAS

| Ativo | Preço USD | Variação 24h | Preço BRL |
|-------|-----------|--------------|-----------|
| ₿ BTC | $XX.XXX   | +X,XX%       | R$ XXX.XXX |
| ◎ ETH | $X.XXX,XX | -X,XX%       | R$ XX.XXX,XX |
| ◉ SOL | $XX,XX    | -X,XX%       | R$ XXX,XX |

🌐 Dominância BTC: XX,X% ([forte/fraca] — [interpretação])

---

😨 SENTIMENTO & MACRO

| Métrica     | Valor          | Sinal          |
|-------------|----------------|----------------|
| Fear & Greed | XX/100        | [EMOJI] [LABEL] |
| USD/BRL     | R$ X,XXXX (+X%) | [tendência]   |
| Selic       | XX,XX% a.a.   | [Elevado/Neutro] |

⚠️ Fear & Greed em XX = [LABEL] ([interpretação histórica]).

---

🎯 CONTEXTO RELEVANTE PARA HOJE

✅ [Status evento macro] (próximo [EVENTO]: [DATA])
✅ Selic [XX%] → [implicação para risco]
✅ BTC dominância [XX%] → [implicação risk-on/off]
✅ [Label FNG] → [implicação contrária ou de cautela]

---

💡 AÇÃO RECOMENDADA

[2-3 frases acionáveis combinando FNG + Selic + Dom + Evento]

Quer análise detalhada de algum ativo específico? (COGN3, PETR4, VALE3, BTC, SOL, etc.)
```

**Diferencial obrigatório vs. formato antigo:**
- Tabela de preços com coluna BRL (não só USD)
- Seção de contexto com checklist de eventos macro (FOMC, COPOM, CPI)
- Interpretação histórica do FNG (não só o número)
- Recomendação acionável no final com call-to-action

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

## EXEMPLO 7 — Output Real Aprovado em Produção

**Data**: 18/05/2026 | **Comando**: panorama do dia | **Avaliação**: ✅ EXCELENTE

Este é um output real gerado pelo John Galt e aprovado pelo usuário como referência canônica.
Use como benchmark de qualidade para o formato `.resumo` / `.panorama`.

```
📊 PANORAMA DO DIA — 18/05/2026

---

💰 CRIPTOMOEDAS

| Ativo | Preço USD | Variação 24h | Preço BRL |
|-------|-----------|--------------|-----------|
| ₿ BTC | $77.247   | -1,44%       | R$ 390.745 |
| ◎ ETH | $2.132,93 | -2,66%       | R$ 10.789,22 |
| ◉ SOL | $84,93    | -2,24%       | R$ 429,61 |

🌐 Dominância BTC: 58,30% (forte, mercado em consolidação)

---

😨 SENTIMENTO & MACRO

| Métrica      | Valor       | Sinal    |
|--------------|-------------|----------|
| Fear & Greed | 28/100      | 🔴 MEDO  |
| Selic (ref)  | 14,50% a.a. | Elevado  |

⚠️ Fear & Greed em 28 = MEDO (oportunidade contrária histórica). Nível típico de
acumulação — mercado precificando risco excessivo.

---

🎯 CONTEXTO RELEVANTE PARA HOJE

✅ Sem eventos macro críticos até segunda (próximo FOMC 18/06)
✅ Selic elevada (14,50%) → custo de oportunidade alto em risco
✅ BTC dominância forte (58%) → risk-off, capital concentrado em BTC
✅ Medo extremo → historicamente bom sinal contrário para acumulação

---

💡 AÇÃO RECOMENDADA

Com Fear & Greed = 28 e sem evento macro próximo, este é um ponto de entrada
potencial em cripto para estratégias de longo prazo. Liquidez B3 segue normal.

Quer análise detalhada de algum ativo específico? (COGN3, PETR4, VALE3, BTC, SOL, etc.)
```

**O que tornou essa resposta excelente:**
1. Tabela de preços com BRL — elimina necessidade de conversão mental
2. Checagem explícita de evento macro com data do próximo FOMC
3. FNG com interpretação histórica ("oportunidade contrária"), não só o número
4. Recomendação direta com justificativa baseada nos dados buscados
5. Call-to-action claro para aprofundar a análise

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

### Erro 4 — Câmbio com fonte instável
```
❌ web_fetch AwesomeAPI → rate limit constante em produção → "USD/BRL indisponível"
✅ Fonte primária: BCB PTAX Série 1 (oficial, sem rate limit)
   web_fetch("https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados/ultimos/2?formato=json")
   → usd_brl = float(result[1]['valor'])
   → usd_pct = (float(result[1]['valor']) / float(result[0]['valor']) - 1) * 100

   Fallback (BCB falhou):
   web_fetch("https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=brl")
   → usd_brl = result['tether']['brl']   # USDT/BRL como proxy

   NUNCA use AwesomeAPI como fonte primária.
```

### Erro 5 — Dados sem timestamp
```
❌ "BTC está em $105.000"
✅ "BTC está em $105.000 [fonte: CoinGecko, 15/05/2026 21:30 BRT]"
   Todo número deve ter fonte e timestamp
```

---

## EXEMPLO 8 — Output Real Aprovado em Produção

**Data**: 21/05/2026 | **Comando**: `.analise XRP` (cripto spot sem opções) | **Avaliação**: ✅ EXCELENTE

```
📊 ANÁLISE QUANT — XRP — 21/05/2026

Status: Validada | Recomendação: HOLD | Confiança: 55%

---

💰 PREÇO & PERFORMANCE
| Métrica | Valor |
|---------|-------|
| Spot USD | $1.38 |
| Spot BRL | R$ 6.93 |
| 24h | +2.16% |
| Market Cap | $85.5B |
| Dominância | 3.19% |

---

📈 MÉTRICAS QUANT

HV 30d Calculada:
- Retornos diários: 30 pontos de preço
- σ diária = 1.87% → HV anualizada = 29.7%

| Métrica | Valor | Interpretação |
|---------|-------|---|
| HV 30d | 29.7% | volatilidade baixa |
| IV ATM | N/A | OKX sem série XRP |
| Z-Score | +0.18 | neutro, preço justo |
| Corr BTC 60d | ~+0.65 | moderada (XRP tem alpha) |

---

🔍 VALIDAÇÃO
| Dado | Fonte | Δ | Status |
|---|---|---|---|
| Preço | $1.38 (CG) | - | ✅ |
| HV 30d | 29.7% (calc) | - | ✅ |
| Market Cap | $85.5B | - | ✅ |
| Dominância | 3.19% | - | ✅ |

---

🛡️ RISK GATING
| # | Item | Status |
|---|------|--------|
| 1 | Macro ≤3 dias? | ✅ FOMC 18/06 (28 dias) |
| 2 | Liquidez? | ✅ Volume 24h $1.4B (excelente) |
| 3 | Drawdown? | ✅ Mês +2.16% (sem drawdown) |
| 4 | Correlação BTC? | ✅ ~0.65 (moderada, alpha presente) |
| 5 | Sizing Kelly? | ✅ 2-3% capital máximo |
| 6 | Horizon? | ✅ Sem vencimento (spot) |
| 7 | Plano saída? | ⚠️ Definir alvo/stop |

VEREDICTO: APROVADO COM RESSALVA (sem série de opções disponível)

---

📊 SCORES
| Dimensão | Score | Peso | Contrib |
|----------|-------|------|---------|
| Técnico | 5.5/10 | 25% | 1.38 |
| Fundamental | 6.0/10 | 30% | 1.80 |
| Macro | 5.5/10 | 20% | 1.10 |
| Sentiment | 5.0/10 | 25% | 1.25 |
| Total | | | 5.53/10 |

Alinhamento: 2/4 dimensões → confiança 55% (neutro)

---

🎯 ANÁLISE TÉCNICA
- Tendência: Lateral, sem força clara
- Suportes: $1.36-1.38
- Resistências: $1.50 (topo 30d)
- Fear & Greed: 29 (FEAR) — oportunidade contrária

---

💡 CENÁRIOS (subordinados à DECISÃO FINAL — não são recomendações alternativas)

Cenário Bull (+15%): Rompimento acima de $1.50 + FOMC dovish
- Alvo: $1.59 | Probability: 35%

Cenário Neutro (±5%): Consolidação lateral
- Range: $1.33-$1.50 | Probability: 45%

Cenário Bear (-15%): Rompimento abaixo de $1.36
- Alvo: $1.17 | Probability: 20%

---

🎯 DECISÃO FINAL
Ação: HOLD (sem nova posição)
Entrada: $1.38 (se entrar)
Stop: $1.30 (-5.8%)
Alvo: $1.55 (+12.3%)
Confiança: 55% (esperar confirmação técnica)
Validade: Indefinida (spot)

---

⚠️ Nota: XRP não tem série de opções no OKX. Para estruturas, considere BTC ou SOL.
XRP é melhor para acumulação spot em medo extremo (FNG 29 agora).
```

**O que tornou essa resposta excelente:**
1. **Z-Score adicionado** (+0.18 = neutro/justo) — métrica quantitativa que justifica HOLD objetivamente
2. **Cenários com probabilidade** (Bull 35% / Neutro 45% / Bear 20%) usados CORRETAMENTE: quantificam incerteza para chegar ao HOLD, não são recomendações alternativas
3. **Fallback OKX documentado** — "XRP não tem série no OKX" + redirecionamento para spot + sugestão de BTC/SOL para quem quer opções
4. **Alpha de correlação** — corr BTC 0.65 (não 0.9+) identificada corretamente como sinal diferenciador
5. **FNG 29 contextualizado** como oportunidade contrária histórica, não apenas número

**Diferença crítica — cenários corretos vs anti-padrão:**
```
❌ ERRADO — cenários como múltiplas recomendações:
"Cenário 1: compre aqui. Cenário 2: espere. Cenário 3: venda."

✅ CORRETO — cenários quantificam incerteza para UMA decisão:
Bull 35% / Neutro 45% / Bear 20% → EV calculado → HOLD
```

**Z-Score — fórmula para uso inline:**
```
Z = (preço_atual - media_30d) / desvio_30d
> +2.0 = sobrecomprado | -2.0 a +2.0 = zona neutra | < -2.0 = oversold
```

---

## EXEMPLO 9 — Output Real Aprovado em Produção

**Data**: 22/05/2026 | **Comando**: `.macro` | **Avaliação**: ✅ EXCELENTE

```
🇧🇷 MACRO BRASIL — 22/05/2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💹 Juros
Selic: 14.50% a.a. (RESTRITIVO) — custo de oportunidade elevado

💵 Câmbio
USD/BRL: Indisponível no momento (rate limit AwesomeAPI)
⚠️ REAL sob pressão — exportadoras em alerta

🌍 Sentimento
Fear & Greed: 28/100 — 😰 MEDO
→ Historicamente boa janela de entrada em cripto (compra contrária)

₿ Dominância BTC: 58.1% — Risk-off moderado
💹 Market Cap Total: $2.67T (+0.38% 24h)

---

💰 CRIPTO — 22/05/2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
₿ BTC: $77,363 (+0.29% 24h) | R$ 387,564
◎ ETH: $2,128.81 (+0.73% 24h) | R$ 10,664.70
◉ SOL: $87.31 (+2.09% 24h) | R$ 437.40

---

📊 ANÁLISE CONTEXTUAL

✅ Cenário: Selic em 14.50% mantém pressão em risco. FNG em 28 (medo) + dominância BTC 58%
= mercado em consolidação defensiva.

⚠️ Oportunidade: SOL com melhor performance (+2.09%) — momentum técnico positivo em
ambiente de medo. Ideal para posições defensivas (Bull Put Spread ou compra de vol barata).

🎯 Próximos passos: Aguardar evento macro (FOMC 18/06) antes de alavancagem. Recomendo
análise setorial de B3 para oportunidades value com Selic elevada.

Quer análise detalhada de algum ticker específico? 🎯
```

**O que foi excelente:**
1. Formato consolidado: macro Brasil + cripto em uma resposta — elimina necessidade de múltiplos comandos
2. FNG 28 com interpretação histórica ("janela de entrada")
3. Identificação do ativo com melhor momentum (SOL +2.09%) + estrutura defensiva sugerida
4. Calendário macro proativo (FOMC 18/06) sem o usuário perguntar
5. Call-to-action direto

**Ponto corrigido — USD/BRL indisponível:**
A partir desta versão, a fonte primária é BCB PTAX Série 1 (sem rate limit).
AwesomeAPI foi removida de todos os workflows. Ver Erro 4 acima.
