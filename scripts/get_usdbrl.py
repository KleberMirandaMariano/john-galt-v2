#!/usr/bin/env python3
"""
Exemplo: Buscar USD/BRL das fontes corretas
"""

import requests
from datetime import datetime

def get_usdbrl_awesomeapi():
    """Método 1: AwesomeAPI (tempo real)"""
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

def get_usdbrl_bcb():
    """Método 2: Banco Central (oficial PTAX)"""
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
    
    # Tentar AwesomeAPI primeiro
    awesome = get_usdbrl_awesomeapi()
    if awesome:
        print(f"✅ {awesome['fonte']}")
        print(f"   Compra: R$ {awesome['bid']:.4f}")
        print(f"   Venda: R$ {awesome['ask']:.4f}")
        print(f"   Máxima: R$ {awesome['high']:.4f}")
        print(f"   Mínima: R$ {awesome['low']:.4f}")
        print(f"   Horário: {awesome['timestamp']}\n")
    
    # Tentar BCB
    bcb = get_usdbrl_bcb()
    if bcb:
        print(f"✅ {bcb['fonte']} (Oficial)")
        print(f"   Compra: R$ {bcb['compra']:.4f}")
        print(f"   Venda: R$ {bcb['venda']:.4f}")
        print(f"   Data: {bcb['data']}\n")
    
    # Fallback CoinGecko
    if not awesome and not bcb:
        cg = get_usdbrl_coingecko()
        if cg:
            print(f"✅ {cg['fonte']} (Fallback)")
            print(f"   BRL: R$ {cg['brl']:.4f}\n")

