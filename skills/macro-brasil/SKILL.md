# Skill: macro-brasil

Execute quando o usuário digitar `.macro`, "macro Brasil", "Selic hoje", "dólar hoje".

## Passo 1 — Buscar dados

```
web_fetch("https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json")
→ selic_pct = float(result[0]['valor'])

web_fetch("https://economia.awesomeapi.com.br/json/last/USD-BRL")
→ usd_brl = float(result['USDBRL']['bid'])
→ usd_pct = float(result['USDBRL']['pctChange'])

web_fetch("https://api.alternative.me/fng/?limit=1")
→ fng_value = int(result['data'][0]['value'])
→ fng_label = result['data'][0]['value_classification']

web_fetch("https://api.coingecko.com/api/v3/global")
→ btc_dom = result['data']['market_cap_percentage']['btc']
```

## Passo 2 — Calcular indicadores

```
selic_diaria = selic_pct / 100 / 252   # usar como r no Black-Scholes B3

regime_juros:
  ≥ 12% → RESTRITIVO — custo de oportunidade alto
  ≥  9% → NEUTRO
   < 9% → EXPANSIVO — favorável a risco

usd tendência:
  > +0.5% → ⬆️ REAL ENFRAQUECENDO — exportadoras se beneficiam (VALE3, PETR4)
  < -0.5% → ⬇️ REAL FORTALECENDO — pressão em exportadoras
  else    → ↔️ ESTÁVEL

btc_dom:
  > 55% → RISK-OFF — capital em BTC, prefira BTC a altcoins
  < 45% → RISK-ON — apetite por altcoins
  else  → NEUTRO

fng:
  <25 → MEDO EXTREMO 😱 → oportunidade contrária
  <45 → MEDO 😰 → acumular
  <56 → NEUTRO 😐
  <75 → GANÂNCIA 😏 → cautela
  ≥75 → GANÂNCIA EXTREMA 🤑 → realizar lucros
```

## Passo 3 — Output

```
🇧🇷 MACRO BRASIL — {DATA} {HORA} BRT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💹 JUROS
Selic: {selic_pct:.2f}% a.a. ({regime_juros})
Taxa diária B3: {selic_diaria:.6f}

💵 CÂMBIO
USD/BRL: R$ {usd_brl:.4f} ({usd_pct:+.2f}%)
{tendencia_cambio}

🌍 SENTIMENTO
Fear & Greed: {fng_value}/100 — {fng_label}
{fng_signal}

₿ DOMINÂNCIA BTC: {btc_dom:.1f}%
{risk_sentiment}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ IMPACTO NAS ESTRATÉGIAS
• B3 Black-Scholes: r = {selic_diaria:.6f}
• {impacto_cambio}
• Cripto: {risk_sentiment}
```

## Notas de contexto

- **Selic > 12%**: alto custo de oportunidade → preferir Bull Put Spread a compra de calls
- **USD/BRL > 5.80**: exportadoras (VALE3, PETR4) tendem a se beneficiar
- **BTC Dom > 55%**: mercado cripto em risk-off, prefira BTC a altcoins
- **FNG < 25**: historicamente boa janela de entrada em cripto (compra contrária)
- **FNG > 75**: historicamente bom momento para realizar lucros em cripto
