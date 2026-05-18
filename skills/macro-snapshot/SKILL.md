# Macro Snapshot — Panorama Completo

## Quando usar
Quando o usuário pedir "panorama", "resumo", "macro", "overview do dia", ou `.resumo`.

## Passo 1 — Buscar todos os dados

```
# Cripto
web_fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd,brl&include_24hr_change=true&include_market_cap=true")
→ bitcoin.usd / bitcoin.brl / bitcoin.usd_24h_change
→ ethereum.usd / ethereum.brl / ethereum.usd_24h_change
→ solana.usd / solana.brl / solana.usd_24h_change

# Dominância BTC
web_fetch("https://api.coingecko.com/api/v3/global")
→ data.market_cap_percentage.btc

# Fear & Greed
web_fetch("https://api.alternative.me/fng/?limit=1")
→ data[0].value / data[0].value_classification

# Selic
web_fetch("https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json")
→ [0]['valor']

# USD/BRL
web_fetch("https://economia.awesomeapi.com.br/json/last/USD-BRL")
→ USDBRL.bid / USDBRL.pctChange
```

## Passo 2 — Interpretar

```
# Dominância BTC
btc_dom > 55% → risk-off — capital concentrado em BTC, evitar altcoins
btc_dom < 45% → risk-on — apetite por altcoins

# Fear & Greed
fng < 25  → 🔴 MEDO EXTREMO — oportunidade contrária histórica, nível de acumulação
fng < 45  → 🟠 MEDO — cautela, mercado precificando risco excessivo
fng < 55  → 🟡 NEUTRO
fng < 75  → 🟢 GANÂNCIA — cautela no topo
fng >= 75 → 🔴 GANÂNCIA EXTREMA — sinal de realização

# Selic como custo de oportunidade
selic >= 12% → Elevado — risco precisa entregar prêmio acima de CDI
selic >= 9%  → Moderado
selic < 9%   → Baixo — favorável a risco

# Evento macro próximo (verificar mentalmente)
Calendário: FOMC (a cada ~6 semanas), COPOM (a cada ~45 dias), CPI EUA (mensal)
Se evento em ≤ 3 dias: sinalizar ⚠️ CAUTELA PRÉ-EVENTO
```

## Passo 3 — Output

```
📊 PANORAMA DO DIA — {DD/MM/AAAA}

---

💰 CRIPTOMOEDAS

| Ativo | Preço USD | Variação 24h | Preço BRL |
|-------|-----------|--------------|-----------|
| ₿ BTC | ${btc_usd} | {btc_delta:+.2f}% | R$ {btc_brl} |
| ◎ ETH | ${eth_usd} | {eth_delta:+.2f}% | R$ {eth_brl} |
| ◉ SOL | ${sol_usd} | {sol_delta:+.2f}% | R$ {sol_brl} |

🌐 Dominância BTC: {btc_dom:.1f}% ({interp_dom})

---

😨 SENTIMENTO & MACRO

| Métrica | Valor | Sinal |
|---------|-------|-------|
| Fear & Greed | {fng}/100 | {fng_emoji} {fng_label} |
| USD/BRL | R$ {usd_brl} ({usd_delta:+.2f}%) | {interp_cambio} |
| Selic | {selic:.2f}% a.a. | {interp_selic} |

{fng_interpretacao}

---

🎯 CONTEXTO RELEVANTE PARA HOJE

{checklist_macro}

---

💡 AÇÃO RECOMENDADA

{recomendacao_sintetica}

Quer análise detalhada de algum ativo específico?
```

## Exemplos de preenchimento dinâmico

```
# fng_interpretacao (baseado no valor)
fng < 25: "⚠️ Fear & Greed em {fng} = MEDO EXTREMO (oportunidade contrária histórica). Nível típico de acumulação — mercado precificando risco excessivo."
fng < 45: "⚠️ Fear & Greed em {fng} = MEDO. Mercado cauteloso — favor confirmar tese antes de posicionar."
fng >= 75: "⚠️ Fear & Greed em {fng} = GANÂNCIA EXTREMA. Historicamente bom momento para realizar lucros parciais."

# checklist_macro (gerar dinamicamente)
"✅ Sem eventos macro críticos até {próximo_evento} ({próxima_data})"
"✅ Selic {selic:.2f}% → custo de oportunidade {interp_selic} em risco"
"✅ BTC dominância {btc_dom:.1f}% → {interp_dom}"
"✅ {fng_label} → {implicacao_fng}"
# Se evento próximo:
"⚠️ {evento} em {data} — reduzir exposição direcional"

# recomendacao_sintetica
# Combina FNG + Selic + Dominância + Evento em 2-3 frases acionáveis
```

## REGRA CRÍTICA
Execute TODOS os web_fetch antes de apresentar qualquer número.
Se uma API falhar, indique "Dado indisponível" — não substitua com memória.
NUNCA mencione preço, Selic ou FNG sem ter feito o fetch nesta sessão.
