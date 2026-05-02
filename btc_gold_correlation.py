#!/usr/bin/env python3
"""
Análise de Correlação BTC vs Gold
Uso: python3 btc_gold_correlation.py [dias]
Default: 90 dias
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sys

def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 90
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    print(f"\n{'='*80}")
    print(f"📊 CORRELAÇÃO BTC vs GOLD - {days} dias")
    print(f"{'='*80}\n")
    
    # Buscar dados
    print("🔍 Buscando dados...")
    btc_data = yf.Ticker('BTC-USD').history(start=start_date, end=end_date)
    gold_data = yf.Ticker('GC=F').history(start=start_date, end=end_date)
    
    print(f"✅ BTC: {len(btc_data)} dias")
    print(f"✅ Gold: {len(gold_data)} dias")
    
    # Normalizar timezone
    btc_data.index = btc_data.index.tz_convert('UTC').tz_localize(None).normalize()
    gold_data.index = gold_data.index.tz_convert('UTC').tz_localize(None).normalize()
    
    df = pd.DataFrame({
        'BTC': btc_data['Close'],
        'GOLD': gold_data['Close']
    }).dropna()
    
    print(f"📊 Alinhados: {len(df)} dias\n")
    
    if len(df) < 30:
        print("❌ Dados insuficientes")
        sys.exit(1)
    
    # Retornos e correlação
    returns = df.pct_change().dropna()
    corr = returns['BTC'].corr(returns['GOLD'])
    
    # Stats BTC
    btc_now = df['BTC'].iloc[-1]
    btc_chg = ((btc_now / df['BTC'].iloc[0]) - 1) * 100
    btc_ret = returns['BTC'].mean() * 100
    btc_vol = returns['BTC'].std() * 100
    
    # Stats Gold
    gold_now = df['GOLD'].iloc[-1]
    gold_chg = ((gold_now / df['GOLD'].iloc[0]) - 1) * 100
    gold_ret = returns['GOLD'].mean() * 100
    gold_vol = returns['GOLD'].std() * 100
    
    print(f"{'='*80}")
    print(f"📊 PREÇOS ATUAIS")
    print(f"{'='*80}")
    print(f"💰 BTC: ${btc_now:,.2f} ({btc_chg:+.2f}%)")
    print(f"🪙 Gold: ${gold_now:,.2f}/oz ({gold_chg:+.2f}%)\n")
    
    print(f"{'='*80}")
    print(f"📊 RETORNOS DIÁRIOS")
    print(f"{'='*80}")
    print(f"BTC:  {btc_ret:+.3f}% média | {btc_vol:.3f}% vol")
    print(f"Gold: {gold_ret:+.3f}% média | {gold_vol:.3f}% vol\n")
    
    print(f"{'='*80}")
    print(f"🎯 CORRELAÇÃO")
    print(f"{'='*80}")
    print(f"📊 Pearson: {corr:.4f}")
    
    # Interpretação
    abs_corr = abs(corr)
    if abs_corr < 0.2:
        strength = "🟢 MUITO FRACA"
    elif abs_corr < 0.4:
        strength = "🟡 FRACA"
    elif abs_corr < 0.6:
        strength = "🟠 MODERADA"
    elif abs_corr < 0.8:
        strength = "🔴 FORTE"
    else:
        strength = "🔴🔴 MUITO FORTE"
    
    direction = "📈 POSITIVA" if corr > 0 else "📉 NEGATIVA"
    
    if corr > 0.5:
        conclusion = "✅ BTC = OURO DIGITAL (forte correlação com ouro)"
    elif corr > 0.2:
        conclusion = "⚠️ BTC = ALGUMA semelhança com ouro"
    elif corr > -0.2:
        conclusion = "⚪ BTC = INDEPENDENTE do ouro"
    elif corr > -0.5:
        conclusion = "⚠️ BTC = MOVIMENTO contrário ao ouro"
    else:
        conclusion = "❌ BTC = ANTI-OURO (correlação negativa forte)"
    
    print(f"\n{strength} | {direction}")
    print(f"{conclusion}\n")
    
    # Comparação de volatilidade
    vol_ratio = btc_vol / gold_vol if gold_vol > 0 else 0
    
    print(f"{'='*80}")
    print(f"💡 ANÁLISE COMPARATIVA")
    print(f"{'='*80}")
    print(f"Volatilidade BTC vs Gold: {vol_ratio:.1f}x")
    print(f"→ BTC é {vol_ratio:.1f}x mais volátil que ouro\n")
    
    # Recomendações
    print(f"{'='*80}")
    print(f"💡 RECOMENDAÇÕES")
    print(f"{'='*80}")
    
    if corr > 0.5:
        print(f"✅ Correlação POSITIVA forte ({corr:.2f})")
        print(f"   → BTC funcionando como 'ouro digital'")
        print(f"   → Ambos servem como store of value")
        print(f"   → Podem substituir um ao outro em portfólio")
        print(f"   → Diversificação limitada entre BTC e ouro")
    elif corr > 0.2:
        print(f"🟡 Correlação POSITIVA moderada ({corr:.2f})")
        print(f"   → BTC tem ALGUMA semelhança com ouro")
        print(f"   → Diversificação moderada")
    elif corr > -0.2:
        print(f"🟢 BTC INDEPENDENTE do ouro ({corr:.2f})")
        print(f"   → Movimentos não relacionados")
        print(f"   → EXCELENTE para diversificação")
        print(f"   → Combine ambos no portfólio")
    else:
        print(f"⚠️ Correlação NEGATIVA ({corr:.2f})")
        print(f"   → BTC move INVERSO ao ouro")
        print(f"   → Hedge natural um do outro")
        print(f"   → Situação atípica de mercado")
    
    print(f"\n💡 Narrativa atual:")
    if corr > 0.3:
        print(f"   → 'BTC = Ouro Digital' narrativa ATIVA")
    elif corr < -0.3:
        print(f"   → 'BTC = Risk-On' narrativa DOMINANTE (ouro = safe haven)")
    else:
        print(f"   → Narrativa INDEFINIDA - BTC procurando identidade")
    
    print(f"\n📚 Fontes adicionais:")
    print(f"   • Gold prices: https://www.kitco.com/")
    print(f"   • TradingView: https://www.tradingview.com/symbols/XAUUSD/")
    print(f"\n{'='*80}\n")
    
    # JSON output
    result = {
        "timestamp": datetime.now().isoformat(),
        "period_days": days,
        "data_points": len(df),
        "btc": {
            "price": round(btc_now, 2),
            "change_pct": round(btc_chg, 2),
            "daily_return_pct": round(btc_ret, 3),
            "daily_vol_pct": round(btc_vol, 3)
        },
        "gold": {
            "price_per_oz": round(gold_now, 2),
            "change_pct": round(gold_chg, 2),
            "daily_return_pct": round(gold_ret, 3),
            "daily_vol_pct": round(gold_vol, 3)
        },
        "correlation": {
            "pearson": round(corr, 4),
            "strength": strength,
            "direction": direction,
            "conclusion": conclusion
        },
        "volatility_ratio": round(vol_ratio, 2)
    }
    
    output_file = "/tmp/btc_gold_correlation.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"💾 JSON salvo: {output_file}")

if __name__ == "__main__":
    main()
