# John Galt v2.0 — Agente Quantitativo B3 + Cripto

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-production-green.svg)]()

Agente quantitativo autônomo para análise de mercado brasileiro (B3) e criptomoedas. Roda dentro do **ZeroClaw**, framework de agentes de IA implantado em VPS, interagindo com usuários via Telegram. O runtime do agente usa Claude Haiku 4.5 via OpenRouter.

**Autor:** Kleber Miranda  
**Última Atualização:** 23/05/2026

---

## Funcionalidades

### Análise Quantitativa B3
- **Black-Scholes completo** (Greeks: Delta, Gamma, Theta, Vega, Rho)
- **Kelly Criterion** + Bayesian Kelly (sizing com atualização de probabilidade por sinais)
- **Opções reais via COTAHIST** — chain completa de PUT/CALL direto da B3, sem IV hardcoded
- **Fundamentais via Fundamentus** (ROE, ROIC, margens, dívida, DY, Graham Value)
- **Estruturas de opções** (Travas, THL, Booster, Iron Condor)
- **Backtesting profissional** (7 estratégias: SMA, EMA, BB, MACD)

### Cripto
- **BTC/ETH/SOL/XRP** — spot + opções OKX (IV, Greeks, Open Interest)
- **Correlações BTC** vs VIX, S&P 500, DXY, Ouro
- **Fear & Greed Index** integrado como sinal bayesiano

### Macro
- **Brasil:** Selic (BCB), USD/BRL (BCB PTAX Série 1)
- **EUA (FRED):** Fed Funds, Treasuries 2Y/10Y, Spread 10Y−2Y, DXY (DTWEXBGS)
- **Índices globais:** S&P 500, Nasdaq, Dow, FTSE, Nikkei, Hang Seng, Ibovespa

### Pipeline de IA (Fases 1–4)
- **Superinteligência (Fase 1):** AgentSwarm paralelo → ReflectionEngine (até 3 iterações de autocrítica) → AutoValidator
- **Memória (Fase 2):** três stores — episódico, semântico (com busca vetorial TF-cosine), procedural
- **Biblioteca de Skills (Fase 3):** extração automática de padrões de episódios bem-sucedidos
- **Aprendizado Autônomo (Fase 4):** A/B testing, currículo de melhoria, benchmarking de qualidade

---

## Instalação

### Pré-requisitos

```bash
pip install -r requirements.txt
```

### Clone

```bash
git clone https://github.com/KleberMirandaMariano/john-galt-v2.git
cd john-galt-v2
```

### Instalar b3_trading_signals (apenas VPS)

```bash
cd /root/.zeroclaw
git clone https://github.com/gkeiel/b3_trading_signals.git
pip install -e b3_trading_signals --break-system-packages
```

### Variáveis de ambiente

```bash
cp .env.example .env
# Preencher: ANTHROPIC_API_KEY, OPENROUTER_API_KEY, BRAPI_TOKEN
# FRED_API_KEY (gratuito em fred.stlouisfed.org) → em SECRETS.md no workspace do VPS
```

---

## Scripts Disponíveis

### Análise de Ticker

```bash
# Pré-processador quantitativo — escreve em /root/.zeroclaw/workspace/{TICKER}_output.txt
python3 analyze_ticker.py COGN3
python3 analyze_ticker.py BTC
```

Saída inclui: Black-Scholes, Greeks, Bayesian Kelly sizing, Graham Value, chain de opções COTAHIST.

### Backtesting B3

```bash
python3 validate_strategy_backtest.py PETR4 180   # 180 dias
python3 validate_strategy_backtest.py VALE3        # 365 dias (default)
```

Estratégias: SMA 9/21, 21/50, 9/21/50 — EMA 9/21, 12/26 — Bollinger Bands 20/2 — MACD 12/26/9  
Output JSON: `/tmp/backtest_TICKER_YYYYMMDD.json`

### Validação de Opções B3

```bash
python3 scripts/validate_options_b3.py PETR4 49.08 52.00 30 0.1375 0.45 PETRF52 2026-06-15 1.50 55.00 10
# Parâmetros: TICKER SPOT STRIKE DIAS TAXA VOL SÉRIE VENCIMENTO PRÊMIO ALVO CONTRATOS
```

### Correlações BTC

```bash
python3 btc_vix_correlation.py 90
python3 btc_spx_correlation.py 90
python3 btc_dxy_correlation.py 90
python3 btc_gold_correlation.py 90
```

### Testes das Fases

```bash
python3 test_phase1_complete.py    # Superinteligência + ReflectionEngine + AutoValidator
python3 test_phase2_memory.py      # Memória episódica/semântica/procedural
python3 test_phase3_skills.py      # Biblioteca de skills
python3 test_phase4_autonomous.py  # A/B testing + aprendizado autônomo
```

---

## Arquitetura

### Runtime: ZeroClaw Agent

O agente implantado usa exclusivamente `web_fetch` para dados externos — sem shell, subprocess, import ou glob_search. Toda computação (Black-Scholes, Kelly, Graham) é feita inline na resposta do LLM.

Configuração em `config/config.toml.example`. Parâmetros principais:
- Modelo: `anthropic/claude-haiku-4.5` via OpenRouter
- Telegram: `allowed_users = ["klebermd13", "1808474055"]`
- Domínios permitidos: CoinGecko, BRAPI, OKX, BCB, FRED, Fundamentus, FinancialDatasets
- Workspace: `/root/.zeroclaw/workspace/`

### Módulos `src/`

| Módulo | Função |
|--------|--------|
| `agent_bus.py` | Barramento A2A in-process: pub/sub, direct, req/reply (asyncio puro) |
| `agent_swarm_a2a.py` | AgentSwarm com comunicação real entre agentes durante execução |
| `bayesian_signals.py` | Atualização bayesiana sequencial de P(sucesso\|sinais) + Kelly integrado |
| `cotahist.py` | Parser do COTAHIST B3 (formato fixo, Latin-1): spot real + chain PUT/CALL |
| `enhanced_memory.py` | Três stores de memória com busca vetorial TF-cosine para semântico |
| `latency_tracker.py` | Instrumentação de latência por etapa (P50/P95, JSONL append-only) |
| `skill_library.py` | Extração automática de padrões de episódios bem-sucedidos |
| `autonomous_learning.py` | A/B testing, currículo de melhoria, detecção de degradação de qualidade |
| `crypto_options.py` | Opções cripto via OKX (IV, Greeks, Open Interest) |

### Skills do ZeroClaw (`skills/`)

| Skill | Gatilho / Função |
|-------|-----------------|
| `bayesian-signals` | Sizing bayesiano — P(sucesso\|sinais) + Kelly capeado |
| `coingecko-live` | Dados cripto via CoinGecko (BTC, ETH, SOL, XRP, etc.) |
| `cross-validation` | Validação dual-source para HV, IV, preço |
| `decision-synthesis` | Scoring 4D (T/F/M/S) → AÇÃO + CONFIANÇA + SIZING |
| `earnings-calendar` | Gate de eventos macro antes de qualquer recomendação |
| `fear-greed-live` | Fear & Greed Index via Alternative.me |
| `file-read-workflow` | Tenta cache antes de `web_fetch` |
| `financial-datasets-live` | Fundamentais NYSE/NASDAQ via FinancialDatasets.ai |
| `fundamentus-b3` | ROE, ROIC, margens, dívida, DY, Graham Value via Fundamentus |
| `macro-brasil` | Selic (BCB) + USD/BRL (BCB PTAX Série 1) |
| `macro-global` | Fed Funds + Treasuries 2Y/10Y + Spread + DXY via FRED |
| `macro-snapshot` | Snapshot macro global consolidado |
| `quant-b3` | Protocolo completo de análise de opções B3 |
| `quant-report-format` | Template obrigatório de relatório com auto-check |
| `risk-gating` | Checklist de 7 itens antes de qualquer recomendação |

**Fluxo de override:** resultado do `risk-gating` rebaixa a recomendação do `decision-synthesis` se reprovado.

### Configuração do Agente (`config/`)

| Arquivo | Conteúdo |
|---------|----------|
| `SOUL.md` | Personalidade, endpoints disponíveis, fórmula HV, formato obrigatório de output |
| `AGENTS.md` | Auto-triggers (ex: "analise TICKER" → workflow completo imediato) + workflows passo a passo |
| `TOOLS.md` | Registro de todos os endpoints com field paths exatos e fórmulas inline |
| `config.toml.example` | Template de configuração do ZeroClaw |

---

## Fontes de Dados

| Ativo | API | Auth |
|-------|-----|------|
| B3 cotações | `brapi.dev/api/quote/{TICKER}` | `BRAPI_TOKEN` |
| B3 opções (real) | COTAHIST via `src/cotahist.py` | Nenhuma (arquivo público B3) |
| B3 fundamentais | `www.fundamentus.com.br/detalhes.php?papel={TICKER}` | Nenhuma |
| US macro (Fed/yields/DXY) | `api.stlouisfed.org/fred/series/observations` | `FRED_API_KEY` (gratuito) |
| Cripto spot/histórico | `api.coingecko.com` | Nenhuma |
| Cripto opções/IV | `www.okx.com/api/v5/public/opt-summary` | Nenhuma |
| Fear & Greed | `api.alternative.me/fng/` | Nenhuma |
| Selic | `api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1` | Nenhuma |
| USD/BRL | BCB PTAX Série 1 (fonte oficial do Banco Central) | Nenhuma |
| NYSE/NASDAQ fundamentais | `api.financialdatasets.ai` | Nenhuma |

> **B3 vs NYSE/NASDAQ:** FinancialDatasets retorna 400 para tickers B3 — use sempre BRAPI/COTAHIST para ações brasileiras.  
> **USD/BRL:** Migrado de AwesomeAPI para BCB PTAX Série 1 (fonte oficial, mais estável).

---

## Estrutura do Projeto

```
john-galt-v2/
├── analyze_ticker.py              # Pré-processador quantitativo principal
├── validate_strategy_backtest.py  # Backtesting B3 (7 estratégias)
├── john_galt_superintelligence.py # Orquestrador Fase 1 (AgentSwarm → Reflection → Validator)
├── reflection_engine.py           # Autocrítica iterativa via OpenRouter
├── auto_validator.py              # Validação de saídas (freshness, Greeks, seções)
├── btc_*_correlation.py          # Correlações BTC vs VIX/SPX/DXY/Gold
├── config/
│   ├── SOUL.md                    # Identidade e formato de output do agente
│   ├── AGENTS.md                  # Auto-triggers e workflows
│   ├── TOOLS.md                   # Endpoints + fórmulas inline
│   └── config.toml.example        # Template ZeroClaw
├── skills/                        # Skills do agente ZeroClaw
│   ├── bayesian-signals/
│   ├── coingecko-live/
│   ├── cross-validation/
│   ├── decision-synthesis/
│   ├── earnings-calendar/
│   ├── fear-greed-live/
│   ├── file-read-workflow/
│   ├── financial-datasets-live/
│   ├── fundamentus-b3/
│   ├── macro-brasil/
│   ├── macro-global/
│   ├── macro-snapshot/
│   ├── quant-b3/
│   ├── quant-report-format/
│   └── risk-gating/
├── src/
│   ├── agent_bus.py               # Barramento A2A in-process
│   ├── agent_swarm_a2a.py         # AgentSwarm com comunicação real entre agentes
│   ├── bayesian_signals.py        # Bayes sequencial + Kelly integrado
│   ├── cotahist.py                # Parser COTAHIST B3 (spot + chain opções)
│   ├── crypto_options.py          # Opções cripto via OKX
│   ├── enhanced_memory.py         # Memória (episódico/semântico/procedural) + busca vetorial
│   ├── latency_tracker.py         # Instrumentação de latência P50/P95
│   ├── skill_library.py           # Extração automática de padrões
│   └── autonomous_learning.py     # A/B testing + aprendizado autônomo
├── b3_trading_signals/            # Engine de backtesting (bundled)
├── scripts/
│   └── validate_options_b3.py     # Validador de opções B3
└── requirements.txt
```

---

## Invariantes Críticos

- **Nunca use dados de memória para valores quantitativos.** HV, IV, correlação e preço devem sempre vir de `web_fetch` fresco. O incidente SOL (02/05/2026) usou HV 38% stale vs 49.8% real, invertendo a estratégia de vol.
- **Toda recomendação deve passar pelos 4 auto-checks:** VALIDAÇÃO, RISK GATING, SCORES, DECISÃO FINAL. Se qualquer seção faltar, reescrever.
- **Caps de Kelly:** 2% do capital para alto risco (OTM), 5% para risco definido (RR > 2:1). Sempre 1/4 Kelly, nunca Kelly pleno.
- **USD/BRL:** usar exclusivamente BCB PTAX Série 1 — AwesomeAPI foi descontinuado por instabilidade.

---

## Troubleshooting

```bash
# YFinance timeout
export YFINANCE_TIMEOUT=30

# b3_trading_signals — bug "Med"
sed -i 's/"Med"/"Mid"/g' /root/.zeroclaw/b3_trading_signals/core/backtester.py

# Deribit API rate limit — reduzir BATCH_SIZE no script (padrão: 50 → 25)
```

---

## Resultados de Testes

### Backtesting PETR4 (180 dias)

| Estratégia | Retorno | Sharpe | Max DD | Trades | Win% |
|------------|---------|--------|--------|--------|------|
| **EMA 9/21** | **+58.73%** | **3.84** | **-7.15%** | 3 | 33.3% |
| EMA 12/26 | +58.37% | 3.80 | -7.15% | 3 | 33.3% |
| SMA 9/21 | +46.98% | 3.52 | -7.15% | 2 | 0.0% |
| MACD 12/26/9 | +46.26% | 3.89 | -6.64% | 8 | 37.5% |
| SMA 21/50 | +41.93% | 3.30 | -7.15% | 1 | 100.0% |
| SMA 9/21/50 | +34.19% | 2.85 | -7.15% | 2 | 50.0% |
| BB 20/2 | +2.04% | 2.07 | 0.00% | 4 | 50.0% |

### Correlações BTC (90 dias)

| Ativo | Pearson | Interpretação |
|-------|---------|---------------|
| VIX | -0.48 | Moderada negativa — hedge contra vol |
| S&P 500 | +0.53 | Moderada positiva — risk-on |
| DXY | -0.19 | Muito fraca — independente |
| Gold | +0.15 | Muito fraca — independente |

---

## Deploy

Push para `main` dispara `.github/workflows/deploy-to-vps.yml` → deploy automático para `/root/.zeroclaw/workspace/`.

Setup do bot Telegram: `zeroclaw onboard --channels-only`

---

## Changelog

### v2.1.0 — 23/05/2026
- Sinais bayesianos com atualização sequencial de P(sucesso|sinais) + Kelly integrado (`src/bayesian_signals.py` + skill `bayesian-signals`)
- Chain de opções B3 real via COTAHIST (`src/cotahist.py`) — substitui estimativa Black-Scholes com IV hardcoded
- Barramento A2A in-process pub/sub/req/reply (`src/agent_bus.py` + `src/agent_swarm_a2a.py`)
- Memória semântica com busca vetorial TF-cosine (`src/enhanced_memory.py`)
- Instrumentação de latência P50/P95 (`src/latency_tracker.py`)
- Macro EUA via FRED: Fed Funds, Treasuries 2Y/10Y, Spread, DXY (skill `macro-global`)
- Fundamentais B3 via Fundamentus + Graham Value (skill `fundamentus-b3`)
- USD/BRL migrado de AwesomeAPI para BCB PTAX Série 1 (fonte oficial)
- Skill `macro-snapshot` com formato canônico de panorama
- Skill `coingecko-live` com suporte a XRP + exemplo de análise canônico
- Remoção de tokens Telegram hardcoded de todos os arquivos

### v2.0.3 — 03/05/2026
- Integração b3_trading_signals (backtesting profissional)
- 4 scripts de correlação BTC (VIX, S&P500, DXY, Gold)
- Deribit BTC options fetcher
- YFinance global indices (8 índices)
- Testes completos PETR4 (EMA 9/21: +58.73%)

### v2.0.2 — 23/04/2026
- Validador genérico de opções B3
- Correção de 9 erros COGN3
- CI/CD GitHub Actions + deploy automático VPS

### v2.0.1 — Initial Release
- Agente quantitativo básico
- Black-Scholes + Kelly Criterion
- SOUL.md + AGENTS.md

---

## Licença

MIT License — veja [LICENSE](LICENSE) para detalhes.

---

## Agradecimentos

- [b3_trading_signals](https://github.com/gkeiel/b3_trading_signals) — backtesting B3
- [YFinance](https://github.com/ranaroussi/yfinance) — dados de mercado
- [CoinGecko](https://www.coingecko.com) — dados cripto
- [FRED / St. Louis Fed](https://fred.stlouisfed.org) — macro EUA
- [Fundamentus](https://www.fundamentus.com.br) — fundamentais B3
- [BCB](https://www.bcb.gov.br) — Selic e PTAX
- [Alternative.me](https://alternative.me) — Fear & Greed Index
- [Claude (Anthropic)](https://anthropic.com) — LLM

---

**Desenvolvido por [Kleber Miranda](https://github.com/KleberMirandaMariano)**
