#!/usr/bin/env python3
"""
Exemplo: Buscar USD/BRL das fontes corretas
"""

import requests
from datetime import datetime

def get_usdbrl_bcb_sgs():
    """Método 1: BCB SGS Série 1 (PTAX - mais confiável)"""
    try:
        resp = requests.get("https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados/ultimos/1?formato=json", timeout=10)
        data = resp.json()
        if data and len(data) > 0:
            return {
                "fonte": "BCB SGS (Série 1 - PTAX)",
                "valor": float(data[0]['valor']),
                "data": data[0]['data'],
                "oficial": True
            }
        return None
    except Exception as e:
        print(f"⚠️ BCB SGS falhou: {e}")
        return None

def get_usdbrl_awesomeapi():
    """Método 2: AwesomeAPI (tempo real - pode ter rate limit)"""
    try:
        resp = requests.get("https://economia.awesomeapi.com.br/json/last/USD-BRL", timeout=10)
        data = resp.json()
        return {
            "fonte": "AwesomeAPI",
            "bid": float(data['USDBRL']['bid']),
            "ask": float(data['USDBRL']['ask']),
            "high": float(data['USDBRL']['high']),
            "low": float(data['USDBRL']['low']),
            "timestamp": data['USDBRL']['create_date']
        }
    except Exception as e:
        print(f"❌ AwesomeAPI falhou: {e}")
        return None

def get_usdbrl_bcb_odata():
    """Método 3: Banco Central OData (oficial PTAX - endpoint alternativo)"""
    try:
        data_hoje = datetime.now().strftime('%m-%d-%Y')
        url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao='{data_hoje}'&$format=json"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return {
            "fonte": "BCB PTAX",
            "compra": data['value'][0]['cotacaoCompra'],
            "venda": data['value'][0]['cotacaoVenda'],
            "data": data['value'][0]['dataHoraCotacao']
        }
    except Exception as e:
        print(f"⚠️ BCB falhou (pode ser fim de semana): {e}")
        return None

def get_usdbrl_coingecko():
    """Método 3: CoinGecko USDT (fallback)"""
    try:
        resp = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=brl", timeout=10)
        data = resp.json()
        return {
            "fonte": "CoinGecko (USDT)",
            "brl": data['tether']['brl']
        }
    except Exception as e:
        print(f"❌ CoinGecko falhou: {e}")
        return None

if __name__ == "__main__":
    print("💱 BUSCAR USD/BRL\n")
    
    # 1. Tentar BCB SGS primeiro (mais confiável, sem rate limit)
    bcb_sgs = get_usdbrl_bcb_sgs()
    if bcb_sgs:
        print(f"✅ {bcb_sgs['fonte']} (RECOMENDADO)")
        print(f"   PTAX: R$ {bcb_sgs['valor']:.4f}")
        print(f"   Data: {bcb_sgs['data']}\n")
    
    # 2. Tentar BCB OData (alternativo)
    bcb = get_usdbrl_bcb_odata()
    if bcb:
        print(f"✅ {bcb['fonte']} (Oficial)")
        print(f"   Compra: R$ {bcb['compra']:.4f}")
        print(f"   Venda: R$ {bcb['venda']:.4f}")
        print(f"   Data: {bcb['data']}\n")
    
    # 3. Tentar AwesomeAPI (pode ter rate limit)
    awesome = get_usdbrl_awesomeapi()
    if awesome:
        print(f"⚠️ {awesome['fonte']} (Pode ter rate limit 429)")
        print(f"   Compra: R$ {awesome['bid']:.4f}")
        print(f"   Venda: R$ {awesome['ask']:.4f}")
        print(f"   Máxima: R$ {awesome['high']:.4f}")
        print(f"   Mínima: R$ {awesome['low']:.4f}")
        print(f"   Horário: {awesome['timestamp']}\n")
    
    # 4. Fallback CoinGecko (última opção)
    if not bcb_sgs and not bcb and not awesome:
        cg = get_usdbrl_coingecko()
        if cg:
            print(f"✅ {cg['fonte']} (Fallback)")
            print(f"   BRL: R$ {cg['brl']:.4f}\n")

