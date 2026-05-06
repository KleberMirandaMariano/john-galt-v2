#!/usr/bin/env python3
"""
Validador de Análise Quant SOL
Valida dados da análise do John Galt contra dados reais
Uso: python3 validate_sol_analysis.py
"""

import sys
import json
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
from scipy import stats

def fetch_sol_data():
    """Busca dados atuais de Solana"""
    print("📊 BUSCANDO DADOS DE SOLANA...")
    
    # SOL-USD no YFinance
    sol = yf.Ticker("SOL-USD")
    
    # Dados históricos (90 dias para cálculos)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    hist = sol.history(start=start_date, end=end_date)
    
    # Preço atual
    current_price = float(hist['Close'].iloc[-1])
    
    # Market Cap (aproximado: preço * supply circulante ~450M SOL)
    # Nota: YFinance não tem market cap direto para cripto
    supply_estimate = 450_000_000  # Supply circulante aproximado
    market_cap = current_price * supply_estimate
    
    # Variação 24h
    price_24h_ago = float(hist['Close'].iloc[-2])
    change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
    
    # Volatilidade Histórica (30 dias, anualizada)
    returns_30d = hist['Close'].pct_change().tail(30)
    hv_30d = returns_30d.std() * np.sqrt(365) * 100
    
    # Z-Score (preço vs média 30d)
    mean_30d = hist['Close'].tail(30).mean()
    std_30d = hist['Close'].tail(30).std()
    z_score = (current_price - mean_30d) / std_30d if std_30d > 0 else 0
    
    return {
        "current_price": current_price,
        "market_cap_billions": market_cap / 1e9,
        "change_24h_pct": change_24h,
        "hv_30d_pct": hv_30d,
        "z_score": z_score,
        "timestamp": datetime.now().isoformat()
    }

def fetch_btc_data():
    """Busca dados de BTC para correlação"""
    print("🔍 BUSCANDO DADOS DE BTC...")
    
    btc = yf.Ticker("BTC-USD")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    hist = btc.history(start=start_date, end=end_date)
    
    return hist['Close']

def fetch_vix_data():
    """Busca dados de VIX para correlação"""
    print("🔍 BUSCANDO DADOS DE VIX...")
    
    vix = yf.Ticker("^VIX")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    hist = vix.history(start=start_date, end=end_date)
    
    current_vix = float(hist['Close'].iloc[-1])
    
    return hist['Close'], current_vix

def calculate_correlations(sol_prices, btc_prices, vix_prices):
    """Calcula correlações SOL vs BTC e SOL vs VIX"""
    print("📈 CALCULANDO CORRELAÇÕES...")
    
    # Criar DataFrame alinhando por data
    df = pd.DataFrame({
        'SOL': sol_prices,
        'BTC': btc_prices,
        'VIX': vix_prices
    })
    
    # Remover NaN
    df_clean = df.dropna()
    
    if len(df_clean) < 30:
        print(f"⚠️ Poucos dados para correlação ({len(df_clean)} pontos)")
        return 0.0, 0.0
    
    # Correlação Pearson
    corr_btc = df_clean['SOL'].corr(df_clean['BTC'])
    corr_vix = df_clean['SOL'].corr(df_clean['VIX'])
    
    # Verificar se há NaN (pode acontecer se variância é zero)
    if pd.isna(corr_btc):
        corr_btc = 0.0
    if pd.isna(corr_vix):
        corr_vix = 0.0
    
    return corr_btc, corr_vix

def validate_kelly_criterion(analysis_data):
    """Valida cálculo de Kelly Criterion"""
    print("🎯 VALIDANDO KELLY CRITERION...")
    
    # Dados da análise original
    p_success = 0.68
    gain_pct = 12.5
    loss_pct = 11.0
    
    b = gain_pct / loss_pct
    
    # Fórmula Kelly: f = (p*b - q) / b
    # onde q = 1 - p
    q = 1 - p_success
    kelly = (p_success * b - q) / b
    
    kelly_quarter = kelly / 4
    
    return {
        "p_success": p_success,
        "b_ratio": b,
        "kelly_full": kelly,
        "kelly_quarter": kelly_quarter,
        "kelly_percentage": kelly * 100,
        "kelly_quarter_percentage": kelly_quarter * 100
    }

def validate_analysis(analysis_claimed, actual_data):
    """Compara dados da análise com dados reais"""
    print("\n" + "="*80)
    print("🔎 VALIDAÇÃO DA ANÁLISE SOL - 02/05/2026")
    print("="*80 + "\n")
    
    # Preço
    price_diff = ((actual_data['current_price'] - analysis_claimed['price']) / analysis_claimed['price']) * 100
    price_status = "✅" if abs(price_diff) < 3 else "⚠️" if abs(price_diff) < 5 else "❌"
    
    print(f"💰 PREÇO:")
    print(f"   Análise:  ${analysis_claimed['price']:.2f}")
    print(f"   Atual:    ${actual_data['current_price']:.2f}")
    print(f"   Diferença: {price_diff:+.2f}% {price_status}")
    print()
    
    # Market Cap
    mc_diff = ((actual_data['market_cap_billions'] - analysis_claimed['market_cap']) / analysis_claimed['market_cap']) * 100
    mc_status = "✅" if abs(mc_diff) < 5 else "⚠️" if abs(mc_diff) < 10 else "❌"
    
    print(f"📊 MARKET CAP:")
    print(f"   Análise:  ${analysis_claimed['market_cap']:.1f}B")
    print(f"   Atual:    ${actual_data['market_cap_billions']:.1f}B")
    print(f"   Diferença: {mc_diff:+.2f}% {mc_status}")
    print()
    
    # Variação 24h
    print(f"📈 VARIAÇÃO 24H:")
    print(f"   Análise:  {analysis_claimed['change_24h']:+.2f}%")
    print(f"   Atual:    {actual_data['change_24h_pct']:+.2f}%")
    print()
    
    # Volatilidade
    hv_diff = abs(actual_data['hv_30d_pct'] - analysis_claimed['hv_30d'])
    hv_status = "✅" if hv_diff < 5 else "⚠️" if hv_diff < 10 else "❌"
    
    print(f"📊 VOLATILIDADE HISTÓRICA (30d):")
    print(f"   Análise:  {analysis_claimed['hv_30d']:.1f}%")
    print(f"   Atual:    {actual_data['hv_30d_pct']:.1f}%")
    print(f"   Diferença: {hv_diff:.1f}pp {hv_status}")
    print()
    
    # Z-Score
    z_diff = abs(actual_data['z_score'] - analysis_claimed['z_score'])
    z_status = "✅" if z_diff < 0.3 else "⚠️" if z_diff < 0.5 else "❌"
    
    print(f"📉 Z-SCORE:")
    print(f"   Análise:  {analysis_claimed['z_score']:.2f}")
    print(f"   Atual:    {actual_data['z_score']:.2f}")
    print(f"   Diferença: {z_diff:.2f} {z_status}")
    print()
    
    return price_diff, mc_diff, hv_diff, z_diff

def main():
    print("\n" + "="*80)
    print("🔬 VALIDADOR DE ANÁLISE QUANT - SOLANA (SOL)")
    print("="*80 + "\n")
    
    # Dados da análise original (02/05/2026 00:45)
    analysis_claimed = {
        "price": 84.20,
        "market_cap": 48.9,
        "change_24h": 0.47,
        "hv_30d": 38.0,
        "z_score": -1.1,
        "fear_greed": 26,
        "corr_btc": 0.92,
        "corr_vix": -0.68,
        "iv_deribit": 45.0,
        "iv_hv_ratio": 0.84,
        "funding_rate": 0.025
    }
    
    # Buscar dados atuais
    sol_data = fetch_sol_data()
    
    # Buscar BTC e VIX para correlações
    btc_prices = fetch_btc_data()
    vix_prices, current_vix = fetch_vix_data()
    
    # Buscar SOL histórico para correlação
    sol = yf.Ticker("SOL-USD")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    sol_hist = sol.history(start=start_date, end=end_date)
    sol_prices = sol_hist['Close']
    
    # Calcular correlações
    corr_btc, corr_vix = calculate_correlations(sol_prices, btc_prices, vix_prices)
    
    # Validar análise
    price_diff, mc_diff, hv_diff, z_diff = validate_analysis(analysis_claimed, sol_data)
    
    # Correlações
    print(f"🔗 CORRELAÇÕES:")
    print(f"   SOL vs BTC:")
    print(f"      Análise:  {analysis_claimed['corr_btc']:+.2f}")
    print(f"      Atual:    {corr_btc:+.2f}")
    corr_btc_diff = abs(corr_btc - analysis_claimed['corr_btc'])
    corr_btc_status = "✅" if corr_btc_diff < 0.1 else "⚠️" if corr_btc_diff < 0.2 else "❌"
    print(f"      Diferença: {corr_btc_diff:.2f} {corr_btc_status}")
    print()
    
    print(f"   SOL vs VIX:")
    print(f"      Análise:  {analysis_claimed['corr_vix']:+.2f}")
    print(f"      Atual:    {corr_vix:+.2f}")
    corr_vix_diff = abs(corr_vix - analysis_claimed['corr_vix'])
    corr_vix_status = "✅" if corr_vix_diff < 0.1 else "⚠️" if corr_vix_diff < 0.2 else "❌"
    print(f"      Diferença: {corr_vix_diff:.2f} {corr_vix_status}")
    print()
    
    # VIX atual
    print(f"📊 VIX ATUAL: {current_vix:.2f}")
    print()
    
    # Validar Kelly Criterion
    kelly_data = validate_kelly_criterion(analysis_claimed)
    
    print(f"🎯 KELLY CRITERION:")
    print(f"   P(Sucesso): {kelly_data['p_success']:.0%}")
    print(f"   Ratio b: {kelly_data['b_ratio']:.3f}")
    print(f"   Kelly Full: {kelly_data['kelly_percentage']:.2f}%")
    print(f"   Kelly 1/4: {kelly_data['kelly_quarter_percentage']:.2f}%")
    
    # Verificar se o cálculo está correto
    kelly_claimed = 0.41  # 41% da análise
    kelly_actual = kelly_data['kelly_full']
    kelly_diff = abs(kelly_actual - kelly_claimed)
    kelly_status = "✅" if kelly_diff < 0.01 else "⚠️" if kelly_diff < 0.05 else "❌"
    
    print(f"\n   Análise: {kelly_claimed:.2f} ({kelly_claimed*100:.0f}%)")
    print(f"   Calculado: {kelly_actual:.2f} ({kelly_actual*100:.0f}%)")
    print(f"   Status: {kelly_status}")
    print()
    
    # Resumo final
    print("="*80)
    print("📋 RESUMO DA VALIDAÇÃO")
    print("="*80)
    print()
    
    validations = []
    
    if abs(price_diff) < 3:
        print("✅ Preço: VALIDADO")
        validations.append(True)
    else:
        print(f"⚠️ Preço: ATENÇÃO (diferença {price_diff:+.2f}%)")
        validations.append(False)
    
    if abs(mc_diff) < 5:
        print("✅ Market Cap: VALIDADO")
        validations.append(True)
    else:
        print(f"⚠️ Market Cap: ATENÇÃO (diferença {mc_diff:+.2f}%)")
        validations.append(False)
    
    if hv_diff < 5:
        print("✅ Volatilidade Histórica: VALIDADA")
        validations.append(True)
    else:
        print(f"⚠️ Volatilidade: ATENÇÃO (diferença {hv_diff:.1f}pp)")
        validations.append(False)
    
    if z_diff < 0.3:
        print("✅ Z-Score: VALIDADO")
        validations.append(True)
    else:
        print(f"⚠️ Z-Score: ATENÇÃO (diferença {z_diff:.2f})")
        validations.append(False)
    
    if corr_btc_diff < 0.1:
        print("✅ Correlação BTC: VALIDADA")
        validations.append(True)
    else:
        print(f"⚠️ Correlação BTC: ATENÇÃO (diferença {corr_btc_diff:.2f})")
        validations.append(False)
    
    if corr_vix_diff < 0.1:
        print("✅ Correlação VIX: VALIDADA")
        validations.append(True)
    else:
        print(f"⚠️ Correlação VIX: ATENÇÃO (diferença {corr_vix_diff:.2f})")
        validations.append(False)
    
    if kelly_diff < 0.01:
        print("✅ Kelly Criterion: CÁLCULO CORRETO")
        validations.append(True)
    else:
        print(f"⚠️ Kelly Criterion: VERIFICAR (diferença {kelly_diff:.2f})")
        validations.append(False)
    
    print()
    
    # Score final
    score = sum(validations) / len(validations) * 100
    
    print("="*80)
    if score >= 90:
        print(f"🏆 ANÁLISE VALIDADA: {score:.0f}% DE ACURÁCIA")
        print("✅ Os dados da análise estão CORRETOS!")
    elif score >= 70:
        print(f"⚠️ ANÁLISE PARCIALMENTE VALIDADA: {score:.0f}% DE ACURÁCIA")
        print("🔍 Alguns dados precisam de revisão")
    else:
        print(f"❌ ANÁLISE COM PROBLEMAS: {score:.0f}% DE ACURÁCIA")
        print("🔴 Múltiplos dados incorretos detectados")
    print("="*80 + "\n")
    
    # Salvar JSON
    output = {
        "validation_date": datetime.now().isoformat(),
        "analysis_date": "2026-05-02T00:45:00-03:00",
        "claimed_data": analysis_claimed,
        "actual_data": {
            **sol_data,
            "corr_btc": round(corr_btc, 4),
            "corr_vix": round(corr_vix, 4),
            "vix_current": round(current_vix, 2)
        },
        "kelly_validation": kelly_data,
        "accuracy_score": round(score, 2),
        "validations": {
            "price": abs(price_diff) < 3,
            "market_cap": abs(mc_diff) < 5,
            "volatility": hv_diff < 5,
            "z_score": z_diff < 0.3,
            "corr_btc": corr_btc_diff < 0.1,
            "corr_vix": corr_vix_diff < 0.1,
            "kelly": kelly_diff < 0.01
        }
    }
    
    output_file = f"/tmp/validate_sol_analysis_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Relatório salvo em: {output_file}\n")

if __name__ == "__main__":
    main()
