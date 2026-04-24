# 🤖 John Galt v2.0 — Agente Quantitativo B3 + Cripto

**Status:** ✅ Produção (23/04/2026)  
**Autor:** Kleber Miranda  
**Stack:** ZeroClaw + Claude Haiku 4.5 + OpenRouter

---

## 📊 O Que é John Galt?

Agente quantitativo autônomo especializado em:

- **Análise de Ações B3** (COGN3, PETR4, VALE3, ITUB4, PCAR3, GMAT3)
- **Opções B3** (Calls, Puts, Travas, THL, Booster Horizontal)
- **Criptomoedas** (BTC, ETH, SOL)
- **Análise Macro** (Selic, Câmbio, Ibovespa, Fear & Greed)

### 🎯 Principais Funcionalidades

✅ **Análise Quantitativa Completa**
- Black-Scholes (gregas: Delta, Gamma, Theta, Vega)
- Kelly Criterion (sizing de posição)
- DVR e FFO (estruturas temporais)
- P(Sucesso), Risk/Reward, Stop Loss

✅ **Dados em Tempo Real**
- CoinGecko (BTC, ETH, SOL)
- Alternative.me (Fear & Greed Index)
- BRAPI (B3 cotações)
- BCB PTAX (USD/BRL oficial)

✅ **Template Padronizado**
- Skill `quant-report-format`
- Formatação consistente
- Validação automática

✅ **Sistema de Fallback**
- Cache local via cron
- Resiliência a falhas de API
- Scripts automáticos (7 linhas crontab)

---

## 🚀 Instalação

### 1. Pré-requisitos

```bash
# Ubuntu 24 / Debian 12
sudo apt update
sudo apt install -y python3 python3-pip curl jq

# Instalar ZeroClaw (Rust)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
cargo install zeroclaw
```

### 2. Configuração

```bash
# Clonar repositório
git clone https://github.com/KleberMirandaMariano/john-galt-v2.git
cd john-galt-v2

# Copiar configurações
cp config/SOUL.md ~/.zeroclaw/workspace/
cp config/AGENTS.md ~/.zeroclaw/workspace/
cp config/TOOLS.md ~/.zeroclaw/workspace/

# Copiar skills
cp -r skills/* ~/.zeroclaw/workspace/skills/

# Instalar scripts
cp scripts/*.py ~/.zeroclaw/workspace/
cp scripts/*.sh ~/.zeroclaw/workspace/
chmod +x ~/.zeroclaw/workspace/*.sh
```

### 3. Configurar API Keys

```bash
# Editar config.toml
nano ~/.zeroclaw/config.toml

# Adicionar:
# OPENROUTER_API_KEY=sk-or-v1-...
```

### 4. Iniciar

```bash
# Iniciar daemon
systemctl --user start zeroclaw

# Verificar status
systemctl --user status zeroclaw
```

---

## 📋 Comandos Disponíveis (Telegram)

| Comando | Descrição | API Calls |
|---------|-----------|-----------|
| `cripto` | BTC/ETH/SOL + Fear & Greed | 2 |
| `resumo` | Cripto + B3 + Macro | 3-4 |
| `analise COGN3` | Análise quantitativa completa | 1 + cálculo |
| `macro` | Selic, câmbio, Ibovespa | 2 |
| `btc` | Análise detalhada BTC | 2 |

---

## 🛠️ Estrutura do Projeto
[200~---

## 🔧 Troubleshooting

### HTTP Requests Bloqueados?

```bash
# Verificar config.toml
grep -A 5 "web_fetch" ~/.zeroclaw/config.toml

# Deve ter: allowed_domains = ["*"]
```

### Skills Não Carregam?

```bash
# Verificar skills carregadas
journalctl --user -u zeroclaw | grep Skills

# Reinstalar skills
cp -r skills/* ~/.zeroclaw/workspace/skills/
systemctl --user restart zeroclaw
```

### USD/BRL Falha?

```bash
# Testar fontes
python3 scripts/get_usdbrl.py

# BCB PTAX (oficial)
# AwesomeAPI (tempo real)
# CoinGecko USDT (fallback)
```

---

## 📊 Análise de Validação

**COGN3 — 6 Erros Encontrados:**

| Erro | Impacto | Correção |
|------|---------|----------|
| DY 580% → 6% | 🔴 Crítico | `correct_cogn3_analysis.py` |
| FOMC não mencionado | 🔴 Crítico | Incluído em análises |
| Série COGNK2 errada | 🟠 Alto | COGNE1207 |
| Theta -0,08 irreal | 🟠 Alto | -0,008 (Deep ITM) |

**Database completo:** [Notion](https://www.notion.so/15e2a10c55bf440fa797dac55afb44ed)

---

## 🤝 Contribuindo

Pull requests são bem-vindos!

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-skill`)
3. Commit suas mudanças (`git commit -m 'Add nova skill'`)
4. Push (`git push origin feature/nova-skill`)
5. Abra um Pull Request

---

## 📝 Licença

MIT License

---

## 🙏 Agradecimentos

- **ZeroClaw** — Framework de agentes
- **Claude (Anthropic)** — LLM
- **OpenRouter** — API Gateway
- **CoinGecko, BRAPI, BCB** — APIs de dados

---

**Última Atualização:** 23/04/2026  
**Autor:** Kleber Miranda ([@KleberMirandaMariano](https://github.com/KleberMirandaMariano))

---

## 🔍 Validador de Opções B3

Script genérico para validar análises quantitativas de **QUALQUER ativo B3**.

### ✅ Erros Corrigidos:

1. 🔴 **Série expirada** (nomenclatura B3: A-L = jan-dez)
2. 🔴 **Delta incorreto** (Black-Scholes correto)
3. 🔴 **P(ITM) incorreto** (probabilidade real)
4. 🔴 **Theta positivo** (impossível para long call)
5. 🔴 **Break-even errado** (Strike + Premium, não Spot + Premium)
6. 🟡 **Classificação ATM/OTM/ITM**
7. 🟡 **P&L calculado**
8. 🟡 **Kelly Criterion**

### 🚀 Uso:

```bash
python3 scripts/validate_options_b3.py \
  TICKER SPOT STRIKE DAYS RATE VOL SERIES DATE PREMIUM TARGET CONTRACTS
```

### 📊 Exemplos:

```bash
# COGN3
python3 scripts/validate_options_b3.py COGN3 2.97 3.35 23 0.1475 0.65 COGND335 2026-04-24 0.085 3.80 10

# PETR4
python3 scripts/validate_options_b3.py PETR4 38.50 40.00 30 0.1475 0.45 PETRJ40 2026-05-15 1.20 42.00 5

# VALE3
python3 scripts/validate_options_b3.py VALE3 65.50 68.00 25 0.1475 0.50 VALEF68 2026-06-15 1.50 70.00 10
```

### 📈 Saída:

- ✅ Gregas Black-Scholes corretas (Delta, Theta, Gamma, Vega)
- ✅ P(ITM) real
- ✅ Break-even correto
- ✅ P&L calculado
- ✅ Kelly Criterion com valor esperado
- ✅ Detecção automática de erros

**Baseado na validação Cowork (24/04/2026) que encontrou 9 erros na análise COGN3.**

