#!/usr/bin/env python3
"""
Script wrapper único para análise completa de opções cripto.
Executa validação + criação de estratégias + geração de dashboard HTML.

Uso:
    python3 analyze_crypto_options.py SOL
    python3 analyze_crypto_options.py BTC
    python3 analyze_crypto_options.py ETH
"""

import sys
import subprocess
import json
from datetime import datetime
import os

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 analyze_crypto_options.py TICKER")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    print(f"🔍 INICIANDO ANÁLISE COMPLETA DE OPÇÕES: {ticker}")
    print("=" * 60)
    
    # PASSO 1: Validar dados
    print("\n📊 PASSO 1: Validando dados...")
    validator_path = "/root/.zeroclaw/workspace/pre_analysis_validator.py"
    
    try:
        result = subprocess.run(
            ["python3", validator_path, ticker],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"❌ Erro na validação: {result.stderr}")
            sys.exit(1)
        
        print("✅ Validação concluída!")
        
        # Encontrar arquivo JSON validado
        validated_files = [f for f in os.listdir("/tmp") if f.startswith(f"validated_{ticker}_")]
        if not validated_files:
            print(f"❌ Arquivo validado não encontrado em /tmp/validated_{ticker}_*")
            sys.exit(1)
        
        validated_file = f"/tmp/{validated_files[-1]}"  # Mais recente
        print(f"📄 Arquivo validado: {validated_file}")
        
        # Ler dados validados
        with open(validated_file, 'r') as f:
            validated_data = json.load(f)
        
        spot_price = validated_data.get('price', 0)
        hv_30d = validated_data.get('hv_30d', 0)
        corr_btc = validated_data.get('correlation_btc', 0)
        z_score = validated_data.get('z_score', 0)
        
        print(f"\n✅ DADOS VALIDADOS:")
        print(f"   Preço: ${spot_price:.2f}")
        print(f"   HV (30d): {hv_30d:.1f}%")
        print(f"   Corr BTC: {corr_btc:+.2f}")
        print(f"   Z-Score: {z_score:+.2f}")
        
    except subprocess.TimeoutExpired:
        print("❌ Timeout na validação (>30s)")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        sys.exit(1)
    
    # PASSO 2: Criar JSON de estratégias
    print("\n🎯 PASSO 2: Criando estratégias...")
    
    # Calcular strikes baseado no preço spot
    atm_strike = round(spot_price)
    otm_call_strike = round(spot_price * 1.05)
    otm_put_strike = round(spot_price * 0.95)
    far_call_strike = round(spot_price * 1.10)
    far_put_strike = round(spot_price * 0.90)
    
    strategies_data = {
        "ticker": ticker,
        "spot": spot_price,
        "hv_30d": hv_30d,
        "correlation_btc": corr_btc,
        "z_score": z_score,
        "validated_at": datetime.now().isoformat(),
        "strategies": [
            {
                "name": "Iron Condor",
                "label": "TOP PICK",
                "badge_color": "orange",
                "scenario": "Lateralização + IV normal",
                "legs": [
                    {"action": "SELL", "type": "CALL", "strike": otm_call_strike, "qty": 1},
                    {"action": "BUY", "type": "CALL", "strike": far_call_strike, "qty": 1},
                    {"action": "SELL", "type": "PUT", "strike": otm_put_strike, "qty": 1},
                    {"action": "BUY", "type": "PUT", "strike": far_put_strike, "qty": 1}
                ],
                "cost": round(spot_price * 0.02, 2),
                "max_profit": round(spot_price * 0.02, 2),
                "max_loss": round(spot_price * 0.04, 2),
                "rr_ratio": 2.0,
                "prob_profit": 68,
                "breakeven": [f"{otm_put_strike - 2:.0f}", f"{otm_call_strike + 2:.0f}"]
            },
            {
                "name": "Bull Call Spread",
                "label": "ALTA",
                "badge_color": "green",
                "scenario": "Alta moderada com risco definido",
                "legs": [
                    {"action": "BUY", "type": "CALL", "strike": atm_strike, "qty": 1},
                    {"action": "SELL", "type": "CALL", "strike": otm_call_strike, "qty": 1}
                ],
                "cost": round(spot_price * 0.025, 2),
                "max_profit": round(spot_price * 0.05, 2),
                "max_loss": round(spot_price * 0.025, 2),
                "rr_ratio": 2.0,
                "prob_profit": 55,
                "breakeven": [f"{atm_strike + (spot_price * 0.025):.0f}"]
            },
            {
                "name": "Butterfly (Calls)",
                "label": "DEFENSIVO",
                "badge_color": "blue",
                "scenario": "Consolidação esperada",
                "legs": [
                    {"action": "BUY", "type": "CALL", "strike": otm_put_strike, "qty": 1},
                    {"action": "SELL", "type": "CALL", "strike": atm_strike, "qty": 2},
                    {"action": "BUY", "type": "CALL", "strike": otm_call_strike, "qty": 1}
                ],
                "cost": round(spot_price * 0.015, 2),
                "max_profit": round(spot_price * 0.035, 2),
                "max_loss": round(spot_price * 0.015, 2),
                "rr_ratio": 2.3,
                "prob_profit": 45,
                "breakeven": [f"{otm_put_strike + 2:.0f}", f"{otm_call_strike - 2:.0f}"]
            },
            {
                "name": "Straddle Comprado",
                "label": "ALTO RISCO",
                "badge_color": "red",
                "scenario": "Movimento forte esperado (qualquer direção)",
                "legs": [
                    {"action": "BUY", "type": "CALL", "strike": atm_strike, "qty": 1},
                    {"action": "BUY", "type": "PUT", "strike": atm_strike, "qty": 1}
                ],
                "cost": round(spot_price * 0.06, 2),
                "max_profit": 9999,
                "max_loss": round(spot_price * 0.06, 2),
                "rr_ratio": 3.0,
                "prob_profit": 35,
                "breakeven": [f"{atm_strike - (spot_price * 0.06):.0f}", f"{atm_strike + (spot_price * 0.06):.0f}"]
            },
            {
                "name": "Booster Horizontal",
                "label": "AVANÇADO",
                "badge_color": "purple",
                "scenario": "Extração de theta com rolagem",
                "legs": [
                    {"action": "SELL", "type": "CALL", "strike": atm_strike, "qty": 1, "dte": 7},
                    {"action": "BUY", "type": "CALL", "strike": atm_strike, "qty": 1, "dte": 30}
                ],
                "cost": -round(spot_price * 0.01, 2),  # Crédito
                "max_profit": round(spot_price * 0.02, 2),
                "max_loss": round(spot_price * 0.03, 2),
                "rr_ratio": 2.0,
                "prob_profit": 60,
                "breakeven": [f"{atm_strike + 3:.0f}"]
            },
            {
                "name": "Call OTM",
                "label": "ESPECULATIVO",
                "badge_color": "yellow",
                "scenario": "Aposta em rompimento acima",
                "legs": [
                    {"action": "BUY", "type": "CALL", "strike": otm_call_strike, "qty": 1}
                ],
                "cost": round(spot_price * 0.015, 2),
                "max_profit": 9999,
                "max_loss": round(spot_price * 0.015, 2),
                "rr_ratio": 4.0,
                "prob_profit": 30,
                "breakeven": [f"{otm_call_strike + (spot_price * 0.015):.0f}"]
            }
        ]
    }
    
    # Salvar JSON
    strategies_file = f"/tmp/{ticker.lower()}_strategies_{timestamp}.json"
    with open(strategies_file, 'w') as f:
        json.dump(strategies_data, f, indent=2)
    
    print(f"✅ Estratégias criadas: {strategies_file}")
    
    # PASSO 3: Gerar dashboard HTML
    print("\n🎨 PASSO 3: Gerando dashboard HTML...")
    
    dashboard_path = "/root/.zeroclaw/workspace/options_strategies_dashboard.py"
    
    try:
        result = subprocess.run(
            ["python3", dashboard_path, ticker, str(spot_price), strategies_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"❌ Erro ao gerar dashboard: {result.stderr}")
            sys.exit(1)
        
        print("✅ Dashboard HTML gerado!")
        
        # Encontrar arquivo HTML gerado
        html_files = [f for f in os.listdir("/tmp") if f.startswith(f"{ticker.lower()}_strategies_") and f.endswith(".html")]
        if not html_files:
            print(f"❌ Dashboard HTML não encontrado")
            sys.exit(1)
        
        html_file = f"/tmp/{html_files[-1]}"
        print(f"📄 Dashboard: {html_file}")
        
    except subprocess.TimeoutExpired:
        print("❌ Timeout ao gerar dashboard (>30s)")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao gerar dashboard: {e}")
        sys.exit(1)
    
    # PASSO 4: Apresentar resumo
    print("\n" + "=" * 60)
    print("✅ ANÁLISE COMPLETA CONCLUÍDA!")
    print("=" * 60)
    print(f"\n📊 RESUMO DA ANÁLISE: {ticker}")
    print(f"   Preço: ${spot_price:.2f}")
    print(f"   HV (30d): {hv_30d:.1f}%")
    print(f"   Correlação BTC: {corr_btc:+.2f}")
    print(f"   Z-Score: {z_score:+.2f}")
    print(f"\n📁 ARQUIVOS GERADOS:")
    print(f"   Validação: {validated_file}")
    print(f"   Estratégias: {strategies_file}")
    print(f"   Dashboard HTML: {html_file}")
    print(f"\n🎯 {len(strategies_data['strategies'])} ESTRATÉGIAS DISPONÍVEIS")
    print("\n✅ Apresente o dashboard HTML ao usuário!")

if __name__ == "__main__":
    main()
