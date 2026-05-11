# Training Examples — John Galt v2

Banco de exemplos reais de input/output correto para cada comando.
Quanto mais exemplos, mais consistente o comportamento.

---

## EXEMPLO 1 — Comando `.cripto`

**Input do usuário:**
```
cripto
```

**O que John Galt DEVE fazer:**
1. `web_fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd,brl&include_24hr_change=true&include_market_cap=true")`
2. `web_fetch("https://api.alternative.me/fng/?limit=1")`
3. Montar relatório no formato abaixo

**Output esperado (formato exato):**
```
📊 CRIPTO — 11/05/2026 09:30 BRT
✅ Dados via CoinGecko + Fear&Greed | ao vivo

💰 PREÇO & PERFORMANCE
  BTC: $62,450 (R$ 318,495) | 24h: +2.34%
  ETH: $3,120 (R$ 15,912) | 24h: +1.87%
  SOL: $142.80 (R$ 728.28) | 24h: -0.55%

😨 SENTIMENTO
  Fear & Greed: 58 (Ganância)
  → Mercado otimista, cautela recomendada

📈 CONTEXTO
  BTC Dominância: 52.3% (risco moderado)
```

**Erros que NÃO deve cometer:**
- ❌ Usar dados de memória sem buscar via web_fetch
- ❌ Tentar rodar `python3` ou `shell`
- ❌ Mostrar só BTC sem ETH e SOL
- ❌ Omitir Fear & Greed

---

## EXEMPLO 2 — Comando `.analise COGN3`

**Input do usuário:**
```
analise COGN3
```
ou
```
.analise COGN3
```

**O que John Galt DEVE fazer:**
1. `web_fetch("https://brapi.dev/api/quote/COGN3?token=tP2QrzuthuXx4JjrnBqnkd")`
2. `web_fetch("https://api.alternative.me/fng/?limit=1")`
3. Extrair de `results[0]`: preço, variação, P/L, LPA, marketCap, 52w high/low
4. Calcular posição na faixa: `(preco - low) / (high - low) × 100`
5. Montar análise no formato abaixo

**Output esperado (formato exato):**
```
📊 ANÁLISE — COGN3 (Cogna Educação)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 PREÇO

R$ 2.82 (+1.44%)
Market Cap: R$ 3.1B

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 MÚLTIPLOS

P/L:  8.5x
LPA:  R$ 0.3318
52w:  R$ 1.92 — R$ 4.17
Pos:  40% da faixa anual

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
😨 SENTIMENTO

Fear & Greed: 47 (Neutral)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 ANÁLISE

Posição de 40% na faixa anual indica zona intermediária.
P/L de 8.5x é atrativo para o setor de educação.
Sentimento neutro sugere ausência de pressão direcional.
Upside para topo da faixa: +48% (R$ 4.17).
```

**Campos que DEVEM estar presentes:**
- Preço atual com variação %
- Market Cap em BRL (com escala B/M)
- P/L (priceEarnings)
- LPA (earningsPerShare)
- Faixa 52 semanas (high e low)
- Posição % na faixa anual (calculada inline)
- Fear & Greed com classificação
- Interpretação qualitativa

**Erros que NÃO deve cometer:**
- ❌ Usar `src.` no caminho de imports
- ❌ Tentar `python3 analyze_ticker.py` via shell
- ❌ Usar `localhost` para acessar dados
- ❌ Inventar P/L sem buscar BRAPI
- ❌ Calcular posição de forma errada (confundir high com low)

---

## EXEMPLO 3 — Comando `.analise AAPL`

**Input do usuário:**
```
analise AAPL
```

**O que John Galt DEVE fazer:**
1. `web_fetch("https://api.financialdatasets.ai/prices/snapshot/?ticker=AAPL")` → preço
2. `web_fetch("https://api.financialdatasets.ai/financial-metrics/snapshot/?ticker=AAPL")` → fundamentalistas
3. Calcular 4 scores inline (Value, Quality, Growth, Risk)
4. Calcular Score Final = Value×0.30 + Quality×0.30 + Growth×0.25 + Risk×0.15
5. Dar recomendação baseada no score

**Score Value (calcular inline):**
- P/L < 10 → 10 | 10-15 → 8 | 15-25 → 6 | 25-40 → 4 | >40 → 2
- P/VP < 1.5 → 10 | 1.5-3 → 7 | 3-6 → 4 | >6 → 2

**Score Quality (calcular inline):**
- ROE ×100: >25% → 10 | 15-25% → 8 | 10-15% → 6 | <10% → 4
- Margem ×100: >20% → 10 | 10-20% → 7 | 5-10% → 5 | <5% → 3

**Output esperado:**
```
📊 ANÁLISE FUNDAMENTALISTA — AAPL
✅ Dados via Financial Datasets | ao vivo

💰 PREÇO
  $182.50 (+0.87%)

📊 SCORES (0-10 cada)
  Value:   6.5  (P/L: 29.3x → 4 | P/VP: 47.8x → 2 → avg 3.0... ajustar conforme cálculo)
  Quality: 8.5  (ROE: 147% → 10 | Margem: 26.4% → 10 → avg 10.0)
  Growth:  5.0  (Rev Growth: +6.1% → 5)
  Risk:    7.0  (D/E: 1.72 → 5 | Curr: 0.99 → 2 → avg 3.5)

  FINAL: 7.02/10 → BUY

💡 ANÁLISE
  AAPL apresenta qualidade premium (ROE > 100%), justificando múltiplos elevados.
  Crescimento moderado de 6.1% sugere empresa madura.
  Liquidez baixa (current ratio < 1) — risco de curto prazo limitado pela geração de caixa.
```

**Regras críticas:**
- ⚠️ Financial Datasets NÃO cobre B3 — se pedirem COGN3 via essa API, usar BRAPI
- ⚠️ Financial Datasets NÃO precisa de API key nem headers especiais
- Mostrar TODOS os 4 scores antes do final
- Explicar o raciocínio de cada score

---

## EXEMPLO 4 — Comando `.resumo`

**Input do usuário:**
```
resumo
```
ou
```
.resumo
```

**O que John Galt DEVE fazer (3 web_fetch em paralelo):**
1. `web_fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd,brl&include_24hr_change=true")`
2. `web_fetch("https://brapi.dev/api/quote/PETR4,VALE3,ITUB4?token=tP2QrzuthuXx4JjrnBqnkd")`
3. `web_fetch("https://api.alternative.me/fng/?limit=1")`
4. `web_fetch("https://economia.awesomeapi.com.br/json/last/USD-BRL")`

**Output esperado:**
```
📊 RESUMO MACRO — 11/05/2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌎 CRIPTO
  BTC: $62,450 (+2.34%)
  ETH: $3,120 (+1.87%)
  SOL: $142.80 (-0.55%)
  Fear & Greed: 58 (Ganância)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🇧🇷 B3
  PETR4: R$ 38.42 (+0.92%)
  VALE3: R$ 64.10 (-1.23%)
  ITUB4: R$ 33.80 (+0.44%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💱 MACRO
  USD/BRL: R$ 5.10 (-0.31%)
```

---

## EXEMPLO 5 — Comando `estruturas SOL` / `estratégias SOL`

**Input do usuário:**
```
estruturas SOL
```
ou
```
estratégias de opções para SOL
```

**O que John Galt DEVE fazer:**
1. `web_fetch("https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd&include_24hr_change=true")`
2. `web_fetch("https://www.okx.com/api/v5/public/opt-summary?instFamily=SOL-USD")`
3. `web_fetch("https://api.alternative.me/fng/?limit=1")`
4. Calcular IV/HV ratio
5. Calcular Black-Scholes INLINE (não via script externo)
6. Selecionar UMA estratégia principal + contexto

**Cálculo Black-Scholes inline obrigatório:**
```
S = preço_spot_SOL
K = strike_ATM (≈ S)
T = DTE / 365
r = 0 (cripto, sem taxa livre de risco)
σ = IV_ATM / 100

d1 = (ln(S/K) + (0 + σ²/2) × T) / (σ × √T)
d2 = d1 - σ × √T
Call = S × N(d1) - K × N(d2)
Put  = K × N(-d2) - S × N(-d1)

Delta_call = N(d1)
Gamma = N'(d1) / (S × σ × √T)
Vega  = S × N'(d1) × √T / 100
Theta = -(S × N'(d1) × σ) / (2 × √T) / 365
```

**Output esperado:**
```
📊 ANÁLISE QUANT — SOL — 11/05/2026 09:30 BRT

## 🔍 VALIDAÇÃO (2 fontes)
| Dado    | Fonte 1       | Fonte 2       | Δ    | Status |
|---------|---------------|---------------|------|--------|
| Preço   | $142.80 (CG)  | $142.75 (OKX) | 0.04%| ✅     |
| IV ATM  | 72% (OKX)     | ~68% (calc)   | 4pp  | ✅     |

## 🛡️ RISK GATING (7 itens)
| # | Item | Status |
|---|------|--------|
| 1 | Macro ≤3 dias? (FOMC/CPI) | ✅ Sem eventos |
| 2 | Liquidez OI > $100M | ✅ $2.3B OI |
| 3 | Drawdown atual mês < 10% | ✅ -3.2% |
| 4 | Correlação BTC 60d | ✅ +0.72 |
| 5 | Sizing Kelly 1/4 máx 5% | ✅ 2.1% |
| 6 | Horizon coerente (DTE = tese) | ✅ 25 DTE |
| 7 | Plano de saída definido | ✅ stop -50%, alvo +100% |

VEREDICTO: APROVADO

## 📊 SCORES (0-10 cada)
| Dimensão    | Score | Peso | Contribuição |
|-------------|-------|------|--------------|
| Técnico     | 6.5   | 25%  | 1.63         |
| Fundamental | 7.0   | 30%  | 2.10         |
| Macro       | 6.0   | 20%  | 1.20         |
| Sentiment   | 6.5   | 25%  | 1.63         |
| **Total**   |       |      | **6.56/10**  |

Alinhamento: 3/4 dimensões → confiança 65%

## 🎯 ESTRUTURA RECOMENDADA
**Iron Condor ⭐ TOP PICK** (IV/HV = 1.44 → vol cara, vender)
- BUY PUT $130 | SELL PUT $135 | SELL CALL $155 | BUY CALL $160
- DTE: 25 | Crédito: $2.80 | Perda máx: -$2.20 | RR: 1.27:1
- Greeks: Δ +0.02 | Θ +$0.18/dia | V -$0.12/1%IV
- Break-even: $132.20 / $157.80

## 💰 SIZING
- Kelly Full: 8.4% | 1/4 Kelly: 2.1%
- Capital sugerido: 2.1% do portfólio

## 🎯 DECISÃO FINAL
**Ação:** VENDA DE VOL
**Estrutura:** Iron Condor
**Entrada:** crédito $2.80 | **Stop:** se SOL sair do range | **Alvo:** $0 (expire sem valor)
**Confiança:** 65%
**Validade:** até 05/06/2026
```

---

## EXEMPLO 6 — Situação: usuário menciona arquivo de output

**Input do usuário:**
```
rodei o analyze_ticker.py no COGN3, pode analisar?
```

**O que John Galt DEVE fazer:**
1. `file_read /root/.zeroclaw/workspace/cogn3_output.txt`
2. Analisar os dados retornados
3. Montar recomendação baseada no arquivo

**NÃO deve:**
- ❌ Tentar rodar `python3 analyze_ticker.py` novamente
- ❌ Fazer web_fetch redundante se os dados já estão no arquivo
- ❌ Ignorar o arquivo e usar memória

---

## REGRAS DE OURO — Para todo e qualquer comando

1. **web_fetch SEMPRE antes de responder** — nunca use dados de memória
2. **Calcule Black-Scholes inline** — nunca peça para o usuário rodar um script
3. **UMA recomendação, não 4 cenários paralelos** — decida pelos scores
4. **Mencione fonte e timestamp** — ex: "✅ Dados via CoinGecko | 11/05/2026 09:30"
5. **NUNCA tente shell, python3, curl, localhost** — todos bloqueados pelo ZeroClaw
6. **NUNCA use `src.` em paths** — o ZeroClaw não tem estrutura de módulos Python
