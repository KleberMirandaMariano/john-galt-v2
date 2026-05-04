# John Galt — Registry de Ferramentas e APIs

## Regra Principal de Output

Quando executar shell ou file_read e receber output:
- SEMPRE exiba o output COMPLETO e LITERAL
- NUNCA resuma, interprete ou parafraseie
- Copie o texto exatamente como veio

## APIs Disponíveis

### API B3 Local — api.analisekmm.tech
Base: http://localhost:3001
- GET /api/stocks → 333 ações B3 com P/L, DY, Upside Graham, opções CALL/PUT
- GET /api/options/:ticker → opções de um ticker específico
- GET /api/status → status da última atualização
- Fonte: COTAHIST B3 (diário) + yfinance

### BRAPI — Cotações B3
Base: https://brapi.dev/api
Token: tP2QrzuthuXx4JjrnBqnkd
- GET /quote/TICKER?token=TOKEN → preço atual, variação, histórico
- Limite: 1 ativo por requisição (plano gratuito)

### CoinGecko — Cripto Spot
Base: https://api.coingecko.com/api/v3
- GET /simple/price?ids=bitcoin,solana,ethereum&vs_currencies=usd,brl&include_24hr_change=true
- GET /global → dominância BTC, market cap total

### OKX v5 — Futuros e Opções Cripto
Base: https://www.okx.com/api/v5
- GET /market/ticker?instId=BTC-USDT → preço spot BTC
- GET /public/funding-rate?instId=BTC-USD-SWAP → funding rate
- GET /market/open-interest?instId=BTC-USD-SWAP → Open Interest

### Fear & Greed Index
URL: https://api.alternative.me/fng/
- GET / → índice atual (0=medo extremo, 100=ganância extrema)

## Scripts do Workspace

### bs_calculator.py — Black-Scholes + Monte Carlo
Uso: python3 /root/.zeroclaw/workspace/bs_calculator.py TICKER ENTRADA ALVO CONTRATOS CALL|PUT
Exemplo: python3 bs_calculator.py COGND335 0.03 0.07 3 CALL
Output: BS, Delta, Gamma, Theta, Vega, Monte Carlo 10k sim, Theta decay, P&L

### bs_telegram.sh — Envio Direto ao Telegram
Uso: /root/.zeroclaw/workspace/bs_telegram.sh TICKER ENTRADA ALVO CONTRATOS CALL|PUT
Envia análise BS completa diretamente ao Telegram sem passar pelo LLM

### b3_update.sh — Atualizar Cache de Cotações
Uso: /root/.zeroclaw/workspace/b3_update.sh
Consulta localhost:3001, salva em b3_cotacoes.txt
Formato: TICKER: R$ X.XX (+Y.YY%) | P/L:Z DY:W% Upside:V%

### b3_quote.sh — Cotação Individual
Uso: /root/.zeroclaw/workspace/b3_quote.sh TICKER
Fonte: BRAPI (tempo real)

### news_scraper.py — Notícias RSS
Uso: python3 /root/.zeroclaw/workspace/news_scraper.py
Salvo em noticias.txt (cron 3x/dia: 09h, 13h, 17h)

### btc_vix_correlation.py — Correlação BTC vs VIX
Uso: python3 /root/.zeroclaw/workspace/btc_vix_correlation.py [dias]
Exemplo: python3 btc_vix_correlation.py 90
Output: Análise de correlação BTC vs VIX (Pearson), preços, retornos, volatilidade
JSON: /tmp/btc_vix_correlation.json
Fontes: YFinance (BTC-USD, ^VIX)

### btc_spx_correlation.py — Correlação BTC vs S&P 500
Uso: python3 /root/.zeroclaw/workspace/btc_spx_correlation.py [dias]
Exemplo: python3 btc_spx_correlation.py 90
Output: Análise de correlação BTC vs S&P 500 (Pearson), teste risk-on/risk-off
JSON: /tmp/btc_spx_correlation.json
Fontes: YFinance (BTC-USD, ^GSPC)

### btc_dxy_correlation.py — Correlação BTC vs Dollar Index
Uso: python3 /root/.zeroclaw/workspace/btc_dxy_correlation.py [dias]
Exemplo: python3 btc_dxy_correlation.py 90
Output: Análise de correlação BTC vs DXY, teste proteção contra USD
JSON: /tmp/btc_dxy_correlation.json
Fontes: YFinance (BTC-USD, DX-Y.NYB)

### btc_gold_correlation.py — Correlação BTC vs Ouro
Uso: python3 /root/.zeroclaw/workspace/btc_gold_correlation.py [dias]
Exemplo: python3 btc_gold_correlation.py 90
Output: Análise de correlação BTC vs Gold, teste "ouro digital", volatilidade comparativa
JSON: /tmp/btc_gold_correlation.json
Fontes: YFinance (BTC-USD, GC=F)

### validate_strategy_backtest.py — Backtesting B3 (b3_trading_signals)
Uso: python3 /root/.zeroclaw/workspace/validate_strategy_backtest.py TICKER [dias]
Exemplo: python3 validate_strategy_backtest.py PETR4 365
Output: Backtesting de 7 estratégias (SMA, EMA, BB, MACD), ranking por retorno/Sharpe/DD
JSON: /tmp/backtest_TICKER_YYYYMMDD.json
Estratégias: Médias Móveis (SMA 9/21, 21/50, 9/21/50), EMA (9/21, 12/26), Bollinger Bands (20,2), MACD (12,26,9)
Métricas: Retorno total %, Sharpe Ratio, Max Drawdown %, Número de trades, Win Rate %
Lib: b3_trading_signals (https://github.com/gkeiel/b3_trading_signals)

## Fórmulas Inline — Python

### Black-Scholes
import math
def norm_cdf(x): return 0.5*(1+math.erf(x/math.sqrt(2)))
def bs(S,K,T,r,sigma,tipo='CALL'):
    d1=(math.log(S/K)+(r+0.5*sigma**2)*T)/(sigma*math.sqrt(T))
    d2=d1-sigma*math.sqrt(T)
    if tipo=='CALL': return S*norm_cdf(d1)-K*math.exp(-r*T)*norm_cdf(d2)
    return K*math.exp(-r*T)*norm_cdf(-d2)-S*norm_cdf(-d1)
# Selic: r=0.1075 | Sigma penny stocks: 0.45

### Kelly Criterion
def kelly(p,ganho,perda):
    b=ganho/perda; q=1-p
    f=(p*b-q)/b
    return max(0,f), max(0,f/4)  # (f*, 1/4 Kelly conservador)

### Valor Graham
def graham(lpa,vpa): return (22.5*lpa*vpa)**0.5 if lpa>0 and vpa>0 else None

### DVR — Diferencial de Volatilidade de Rolagem
def dvr(iv_curto,iv_longo):
    d=iv_curto-iv_longo
    return d, "favorável THL" if d>0 else "invertida — cautela"

## Próximos Scripts a Implementar

- news_filter.py — filtrar notícias por região (news btc, news brasil)
- kelly_telegram.sh — Kelly Criterion via Telegram
- macro_snapshot.sh — Selic, câmbio, Ibovespa, CDS via API BCB
- cripto_status.sh — BTC/SOL/ETH completo via OKX + CoinGecko
- iv_calculator.py — Volatilidade implícita real via BRAPI

### pre_analysis_validator.py — Validador Pré-Análise Cripto
**USO OBRIGATÓRIO ANTES DE QUALQUER ANÁLISE QUANTITATIVA DE CRIPTO**

Uso: python3 /root/.zeroclaw/workspace/pre_analysis_validator.py TICKER
Exemplo: python3 pre_analysis_validator.py SOL

**SEMPRE executar ANTES de gerar análise de:**
- BTC, ETH, SOL, XRP, ADA, AVAX, DOT, MATIC

**Output:**
- Preço atual validado
- Market Cap validado
- HV (30d anualizada) calculado ✅ NUNCA ESTIMAR!
- Z-Score calculado
- Correlação BTC calculada (90d)
- Correlação VIX calculada (90d)
- JSON: /tmp/validated_TICKER_YYYYMMDD.json

**Metodologia Correta:**

1. **Volatilidade Histórica (HV):**
```python
returns_30d = hist['Close'].pct_change().tail(30)
hv_30d = returns_30d.std() * np.sqrt(365) * 100
```
⚠️ CRÍTICO: Sempre anualizar (× √365)
⚠️ CRÍTICO: Nunca estimar ou assumir valor

2. **Correlação:**
```python
# Sempre usar 90 dias mínimo
corr_btc = df['Asset'].corr(df['BTC'])
```
⚠️ CRÍTICO: Nunca assumir correlação alta
⚠️ CRÍTICO: Sempre calcular, não estimar

3. **Z-Score:**
```python
mean_30d = hist['Close'].tail(30).mean()
std_30d = hist['Close'].tail(30).std()
z_score = (current_price - mean_30d) / std_30d
```
⚠️ CRÍTICO: Atualizar diariamente
⚠️ CRÍTICO: Muda rapidamente

**Checklist Validação:**
- [ ] Dados históricos ≥ 90 dias
- [ ] Market Cap disponível
- [ ] HV calculado (não estimado)
- [ ] Correlação BTC calculada
- [ ] Correlação VIX calculada
- [ ] JSON salvo

**NUNCA:**
- ❌ Estimar volatilidade
- ❌ Assumir correlação sem calcular
- ❌ Usar dados > 24h sem recalcular
- ❌ Confiar em memória/conhecimento prévio

**SEMPRE:**
- ✅ Executar validador ANTES da análise
- ✅ Usar dados do JSON gerado
- ✅ Mencionar data da validação
- ✅ Recalcular se análise > 24h

**Erros Históricos Corrigidos:**
1. SOL 02/05/2026: HV 38% (errado) → 49.8% (correto)
2. SOL 02/05/2026: Corr BTC +0.92 (errado) → +0.41 (correto)
