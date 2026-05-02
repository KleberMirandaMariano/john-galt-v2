#!/usr/bin/env python3
"""
Análise de Correlação BTC vs VIX
Uso: python3 btc_vix_correlation.py [dias]
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
    print(f"📊 CORRELAÇÃO BTC vs VIX - {days} dias")
    print(f"{'='*80}\n")
    
    # Buscar dados
    print("🔍 Buscando dados...")
    btc_data = yf.Ticker('BTC-USD').history(start=start_date, end=end_date)
    vix_data = yf.Ticker('^VIX').history(start=start_date, end=end_date)
    
    print(f"✅ BTC: {len(btc_data)} dias")
    print(f"✅ VIX: {len(vix_data)} dias")
    
    # Normalizar timezone
    btc_data.index = btc_data.index.tz_convert('UTC').tz_localize(None).normalize()
    vix_data.index = vix_data.index.tz_convert('UTC').tz_localize(None).normalize()
    
    df = pd.DataFrame({
        'BTC': btc_data['Close'],
        'VIX': vix_data['Close']
    }).dropna()
    
    print(f"📊 Alinhados: {len(df)} dias\n")
    
    if len(df) < 30:
        print("❌ Dados insuficientes")
        sys.exit(1)
    
    # Retornos e correlação
    returns = df.pct_change().dropna()
    corr = returns['BTC'].corr(returns['VIX'])
    
    # Stats BTC
    btc_now = df['BTC'].iloc[-1]
    btc_chg = ((btc_now / df['BTC'].iloc[0]) - 1) * 100
    btc_ret = returns['BTC'].mean() * 100
    btc_vol = returns['BTC'].std() * 100
    
    # Stats VIX
    vix_now = df['VIX'].iloc[-1]
    vix_chg = ((vix_now / df['VIX'].iloc[0]) - 1) * 100
    vix_ret = returns['VIX'].mean() * 100
    vix_vol = returns['VIX'].std() * 100
    
    print(f"{'='*80}")
    print(f"📊 PREÇOS ATUAIS")
    print(f"{'='*80}")
    print(f"💰 BTC: ${btc_now:,.2f} ({btc_chg:+.2f}%)")
    print(f"📊 VIX: {vix_now:.2f} ({vix_chg:+.2f}%)\n")
    
    print(f"{'='*80}")
    print(f"📊 RETORNOS DIÁRIOS")
    print(f"{'='*80}")
    print(f"BTC: {btc_ret:+.3f}% média | {btc_vol:.3f}% vol")
    print(f"VIX: {vix_ret:+.3f}% média | {vix_vol:.3f}% vol\n")
    
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
    
    if corr < -0.3:
        conclusion = "✅ BTC = HEDGE contra volatilidade"
    elif corr < -0.1:
        conclusion = "⚠️ BTC = ALGUMA proteção"
    elif corr < 0.1:
        conclusion = "⚪ BTC = INDEPENDENTE"
    elif corr < 0.3:
        conclusion = "⚠️ BTC = ALGUMA correlação"
    else:
        conclusion = "❌ BTC = RISK-ON (move com VIX)"
    
    print(f"\n{strength} | {direction}")
    print(f"{conclusion}\n")
    
    # Recomendações
    print(f"{'='*80}")
    print(f"💡 RECOMENDAÇÕES")
    print(f"{'='*80}")
    
    if vix_now < 15:
        print(f"🟢 VIX baixo ({vix_now:.1f}) - Mercado CALMO")
        print(f"   → Ambiente favorável para BTC (se corr negativa)")
    elif vix_now < 20:
        print(f"🟡 VIX normal ({vix_now:.1f}) - Mercado NEUTRO")
        print(f"   → BTC em zona de conforto")
    elif vix_now < 30:
        print(f"🟠 VIX elevado ({vix_now:.1f}) - Mercado NERVOSO")
        print(f"   → Cautela com BTC (se corr negativa)")
    else:
        print(f"🔴 VIX alto ({vix_now:.1f}) - Mercado em PÂNICO")
        print(f"   → BTC provavelmente sob pressão")
    
    print(f"\n📚 Fontes adicionais:")
    print(f"   • CBOE VIX oficial: https://www.cboe.com/vix")
    print(f"   • TradingView overlay: https://www.tradingview.com/symbols/BTCUSD/")
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
        "vix": {
            "level": round(vix_now, 2),
            "change_pct": round(vix_chg, 2),
            "daily_return_pct": round(vix_ret, 3),
            "daily_vol_pct": round(vix_vol, 3)
        },
        "correlation": {
            "pearson": round(corr, 4),
            "strength": strength,
            "direction": direction,
            "conclusion": conclusion
        }
    }
    
    output_file = "/tmp/btc_vix_correlation.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"💾 JSON salvo: {output_file}")

if __name__ == "__main__":
    main()
