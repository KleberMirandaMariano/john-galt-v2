#!/usr/bin/env python3
"""
Exemplo de como buscar cripto de forma OTIMIZADA (2 requests, não 6+)
"""

import requests
import json
from datetime import datetime

def get_crypto_optimized():
    """Buscar BTC+ETH+SOL com apenas 2 requests"""
    
    # 1. CoinGecko - traz BTC+ETH+SOL de uma vez
    url_cg = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd,brl&include_24hr_change=true&include_market_cap=true"
    
    try:
        resp_cg = requests.get(url_cg, timeout=10)
        cripto = resp_cg.json()
    except:
        print("❌ CoinGecko falhou")
        return
    
    # 2. Fear & Greed
    url_fng = "https://api.alternative.me/fng/?limit=1"
    
    try:
        resp_fng = requests.get(url_fng, timeout=10)
        fng = resp_fng.json()['data'][0]
    except:
        fng = {"value": "N/A", "value_classification": "N/A"}
    
    # Formatar resposta
    now = datetime.now()
    
    btc = cripto['bitcoin']
    eth = cripto['ethereum']
    sol = cripto['solana']
    
    fng_emoji = "😱" if fng['value'] != "N/A" and int(fng['value']) < 25 else "😰" if fng['value'] != "N/A" and int(fng['value']) < 50 else "😐"
    
    response = f"""🪙 **CRIPTO — {now.strftime('%d/%m/%Y %H:%M')} BRT**

- **BTC:** ${btc['usd']:,.0f} (R$ {btc['brl']:,.0f}) {btc['usd_24h_change']:+.2f}% 24h
- **ETH:** ${eth['usd']:,.2f} (R$ {eth['brl']:,.0f}) {eth['usd_24h_change']:+.2f}% 24h
- **SOL:** ${sol['usd']:,.2f} (R$ {sol['brl']:,.0f}) {sol['usd_24h_change']:+.2f}% 24h

{fng_emoji} **Fear & Greed:** {fng['value']} ({fng['value_classification']})

---
**Total de requests:** 2 (CoinGecko + FNG)
"""
    
    return response

if __name__ == "__main__":
    print(get_crypto_optimized())

