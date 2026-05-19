# Skill: bayesian-signals

**name**: bayesian-signals
**description**: Atualização bayesiana de P(sucesso) com sinais de mercado + Kelly integrado. Invocado quando o usuário pede sizing bayesiano, análise de sinais com probabilidade, ou quando decision-synthesis solicita sizing mais preciso.

---

## QUANDO INVOCAR

- Usuário menciona "Bayes", "probabilidade de sucesso", "sizing bayesiano"
- Após `risk-gating` APROVADO, para sizing mais preciso que Kelly simples
- Em `.analise TICKER` — aplica após coletar dados de preço e macro

---

## FÓRMULA CENTRAL

```
P(H|E) = P(E|H) × P(H)
         ─────────────────────────────────────
         P(E|H)×P(H) + P(E|¬H)×(1-P(H))
```

**Prior padrão**: 0.50 (sem informação prévia)
**Atualização sequencial**: posterior vira novo prior para o próximo sinal

---

## TABELA DE LIKELIHOODS — B3

| Sinal | P(E\|H✓) | P(E\|H✗) | Interpretação |
|-------|----------|----------|---------------|
| `mm20_breakup` | 0.65 | 0.35 | Rompe MM20 para cima |
| `mm20_breakdown` | 0.28 | 0.62 | Rompe MM20 para baixo (negativo) |
| `volume_spike` | 0.60 | 0.35 | Volume > 2× média 20d |
| `rsi_oversold` | 0.48 | 0.22 | RSI < 30 (sinal contrário) |
| `rsi_overbought` | 0.22 | 0.48 | RSI > 70 (negativo) |
| `iv_hv_low` | 0.60 | 0.40 | IV/HV < 0.8 → vol barata |
| `iv_hv_high` | 0.35 | 0.60 | IV/HV > 1.2 → vol cara |
| `macd_crossover_up` | 0.58 | 0.38 | MACD cruza sinal para cima |
| `macd_crossover_down` | 0.35 | 0.60 | MACD cruza sinal para baixo (negativo) |
| `ibov_positive` | 0.65 | 0.42 | Ibovespa positivo no dia |
| `above_vwap` | 0.62 | 0.40 | Preço acima VWAP intraday |
| `selic_restrictive` | 0.38 | 0.55 | Selic ≥ 12% (custo de oportunidade alto) |

---

## TABELA DE LIKELIHOODS — CRIPTO

| Sinal | P(E\|H✓) | P(E\|H✗) | Interpretação |
|-------|----------|----------|---------------|
| `fng_extreme_fear` | 0.55 | 0.35 | FNG < 25 — oportunidade contrária |
| `fng_extreme_greed` | 0.28 | 0.55 | FNG > 75 — sinal de topo (negativo) |
| `fng_neutral` | 0.50 | 0.50 | FNG 45-55 — sem edge |
| `btc_dom_high` | 0.38 | 0.55 | BTC dom > 55% = risk-off altcoins |
| `btc_dom_low` | 0.60 | 0.42 | BTC dom < 45% = risk-on altcoins |
| `funding_positive` | 0.38 | 0.58 | Funding rate > 0 (mercado long-alavancado) |
| `funding_negative` | 0.60 | 0.40 | Funding rate < 0 (shorts dominam) |
| `hv_low` | 0.58 | 0.42 | HV 30d < 40% — vol comprimida |
| `hv_high` | 0.35 | 0.58 | HV 30d > 80% — vol elevada |
| `onchain_inflow` | 0.35 | 0.55 | Fluxo para exchanges (pressão de venda) |

---

## PROCEDIMENTO INLINE (sem executar código)

**Passo 1 — Inicializar prior**
```
P₀ = 0.50   (neutro) ou P₀ = 0.60 (contexto macro favorável)
```

**Passo 2 — Para cada sinal observado, calcular novo posterior**
```
Para cada sinal_i:
  LR_i = P(E_i | H✓) / P(E_i | H✗)
  P_new = (LR_i × P_old) / (LR_i × P_old + 1 - P_old)
  P_old = P_new   ← posterior vira novo prior
```

**Passo 3 — Kelly Bayesiano**
```
p = P_final (posterior acumulado)
q = 1 - p
b = ganho_esperado / perda_maxima

f* = (p×b - q) / b
f_quarter = f* / 4          ← SEMPRE usar 1/4 Kelly
f_capped = min(f_quarter, cap)  ← cap: 2% OTM | 5% spread RR>2:1
```

**Passo 4 — Regime de mercado** (se relevante)
```
trending:  P(trending) → atualizar com momentum_signals
reverting: P(reverting) → atualizar com mean_reversion_signals
volatile:  P(volatile) → atualizar com vol_signals

Regime dominante = argmax(P_trending, P_reverting, P_volatile)
```

---

## EXEMPLO DE OUTPUT

```
📐 ANÁLISE BAYESIANA — COGN3

Prior: 0.50 (neutro)
Sinais observados:
  selic_restrictive → LR=0.691 → P: 0.500 → 0.408
  ibov_positive     → LR=1.548 → P: 0.408 → 0.515
  iv_hv_low         → LR=1.500 → P: 0.515 → 0.614

Posterior acumulado: 61.4%
Razão de Verossimilhança total: 1.61×

🎯 KELLY BAYESIANO
  p = 0.614 | q = 0.386 | b = ganho/perda
  f* = 22.8% | 1/4 Kelly = 5.7%
  Cap aplicado: 2.0% (OTM) | 5.0% (spread)
  → Sizing recomendado: 2.0% do capital (high-risk)

📊 REGIME ESTIMADO: REVERTING (baseado em RSI oversold + Selic alta)
→ Estratégia alinhada: Bull Put Spread / Cash Secured Put
```

---

## REGRAS

- **Nunca use prior > 0.70** sem pelo menos 4 sinais confirmando
- **Selic ≥ 12%** é sempre um sinal negativo a incluir (contexto atual: 14.75%)
- **FNG < 25** ativa automaticamente `fng_extreme_fear` para qualquer cripto
- Inclua o número de sinais e o LR total no output para transparência
- Se não há sinais disponíveis: use prior 0.50 e Kelly simples (p=0.55 padrão)
