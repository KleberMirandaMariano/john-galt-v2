# Skill: crypto-options

Execute quando o usuário pedir análise de opções cripto: Bull Call Spread, estruturas multi-leg, Greeks de BTC/ETH/SOL, IV real via OKX, ou sizing Kelly para cripto com opções.

---

## Passo 1 — Obter preço spot via CoinGecko

```
web_fetch("https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd")
→ data[{coin_id}]['usd']   # preço spot em USD
```

Mapeamento de ticker para coin_id:
| Ticker | coin_id |
|--------|---------|
| BTC | bitcoin |
| ETH | ethereum |
| SOL | solana |
| XRP | ripple |

---

## Passo 2 — Obter chain de opções + IV via OKX

```
web_fetch("https://www.okx.com/api/v5/public/opt-summary?instFamily={TICKER}-USD")
→ data.data[]   # array de opções
```

Campos relevantes por opção:
| Campo | Descrição |
|-------|-----------|
| `instId` | ID do instrumento (ex: BTC-USD-20260627-100000-C) |
| `markVol` | IV de mercado (%) |
| `delta` | Delta (de -1 a 1) |
| `gamma` | Gamma |
| `vega` | Vega |
| `theta` | Theta |
| `openInterest` | Open Interest (contratos) |
| `markPx` | Preço de mercado (USD) |

Filtrar por vencimento: o `instId` contém a data `YYYYMMDD` na posição 3 (ex: `BTC-USD-20260627-...`).

---

## Passo 3 — Calcular Greeks inline (Black-Scholes)

**Quando OKX não retorna Greeks, calcular inline:**

```
d1 = (ln(S/K) + (r + σ²/2) × T) / (σ × √T)
d2 = d1 - σ × √T

# CALL
preço_call = S × N(d1) - K × e^(-rT) × N(d2)
delta_call = N(d1)
theta_call = -(S × N'(d1) × σ) / (2√T) - r × K × e^(-rT) × N(d2)

# PUT
preço_put  = K × e^(-rT) × N(-d2) - S × N(-d1)
delta_put  = -N(-d1)
theta_put  = -(S × N'(d1) × σ) / (2√T) + r × K × e^(-rT) × N(-d2)

# Greeks comuns (CALL e PUT)
gamma = N'(d1) / (S × σ × √T)
vega  = S × N'(d1) × √T / 100      # por 1pp de IV
theta = theta / 365                  # por dia
rho   = K × T × e^(-rT) × N(d2) / 100   # por 1pp de taxa
```

Onde:
- `S` = spot, `K` = strike, `T` = dias / 365, `r` = 0.05 (risk-free)
- `σ` = IV OKX (ou IV estimada)
- `N(x)` = CDF normal padrão, `N'(x)` = PDF normal padrão

---

## Passo 4 — Análise de estrutura (Bull Call Spread)

```
# Leg 1 — CALL comprada (ATM ou ligeiramente ITM)
custo_long  = preço_call(S, K_long,  T, r, σ)
delta_long  = N(d1_long)

# Leg 2 — CALL vendida (OTM)
custo_short = preço_call(S, K_short, T, r, σ)
delta_short = N(d1_short)

# Resultado da trava
custo_trava = custo_long - custo_short
ganho_max   = (K_short - K_long) - custo_trava
perda_max   = custo_trava
break_even  = K_long + custo_trava
roi         = ganho_max / custo_trava

# Greeks net
delta_net = delta_long - delta_short
gamma_net = gamma_long - gamma_short
vega_net  = vega_long  - vega_short
theta_net = theta_long - theta_short

# Probabilidades (via delta)
P(ganho_max) ≈ delta_short    # probabilidade de fechar acima do strike short
P(break_even) ≈ delta_long    # probabilidade de fechar acima do break-even
```

---

## Passo 5 — Kelly Criterion para sizing

```
p = P(break_even) = delta_long
q = 1 - p
b = ganho_max / perda_max     # razão ganho/perda

f* = (p × b - q) / b
f_quarter = f* / 4            # 1/4 Kelly (padrão)
f_capped  = min(f_quarter, 0.05)   # cap: 5% para spreads (RR definido)
```

---

## Passo 6 — Output obrigatório

```
📊 CRIPTO OPTIONS — {TICKER} BULL CALL SPREAD — {DATA}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 SPOT: ${spot:.2f} (CoinGecko)
📈 IV ATM: {iv_atm:.0f}% a.a. (OKX markVol)

🔷 ESTRUTURA: BULL CALL SPREAD
  Long Call:  ${K_long}  | ${custo_long:.2f}
  Short Call: ${K_short} | ${custo_short:.2f}
  Vencimento: {DATA} ({dias}d)

💵 FINANCEIRO
  Custo trava:  ${custo_trava:.2f}
  Ganho máx:   ${ganho_max:.2f}
  Break-even:  ${break_even:.2f}
  ROI potencial: {roi:.0f}%

📐 GREEKS (net da trava)
  Delta: {delta_net:.3f} | Gamma: {gamma_net:.5f}
  Vega:  ${vega_net:.2f}/1%IV | Theta: ${theta_net:.2f}/dia

🎯 PROBABILIDADES
  P(ganho máx):  {P_max:.0f}%  (acima de ${K_short})
  P(break-even): {P_be:.0f}%  (acima de ${break_even:.2f})
  P(perda máx):  {P_loss:.0f}%

💎 KELLY
  f* = {f_star:.1f}% | 1/4 Kelly = {f_quarter:.1f}%
  Cap aplicado: {f_capped:.1f}% do capital

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏦 FONTES: CoinGecko (spot) + OKX (IV) + BS (Greeks)
```

---

## Regras

- **Nunca use IV de memória.** Sempre buscar via OKX `markVol` antes de qualquer cálculo de Greeks.
- **Se OKX retornar data vazio ou erro**, use IV estimada via HV 30d (do analyze_ticker output) com aviso explícito.
- **Para outros ativos além de BTC/ETH/SOL**, OKX pode não ter opções — informar e usar somente análise de spot.
- **Cap de Kelly para cripto opções:** 5% (spread RR definido) ou 2% (OTM puro). Nunca exceder.
- **Sempre informar o vencimento exato** — nunca deixar implícito.
