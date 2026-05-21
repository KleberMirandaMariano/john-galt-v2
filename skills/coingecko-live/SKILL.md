# Cripto Live — Preços e Análise Quant em Tempo Real

## Quando usar
- `.cripto` → preços spot rápidos (BTC/ETH/SOL/XRP)
- `.analise [CRIPTO]` → análise quant completa (HV, Z-Score, Risk Gating, Scores, Decisão)
- Qualquer menção a preços de cripto → NUNCA use memória, sempre web_fetch

---

## Fonte Principal — CoinGecko (sem API key)

### Preços spot + variação
```
web_fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,ripple&vs_currencies=usd,brl&include_24hr_change=true&include_market_cap=true")
→ {id}.usd              # preço USD
→ {id}.brl              # preço BRL
→ {id}.usd_24h_change   # variação 24h %
→ {id}.usd_market_cap   # market cap USD
```
IDs: `bitcoin`, `ethereum`, `solana`, `ripple`, `cardano`, `avalanche-2`

### HV 30d (SEMPRE calcular — nunca usar memória)
```
web_fetch("https://api.coingecko.com/api/v3/coins/{id}/market_chart?vs_currency=usd&days=30&interval=daily")
→ prices: [[timestamp_ms, price], ...]

retornos = [ln(P[i]/P[i-1]) for i in 1..29]
σ_diária = std(retornos)
HV_30d   = σ_diária × √365 × 100   # % anualizada
Z_Score  = (preço_atual - media_30d) / desvio_30d
```

### Dominância BTC
```
web_fetch("https://api.coingecko.com/api/v3/global")
→ data.market_cap_percentage.btc   # dominância BTC %
→ data.market_cap_percentage.{id}  # dominância do ativo
```

---

## Interpretação Dominância BTC
- > 60%: Bitcoin dominante — risk-off altcoins
- 50-60%: Equilíbrio
- < 45%: Altseason em curso

## Interpretação Z-Score
- > +2.0: sobrecomprado → cautela
- -2.0 a +2.0: zona neutra/justa
- < -2.0: oversold → oportunidade potencial

---

## FORMATO RÁPIDO — Comando `.cripto`

```
🪙 CRIPTO — [DATA] [HORA] BRT

₿ BTC: $XX,XXX (+X.XX%) | R$ XXX,XXX
◎ ETH: $X,XXX (+X.XX%) | R$ X,XXX
◉ SOL: $XXX (+X.XX%)
◈ XRP: $X.XX (+X.XX%)

🌐 Dominância BTC: XX.X%
💹 Market Cap Total: $X.XXt
📌 Fonte: CoinGecko | [TIMESTAMP]
```

---

## FORMATO COMPLETO — Comando `.analise [CRIPTO]`

Workflow obrigatório:
```
Step 1: web_fetch CoinGecko /simple/price (spot + variação + mcap)
Step 2: web_fetch CoinGecko /coins/{id}/market_chart (30 preços → calcular HV + Z-Score)
Step 3: web_fetch CoinGecko /global (dominância)
Step 4: web_fetch Alternative.me /fng/ (Fear & Greed)
Step 5: web_fetch OKX /opt-summary?instFamily={ATIVO}-USD (IV — se disponível)
```

**Nota OKX**: BTC e ETH têm séries de opções. SOL tem liquidez limitada. XRP, ADA, AVAX geralmente NÃO têm série no OKX → indicar no output e recomendar spot apenas.

Output canônico aprovado em produção (21/05/2026 — XRP):
```
📊 ANÁLISE QUANT — {TICKER} — {DATA}

Status: Validada | Recomendação: {AÇÃO} | Confiança: {XX}%

💰 PREÇO & PERFORMANCE
| Spot USD | $X.XX |
| Spot BRL | R$ X.XX |
| 24h | +X.XX% |
| Market Cap | $XXB |

📈 MÉTRICAS QUANT
| HV 30d | XX.X% | {interpretação} |
| IV ATM | XX% ou N/A (sem série OKX) |
| Z-Score | +X.XX | {neutro/sobrecomprado/oversold} |
| Corr BTC 60d | ~+X.XX | {interpretação alpha} |

🔍 VALIDAÇÃO (2 fontes quando possível)
🛡️ RISK GATING (7 itens)
📊 SCORES (T/F/M/S → Total/10)

💡 CENÁRIOS (subordinados à DECISÃO — não são recomendações alternativas)
Cenário Bull: +XX% | Probabilidade: XX%
Cenário Neutro: ±XX% | Probabilidade: XX%
Cenário Bear: -XX% | Probabilidade: XX%

🎯 DECISÃO FINAL
Ação: {UMA AÇÃO} | Stop: $X.XX | Alvo: $X.XX | Confiança: XX%
```

---

## REGRAS CRÍTICAS

- **NUNCA** cite preços de cripto sem executar web_fetch
- **SEMPRE** calcular HV via market_chart — nunca usar HV de memória (incidente SOL 02/05/2026)
- **SEMPRE** incluir Z-Score na seção de métricas quant
- **Cenários com probabilidade** são permitidos e recomendados — mas devem ser SUBORDINADOS à DECISÃO FINAL única, nunca apresentados como recomendações alternativas
- Se OKX não tem série para o ativo: registrar "IV ATM: N/A" + redirecionar para spot + sugerir BTC/SOL para quem quer estruturas de opções
- Se API falhar: "Dados indisponíveis. Consulte coingecko.com" — JAMAIS invente valores
