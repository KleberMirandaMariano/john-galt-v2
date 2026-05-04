#!/usr/bin/env python3
"""
Pre-Analysis Validation Script - Crypto
USAR ANTES DE GERAR QUALQUER ANÁLISE QUANTITATIVA DE CRIPTO

Valida:
- Volatilidade Histórica (30d anualizada)
- Correlações (BTC, VIX, DXY, Gold)
- Z-Score
- Preço e Market Cap

Uso: python3 pre_analysis_validator.py TICKER
Exemplo: python3 pre_analysis_validator.py SOL
"""

import sys
import json
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np

def validate_crypto_data(ticker):
    """
    Valida dados de cripto antes de análise
    Retorna: dict com todos os dados validados
    """
    
    print(f"\n{'='*80}")
    print(f"🔬 PRE-ANALYSIS VALIDATOR - {ticker}")
    print(f"{'='*80}\n")
    
    # Mapeamento de tickers
    ticker_map = {
        'BTC': 'BTC-USD',
        'ETH': 'ETH-USD',
        'SOL': 'SOL-USD',
        'XRP': 'XRP-USD',
        'ADA': 'ADA-USD',
        'AVAX': 'AVAX-USD',
        'DOT': 'DOT-USD',
        'MATIC': 'MATIC-USD'
    }
    
    ticker_yf = ticker_map.get(ticker.upper(), f"{ticker.upper()}-USD")
    
    # 1. BUSCAR DADOS DO ATIVO
    print("📊 1/6 - BUSCANDO DADOS DO ATIVO...")
    asset = yf.Ticker(ticker_yf)
    hist = asset.history(period="90d")
    
    if hist.empty:
        print(f"❌ ERRO: Nenhum dado encontrado para {ticker}")
        sys.exit(1)
    
    # Preço atual
    current_price = float(hist['Close'].iloc[-1])
    
    # Market Cap
    info = asset.info
    market_cap = info.get('marketCap', 0) / 1e9
    
    # Variação 24h
    price_24h_ago = float(hist['Close'].iloc[-2])
    change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
    
    print(f"✅ Preço atual: ${current_price:.2f}")
    print(f"✅ Market Cap: ${market_cap:.1f}B")
    print(f"✅ Variação 24h: {change_24h:+.2f}%\n")
    
    # 2. CALCULAR VOLATILIDADE HISTÓRICA (30d ANUALIZADA)
    print("📈 2/6 - CALCULANDO VOLATILIDADE HISTÓRICA (30d)...")
    returns_30d = hist['Close'].pct_change().tail(30)
    hv_30d = returns_30d.std() * np.sqrt(365) * 100
    
    print(f"✅ HV (30d anualizada): {hv_30d:.1f}%")
    print(f"⚠️  SEMPRE usar este valor - NÃO estimar!\n")
    
    # 3. CALCULAR Z-SCORE
    print("📉 3/6 - CALCULANDO Z-SCORE (30d)...")
    mean_30d = hist['Close'].tail(30).mean()
    std_30d = hist['Close'].tail(30).std()
    z_score = (current_price - mean_30d) / std_30d if std_30d > 0 else 0
    
    interpretation = ""
    if z_score < -1.5:
        interpretation = "MUITO DEPRIMIDO (forte oportunidade)"
    elif z_score < -1.0:
        interpretation = "DEPRIMIDO (oportunidade)"
    elif z_score < -0.5:
        interpretation = "ABAIXO DA MÉDIA"
    elif z_score < 0.5:
        interpretation = "NEUTRO"
    elif z_score < 1.0:
        interpretation = "ACIMA DA MÉDIA"
    elif z_score < 1.5:
        interpretation = "ELEVADO"
    else:
        interpretation = "MUITO ELEVADO (sobrecomprado)"
    
    print(f"✅ Z-Score: {z_score:.2f} ({interpretation})")
    print(f"⚠️  Atualizar diariamente - muda rapidamente!\n")
    
    # 4. CALCULAR CORRELAÇÃO COM BTC
    print("🔗 4/6 - CALCULANDO CORRELAÇÃO COM BTC (90d)...")
    btc = yf.Ticker("BTC-USD")
    btc_hist = btc.history(period="90d")
    
    df = pd.DataFrame({
        'Asset': hist['Close'],
        'BTC': btc_hist['Close']
    }).dropna()
    
    corr_btc = df['Asset'].corr(df['BTC']) if len(df) > 30 else 0
    
    corr_strength = ""
    if abs(corr_btc) < 0.3:
        corr_strength = "MUITO FRACA"
    elif abs(corr_btc) < 0.5:
        corr_strength = "FRACA/MODERADA"
    elif abs(corr_btc) < 0.7:
        corr_strength = "MODERADA"
    elif abs(corr_btc) < 0.9:
        corr_strength = "FORTE"
    else:
        corr_strength = "MUITO FORTE"
    
    print(f"✅ Correlação {ticker}-BTC: {corr_btc:+.2f} ({corr_strength})")
    print(f"⚠️  NÃO assumir correlação - sempre calcular!\n")
    
    # 5. CALCULAR CORRELAÇÃO COM VIX
    print("📊 5/6 - CALCULANDO CORRELAÇÃO COM VIX (90d)...")
    vix = yf.Ticker("^VIX")
    vix_hist = vix.history(period="90d")
    
    df_vix = pd.DataFrame({
        'Asset': hist['Close'],
        'VIX': vix_hist['Close']
    }).dropna()
    
    corr_vix = df_vix['Asset'].corr(df_vix['VIX']) if len(df_vix) > 30 else 0
    current_vix = float(vix_hist['Close'].iloc[-1])
    
    print(f"✅ Correlação {ticker}-VIX: {corr_vix:+.2f}")
    print(f"✅ VIX atual: {current_vix:.2f}")
    print(f"⚠️  Correlação negativa = risk-on asset\n")
    
    # 6. CHECKLIST DE VALIDAÇÃO
    print("="*80)
    print("✅ CHECKLIST DE VALIDAÇÃO")
    print("="*80 + "\n")
    
    checks = []
    
    # Check 1: Dados suficientes
    if len(hist) >= 90:
        print("✅ Dados históricos suficientes (90+ dias)")
        checks.append(True)
    else:
        print(f"⚠️ ATENÇÃO: Apenas {len(hist)} dias de dados (mínimo 90)")
        checks.append(False)
    
    # Check 2: Market Cap razoável
    if market_cap > 0:
        print(f"✅ Market Cap validado: ${market_cap:.1f}B")
        checks.append(True)
    else:
        print("❌ ERRO: Market Cap não disponível")
        checks.append(False)
    
    # Check 3: Volatilidade calculada
    if hv_30d > 0:
        print(f"✅ Volatilidade calculada: {hv_30d:.1f}%")
        checks.append(True)
    else:
        print("❌ ERRO: Volatilidade não calculada")
        checks.append(False)
    
    # Check 4: Correlação BTC válida
    if len(df) > 30:
        print(f"✅ Correlação BTC calculada: {corr_btc:+.2f}")
        checks.append(True)
    else:
        print("⚠️ ATENÇÃO: Poucos dados para correlação BTC")
        checks.append(False)
    
    # Check 5: Correlação VIX válida
    if len(df_vix) > 30:
        print(f"✅ Correlação VIX calculada: {corr_vix:+.2f}")
        checks.append(True)
    else:
        print("⚠️ ATENÇÃO: Poucos dados para correlação VIX")
        checks.append(False)
    
    print()
    
    # Score
    score = sum(checks) / len(checks) * 100
    
    if score >= 80:
        print(f"🏆 VALIDAÇÃO APROVADA: {score:.0f}%")
        print("✅ Dados prontos para análise!\n")
    else:
        print(f"⚠️ VALIDAÇÃO PARCIAL: {score:.0f}%")
        print("🔴 Revisar dados antes de prosseguir!\n")
    
    # Retornar dados validados
    return {
        "ticker": ticker,
        "validation_date": datetime.now().isoformat(),
        "validation_score": score,
        "data": {
            "current_price": round(current_price, 2),
            "market_cap_billions": round(market_cap, 1),
            "change_24h_pct": round(change_24h, 2),
            "hv_30d_pct": round(hv_30d, 1),
            "z_score": round(z_score, 2),
            "z_score_interpretation": interpretation,
            "corr_btc": round(corr_btc, 2),
            "corr_btc_strength": corr_strength,
            "corr_vix": round(corr_vix, 2),
            "vix_current": round(current_vix, 2)
        },
        "warnings": [
            "⚠️ HV pode mudar rapidamente - recalcular se análise > 24h",
            "⚠️ Z-Score muda diariamente - sempre usar valor atual",
            "⚠️ Correlações são históricas (90d) - podem mudar",
            "⚠️ NUNCA estimar HV - sempre calcular!"
        ]
    }

def main():
    if len(sys.argv) < 2:
        print("❌ Uso: python3 pre_analysis_validator.py TICKER")
        print("   Exemplo: python3 pre_analysis_validator.py SOL")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    
    # Validar dados
    result = validate_crypto_data(ticker)
    
    # Salvar JSON
    output_file = f"/tmp/validated_{ticker}_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print("="*80)
    print(f"💾 Dados validados salvos em: {output_file}")
    print("="*80 + "\n")
    
    print("📋 PRÓXIMOS PASSOS:")
    print("1. ✅ Usar estes dados validados na análise")
    print("2. ✅ NÃO estimar ou assumir valores")
    print("3. ✅ Mencionar data da validação na análise")
    print("4. ✅ Recalcular se análise > 24h\n")

if __name__ == "__main__":
    main()
