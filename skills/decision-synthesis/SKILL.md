---
name: decision-synthesis
description: >
  Combina sinais técnico + fundamental + macro + sentiment em decisão única com confiança
  calibrada. Disparar quando o usuário pedir "recomendação", "análise completa",
  "estratégia para [TICKER]", "compro ou vendo", "qual a melhor estrutura". Tem prioridade
  sobre relatórios descritivos — converte dados em ação.
---

# Decision Synthesis — De dados para decisão

## Regra de ouro
**Análise sem decisão é ruído.**
Toda análise termina em: AÇÃO + CONFIANÇA + SIZING.

## Framework de scoring (4 dimensões, 0-10 cada)

### 1. Técnico (T) — peso 25%
- Tendência (EMA21 vs SMA50): 0-3
- Momentum (RSI, MACD): 0-3
- Z-Score regressão: 0-2
- Suporte/resistência: 0-2

### 2. Fundamentalista (F) — peso 30%
- Value (P/L, P/VP): 0-3
- Quality (ROE, margem): 0-3
- Growth (receita, lucro): 0-2
- Risk (dívida, liquidez): 0-2

### 3. Macro (M) — peso 20%
- Selic/Fed direção: 0-3
- Câmbio coerente com tese: 0-2
- Risk-on/risk-off global: 0-3
- Eventos próximos: 0-2

### 4. Sentiment (S) — peso 25%
- Fear & Greed: 0-3
- IV/HV (vol cara/barata): 0-3
- Funding rate (cripto): 0-2
- Open Interest tendência: 0-2

## Score final

```
Score = 0.25·T + 0.30·F + 0.20·M + 0.25·S
```

## Mapa de decisão

| Score | Ação | Confiança | Sizing |
|-------|------|-----------|--------|
| ≥ 8.0 | COMPRA forte | 80%+ | até 5% capital (RR>2:1) |
| 6.5-7.9 | COMPRA | 65-80% | até 3% capital |
| 5.5-6.4 | NEUTRO/HOLD | 50-65% | sem nova posição |
| 4.0-5.4 | VENDA | 65-80% | reduzir/short defined |
| < 4.0 | VENDA forte | 80%+ | sair/short com hedge |

**Override de risco:** Se `risk-gating` bloquear ou rebaixar, decisão final **rebaixa um nível**.

## Confiança calibrada

Confiança = % das 4 dimensões alinhadas:
- 4/4 alinhadas (todas COMPRA ou todas VENDA) → 85%
- 3/4 alinhadas → 70%
- 2/4 alinhadas → 50% (NEUTRO recomendado)
- < 2/4 → 35% (sem decisão clara)

**Nunca afirmar confiança > 90%** — mercado tem ruído irredutível.

## Estrutura por cenário (após decisão)

| Decisão | IV/HV | Estrutura preferida |
|---------|-------|---------------------|
| COMPRA forte | < 0.8 | Long Call OTM |
| COMPRA | qualquer | Bull Call Spread |
| COMPRA defensiva | > 1.0 | Bull Put Spread (crédito) |
| NEUTRO | > 1.2 | Iron Condor |
| NEUTRO | < 0.8 | Long Straddle (vol play) |
| VENDA | qualquer | Bear Put Spread |
| VENDA forte | < 0.8 | Long Put OTM |

## Output obrigatório

```
🎯 DECISÃO SINTÉTICA — {TICKER}

Scores:
  Técnico:        7.2/10  🟢
  Fundamental:    8.1/10  🟢
  Macro:          5.5/10  🟡
  Sentiment:      6.8/10  🟢

Score final: 7.0/10
Alinhamento:  3/4 dimensões → confiança 70%

DECISÃO: COMPRA
Estrutura: Bull Call Spread (IV neutro)
Sizing:    3% capital (Kelly 1/4)
Stop:      R$ X,XX
Alvo:      R$ Y,YY
Validade:  até DD/MM (vencimento da opção)

⚠️ Pendências macro: COPOM em DD/MM — reduzir size 50% se ≤3 dias
```

## Anti-padrão
```
❌ "SOL teve alta 5%, IV em 50%, FNG em 60..." (lista de dados)
✅ "SOL: COMPRA, 70% confiança, Bull Call Spread 84/90, 3% capital, alvo $95"
```
