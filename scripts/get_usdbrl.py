#!/usr/bin/env python3
"""
Buscar USD/BRL das fontes corretas com fallback automático.
"""

import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 10


def get_usdbrl_awesomeapi():
    """Método 1: AwesomeAPI (tempo real)"""
    try:
        resp = requests.get("https://economia.awesomeapi.com.br/json/last/USD-BRL", timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
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
        logger.warning("AwesomeAPI falhou: %s", e)
        return None


def get_usdbrl_bcb():
    """Método 2: Banco Central (oficial PTAX) — só disponível em dias úteis"""
    try:
        data_hoje = datetime.now().strftime('%m-%d-%Y')
        url = (
            f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
            f"CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao='{data_hoje}'&$format=json"
        )
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        if not data.get('value'):
            logger.info("BCB sem dados para hoje (fim de semana ou feriado)")
            return None
        return {
            "fonte": "BCB PTAX",
            "compra": data['value'][0]['cotacaoCompra'],
            "venda": data['value'][0]['cotacaoVenda'],
            "data": data['value'][0]['dataHoraCotacao']
        }
    except Exception as e:
        logger.warning("BCB PTAX falhou: %s", e)
        return None


def get_usdbrl_coingecko():
    """Método 3: CoinGecko USDT/BRL (fallback — aproximação via crypto)"""
    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=brl",
            timeout=REQUEST_TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "fonte": "CoinGecko (USDT/BRL — fallback)",
            "brl": data['tether']['brl']
        }
    except Exception as e:
        logger.error("CoinGecko também falhou: %s", e)
        return None


def get_usdbrl():
    """Retorna USD/BRL da melhor fonte disponível (AwesomeAPI → BCB → CoinGecko)."""
    result = get_usdbrl_awesomeapi()
    if result:
        return result
    result = get_usdbrl_bcb()
    if result:
        return result
    return get_usdbrl_coingecko()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    print("💱 BUSCAR USD/BRL\n")

    awesome = get_usdbrl_awesomeapi()
    if awesome:
        print(f"✅ {awesome['fonte']}")
        print(f"   Compra: R$ {awesome['bid']:.4f}")
        print(f"   Venda:  R$ {awesome['ask']:.4f}")
        print(f"   Máx:    R$ {awesome['high']:.4f}")
        print(f"   Mín:    R$ {awesome['low']:.4f}")
        print(f"   Horário: {awesome['timestamp']}\n")

    bcb = get_usdbrl_bcb()
    if bcb:
        print(f"✅ {bcb['fonte']} (Oficial)")
        print(f"   Compra: R$ {bcb['compra']:.4f}")
        print(f"   Venda:  R$ {bcb['venda']:.4f}")
        print(f"   Data: {bcb['data']}\n")

    if not awesome and not bcb:
        cg = get_usdbrl_coingecko()
        if cg:
            print(f"✅ {cg['fonte']}")
            print(f"   BRL: R$ {cg['brl']:.4f}\n")
        else:
            print("❌ Todas as fontes falharam.")
