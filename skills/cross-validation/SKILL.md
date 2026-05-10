---
name: cross-validation
description: >
  Valida dados críticos (HV, IV, preço, fundamentalistas) com 2+ fontes independentes
  antes de uso em recomendação. Disparar quando: usar HV/IV em decisão, citar preço para
  estrutura de opções, comparar P/L ou ROE, ou qualquer dado que afete sizing/recomendação.
---

# Cross-Validation — Confirme antes de decidir

## Regra crítica
**Dado crítico = dado que muda a recomendação.**
Para todo dado crítico: 2 fontes. Se divergem > 5%, alertar.

## Dados que EXIGEM validação dupla

| Dado | Fonte 1 | Fonte 2 | Tolerância |
|------|---------|---------|-----------|
| Preço B3 | BRAPI | Yahoo Finance via yfinance | ±0.5% |
| Preço cripto | CoinGecko | OKX (`/v5/market/ticker`) | ±0.5% |
| HV cripto | OKX `mark-vol` | Calcular inline com OHLCV | ±10% |
| IV ATM cripto | OKX `opt-summary` | Calcular IV implícita (newton) | ±5% |
| P/L B3 | BRAPI `priceEarnings` | Calcular: preço/LPA | ±2% |
| Selic | BCB SGS 432 | BCB página oficial | exata |
| USD/BRL | BCB | AwesomeAPI | ±0.3% |

## Workflow

```
1. Buscar fonte primária (web_fetch)
2. Buscar fonte secundária (web_fetch)
3. Comparar:
   - Δ ≤ tolerância → usar média ou primária
   - Δ > tolerância → ALERTAR usuário, mostrar ambos, pedir decisão
4. Documentar no relatório:
   "Preço SOL: $86.22 (CoinGecko) / $86.31 (OKX) — convergente ✅"
```

## Erros históricos a evitar

**SOL 02/05/2026:**
- HV usada: 38% (memória)
- HV real: 49.8%
- Resultado: estratégia invertida — recomendou venda de vol quando vol estava cara
- **Solução:** sempre buscar HV fresca de 2 fontes

**Correlação BTC:**
- Estimada: +0.92
- Real: +0.41
- Resultado: alpha subestimado, sizing errado
- **Solução:** calcular correlação 60d com dados de 2 fontes, nunca estimar

## Output obrigatório

Em qualquer relatório que use dado crítico:

```
🔍 VALIDAÇÃO DE DADOS

Preço SOL:    $86.22 (CG) / $86.31 (OKX) → ±0.1% ✅ usar
HV 30d:       49.8% (OKX) / 50.2% (calc) → ±0.4% ✅ usar 50.0%
IV ATM:       52.1% (OKX) / 51.4% (BS)   → ±1.4% ✅ usar 51.7%
Corr BTC 60d: +0.41 (CG)  / +0.43 (TV)   → ±2pp  ✅ usar 0.42
```

## Quando recusar análise
- 2+ dados críticos divergem > tolerância → recusar até reconciliar
- 1 fonte indisponível para dado crítico → marcar análise como "parcial"
- Fonte única para HV ou IV → exigir 2ª fonte ou rebaixar confiança da recomendação
