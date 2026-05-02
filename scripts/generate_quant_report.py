#!/usr/bin/env python3
"""
generate_quant_report.py — Gerar relatório quantitativo formatado
Usa template da skill quant-report-format
"""

import os
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(os.getenv('ZEROCLAW_WORKSPACE', '/root/.zeroclaw/workspace'))

def generate_quant_report(
    ticker: str,
    fundamentalista: dict,
    estatistico: dict,
    opcoes: dict,
    gregas: dict,
    kelly: dict,
    riscos: dict,
    recomendacao: dict,
    status: str = "Validada",
    risco_retorno: str = "Moderado"
):
    """Gerar relatório formatado segundo skill quant-report-format"""
    
    data = datetime.now().strftime("%d/%m/%Y")
    
    report = f"""# 📊 ANÁLISE QUANT — {ticker} — {data}

**Status:** {status}
**Risco/Retorno:** {risco_retorno}
**Recomendação:** {recomendacao['acao']}

---

## 🎯 TESE CENTRAL

{recomendacao.get('tese', 'N/A')}

---

## 📈 FUNDAMENTALISTA

| Métrica | Valor | Status |
|---------|-------|--------|
| Preço Atual | R$ {fundamentalista['preco_atual']:.2f} | {fundamentalista.get('status_preco', 'N/A')} |
| P/L | {fundamentalista['p_l']:.2f} | {fundamentalista.get('status_pl', 'N/A')} |
| P/VP | {fundamentalista.get('p_vp', 'N/A')} | {fundamentalista.get('status_pvp', 'N/A')} |
| Dividend Yield | {fundamentalista['dividend_yield']*100:.1f}% | {fundamentalista.get('status_dy', 'N/A')} |
| ROE | {fundamentalista.get('roe', 'N/A')} | {fundamentalista.get('status_roe', 'N/A')} |
| Upside Graham | {fundamentalista['upside_graham']*100:.0f}% | Alvo: R$ {fundamentalista['preco_justo_graham']:.2f} |
| Preço Justo | R$ {fundamentalista['preco_justo_graham']:.2f} - {fundamentalista.get('preco_justo_graham_max', fundamentalista['preco_justo_graham']):.2f} | Intervalo conservador-otimista |

**Avaliação:** {fundamentalista['avaliacao']}

---

## 📊 ESTATÍSTICO

| Métrica | Valor | Interpretação |
|---------|-------|---------------|
| Variação 24h | {estatistico.get('var_24h', 0)*100:+.2f}% | {estatistico.get('interpretacao_var', 'N/A')} |
| Z-Score | {estatistico.get('z_score', 'N/A')} | {estatistico.get('interpretacao_z', 'N/A')} |
| HV (Vol. Histórica) | {estatistico.get('hv', 0)*100:.0f}% | {estatistico.get('interpretacao_hv', 'N/A')} |
| IV (Vol. Implícita) | {estatistico.get('iv', 0)*100:.0f}% | {estatistico.get('interpretacao_iv', 'N/A')} |
| IV/HV Ratio | {estatistico.get('iv_hv', 'N/A')} | {estatistico.get('interpretacao_iv_hv', 'N/A')} |
| DVR (Curto-Longo) | {estatistico.get('dvr', 'N/A')} | {estatistico.get('interpretacao_dvr', 'N/A')} |
| Tendência (Regressão) | {estatistico.get('tendencia', 'N/A')} | R²: {estatistico.get('r2', 'N/A')} / Slope: {estatistico.get('slope', 'N/A')} |

**Contexto de Mercado:**
{estatistico.get('contexto_mercado', '- Sem eventos relevantes identificados')}

---

## 🎯 ESTRUTURA RECOMENDADA

### {opcoes['nome_estrutura']}

**Posição:**
**Parâmetros Financeiros:**
- **Investimento Total:** R$ {opcoes.get('investimento_total', 0):,.2f}
- **Break-even:** R$ {opcoes['break_even']:.2f}
- **Alvo Conservador:** R$ {opcoes['alvo_conservador']:.2f} (Ganho: R$ {opcoes['ganho_conservador']:,.0f})
- **Alvo Realista:** R$ {opcoes['alvo_realista']:.2f} (Ganho: R$ {opcoes['ganho_realista']:,.0f})
- **Alvo Bull:** R$ {opcoes.get('alvo_bull', opcoes['alvo_realista']):.2f} (Ganho: R$ {opcoes.get('ganho_bull', opcoes['ganho_realista']):,.0f})
- **Stop Loss:** R$ {opcoes.get('stop', 'N/A')} (Perda máx: R$ {opcoes.get('perda_max', 'N/A')})

**Gregas:**
- **Delta:** {gregas['delta']:.2f} ({gregas.get('tipo_moneyness', 'N/A')})
- **Theta:** {gregas['theta_diario']:.3f}/dia ({gregas.get('urgencia', 'N/A')})
- **Vega:** {gregas.get('vega', 'N/A')} ({gregas.get('sensibilidade_iv', 'N/A')})
- **Gamma:** {gregas.get('gamma', 'N/A')}

**Probabilidades:**
- **P(ITM):** {gregas['p_itm']*100:.0f}%
- **P(Profit):** {gregas.get('p_profit', gregas['p_itm'])*100:.0f}%
- **P(Max Loss):** {gregas.get('p_max_loss', 1-gregas['p_itm'])*100:.0f}%

---

## 💰 KELLY CRITERION & SIZING

**Cálculo:**
**Recomendação de Capital:**
- **Kelly Full:** {kelly['f_star']*100:.0f}% do capital (R$ {kelly.get('capital_full', 'N/A'):,.0f})
- **Kelly 1/4 (Conservador):** {kelly['kelly_conservador']*100:.0f}% do capital (R$ {kelly['capital_recomendado']:,.0f})
- **Quantidade:** ~{kelly['n_opcoes']} opções OU {kelly.get('n_lotes', 'N/A')} lotes de 100
- **Custo Total:** R$ {kelly.get('preco_total_lotes', kelly['capital_recomendado']):,.0f}

---

## ⚠️ RISCOS & ALERTAS

### 🔴 Riscos Críticos
{chr(10).join(f'- {r}' for r in riscos.get('criticos', ['Nenhum risco crítico identificado']))}

### 🟠 Riscos Altos
{chr(10).join(f'- {r}' for r in riscos.get('altos', ['Nenhum risco alto identificado']))}

### 🟡 Riscos Médios
{chr(10).join(f'- {r}' for r in riscos.get('medios', ['Nenhum risco médio identificado']))}

### 📅 Calendário de Eventos
{chr(10).join(f'- {e}' for e in riscos.get('eventos', ['Nenhum evento relevante identificado']))}

---

## 🎯 RECOMENDAÇÃO FINAL

**Ação:** {recomendacao['acao']}
**Estrutura:** {recomendacao['estrutura']}
**Entrada:** R$ {recomendacao['entrada']:.2f}
**Quantidade:** {recomendacao['quantidade']}
**Stop:** R$ {recomendacao['stop']:.2f}
**Alvo:** R$ {recomendacao['alvo']:.2f} ({recomendacao.get('tipo_alvo', 'Realista')})
**Kelly:** {recomendacao['kelly_percent']}% do capital (R$ {recomendacao['kelly_valor']:,.0f})
**Observações:** {recomendacao.get('observacoes', 'Nenhuma observação adicional')}

---

**P(Sucesso) = {gregas['p_itm']*100:.0f}%**
"""
    
    return report


# Exemplo de uso com COGN3 corrigido
if __name__ == "__main__":
    
    report = generate_quant_report(
        ticker="COGN3",
        fundamentalista={
            "preco_atual": 3.27,
            "p_l": 10.89,
            "p_vp": 0.51,
            "dividend_yield": 0.06,
            "roe": "N/A",
            "upside_graham": 0.95,
            "preco_justo_graham": 5.42,
            "preco_justo_graham_max": 6.63,
            "avaliacao": "Subvalorizada segundo Graham",
            "status_preco": "Subvalorizado",
            "status_pl": "Atrativo (<15)",
            "status_pvp": "<1.0 = Barato",
            "status_dy": "Alto (>5%)"
        },
        estatistico={
            "var_24h": 0.0092,
            "interpretacao_var": "Recuperação leve",
            "z_score": -1.2,
            "interpretacao_z": "Deprimido (candidato a compra)",
            "hv": 0.45,
            "interpretacao_hv": "Alta (penny stock)",
            "iv": 0.52,
            "interpretacao_iv": "Cara para o ativo",
            "iv_hv": 1.15,
            "interpretacao_iv_hv": ">1.0 = Vol ligeiramente cara",
            "dvr": "Positivo",
            "interpretacao_dvr": "Favorável para THL",
            "tendencia": "Alta",
            "r2": 0.65,
            "slope": 0.02,
            "contexto_mercado": "- FOMC em 28-29 de abril (SEMANA QUE VEM!)\n- COPOM em 20 de maio\n- Alto risco de gap em volatilidade"
        },
        opcoes={
            "nome_estrutura": "Call Simples ATM",
            "serie": "COGNE600",
            "tipo": "Call",
            "strike": 0.60,
            "premio": 2.75,
            "vencimento": "15/05/2026",
            "dias_restantes": 24,
            "quantidade": 290,
            "lotes": 3,
            "investimento_total": 825,
            "break_even": 3.35,
            "alvo_conservador": 5.42,
            "ganho_conservador": 773,
            "alvo_realista": 6.63,
            "ganho_realista": 1121,
            "alvo_bull": 6.90,
            "ganho_bull": 1195,
            "stop": 2.00,
            "perda_max": 225
        },
        gregas={
            "delta": 0.95,
            "tipo_moneyness": "Deep ITM",
            "theta_diario": -0.008,
            "urgencia": "Mínimo (sem urgência)",
            "vega": 0.15,
            "sensibilidade_iv": "Baixa",
            "gamma": 0.02,
            "p_itm": 0.95,
            "p_profit": 0.68,
            "p_max_loss": 0.05
        },
        kelly={
            "b": 1.17,
            "p_success": 0.95,
            "f_star": 0.32,
            "kelly_conservador": 0.08,
            "capital_recomendado": 825,
            "n_opcoes": 290,
            "n_lotes": 3,
            "preco_total_lotes": 825
        },
        riscos={
            "criticos": [
                "FOMC 28-29/04 pode gerar gap de volatilidade",
                "Liquidez restrita em séries OTM",
                "Penny stock com alta volatilidade intrínseca"
            ],
            "altos": [
                "Vencimento em 24 dias (15/05/2026)",
                "IV/HV 1.15 (vol ligeiramente cara)"
            ],
            "medios": [
                "Spread bid-ask pode ser alto",
                "Eventos corporativos não mapeados"
            ],
            "eventos": [
                "28-29/04 — FOMC (FED)",
                "15/05 — Vencimento COGNE600 (sexta-feira)",
                "20/05 — COPOM (Banco Central)"
            ]
        },
        recomendacao={
            "acao": "COMPRA",
            "tese": "COGN3 em recuperação técnica (+0,92% hoje) com upside Graham de 95%. Penny stock subvalorizada (P/VP 0,51). Call ATM COGNE600 oferece exposição alavancada com theta controlado (-0,008/dia). Monitorar FOMC antes de entrar.",
            "estrutura": "Call ATM COGNE600",
            "entrada": 2.75,
            "quantidade": "~290 opções OU 3 lotes",
            "stop": 2.00,
            "alvo": 6.63,
            "tipo_alvo": "Realista",
            "kelly_percent": 8,
            "kelly_valor": 825,
            "observacoes": "⚠️ Monitorar FOMC 28-29/04. Theta mínimo permite carregar sem urgência."
        },
        status="Validada e Corrigida",
        risco_retorno="Moderado"
    )
    
    print(report)
    
    # Salvar
    output_file = WORKSPACE / "cogn3_report_formatted.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Relatório salvo em: {output_file}")

