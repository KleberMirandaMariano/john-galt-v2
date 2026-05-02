#!/usr/bin/env python3
"""
Análise de Correlação BTC vs S&P 500
Uso: python3 btc_spx_correlation.py [dias]
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
    print(f"📊 CORRELAÇÃO BTC vs S&P 500 - {days} dias")
    print(f"{'='*80}\n")
    
    # Buscar dados
    print("🔍 Buscando dados...")
    btc_data = yf.Ticker('BTC-USD').history(start=start_date, end=end_date)
    spx_data = yf.Ticker('^GSPC').history(start=start_date, end=end_date)
    
    print(f"✅ BTC: {len(btc_data)} dias")
    print(f"✅ S&P 500: {len(spx_data)} dias")
    
    # Normalizar timezone
    btc_data.index = btc_data.index.tz_convert('UTC').tz_localize(None).normalize()
    spx_data.index = spx_data.index.tz_convert('UTC').tz_localize(None).normalize()
    
    df = pd.DataFrame({
        'BTC': btc_data['Close'],
        'SPX': spx_data['Close']
    }).dropna()
    
    print(f"📊 Alinhados: {len(df)} dias\n")
    
    if len(df) < 30:
        print("❌ Dados insuficientes")
        sys.exit(1)
    
    # Retornos e correlação
    returns = df.pct_change().dropna()
    corr = returns['BTC'].corr(returns['SPX'])
    
    # Stats BTC
    btc_now = df['BTC'].iloc[-1]
    btc_chg = ((btc_now / df['BTC'].iloc[0]) - 1) * 100
    btc_ret = returns['BTC'].mean() * 100
    btc_vol = returns['BTC'].std() * 100
    
    # Stats SPX
    spx_now = df['SPX'].iloc[-1]
    spx_chg = ((spx_now / df['SPX'].iloc[0]) - 1) * 100
    spx_ret = returns['SPX'].mean() * 100
    spx_vol = returns['SPX'].std() * 100
    
    print(f"{'='*80}")
    print(f"📊 PREÇOS ATUAIS")
    print(f"{'='*80}")
    print(f"💰 BTC: ${btc_now:,.2f} ({btc_chg:+.2f}%)")
    print(f"📈 S&P 500: {spx_now:,.2f} ({spx_chg:+.2f}%)\n")
    
    print(f"{'='*80}")
    print(f"📊 RETORNOS DIÁRIOS")
    print(f"{'='*80}")
    print(f"BTC: {btc_ret:+.3f}% média | {btc_vol:.3f}% vol")
    print(f"SPX: {spx_ret:+.3f}% média | {spx_vol:.3f}% vol\n")
    
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
        conclusion = "❌ BTC = RISK-ON (move com ações)"
    elif corr > 0.2:
        conclusion = "⚠️ BTC = CORRELAÇÃO MODERADA com ações"
    elif corr > -0.2:
        conclusion = "⚪ BTC = INDEPENDENTE das ações"
    elif corr > -0.5:
        conclusion = "⚠️ BTC = ALGUMA proteção contra queda de ações"
    else:
        conclusion = "✅ BTC = HEDGE contra queda de ações"
    
    print(f"\n{strength} | {direction}")
    print(f"{conclusion}\n")
    
    # Recomendações
    print(f"{'='*80}")
    print(f"💡 RECOMENDAÇÕES")
    print(f"{'='*80}")
    
    if corr > 0.5:
        print(f"⚠️ Correlação POSITIVA forte ({corr:.2f})")
        print(f"   → BTC move JUNTO com ações")
        print(f"   → Se ações caírem, BTC provavelmente cai também")
        print(f"   → NÃO use BTC como diversificação")
    elif corr > 0.2:
        print(f"🟡 Correlação POSITIVA moderada ({corr:.2f})")
        print(f"   → BTC tem ALGUMA relação com ações")
        print(f"   → Diversificação limitada")
    elif corr > -0.2:
        print(f"🟢 BTC INDEPENDENTE das ações ({corr:.2f})")
        print(f"   → BTC oferece BOA diversificação")
        print(f"   → Movimentos não estão relacionados")
    else:
        print(f"✅ BTC move INVERSO às ações ({corr:.2f})")
        print(f"   → BTC pode servir como PROTEÇÃO")
        print(f"   → Excelente para diversificação")
    
    print(f"\n📚 Fontes adicionais:")
    print(f"   • S&P 500 oficial: https://www.spglobal.com/spdji/en/indices/equity/sp-500/")
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
        "spx": {
            "level": round(spx_now, 2),
            "change_pct": round(spx_chg, 2),
            "daily_return_pct": round(spx_ret, 3),
            "daily_vol_pct": round(spx_vol, 3)
        },
        "correlation": {
            "pearson": round(corr, 4),
            "strength": strength,
            "direction": direction,
            "conclusion": conclusion
        }
    }
    
    output_file = "/tmp/btc_spx_correlation.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"💾 JSON salvo: {output_file}")

if __name__ == "__main__":
    main()
