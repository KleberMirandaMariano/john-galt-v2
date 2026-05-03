# 🤖 John Galt v2.0 — Agente Quantitativo B3 + Cripto

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-production-green.svg)]()

**Agente quantitativo autônomo para análise de mercado brasileiro (B3) e criptomoedas.**

**Stack:** Claude Haiku 4.5 + OpenRouter + YFinance + b3_trading_signals  
**Autor:** Kleber Miranda  
**Última Atualização:** 03/05/2026

---

## 📊 Funcionalidades

### 🎯 **Análise Quantitativa B3**
- ✅ **Black-Scholes completo** (Greeks: Delta, Gamma, Theta, Vega, Rho)
- ✅ **Kelly Criterion** (position sizing)
- ✅ **Estruturas de opções** (Travas, THL, Booster, Iron Condor)
- ✅ **Backtesting profissional** (7 estratégias: SMA, EMA, BB, MACD)
- ✅ **Validação automática** de análises (9 erros detectados)

### 💰 **Dados de Mercado**
- ✅ **B3 Opções:** 333 ações (PETR4, VALE3, COGN3, ITUB4, etc)
- ✅ **Cripto:** BTC, ETH, SOL (spot + opções Deribit)
- ✅ **Índices Globais:** S&P 500, Nasdaq, Dow, FTSE, Nikkei, Hang Seng, Ibovespa
- ✅ **Macro:** Selic, USD/BRL, Fear & Greed Index

### 📈 **Análise de Correlações**
- ✅ **BTC vs VIX** (volatilidade)
- ✅ **BTC vs S&P 500** (risk-on/risk-off)
- ✅ **BTC vs DXY** (dólar)
- ✅ **BTC vs Gold** (ouro digital)

### 🔬 **Backtesting B3**
- ✅ **7 Estratégias:** SMA (9/21, 21/50, 9/21/50), EMA (9/21, 12/26), BB (20,2), MACD (12,26,9)
- ✅ **Métricas completas:** Retorno total, Sharpe Ratio, Max Drawdown, Win Rate
- ✅ **Ranking automático** por performance
- ✅ **Output JSON** estruturado

---

## 🚀 Instalação

### 1. Pré-requisitos

```bash
# Ubuntu 24 / Debian 12
sudo apt update
sudo apt install -y python3 python3-pip git curl

# Python packages
pip install --break-system-packages \
  pandas numpy matplotlib yfinance \
  scipy requests python-dotenv \
  openpyxl scikit-learn
```

### 2. Clone do Repositório

```bash
git clone https://github.com/KleberMirandaMariano/john-galt-v2.git
cd john-galt-v2
```

### 3. Instalar b3_trading_signals

```bash
cd /root/.zeroclaw
git clone https://github.com/gkeiel/b3_trading_signals.git
cd b3_trading_signals
pip install -e . --break-system-packages
```

---

## 📋 Scripts Disponíveis

### **📊 Análise de Opções B3**

#### `validate_options_b3.py` — Validador de Opções
```bash
python3 validate_options_b3.py TICKER SPOT STRIKE DAYS RATE VOL SERIES DATE PREMIUM TARGET CONTRACTS

# Exemplo PETR4
python3 validate_options_b3.py PETR4 49.08 52.00 30 0.1375 0.45 PETRF52 2026-06-15 1.50 55.00 10
```

**Output:** Greeks (Black-Scholes), P(ITM), Break-even, P&L, Kelly Criterion

---

### **🔬 Backtesting B3**

#### `validate_strategy_backtest.py` — Backtest Profissional
```bash
python3 validate_strategy_backtest.py TICKER [dias]

# Exemplos
python3 validate_strategy_backtest.py PETR4      # 365 dias (default)
python3 validate_strategy_backtest.py VALE3 180  # 180 dias
python3 validate_strategy_backtest.py COGN3 90   # 90 dias
```

**Estratégias testadas:**
- SMA 9/21, 21/50, 9/21/50
- EMA 9/21, 12/26
- Bollinger Bands 20/2
- MACD 12/26/9

**Output JSON:** `/tmp/backtest_TICKER_YYYYMMDD.json`

**Resultado PETR4 (180 dias):**
```
🥇 EMA 9/21:    +58.73% (Sharpe 3.84, DD -7.15%)
🥈 EMA 12/26:   +58.37% (Sharpe 3.80, DD -7.15%)
🥉 SMA 9/21:    +46.98% (Sharpe 3.52, DD -7.15%)
```

---

### **📈 Análise de Correlações BTC**

#### `btc_vix_correlation.py` — BTC vs VIX
```bash
python3 btc_vix_correlation.py [dias]
python3 btc_vix_correlation.py 90  # 90 dias (default)
```

**Resultado (02/05/2026):**
```
Correlação: -0.4813 (MODERADA NEGATIVA)
BTC = HEDGE contra volatilidade
```

#### `btc_spx_correlation.py` — BTC vs S&P 500
```bash
python3 btc_spx_correlation.py 90
```

**Resultado:**
```
Correlação: +0.5338 (MODERADA POSITIVA)
BTC = RISK-ON (move com ações)
```

#### `btc_dxy_correlation.py` — BTC vs Dollar Index
```bash
python3 btc_dxy_correlation.py 90
```

**Resultado:**
```
Correlação: -0.1896 (MUITO FRACA)
BTC = INDEPENDENTE do dólar
```

#### `btc_gold_correlation.py` — BTC vs Ouro
```bash
python3 btc_gold_correlation.py 90
```

**Resultado:**
```
Correlação: +0.1474 (MUITO FRACA)
BTC = INDEPENDENTE do ouro
Volatilidade: BTC 1.7x maior que ouro
```

---

### **💰 Coleta de Dados**

#### `deribit_btc_options.py` — Opções BTC Deribit
```bash
python3 deribit_btc_options.py
```

**Output:**
- 946 opções BTC (Calls + Puts)
- Greeks completos
- Volatilidade Implícita
- Open Interest
- JSON: `/tmp/deribit_btc_options.json`

#### `yfinance_indices.py` — Índices Globais
```bash
python3 yfinance_indices.py
```

**Output:**
- 8 índices: S&P 500, Dow, Nasdaq, FTSE, Nikkei, Taiwan, Hang Seng, Ibovespa
- Volatilidade histórica (20 dias)
- Retornos diários
- JSON: `/tmp/yfinance_indices.json`

---

## 🛠️ Estrutura do Projeto

```
john-galt-v2/
├── README.md                          # Este arquivo
├── config/
│   ├── SOUL.md                        # Personalidade do agente
│   ├── AGENTS.md                      # Configuração de agentes
│   ├── TOOLS.md                       # Ferramentas disponíveis
│   └── config.json                    # Config backtester
├── btc_vix_correlation.py            # BTC vs VIX
├── btc_spx_correlation.py            # BTC vs S&P 500
├── btc_dxy_correlation.py            # BTC vs DXY
├── btc_gold_correlation.py           # BTC vs Gold
├── deribit_btc_options.py            # Opções BTC Deribit
├── yfinance_indices.py               # Índices globais
├── validate_strategy_backtest.py     # Backtesting B3
├── validate_options_b3.py            # Validador opções B3
└── requirements.txt                   # Dependências Python
```

---

## 📊 Resultados de Testes

### **Backtesting PETR4 (180 dias)**

| Estratégia | Retorno | Sharpe | Max DD | Trades | Win% |
|------------|---------|--------|--------|--------|------|
| **EMA 9/21** | **+58.73%** | **3.84** | **-7.15%** | **3** | **33.3%** |
| EMA 12/26 | +58.37% | 3.80 | -7.15% | 3 | 33.3% |
| SMA 9/21 | +46.98% | 3.52 | -7.15% | 2 | 0.0% |
| MACD 12/26/9 | +46.26% | 3.89 | -6.64% | 8 | 37.5% |
| SMA 21/50 | +41.93% | 3.30 | -7.15% | 1 | 100.0% |
| SMA 9/21/50 | +34.19% | 2.85 | -7.15% | 2 | 50.0% |
| BB 20/2 | +2.04% | 2.07 | 0.00% | 4 | 50.0% |

**Melhor estratégia:** EMA 9/21 com **+58.73% em 6 meses** (117% anualizado)

### **Correlações BTC (90 dias - 02/05/2026)**

| Ativo | Pearson | Força | Interpretação |
|-------|---------|-------|---------------|
| **VIX** | -0.48 | 🟠 Moderada | Hedge contra vol |
| **S&P 500** | +0.53 | 🟠 Moderada | Risk-On |
| **DXY** | -0.19 | 🟢 Muito Fraca | Independente |
| **Gold** | +0.15 | 🟢 Muito Fraca | Independente |

**Conclusão:** BTC comporta-se como **tech stock** (correlacionado com ações), não como safe haven.

---

## 🔧 Configuração de Automação

### **Cron Jobs (Execução Diária)**

```bash
crontab -e

# Índices globais - 12:00
0 12 * * 1-5 python3 /root/.zeroclaw/workspace/yfinance_indices.py >> /tmp/yfinance_cron.log 2>&1

# Opções BTC Deribit - 12:05
5 12 * * 1-5 python3 /root/.zeroclaw/workspace/deribit_btc_options.py >> /tmp/deribit_cron.log 2>&1

# Correlações BTC - 12:15-12:18
15 12 * * 1-5 python3 /root/.zeroclaw/workspace/btc_vix_correlation.py 90 >> /tmp/btc_corr_cron.log 2>&1
16 12 * * 1-5 python3 /root/.zeroclaw/workspace/btc_spx_correlation.py 90 >> /tmp/btc_corr_cron.log 2>&1
17 12 * * 1-5 python3 /root/.zeroclaw/workspace/btc_dxy_correlation.py 90 >> /tmp/btc_corr_cron.log 2>&1
18 12 * * 1-5 python3 /root/.zeroclaw/workspace/btc_gold_correlation.py 90 >> /tmp/btc_corr_cron.log 2>&1
```

---

## 🐛 Troubleshooting

### **YFinance Timeout**
```bash
# Aumentar timeout
export YFINANCE_TIMEOUT=30
```

### **Deribit API Rate Limit**
```bash
# Reduzir batch size no script
# Linha 45: BATCH_SIZE = 25  # Default: 50
```

### **Backtesting Erro "Med"**
```bash
# Aplicar fix no b3_trading_signals
cd /root/.zeroclaw/b3_trading_signals
sed -i 's/"Med"/"Mid"/g' core/backtester.py
```

---

## 📚 Documentação Completa

**Notion:** https://www.notion.so/33f75c18ae098142b3cce5be5982649f

Inclui:
- 📊 Análise PETR4 completa
- 🔬 Backtesting metodologia
- 📈 Correlações BTC interpretação
- 🛠️ Troubleshooting detalhado
- 📝 Changelog completo

---

## 🤝 Contribuindo

Pull requests são bem-vindos!

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Add nova feature'`)
4. Push (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📝 Licença

MIT License — Veja [LICENSE](LICENSE) para detalhes.

---

## 🙏 Agradecimentos

- **[b3_trading_signals](https://github.com/gkeiel/b3_trading_signals)** — Biblioteca de backtesting B3
- **[YFinance](https://github.com/ranaroussi/yfinance)** — Dados de mercado
- **[CoinGecko](https://www.coingecko.com)** — Dados de cripto
- **[Deribit](https://www.deribit.com)** — Opções BTC
- **[Alternative.me](https://alternative.me)** — Fear & Greed Index
- **Claude (Anthropic)** — LLM
- **OpenRouter** — API Gateway

---

## 📊 Changelog

### v2.0.3 — 03/05/2026
- ✅ Integração b3_trading_signals (backtesting profissional)
- ✅ 4 scripts de correlação BTC (VIX, S&P500, DXY, Gold)
- ✅ Deribit BTC options fetcher (946 opções)
- ✅ YFinance global indices (8 índices)
- ✅ Testes completos PETR4 (EMA 9/21: +58.73%)

### v2.0.2 — 23/04/2026
- ✅ Validador genérico de opções B3
- ✅ Correção 9 erros COGN3
- ✅ CI/CD GitHub Actions
- ✅ Deploy automático VPS

### v2.0.1 — Initial Release
- ✅ Agente quantitativo básico
- ✅ Black-Scholes + Kelly Criterion
- ✅ SOUL.md + AGENTS.md

---

**Desenvolvido com ❤️ por [Kleber Miranda](https://github.com/KleberMirandaMariano)**  
**Última Atualização:** 03/05/2026
