# Skill: fundamentus-b3

Execute quando o usuário pedir fundamentalistas de empresa B3: ROE, ROA, margem, dívida, dividend yield, P/VP, EV/EBITDA, ou quando o score Fundamental do `decision-synthesis` precisar de dados além do que o BRAPI fornece.

## Passo 1 — Buscar HTML do Fundamentus

```
web_fetch("https://www.fundamentus.com.br/detalhes.php?papel={TICKER}")
→ retorna HTML com duas tabelas de indicadores
```

> Encoding: Latin-1. Valores em formato brasileiro: `1.234,56%` = 1234.56%

## Passo 2 — Extrair campos do HTML

Procure os rótulos abaixo no HTML e capture o valor na `<td>` imediatamente seguinte:

### Valuation
| Rótulo no HTML | Campo | Unidade |
|----------------|-------|---------|
| `P/L` | P/E ratio | x |
| `P/VP` | Preço / Valor Patrimonial | x |
| `EV/EBITDA` | EV/EBITDA | x |
| `EV/EBIT` | EV/EBIT | x |
| `Div.Yield` | Dividend Yield | % a.a. |

### Rentabilidade
| Rótulo no HTML | Campo | Unidade |
|----------------|-------|---------|
| `ROE` | Return on Equity | % a.a. |
| `ROIC` | Return on Invested Capital | % a.a. |
| `Marg.Líquida` | Margem Líquida | % |
| `Marg.EBIT` | Margem EBIT | % |
| `Cresc. Rec.5a` | Crescimento de Receita 5 anos | % |

### Endividamento e Liquidez
| Rótulo no HTML | Campo | Unidade |
|----------------|-------|---------|
| `Dív.Bruta/Patrim.` | Dívida Bruta / PL | x |
| `Líq. Corr.` | Liquidez Corrente | x |
| `Líq.2meses` | Volume médio diário | R$ |

> **Parsing:** remova `.` separador de milhar e substitua `,` por `.` antes de converter para float.
> Ex: `"1.234,56%"` → `float("1234.56")` = 1234.56 → dividir por 100 = 12.3456

## Passo 3 — Interpretar

```
# Valuation
pl:
  < 0      → prejuízo — não aplicar múltiplo
  < 10     → barato historicamente para B3
  10-20    → justo
  > 20     → caro ou crescimento precificado

pvp:
  < 1.0    → abaixo do valor patrimonial
  1.0-2.0  → faixa saudável
  > 3.0    → caro / mercado precifica crescimento relevante

ev_ebitda:
  < 6      → potencialmente barato
  6-12     → faixa razoável
  > 15     → caro

# Rentabilidade
roe:
  < 10%    → fraco
  10-20%   → razoável
  > 20%    → forte — empresa com vantagem competitiva

margem_liquida:
  < 5%     → margem apertada
  5-15%    → saudável
  > 15%    → excelente (commodities costumam oscilar muito)

# Endividamento
divida_pl:
  < 0.5    → conservador
  0.5-1.5  → aceitável
  > 2.0    → alavancado — risco com Selic alta

# Dividend Yield
dy:
  > 6%     → renda relevante (comparar com Selic)
  Selic/2  → mínimo aceitável como tese de dividendo
```

## Passo 4 — Valor Graham (calcular inline)

```
# Requer: LPA (EPS via BRAPI) e VPA (Valor Patrimonial por Ação)
# VPA = resultado de P/VP: VPA = Preço / PVP

VPA = preço_atual / pvp
VG  = √(22.5 × LPA × VPA)   # válido só se LPA > 0 e VPA > 0
upside = (VG - preço_atual) / preço_atual × 100
```

## Passo 5 — Output

```
📊 FUNDAMENTUS — {TICKER} — {DATA}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 VALUATION
  P/L: {pl:.1f}x ({interp_pl})
  P/VP: {pvp:.2f}x | EV/EBITDA: {ev_ebitda:.1f}x
  Div.Yield: {dy:.1f}% a.a. (Selic: {selic:.1f}%)

📈 RENTABILIDADE
  ROE: {roe:.1f}% | ROIC: {roic:.1f}%
  Marg.Líquida: {ml:.1f}% | Marg.EBIT: {mebit:.1f}%
  Cresc.Receita 5a: {cresc:.1f}%

🏦 ENDIVIDAMENTO
  Dív/PL: {div_pl:.2f}x ({interp_divida})
  Líq.Corrente: {liq_corr:.2f}x

📐 VALOR GRAHAM: R$ {vg:.2f} ({upside:+.1f}% vs preço atual)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ SCORE FUNDAMENTAL (0-10)
  {score_fund:.1f} — {justificativa}
```

## REGRA CRÍTICA
NUNCA cite ROE, margem ou dívida de memória. Sempre buscar via Fundamentus antes.
Se o ticker não existir na página, Fundamentus retorna tabela vazia — informar o usuário e usar apenas BRAPI.
