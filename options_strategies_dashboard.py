#!/usr/bin/env python3
"""
Options Strategies Dashboard Generator
Gera quadro visual HTML com estratégias de opções
Uso: python3 options_strategies_dashboard.py TICKER SPOT [strategies_json]
"""

import sys
import json
from datetime import datetime

# Template HTML base
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{ticker} Options - Estratégias Recomendadas | {date}</title>
<style>
  :root {{
    --bg: #0d1117; --bg2: #161b22; --bg3: #21262d;
    --border: #30363d; --text: #e6edf3; --muted: #8b949e;
    --green: #3fb950; --red: #f85149; --blue: #58a6ff;
    --yellow: #d29922; --purple: #bc8cff; --orange: #ffa657;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; font-size: 13px; padding: 20px; }}

  header {{ background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 24px; }}
  .logo {{ display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }}
  .logo-icon {{ width: 40px; height: 40px; background: linear-gradient(135deg, #9945FF, #14F195);
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-weight: 900; font-size: 16px; color: #000; }}
  .logo h1 {{ font-size: 22px; font-weight: 700; }}
  .header-meta {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-top: 12px; }}
  .hm {{ background: var(--bg3); border-radius: 8px; padding: 10px; }}
  .hm .val {{ font-size: 20px; font-weight: 700; color: var(--green); }}
  .hm .lbl {{ font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: .5px; margin-top: 2px; }}

  .badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 10px; font-weight: 600; }}
  .badge-green {{ background: rgba(63,185,80,.15); color: var(--green); border: 1px solid rgba(63,185,80,.3); }}
  .badge-blue {{ background: rgba(88,166,255,.15); color: var(--blue); border: 1px solid rgba(88,166,255,.3); }}
  .badge-orange {{ background: rgba(255,166,87,.15); color: var(--orange); border: 1px solid rgba(255,166,87,.3); }}
  .badge-red {{ background: rgba(248,81,73,.15); color: var(--red); border: 1px solid rgba(248,81,73,.3); }}
  .badge-purple {{ background: rgba(188,140,255,.15); color: var(--purple); border: 1px solid rgba(188,140,255,.3); }}
  .badge-yellow {{ background: rgba(210,153,34,.15); color: var(--yellow); border: 1px solid rgba(210,153,34,.3); }}

  .section-title {{ font-size: 13px; font-weight: 600; color: var(--muted); text-transform: uppercase;
    letter-spacing: .8px; margin: 24px 0 16px 0; }}

  .strat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }}
  .strat {{ background: var(--bg2); border: 1px solid var(--border); border-radius: 12px; padding: 18px; }}
  .strat-header {{ display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 12px; }}
  .strat-name {{ font-size: 16px; font-weight: 700; }}
  .strat-type {{ font-size: 11px; color: var(--muted); margin-top: 3px; }}
  .strat-metrics {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 12px 0; }}
  .sm {{ background: var(--bg3); border-radius: 8px; padding: 10px; }}
  .sm .sv {{ font-size: 15px; font-weight: 700; }}
  .sm .sl {{ font-size: 10px; color: var(--muted); margin-top: 3px; text-transform: uppercase; letter-spacing: .5px; }}
  .strat-legs {{ margin-top: 12px; border-top: 1px solid var(--border); padding-top: 12px; }}
  .leg {{ display: flex; justify-content: space-between; padding: 4px 0; font-size: 12px; }}
  .leg-buy {{ color: var(--green); }}
  .leg-sell {{ color: var(--red); }}
  .strat-note {{ font-size: 11px; color: var(--muted); margin-top: 12px; padding-top: 12px; 
    border-top: 1px solid var(--border); line-height: 1.6; }}

  footer {{ text-align: center; padding: 20px; color: var(--muted); font-size: 11px; 
    border-top: 1px solid var(--border); margin-top: 24px; }}
</style>
</head>
<body>

<header>
  <div class="logo">
    <div class="logo-icon">{icon}</div>
    <div>
      <h1>{ticker} Options - Estratégias Recomendadas</h1>
    </div>
  </div>
  <div class="header-meta">
    <div class="hm">
      <div class="val">${spot}</div>
      <div class="lbl">Spot Atual</div>
    </div>
    <div class="hm">
      <div class="val" style="color:var(--purple)">{iv_atm}%</div>
      <div class="lbl">IV ATM</div>
    </div>
    <div class="hm">
      <div class="val" style="color:var(--blue)">{dte} dias</div>
      <div class="lbl">DTE</div>
    </div>
    <div class="hm">
      <div class="val" style="color:var(--text)">{date}</div>
      <div class="lbl">Gerado em</div>
    </div>
  </div>
</header>

<div class="section-title">🎯 Estratégias Recomendadas</div>

<div class="strat-grid">
{strategies_html}
</div>

<footer>
  Dados validados em: {timestamp}<br>
  <strong>Não é recomendação de investimento</strong> • Opções envolvem risco de perda total
</footer>

</body>
</html>"""

# Template de estratégia individual
STRATEGY_TEMPLATE = """  <div class="strat">
    <div class="strat-header">
      <div>
        <div class="strat-name">{emoji} {name}</div>
        <div class="strat-type">{type_desc}</div>
      </div>
      <span class="badge badge-{badge_color}">{badge_text}</span>
    </div>
    <div class="strat-metrics">
      <div class="sm"><div class="sv" style="color:var(--{metric1_color})">{metric1_val}</div><div class="sl">{metric1_label}</div></div>
      <div class="sm"><div class="sv" style="color:var(--{metric2_color})">{metric2_val}</div><div class="sl">{metric2_label}</div></div>
      <div class="sm"><div class="sv" style="color:var(--{metric3_color})">{metric3_val}</div><div class="sl">{metric3_label}</div></div>
      <div class="sm"><div class="sv" style="color:var(--{metric4_color})">{metric4_val}</div><div class="sl">{metric4_label}</div></div>
    </div>
    <div class="strat-legs">
{legs_html}
    </div>
    <div class="strat-note">
      💡 {note}
    </div>
  </div>"""


def generate_strategy_html(strategy):
    """Gera HTML de uma estratégia individual"""
    
    # Gerar HTML das pernas
    legs_html = ""
    for leg in strategy.get('legs', []):
        leg_class = "leg-buy" if leg['action'] == 'BUY' else "leg-sell"
        arrow = "▲" if leg['action'] == 'BUY' else "▼"
        action_text = "Compra" if leg['action'] == 'BUY' else "Vende"
        legs_html += f'      <div class="leg {leg_class}">{arrow} {action_text} {leg["strike"]}-{leg["type"]} @ ${leg["premium"]:.2f}</div>\n'
    
    return STRATEGY_TEMPLATE.format(
        emoji=strategy.get('emoji', '🎯'),
        name=strategy['name'],
        type_desc=strategy['type_desc'],
        badge_color=strategy.get('badge_color', 'blue'),
        badge_text=strategy.get('badge_text', 'ESTRATÉGIA'),
        metric1_val=strategy['metrics'][0]['value'],
        metric1_label=strategy['metrics'][0]['label'],
        metric1_color=strategy['metrics'][0].get('color', 'text'),
        metric2_val=strategy['metrics'][1]['value'],
        metric2_label=strategy['metrics'][1]['label'],
        metric2_color=strategy['metrics'][1].get('color', 'text'),
        metric3_val=strategy['metrics'][2]['value'],
        metric3_label=strategy['metrics'][2]['label'],
        metric3_color=strategy['metrics'][2].get('color', 'text'),
        metric4_val=strategy['metrics'][3]['value'],
        metric4_label=strategy['metrics'][3]['label'],
        metric4_color=strategy['metrics'][3].get('color', 'text'),
        legs_html=legs_html,
        note=strategy['note']
    )


def generate_dashboard(ticker, spot, strategies, iv_atm=50, dte=25):
    """Gera dashboard HTML completo"""
    
    # Gerar HTML de todas as estratégias
    strategies_html = "\n".join([generate_strategy_html(s) for s in strategies])
    
    # Ícone baseado no ticker
    icons = {
        'SOL': '◎',
        'BTC': '₿',
        'ETH': 'Ξ',
        'PETR4': '🛢️',
        'VALE3': '⛏️',
        'COGN3': '📚',
    }
    icon = icons.get(ticker, '📊')
    
    # Preencher template
    html = HTML_TEMPLATE.format(
        ticker=ticker,
        icon=icon,
        spot=f"{spot:.2f}",
        iv_atm=f"{iv_atm:.1f}",
        dte=dte,
        date=datetime.now().strftime('%d %b %Y'),
        strategies_html=strategies_html,
        timestamp=datetime.now().strftime('%d/%m/%Y %H:%M BRT')
    )
    
    return html


def main():
    if len(sys.argv) < 3:
        print("❌ Uso: python3 options_strategies_dashboard.py TICKER SPOT [strategies.json]")
        print("   Exemplo: python3 options_strategies_dashboard.py SOL 84.09 strategies.json")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    spot = float(sys.argv[2])
    
    # Carregar estratégias do JSON ou usar exemplo
    if len(sys.argv) > 3:
        with open(sys.argv[3], 'r') as f:
            data = json.load(f)
            strategies = data['strategies']
            iv_atm = data.get('iv_atm', 50)
            dte = data.get('dte', 25)
    else:
        # Exemplo padrão
        strategies = [
            {
                "emoji": "🦅",
                "name": "Iron Condor",
                "type_desc": "Neutro · Range-bound · Vende volatilidade",
                "badge_color": "orange",
                "badge_text": "⭐ TOP PICK",
                "metrics": [
                    {"value": "+$2.73", "label": "Crédito Recebido", "color": "green"},
                    {"value": "-$1.27", "label": "Perda Máxima", "color": "red"},
                    {"value": "2.15:1", "label": "Risk/Reward", "color": "blue"},
                    {"value": "$77-$95", "label": "Break-evens", "color": "yellow"}
                ],
                "legs": [
                    {"action": "BUY", "strike": 80, "type": "PUT", "premium": 2.56},
                    {"action": "SELL", "strike": 84, "type": "PUT", "premium": 4.27},
                    {"action": "SELL", "strike": 88, "type": "CALL", "premium": 2.79},
                    {"action": "BUY", "strike": 92, "type": "CALL", "premium": 1.77}
                ],
                "note": f"{ticker} precisa ficar entre $84 e $88 no vencimento para lucro máximo. Estrutura neutra ideal quando IV está elevada."
            },
            {
                "emoji": "🐂",
                "name": "Bull Call Spread",
                "type_desc": "Otimista moderado · Custo limitado",
                "badge_color": "green",
                "badge_text": "ALTA",
                "metrics": [
                    {"value": "-$2.17", "label": "Débito (custo)", "color": "red"},
                    {"value": "+$3.83", "label": "Lucro Máximo", "color": "green"},
                    {"value": "1.77:1", "label": "Risk/Reward", "color": "blue"},
                    {"value": "$86.17", "label": "Break-even", "color": "yellow"}
                ],
                "legs": [
                    {"action": "BUY", "strike": 84, "type": "CALL", "premium": 4.39},
                    {"action": "SELL", "strike": 90, "type": "CALL", "premium": 2.22}
                ],
                "note": f"Aposta em rally moderado. Lucro máximo se {ticker} ≥ $90 no vencimento. Risco máximo é o prêmio pago."
            },
            {
                "emoji": "🛡️",
                "name": "Bull Put Spread",
                "type_desc": "Otimista/Neutro · Vende put skew",
                "badge_color": "blue",
                "badge_text": "DEFENSIVO",
                "metrics": [
                    {"value": "+$1.71", "label": "Crédito Recebido", "color": "green"},
                    {"value": "-$2.29", "label": "Perda Máxima", "color": "red"},
                    {"value": "0.75:1", "label": "Risk/Reward", "color": "blue"},
                    {"value": "$82.29", "label": "Break-even", "color": "yellow"}
                ],
                "legs": [
                    {"action": "SELL", "strike": 84, "type": "PUT", "premium": 4.27},
                    {"action": "BUY", "strike": 80, "type": "PUT", "premium": 2.56}
                ],
                "note": f"Coleta prêmio apostando que {ticker} não cai abaixo de $84. Ideal se expectativa é lateralização ou alta leve."
            }
        ]
        iv_atm = 50
        dte = 25
    
    # Gerar HTML
    html = generate_dashboard(ticker, spot, strategies, iv_atm, dte)
    
    # Salvar arquivo
    output_file = f"/tmp/{ticker.lower()}_strategies_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ Dashboard gerado com sucesso!")
    print(f"📁 Arquivo: {output_file}")
    print(f"🌐 Abra no navegador para visualizar\n")
    
    return output_file


if __name__ == "__main__":
    main()
