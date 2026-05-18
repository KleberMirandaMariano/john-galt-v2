# Skill: macro-global

Execute quando o usuário pedir "macro global", "Fed", "juros EUA", "yields", "DXY", "curva de juros", "Treasury", ou quando for incluir contexto macro americano em análises de BTC e B3.

## Passo 1 — Obter FRED_API_KEY

```
file_read("/root/.zeroclaw/workspace/SECRETS.md")
→ FRED_API_KEY
```

## Passo 2 — Buscar dados via FRED

### Fed Funds Rate
```
web_fetch("https://api.stlouisfed.org/fred/series/observations?series_id=DFF&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=2")
→ observations[0].value   # % atual (use [1] se [0].value == ".")
→ observations[0].date    # data YYYY-MM-DD
```

### Treasury Yield 10 anos
```
web_fetch("https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=2")
→ observations[0].value   # % yield 10Y
```

### Treasury Yield 2 anos
```
web_fetch("https://api.stlouisfed.org/fred/series/observations?series_id=DGS2&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=2")
→ observations[0].value   # % yield 2Y
```

### Spread da Curva de Juros (10Y − 2Y)
```
web_fetch("https://api.stlouisfed.org/fred/series/observations?series_id=T10Y2Y&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=2")
→ observations[0].value   # pp spread (negativo = inversão)
```

### Índice do Dólar — proxy via DTWEXBGS
```
web_fetch("https://api.stlouisfed.org/fred/series/observations?series_id=DTWEXBGS&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=2")
→ observations[0].value   # índice base 2006=100 (atualização semanal)
```

> ⚠️ Se `observations[0].value == "."` (feriado/fim de semana), use `observations[1]`.

## Passo 3 — Interpretar

```
fed_funds   = float(DFF)
yield_10y   = float(DGS10)
yield_2y    = float(DGS2)
spread      = float(T10Y2Y)
dxy         = float(DTWEXBGS)

# Política monetária do Fed
politica:
  fed_funds >= 5.0 → RESTRITIVO — custo de capital alto, pressão em growth e cripto
  fed_funds >= 3.0 → NEUTRO
  fed_funds  < 3.0 → EXPANSIVO — favorável a risco

# Curva de juros
curva:
  spread <  0.0  → INVERTIDA ⚠️ — sinal histórico de recessão (~12-18 meses)
  spread <  0.5  → FLAT — incerteza sobre crescimento
  spread >= 0.5  → NORMAL — expansão esperada

# DXY (DTWEXBGS)
dxy_regime:
  dxy > 115 → DÓLAR MUITO FORTE — pressão intensa em BTC e mercados emergentes
  dxy > 105 → DÓLAR FORTE — cautela em EM e cripto
  dxy > 100 → DÓLAR ELEVADO — neutro/leve pressão
  dxy < 100 → DÓLAR FRACO — favorável a BTC e B3
```

## Passo 4 — Output

```
🌐 MACRO GLOBAL — {DATA} (Fonte: FRED / St. Louis Fed)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏦 FED FUNDS RATE: {fed_funds:.2f}% → {politica}

📈 TREASURIES (US)
  2Y: {yield_2y:.2f}%  |  10Y: {yield_10y:.2f}%
  Spread 10Y−2Y: {spread:+.2f}pp → {curva}

💵 DÓLAR (DTWEXBGS): {dxy:.1f} → {dxy_regime}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ IMPACTO NAS ESTRATÉGIAS
• BTC:  {impacto_btc}
• B3:   {impacto_b3}
```

## Notas de impacto

**BTC:**
- Fed Funds ≥ 5% + curva invertida → risk-off — reduza sizing, evite longs especulativos
- DXY > 105 → pressão vendedora em cripto — prefira estruturas com hedge (put/spread)
- Fed Funds < 3% + curva normal → risk-on — sizing mais agressivo permitido pelo Kelly

**B3:**
- Yield 10Y subindo → fluxo saindo de mercados emergentes → pressão negativa no Ibovespa
- DXY > 105 → exportadoras (VALE3, PETR4) protegidas pelo câmbio, mas fluxo total se retira de B3
- Curva invertida → sinal de recessão americana → cautela global, reduzir exposição direcional

## REGRA CRÍTICA
NUNCA mencione Fed Funds, yields ou DXY de memória. Sempre buscar via FRED antes de qualquer menção.
