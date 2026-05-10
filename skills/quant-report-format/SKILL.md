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

## Seções obrigatórias
Tese, Fundamental, Estatístico, **Validação**, Estrutura, **Risk Gating**, Sizing, **Decisão Final**.
Sem qualquer dessas → relatório incompleto.

## Integração
- `decision-synthesis` produz a decisão final
- `risk-gating` produz a seção Risk Gating
- `cross-validation` produz a seção Validação
