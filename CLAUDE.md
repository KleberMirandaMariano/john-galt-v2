# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

John Galt v2.0 is an autonomous quantitative trading agent for Brazilian stocks (B3) and crypto. It runs inside **ZeroClaw**, a custom AI agent framework deployed on a VPS, interacting with users via Telegram. The agent's "runtime self" is Claude Haiku 4.5 via OpenRouter, constrained to `web_fetch` for all external data — no shell, subprocess, or import from the agent context.

## Environment Setup

```bash
pip install -r requirements.txt
```

The `b3_trading_signals` library is a separate dependency installed locally on the VPS:
```bash
# Only needed on VPS — not in this repo
cd /root/.zeroclaw
git clone https://github.com/gkeiel/b3_trading_signals.git
pip install -e b3_trading_signals --break-system-packages
```

Copy and fill the environment file:
```bash
cp .env.example .env
# Fill: ANTHROPIC_API_KEY, OPENROUTER_API_KEY, BRAPI_TOKEN
```

## Running Scripts

```bash
# Quantitative analysis — outputs to /root/.zeroclaw/workspace/{ticker}_output.txt
python3 analyze_ticker.py COGN3
python3 analyze_ticker.py BTC

# Backtesting B3 — outputs JSON to /tmp/backtest_TICKER_YYYYMMDD.json
python3 validate_strategy_backtest.py PETR4 180
python3 scripts/validate_options_b3.py PETR4 49.08 52.00 30 0.1375 0.45 PETRF52 2026-06-15 1.50 55.00 10

# BTC correlations
python3 btc_vix_correlation.py 90
python3 btc_spx_correlation.py 90

# Phase integration tests
python3 test_phase1_complete.py
python3 test_phase2_memory.py
python3 test_phase3_skills.py
python3 test_phase4_autonomous.py

# YFinance trouble: set YFINANCE_TIMEOUT=30
# b3_trading_signals "Med" bug: sed -i 's/"Med"/"Mid"/g' /root/.zeroclaw/b3_trading_signals/core/backtester.py
```

## Architecture

### Runtime: ZeroClaw Agent

The deployed agent **cannot** use `shell`, `python3`, `curl`, `import`, or `glob_search` — all blocked. The only data-fetching tool is `web_fetch`. All analysis (Black-Scholes, Kelly, Graham) is computed inline in the LLM response, not executed as code.

Configuration lives in `config/config.toml.example` (copy to ZeroClaw config dir). Key runtime parameters:
- Model: `anthropic/claude-haiku-4.5` via OpenRouter
- Telegram bot: `allowed_users` = `["klebermd13", "1808474055"]`
- `web_fetch` allowed domains: CoinGecko, BRAPI, OKX, BCB, AwesomeAPI, Financial Datasets
- Workspace: `/root/.zeroclaw/workspace/`

### Agent Identity and Behavior

`config/SOUL.md` defines the agent's personality, available API endpoints, HV calculation formula, and the **mandatory output format** for every recommendation. All recommendations must include four sections: VALIDAÇÃO (2 sources), RISK GATING (7 items), SCORES (T/F/M/S), DECISÃO FINAL.

`config/AGENTS.md` defines auto-triggers (e.g. "analise TICKER" → execute full workflow immediately without asking) and full step-by-step workflows for cripto, B3, and global equities.

`config/TOOLS.md` is the registry of all API endpoints with exact field paths and all inline formulas (Black-Scholes, Kelly, Graham, IV/HV ratio).

### Skills System (`skills/`)

Each subdirectory contains a `SKILL.md` with `name`, `description` (trigger phrases), and the protocol/output format for that skill. Skills are loaded by ZeroClaw and invoked by the agent. Current skills:

| Skill | Role |
|---|---|
| `file-read-workflow` | Try cache file before `web_fetch` |
| `cross-validation` | Dual-source validation for HV, IV, price |
| `decision-synthesis` | 4-dimension scoring → single AÇÃO+CONFIANÇA+SIZING |
| `risk-gating` | 7-item checklist before any buy/sell recommendation |
| `quant-b3` | B3 options analysis protocol |
| `quant-report-format` | Mandatory report template with auto-check |
| `coingecko-live` | Crypto data via CoinGecko |
| `fear-greed-live` | Fear & Greed index |
| `macro-brasil` | Selic + USD/BRL + macro context |
| `financial-datasets-live` | NYSE/NASDAQ fundamentals (not B3) |
| `earnings-calendar` | Upcoming macro events gate |
| `macro-snapshot` | Global macro snapshot |

For any recommendation (`decision-synthesis` output), the `risk-gating` verdict acts as an override: if blocked, recommendation downgrades one level.

### Python Utilities (run locally on VPS, not in ZeroClaw agent)

**Phase 1 — Superintelligence Pipeline** (`john_galt_superintelligence.py`):
Orchestrates: `AgentSwarmAnalyzer` (parallel async data fetch) → initial analysis → `ReflectionEngine` (up to 3 self-critique iterations via OpenRouter) → `AutoValidator` (freshness, Greeks ranges, required sections). Entry point for programmatic analysis.

**Phase 2 — Memory** (`src/enhanced_memory.py`):
Three stores at `/root/.zeroclaw/memory/`: episodic (`episodic.jsonl` — past analyses), semantic (`semantic.json` — accumulated knowledge), procedural (`procedural.json` — successful patterns).

**Phase 3 — Skill Library** (`src/skill_library.py`):
Auto-extracts reusable code patterns from successful episodes. Stores skills at `/root/.zeroclaw/skills/`.

**Phase 4 — Autonomous Learning** (`src/autonomous_learning.py`):
A/B testing framework, self-improvement curriculum, performance benchmarking, quality degradation detection. State at `/root/.zeroclaw/learning/`.

**`analyze_ticker.py`**: Self-contained quantitative pre-processor. Fetches data from BRAPI (B3) or CoinGecko (crypto), computes Black-Scholes ATM, Greeks, Kelly Criterion, Graham value, and writes output to `/root/.zeroclaw/workspace/{ticker}_output.txt`. The ZeroClaw agent then reads this file with `file_read` rather than recomputing everything via `web_fetch`.

### `b3_trading_signals/` Package

Backtesting engine bundled in this repo (separate from the VPS-installed version). `core/backtester.py` runs strategies on OHLCV DataFrames; `core/strategies.py` generates signals for SMA/EMA/BB/MACD; `core/indicator.py` computes indicators. Config loaded from `config.json`.

## Key Data Sources

| Asset class | API | Auth |
|---|---|---|
| B3 quotes + options | `brapi.dev/api/quote/{TICKER}` | `BRAPI_TOKEN` in SECRETS.md (not versioned) |
| Crypto spot/history | `api.coingecko.com` | None |
| Crypto options/IV | `www.okx.com/api/v5/public/opt-summary?instFamily=BTC-USD` | None |
| Fear & Greed | `api.alternative.me/fng/` | None |
| Selic (rate-free) | `api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1` | None |
| USD/BRL | `economia.awesomeapi.com.br/json/last/USD-BRL` | None |
| NYSE/NASDAQ fundamentals | `api.financialdatasets.ai` | None (public) |

> Financial Datasets (`financialdatasets.ai`) only works for NYSE/NASDAQ tickers — returns 400 for B3 tickers. Always use BRAPI for Brazilian stocks.

## Deployment

Push to `main` triggers `.github/workflows/deploy-to-vps.yml` which clones the repo to `/tmp/john-galt-ci/`. Manual copy to the VPS workspace (`/root/.zeroclaw/workspace/`) is the current final deployment step.

ZeroClaw Telegram bot setup: `zeroclaw onboard --channels-only` (generates and encrypts the bot token in `config.toml`).

## Critical Invariants

- **Never use memory data for quantitative values** — HV, IV, correlation, price must always come from fresh `web_fetch`. The SOL incident (2026-05-02) used stale HV 38% vs real 49.8%, inverting the vol strategy.
- **Every recommendation must pass all 4 auto-checks** before sending: VALIDAÇÃO, RISK GATING, SCORES, DECISÃO FINAL. If any section is missing, rewrite.
- **Kelly sizing caps**: 2% capital for high-risk (OTM), 5% for defined-risk (RR > 2:1). Always use 1/4 Kelly, never full Kelly.
- **`reflection_engine.py` uses `OPENROUTER_API_KEY`**; `agent_swarm_v2_0_bedrock.py` uses AWS credentials — do not mix.
