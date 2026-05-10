---
name: quant-report-format
description: >
  Template padronizado para relatórios quant (B3, cripto, opções). Disparar com: "análise
  quant", "relatório quantitativo", "formatar análise", ticker + "análise". Garante
  consistência e seções obrigatórias.
---

# Quant Report Format — Template oficial

## Template (markdown)

```markdown
# 📊 ANÁLISE QUANT — {TICKER} — {DD/MM/YYYY}

**Status:** {Em Análise | Validada | Executada}
**Recomendação:** {COMPRA | VENDA | HOLD}
**Confiança:** XX%

---

## 🎯 TESE
{1-2 parágrafos}

## 📈 FUNDAMENTALISTA
| Métrica | Valor | Status |
|---|---|---|
| Preço | R$ X,XX | - |
| P/L | X,X | <15 atrativo |
| P/VP | X,X | <1.5 atrativo |
| ROE | X,X% | >15% bom |
| DY | X,X% | >5% alto |
| Graham | R$ X,XX | upside +X% |

## 📊 ESTATÍSTICO
| Métrica | Valor | Interpretação |
|---|---|---|
| Z-Score | X,X | <-1 deprimido |
| HV 30d | XX% | - |
| IV ATM | XX% | - |
| IV/HV | X,XX | <0.8 vol barata |

## 🔍 VALIDAÇÃO (cross-validation)
- Preço: $X (CG) / $Y (OKX) → ±X% ✅
- HV: X% (OKX) / Y% (calc) → ✅

## 🎯 ESTRUTURA
**{Nome da estrutura}**
- Strikes: ___
- Vencimento: DD/MM (XX dias)
- Prêmio: R$ ___
- Break-even: R$ ___ / R$ ___
- Ganho máx: R$ ___ | Perda máx: R$ ___
- Greeks: Δ X | Θ X | V X
- P(ITM): XX%

## 🛡️ RISK GATING
✅ Macro: sem evento até DD/MM
✅ Liquidez: OI XXX
✅ Sizing: X% capital (Kelly 1/4)
✅ Saída: alvo R$X / stop R$Y

## 💰 SIZING
- Kelly Full: XX% | 1/4 Kelly: X%
- Capital alocado: R$ ___

## 🎯 DECISÃO FINAL
**Ação:** COMPRA / VENDA / HOLD
**Estrutura:** ___
**Entrada:** R$ ___
**Stop:** R$ ___ | **Alvo:** R$ ___
**Confiança:** XX% (X/4 dimensões alinhadas)
```

## Regras de formatação

- Preços: R$ 0,00 (2 casas)
- %: 1 casa (12,5%)
- Greeks: 2-3 casas
- Datas: DD/MM/YYYY
- Status: 🔴 crítico | 🟠 alto | 🟡 médio | 🟢 baixo | ✅ ok | ⚠️ atenção

## Seções obrigatórias (TODAS — sem exceção)

```
1. Tese
2. Fundamentalista
3. Estatístico
4. 🔍 VALIDAÇÃO         ← cross-validation
5. Estrutura
6. 🛡️ RISK GATING       ← risk-gating
7. 📊 SCORES (T/F/M/S)  ← decision-synthesis
8. Sizing
9. 🎯 DECISÃO FINAL     ← decision-synthesis
```

## ⛔ AUTO-CHECK obrigatório antes de enviar

Antes de retornar a resposta ao usuário, verifique:

```
[ ] Seção "🔍 VALIDAÇÃO" presente com 2+ fontes para preço, HV, IV
[ ] Seção "🛡️ RISK GATING" presente com os 7 itens marcados ✅/❌
[ ] Seção "📊 SCORES" presente: T/F/M/S com pesos e total
[ ] Seção "🎯 DECISÃO FINAL" com AÇÃO + CONFIANÇA % + SIZING %
```

**Se QUALQUER item faltar → REESCREVA antes de enviar.**

Resposta sem essas seções = análise incompleta = recusada.

## Exemplo concreto de output completo

```markdown
# 📊 ANÁLISE QUANT — SOL — 10/05/2026

**Recomendação:** COMPRA | **Confiança:** 70%

## 🎯 TESE
SOL em recuperação após teste de $94. Momentum técnico positivo, vol normal,
sem evento macro até FOMC (18/05). Tese: alta moderada para $100-105 em 30d.

## 📈 FUNDAMENTALISTA
| Métrica | Valor | Status |
|---|---|---|
| Preço | $96.60 | - |
| Market Cap | $52B | - |

## 📊 ESTATÍSTICO
| Métrica | Valor | Interpretação |
|---|---|---|
| Var 24h | +3.47% | momentum |
| HV 30d | 49.8% | vol normal |
| IV ATM | 51.2% | IV/HV 1.03 — vol justa |
| Z-Score | +0.4 | neutro |

## 🔍 VALIDAÇÃO (cross-validation)
| Dado | Fonte 1 | Fonte 2 | Δ | Status |
|---|---|---|---|---|
| Preço | $96.60 (CG) | $96.55 (OKX) | 0.05% | ✅ |
| HV 30d | 49.8% (OKX) | 50.2% (calc) | 0.4pp | ✅ |
| IV ATM | 51.2% (OKX) | 50.8% (BS) | 0.4pp | ✅ |
| Corr BTC 60d | +0.41 (CG) | +0.43 (calc) | 2pp | ✅ |

## 🎯 ESTRUTURA — Bull Call Spread
- Compra Call $96 / Vende Call $103
- DTE: 30d (vence 09/06)
- Custo: $2.38 | Ganho máx: $4.62 | RR: 1.94:1
- Greeks: Δ líquido 0.42 | Θ +$0.016/dia | V $0.18

## 🛡️ RISK GATING
| # | Item | Status |
|---|------|--------|
| 1 | Macro ≤3 dias? | ✅ FOMC em 18/05 (8 dias) |
| 2 | Liquidez? | ✅ OI $96 = 1.2k contratos |
| 3 | Drawdown atual? | ✅ -2% mês (limite -10%) |
| 4 | Corr BTC 60d? | ⚠️ 0.41 (moderada — OK) |
| 5 | Sizing Kelly 1/4? | ✅ 3% capital |
| 6 | Horizon coerente? | ✅ DTE 30d = tese 30d |
| 7 | Plano saída? | ✅ Stop $94 / Alvo $103 / Saída 09/06 |

VEREDICTO: APROVADO

## 📊 SCORES (decision-synthesis)
| Dimensão | Score | Peso | Contribuição |
|---|---|---|---|
| Técnico (T) | 7.2/10 | 25% | 1.80 |
| Fundamental (F) | 6.5/10 | 30% | 1.95 |
| Macro (M) | 6.8/10 | 20% | 1.36 |
| Sentiment (S) | 7.0/10 | 25% | 1.75 |
| **Total** | | | **6.86/10** |

Alinhamento: 4/4 dimensões → confiança 70%

## 💰 SIZING
- Kelly Full: 12% | 1/4 Kelly: 3%
- Capital: R$ 3.000 → 6 contratos

## 🎯 DECISÃO FINAL
**Ação:** COMPRA (Bull Call Spread 96/103)
**Entrada:** $2.38 (mid)
**Stop:** $94 spot | **Alvo:** $103 spot
**Confiança:** 70% (4/4 dimensões alinhadas)
**Validade:** até 09/06 (vencimento)
```

## Integração
- `decision-synthesis` produz "📊 SCORES" + "🎯 DECISÃO FINAL"
- `risk-gating` produz "🛡️ RISK GATING"
- `cross-validation` produz "🔍 VALIDAÇÃO"
- Sem essas 3 seções, a resposta é narrativa criativa — não é análise quant
