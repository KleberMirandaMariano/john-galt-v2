#!/usr/bin/env python3
"""
Telegram Markdown Summary Generator
Gera resumo Markdown compacto das top estratégias para envio no Telegram
Uso: python3 telegram_summary_generator.py strategies.json
"""

import sys
import json
from datetime import datetime

def generate_telegram_summary(strategies_json):
    """Gera resumo Markdown formatado para Telegram"""
    
    with open(strategies_json, 'r') as f:
        data = json.load(f)
    
    ticker = data['ticker']
    spot = data['spot']
    iv_atm = data.get('iv_atm', 'N/A')
    dte = data.get('dte', 'N/A')
    strategies = data['strategies']
    
    # Mapear badges para emoji
    badge_emoji = {
        'orange': '⭐',
        'green': '🟢',
        'blue': '🔵',
        'red': '🔴',
        'purple': '🟣',
        'yellow': '🟡'
    }
    
    # Pegar top 3 estratégias (ou todas se menos de 3)
    top_strategies = strategies[:3]
    
    # Construir resumo
    summary = f"""🎮 *{ticker} Options Dashboard*

💰 Spot: ${spot:.2f}
📊 IV ATM: {iv_atm}%
⏳ DTE: {dte} dias
📅 {datetime.now().strftime('%d/%m/%Y %H:%M BRT')}

---

🎯 *TOP {len(top_strategies)} ESTRATÉGIAS:*

"""
    
    for i, strat in enumerate(top_strategies, 1):
        emoji = strat.get('emoji', '🎯')
        name = strat['name']
        type_desc = strat['type_desc']
        badge_color = strat.get('badge_color', 'blue')
        badge_text = strat.get('badge_text', '')
        badge_icon = badge_emoji.get(badge_color, '🔵')
        
        # Extrair métricas principais
        metrics = strat['metrics']
        metric1 = metrics[0]['value'] if len(metrics) > 0 else ''
        metric2 = metrics[1]['value'] if len(metrics) > 1 else ''
        metric3 = metrics[2]['value'] if len(metrics) > 2 else ''
        
        # Pegar primeira frase completa da nota (até primeiro ponto)
        note_parts = strat['note'].split('. ')
        note = note_parts[0] + '.' if note_parts else strat['note'][:100] + '...'
        # Limitar tamanho para Telegram
        if len(note) > 150:
            note = note[:147] + '...'
        
        summary += f"""*{i}. {emoji} {name}* {badge_icon} {badge_text}
_{type_desc}_

• Custo/Crédito: {metric1}
• Lucro/Perda Máx: {metric2}
• RR: {metric3}

💡 {note}

"""
    
    # Footer
    summary += f"""---

📎 *Dashboard completo anexado!*
🌐 Abra o HTML para ver todas as {len(strategies)} estratégias com detalhes completos.

⚠️ Não é recomendação de investimento
"""
    
    return summary


def main():
    if len(sys.argv) < 2:
        print("❌ Uso: python3 telegram_summary_generator.py strategies.json")
        sys.exit(1)
    
    strategies_json = sys.argv[1]
    
    try:
        summary = generate_telegram_summary(strategies_json)
        
        # Salvar resumo
        output_file = strategies_json.replace('.json', '_telegram.md')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"\n✅ Resumo Telegram gerado!")
        print(f"📁 Arquivo: {output_file}")
        print(f"\n{summary}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
