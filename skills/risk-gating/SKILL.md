---
name: risk-gating
description: >
  Checklist obrigatório de risco ANTES de qualquer recomendação de compra/venda/estrutura.
  Bloqueia recomendações sem validação prévia. Disparar SEMPRE que estiver prestes a sugerir
  COMPRA, VENDA, "monte essa estrutura", "entre em [posição]", ou qualquer alocação de capital.
---

# Risk Gating — Checklist anti-recomendação prematura

## Regra crítica
**NUNCA recomende posição sem responder os 7 itens abaixo.**

Se algum item estiver vermelho ❌, ou rebaixe a recomendação, ou recuse.

## Checklist (responder TODOS antes de recomendar)

### 1. ⚠️ Evento macro próximo? (≤ 3 dias)
- COPOM, FOMC, CPI, Payroll, earnings da empresa
- ❌ Se SIM: aguardar evento OU reduzir size 50%
- Fonte: skill `earnings-calendar` ou web_fetch BCB/FED

### 2. 💧 Liquidez suficiente?
- B3 opções: volume diário ≥ 100 contratos OU OI ≥ 500
- B3 ações: volume médio ≥ R$ 10M/dia
- Cripto: volume 24h ≥ $100M
- ❌ Se NÃO: reduzir size ou recusar (slippage destrói edge)

### 3. 📉 Drawdown atual da estratégia
- Se drawdown mensal > 10%: PARAR e revisar
- Se drawdown semanal > 5%: reduzir size 50%
- Se drawdown YTD > 20%: tese pode estar quebrada, reavaliar

### 4. 🔗 Correlação com BTC (cripto) ou Ibov (B3)
- Cripto vs BTC: corr > 0.85 = não é alpha, é beta — diversificação ilusória
- Ações vs Ibov: beta > 1.5 = trade alavancado em índice, não em alpha do ativo
- Validar correlação real (60d), nunca estimar

### 5. 💰 Sizing — Kelly conservador
- Máximo 2% do capital em alto risco (OTM, alavancado)
- Máximo 5% em risco limitado (RR > 2:1, defined-risk)
- Nunca usar Kelly Full — sempre 1/4 Kelly
- Stop: drawdown > 10% mês → parar

### 6. ⏱️ Time horizon coerente?
- DTE da opção compatível com tese? (tese de 30d, opção 5d → não)
- Stop-loss técnico antes do vencimento?
- Theta consumindo edge?

### 7. 🚪 Plano de saída definido
- Alvo de lucro: R$ ___ (X% upside)
- Stop de perda: R$ ___ (Y% downside)
- Stop de tempo: data ___
- ❌ Sem plano = não opere

## Output obrigatório

Antes da recomendação final, mostrar:

```
🛡️ RISK GATING

✅ Macro: sem evento até DD/MM
✅ Liquidez: volume médio R$ X.XM
✅ Drawdown: -X% (dentro do limite)
⚠️ Correlação BTC: 0.78 (alta, atenção)
✅ Sizing: 2% capital (R$ X.XXX)
✅ Horizon: 25 DTE compatível com tese 30d
✅ Saída: alvo R$ X / stop R$ Y / saída DD/MM

VEREDICTO: APROVADO (com size reduzido por correlação)
```

## Quando bloquear
- 2+ itens ❌ → recusar recomendação, pedir mais dados
- Evento macro ≤ 24h sem cobertura de hedge → recusar
- Liquidez insuficiente → recusar
