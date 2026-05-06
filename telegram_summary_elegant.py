#!/usr/bin/env python3
"""
Telegram Markdown Summary Generator - ELEGANT VERSION
Gera resumo em Markdown PREMIUM formatado para Telegram (top 3 estratégias)
Uso: python3 telegram_summary_elegant.py strategies.json
"""

import sys
import json
from datetime import datetime

def get_badge_emoji(badge_text: str) -> str:
    """Retorna emoji baseado no badge"""
    badge_map = {
        "TOP PICK": "⭐",
        "RECOMENDADO": "✅",
        "ALTO RISCO": "⚠️",
        "ESPECULATIVO": "🎲",
        "CONSERVADOR": "🛡️",
        "MODERADO": "⚖️",
        "AVANÇADO": "🎓"
    }
    return badge_map.get(badge_text, "📊")

def generate_elegant_summary(strategies_json):
    """Gera resumo ELEGANTE em Markdown para Telegram"""
    
    with open(strategies_json, 'r') as f:
        data = json.load(f)
    
    ticker = data['ticker']
    spot = data['spot']
    iv_atm = data.get('iv_atm', 'N/A')
    dte = data.get('dte', 30)
    strategies = data['strategies']
    
    now = datetime.now()
    timestamp = now.strftime("%d/%m/%Y %H:%M BRT")
    
    # Header elegante com separadores visuais
    summary = f"""╔═══════════════════════════════════╗
  {ticker} OPTIONS DASHBOARD
╚═══════════════════════════════════╝

💰 *Spot Price*
   ${spot:,.2f}

📊 *Volatilidade Implícita*
   {iv_atm}% a.a.

⏰ *Dias até Vencimento*
   {dte} dias

🕐 *Última Atualização*
   {timestamp}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    
    # Top 3 estratégias com design elegante
    top_strategies = strategies[:3]
    
    for i, strat in enumerate(top_strategies, 1):
        emoji = strat.get('emoji', '🎯')
        name = strat['name']
        type_desc = strat['type_desc']
        badge_text = strat.get('badge_text', '')
        badge_emoji = get_badge_emoji(badge_text)
        
        # Separador entre estratégias
        if i > 1:
            summary += "\n┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n\n"
        
        # Título da estratégia com box
        summary += f"╭─── ESTRATÉGIA #{i} ───────────────\n"
        summary += f"│ {emoji} *{name}*\n"
        summary += f"│ {badge_emoji} _{badge_text}_\n"
        summary += f"╰────────────────────────────────\n\n"
        
        # Tipo de estratégia
        summary += f"📋 {type_desc}\n\n"
        
        # Métricas em blocos visuais
        metrics = strat['metrics'][:3]
        summary += "📊 *MÉTRICAS PRINCIPAIS*\n\n"
        
        for metric in metrics:
            value = metric['value']
            label = metric['label']
            
            # Emoji por tipo de métrica
            if "Custo" in label or "Crédito" in label:
                m_emoji = "💵"
            elif "Lucro" in label or "Ganho" in label:
                m_emoji = "💰"
            elif "Risk" in label or "RR" in label or "Reward" in label:
                m_emoji = "⚖️"
            elif "Break" in label:
                m_emoji = "🎯"
            else:
                m_emoji = "📌"
            
            summary += f"   {m_emoji} {label}\n"
            summary += f"   `{value}`\n\n"
        
        # Insight em destaque (primeira frase)
        note = strat['note']
        first_sentence = note.split(".")[0] + "." if "." in note else note[:120] + "..."
        
        summary += f"💡 *INSIGHT*\n"
        summary += f"_{first_sentence}_\n"
    
    # Footer elegante
    summary += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📎 *ANÁLISE COMPLETA DISPONÍVEL*

🌐 Abra o arquivo HTML anexado para:
   • Ver todas as {len(strategies)} estratégias
   • Métricas detalhadas completas
   • Cálculos Black-Scholes
   • Análise de cenários

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ _Este material não constitui recomendação_
_de investimento. Consulte seu assessor._

"""
    
    return summary


def main():
    if len(sys.argv) < 2:
        print("❌ Uso: python3 telegram_summary_elegant.py strategies.json")
        sys.exit(1)
    
    strategies_json = sys.argv[1]
    
    try:
        summary = generate_elegant_summary(strategies_json)
        
        # Salvar resumo
        output_file = strategies_json.replace('.json', '_telegram_elegant.md')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"\n✅ Resumo Telegram ELEGANTE gerado!")
        print(f"📁 Arquivo: {output_file}")
        print(f"\n{summary}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
