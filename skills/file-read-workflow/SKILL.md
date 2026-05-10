---
name: file-read-workflow
description: >
  Use SEMPRE antes de fazer múltiplos web_fetch para um ticker. Verifica se já existe
  análise pré-computada em /root/.zeroclaw/workspace/ via file_read, economizando 5-10
  chamadas HTTP. Disparar quando: usuário pedir análise de TICKER, pedir relatório diário,
  ou mencionar ticker B3/cripto. Tem prioridade sobre coingecko-live, macro-snapshot,
  financial-datasets-live e quant-b3.
---

# File-Read Workflow — Use cache antes de fetch

## Regra de ouro
**Antes de qualquer `web_fetch`, tente `file_read` no path padrão.**

## Paths padronizados

```
/root/.zeroclaw/workspace/{ticker_minusculo}_output.txt   # analyze_ticker.py
/root/.zeroclaw/workspace/daily_report_YYYYMMDD_HHMM.md   # daily_report.py
/root/.zeroclaw/workspace/cogn3_output.txt
/root/.zeroclaw/workspace/petr4_output.txt
/root/.zeroclaw/workspace/btc_output.txt
/root/.zeroclaw/workspace/sol_output.txt
```

## Workflow obrigatório

```
1. file_read /root/.zeroclaw/workspace/{ticker}_output.txt
2. Se SUCESSO:
   - Checar timestamp no arquivo
   - Se < 4h atrás: USAR dados, NÃO fazer web_fetch
   - Se 4-24h: usar fundamentalistas, atualizar APENAS preço via web_fetch
   - Se > 24h: pedir ao usuário rodar analyze_ticker.py novamente
3. Se ARQUIVO NÃO EXISTE:
   - Pedir: "Rode `python3 /root/.zeroclaw/workspace/analyze_ticker.py {TICKER}` e me avise"
   - OU buscar via web_fetch (fallback)
```

## Conteúdo dos arquivos

`{ticker}_output.txt` contém:
- Cotação, variação, market cap
- P/L, LPA, VPA, DY, Valor Graham
- Black-Scholes ATM (Call+Put) com Greeks
- Kelly Criterion
- Fear & Greed (cripto)

`daily_report_*.md` contém:
- Ranking fundamentalista (NYSE/NASDAQ + ADRs)
- Top 3 detalhado
- Oportunidades Value
- Líderes Quality

## Anti-padrão (NÃO fazer)
```
❌ ERRADO: web_fetch(brapi) + web_fetch(bcb) + web_fetch(awesomeapi) + ...
✅ CERTO:   file_read /root/.zeroclaw/workspace/cogn3_output.txt
```

## Quando NÃO usar este skill
- Dados de mercado real-time (preço cripto na hora) — usar coingecko-live
- Eventos macro de hoje (FOMC, COPOM) — usar macro-snapshot
- Notícias — não há cache de notícias
