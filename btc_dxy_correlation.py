#!/usr/bin/env python3
"""
Análise de Correlação BTC vs DXY (Dollar Index)
Uso: python3 btc_dxy_correlation.py [dias]
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
    print(f"📊 CORRELAÇÃO BTC vs DXY - {days} dias")
    print(f"{'='*80}\n")
    
    # Buscar dados
    print("🔍 Buscando dados...")
    btc_data = yf.Ticker('BTC-USD').history(start=start_date, end=end_date)
    dxy_data = yf.Ticker('DX-Y.NYB').history(start=start_date, end=end_date)
    
    print(f"✅ BTC: {len(btc_data)} dias")
    print(f"✅ DXY: {len(dxy_data)} dias")
    
    # Normalizar timezone
    btc_data.index = btc_data.index.tz_convert('UTC').tz_localize(None).normalize()
    dxy_data.index = dxy_data.index.tz_convert('UTC').tz_localize(None).normalize()
    
    df = pd.DataFrame({
        'BTC': btc_data['Close'],
        'DXY': dxy_data['Close']
    }).dropna()
    
    print(f"📊 Alinhados: {len(df)} dias\n")
    
    if len(df) < 30:
        print("❌ Dados insuficientes")
        sys.exit(1)
    
    # Retornos e correlação
    returns = df.pct_change().dropna()
    corr = returns['BTC'].corr(returns['DXY'])
    
    # Stats BTC
    btc_now = df['BTC'].iloc[-1]
    btc_chg = ((btc_now / df['BTC'].iloc[0]) - 1) * 100
    btc_ret = returns['BTC'].mean() * 100
    btc_vol = returns['BTC'].std() * 100
    
    # Stats DXY
    dxy_now = df['DXY'].iloc[-1]
    dxy_chg = ((dxy_now / df['DXY'].iloc[0]) - 1) * 100
    dxy_ret = returns['DXY'].mean() * 100
    dxy_vol = returns['DXY'].std() * 100
    
    print(f"{'='*80}")
    print(f"📊 PREÇOS ATUAIS")
    print(f"{'='*80}")
    print(f"💰 BTC: ${btc_now:,.2f} ({btc_chg:+.2f}%)")
    print(f"💵 DXY: {dxy_now:.2f} ({dxy_chg:+.2f}%)\n")
    
    print(f"{'='*80}")
    print(f"📊 RETORNOS DIÁRIOS")
    print(f"{'='*80}")
    print(f"BTC: {btc_ret:+.3f}% média | {btc_vol:.3f}% vol")
    print(f"DXY: {dxy_ret:+.3f}% média | {dxy_vol:.3f}% vol\n")
    
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
    
    if corr < -0.5:
        conclusion = "✅ BTC = ANTI-DÓLAR (forte proteção contra alta do USD)"
    elif corr < -0.2:
        conclusion = "⚠️ BTC = ALGUMA proteção contra alta do USD"
    elif corr < 0.2:
        conclusion = "⚪ BTC = INDEPENDENTE do dólar"
    elif corr < 0.5:
        conclusion = "⚠️ BTC = ALGUMA correlação com dólar"
    else:
        conclusion = "❌ BTC = PRO-DÓLAR (move junto com USD)"
    
    print(f"\n{strength} | {direction}")
    print(f"{conclusion}\n")
    
    # Recomendações
    print(f"{'='*80}")
    print(f"💡 RECOMENDAÇÕES")
    print(f"{'='*80}")
    
    if corr < -0.3:
        print(f"✅ Correlação NEGATIVA ({corr:.2f})")
        print(f"   → Dólar forte = BTC fraco (típico)")
        print(f"   → Dólar fraco = BTC forte")
        print(f"   → BTC pode servir como hedge contra USD")
    elif corr < 0.2:
        print(f"🟢 BTC INDEPENDENTE do dólar ({corr:.2f})")
        print(f"   → Movimentos não relacionados")
        print(f"   → Relação tradicional quebrada")
    else:
        print(f"⚠️ Correlação POSITIVA ({corr:.2f})")
        print(f"   → BTC move JUNTO com dólar (anormal!)")
        print(f"   → Ambos como ativos de risco/refúgio")
        print(f"   → Situação atípica de mercado")
    
    print(f"\nContexto DXY:")
    if dxy_now > 105:
        print(f"🔴 DXY forte ({dxy_now:.1f}) - Pressão sobre BTC e ativos risk-on")
    elif dxy_now > 100:
        print(f"🟡 DXY elevado ({dxy_now:.1f}) - Vento contrário para BTC")
    elif dxy_now > 95:
        print(f"🟢 DXY neutro ({dxy_now:.1f}) - Sem pressão sobre BTC")
    else:
        print(f"✅ DXY fraco ({dxy_now:.1f}) - Favorável para BTC")
    
    print(f"\n📚 Fontes adicionais:")
    print(f"   • DXY oficial: https://www.theice.com/marketdata/indices/us-dollar-index")
    print(f"   • TradingView: https://www.tradingview.com/symbols/TVC-DXY/")
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
        "dxy": {
            "level": round(dxy_now, 2),
            "change_pct": round(dxy_chg, 2),
            "daily_return_pct": round(dxy_ret, 3),
            "daily_vol_pct": round(dxy_vol, 3)
        },
        "correlation": {
            "pearson": round(corr, 4),
            "strength": strength,
            "direction": direction,
            "conclusion": conclusion
        }
    }
    
    output_file = "/tmp/btc_dxy_correlation.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"💾 JSON salvo: {output_file}")

if __name__ == "__main__":
    main()
