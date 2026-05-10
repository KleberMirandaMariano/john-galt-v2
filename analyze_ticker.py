#!/usr/bin/env python3
"""
analyze_ticker.py — Análise quantitativa completa via APIs públicas
Salva output em /root/.zeroclaw/workspace/{ticker}_output.txt
John Galt lê o arquivo com file_read após execução.

Uso:
  python3 analyze_ticker.py COGN3
  python3 analyze_ticker.py PETR4
  python3 analyze_ticker.py SOL
  python3 analyze_ticker.py BTC
"""

import sys
import json
import math
import requests
from datetime import datetime

BRAPI_TOKEN = "tP2QrzuthuXx4JjrnBqnkd"
OUTPUT_DIR = "/root/.zeroclaw/workspace"

def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def norm_pdf(x):
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)

def black_scholes(S, K, T, r, sigma, tipo="CALL"):
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return None, {}
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if tipo == "CALL":
        price = S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
        delta = norm_cdf(d1)
    else:
        price = K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)
        delta = norm_cdf(d1) - 1
    gamma = norm_pdf(d1) / (S * sigma * math.sqrt(T))
    vega  = S * norm_pdf(d1) * math.sqrt(T) / 100
    theta = -(S * norm_pdf(d1) * sigma) / (2 * math.sqrt(T)) / 365
    greeks = {"delta": round(delta, 4), "gamma": round(gamma, 6),
              "vega": round(vega, 4), "theta": round(theta, 4)}
    return round(price, 4), greeks

def kelly(p, ganho, perda):
    if perda == 0:
        return 0, 0
    b = ganho / perda
    q = 1 - p
    f = max(0, (p * b - q) / b)
    return round(f, 4), round(f / 4, 4)

def graham(lpa, vpa):
    if lpa > 0 and vpa > 0:
        return round(math.sqrt(22.5 * lpa * vpa), 2)
    return None

def fetch_b3(ticker):
    url = f"https://brapi.dev/api/quote/{ticker}?token={BRAPI_TOKEN}&fundamental=true&history=false"
    try:
        r = requests.get(url, timeout=15)
        data = r.json()
        if "results" in data and len(data["results"]) > 0:
            return data["results"][0]
    except Exception as e:
        print(f"  ⚠️  Erro BRAPI: {e}")
    return None

def fetch_selic():
    url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json"
    try:
        r = requests.get(url, timeout=10)
        return float(r.json()[0]["valor"].replace(",", "."))
    except:
        return 13.75

def fetch_usdbrl():
    url = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
    try:
        r = requests.get(url, timeout=10)
        return float(r.json()["USDBRL"]["bid"])
    except:
        return None

def fetch_crypto(ticker_map):
    ids = ",".join(ticker_map.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd,brl&include_24hr_change=true&include_market_cap=true"
    try:
        r = requests.get(url, timeout=15)
        return r.json()
    except Exception as e:
        print(f"  ⚠️  Erro CoinGecko: {e}")
    return {}

def fetch_fng():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=10)
        d = r.json()["data"][0]
        return int(d["value"]), d["value_classification"]
    except:
        return None, None

CRYPTO_IDS = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
              "XRP": "ripple", "ADA": "cardano", "AVAX": "avalanche-2"}

def analyze_b3(ticker):
    print(f"\n🔍 Buscando dados B3 para {ticker}...")
    q = fetch_b3(ticker)
    selic = fetch_selic()
    usd = fetch_usdbrl()

    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"📊 ANÁLISE B3 — {ticker}")
    lines.append(f"{'='*60}")
    lines.append(f"📅 Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')} BRT")
    lines.append(f"🏦 Selic: {selic:.2f}% a.a.")
    if usd:
        lines.append(f"💱 USD/BRL: R$ {usd:.4f}")
    lines.append("")

    if not q:
        lines.append(f"❌ Dados não encontrados para {ticker} via BRAPI.")
        return "\n".join(lines)

    preco = q.get("regularMarketPrice", 0)
    var   = q.get("regularMarketChangePercent", 0)
    pl    = q.get("priceEarnings")
    lpa   = q.get("earningsPerShare")
    vpa   = q.get("bookValue")
    dy    = q.get("dividendYield")
    mcap  = q.get("marketCap")
    nome  = q.get("longName", ticker)

    lines.append(f"🏢 {nome}")
    lines.append(f"")
    lines.append(f"💰 COTAÇÃO")
    lines.append(f"   Preço:    R$ {preco:.2f}")
    lines.append(f"   Variação: {var:+.2f}% hoje")
    if mcap:
        lines.append(f"   Market Cap: R$ {mcap/1e9:.2f}B")
    lines.append("")

    lines.append(f"📈 FUNDAMENTALISTA")
    if pl:
        lines.append(f"   P/L:  {pl:.1f}x")
    if lpa:
        lines.append(f"   LPA:  R$ {lpa:.4f}")
    if vpa:
        lines.append(f"   VPA:  R$ {vpa:.2f}")
        pvpa = preco / vpa if vpa != 0 else None
        if pvpa:
            lines.append(f"   P/VPA: {pvpa:.2f}x")
    if dy:
        lines.append(f"   DY:   {dy:.2f}%")

    g = graham(lpa, vpa) if lpa and vpa else None
    if g:
        upside = (g / preco - 1) * 100
        lines.append(f"   Graham: R$ {g:.2f} (upside: {upside:+.1f}%)")
    lines.append("")

    lines.append(f"📊 ANÁLISE DE OPÇÕES (Black-Scholes)")
    r_diario = (selic / 100) / 252
    sigma_est = 0.45
    dte = 30
    T = dte / 365
    K_atm = round(preco, 2)

    call_price, call_greeks = black_scholes(preco, K_atm, T, r_diario * 252, sigma_est, "CALL")
    put_price,  put_greeks  = black_scholes(preco, K_atm, T, r_diario * 252, sigma_est, "PUT")

    lines.append(f"   Parâmetros: Spot={preco:.2f} | Strike ATM={K_atm:.2f} | DTE={dte}d")
    lines.append(f"   IV estimada: {sigma_est*100:.0f}% | Selic: {selic:.2f}%")
    if call_price:
        lines.append(f"   Call ATM: R$ {call_price:.4f} | Δ={call_greeks['delta']} θ={call_greeks['theta']}")
    if put_price:
        lines.append(f"   Put  ATM: R$ {put_price:.4f} | Δ={put_greeks['delta']} θ={put_greeks['theta']}")

    f_full, f_cons = kelly(0.55, 0.10, 0.05)
    lines.append(f"")
    lines.append(f"🎯 KELLY CRITERION")
    lines.append(f"   f* = {f_full:.2%} | Conservador (1/4): {f_cons:.2%}")
    lines.append(f"   Máx capital: 2% (alto risco) | 5% (risco limitado)")
    lines.append("")
    lines.append(f"{'='*60}")

    return "\n".join(lines)

def analyze_crypto(ticker):
    ticker = ticker.upper()
    cg_id = CRYPTO_IDS.get(ticker)
    if not cg_id:
        return f"❌ Ticker cripto '{ticker}' não suportado. Use: {', '.join(CRYPTO_IDS.keys())}"

    print(f"\n🔍 Buscando dados cripto para {ticker}...")
    data = fetch_crypto({ticker: cg_id})
    fng_val, fng_label = fetch_fng()
    usd = fetch_usdbrl()

    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"🪙 ANÁLISE CRIPTO — {ticker}")
    lines.append(f"{'='*60}")
    lines.append(f"📅 Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')} BRT")
    lines.append("")

    if cg_id not in data:
        lines.append(f"❌ Dados não encontrados para {ticker} via CoinGecko.")
        return "\n".join(lines)

    d = data[cg_id]
    preco_usd = d.get("usd", 0)
    preco_brl = d.get("brl", 0)
    var_24h   = d.get("usd_24h_change", 0)
    mcap      = d.get("usd_market_cap", 0)

    lines.append(f"💰 PREÇO")
    lines.append(f"   USD: ${preco_usd:,.2f} ({var_24h:+.2f}% 24h)")
    if preco_brl:
        lines.append(f"   BRL: R$ {preco_brl:,.2f}")
    if mcap:
        lines.append(f"   Market Cap: ${mcap/1e9:.1f}B")
    if usd:
        lines.append(f"   USD/BRL: R$ {usd:.4f}")
    lines.append("")

    if fng_val:
        lines.append(f"😱 SENTIMENTO")
        lines.append(f"   Fear & Greed: {fng_val} — {fng_label}")
        if fng_val < 25:
            lines.append(f"   → Medo Extremo: possível oportunidade de compra")
        elif fng_val > 75:
            lines.append(f"   → Ganância Extrema: cautela, possível topo")
        lines.append("")

    lines.append(f"📊 ANÁLISE DE OPÇÕES (Black-Scholes)")
    sigma_est = 0.80
    dte = 30
    T = dte / 365
    K_atm = round(preco_usd, 2)

    call_price, call_greeks = black_scholes(preco_usd, K_atm, T, 0, sigma_est, "CALL")
    put_price,  put_greeks  = black_scholes(preco_usd, K_atm, T, 0, sigma_est, "PUT")

    lines.append(f"   Parâmetros: Spot=${preco_usd:,.2f} | Strike ATM=${K_atm:,.2f}")
    lines.append(f"   IV estimada: {sigma_est*100:.0f}% | DTE: {dte}d")
    if call_price:
        lines.append(f"   Call ATM: ${call_price:.4f} | Δ={call_greeks['delta']} θ={call_greeks['theta']}")
    if put_price:
        lines.append(f"   Put  ATM: ${put_price:.4f} | Δ={put_greeks['delta']} θ={put_greeks['theta']}")
    lines.append("")

    lines.append(f"🎯 ESTRATÉGIAS SUGERIDAS")
    iv_hv = 1.0
    if iv_hv > 1.2:
        lines.append(f"   IV/HV > 1.2 → vol cara → Iron Condor / Straddle vendido")
    elif iv_hv < 0.8:
        lines.append(f"   IV/HV < 0.8 → vol barata → Long Straddle / Calendar")
    else:
        lines.append(f"   IV/HV ≈ 1.0 → vol justa → Bull Call Spread (se alta) / Iron Condor (neutro)")

    f_full, f_cons = kelly(0.55, 0.15, 0.08)
    lines.append(f"")
    lines.append(f"   Kelly f*={f_full:.2%} | Conservador: {f_cons:.2%}")
    lines.append(f"   Máx: 2% capital (alto risco) | 5% (risco limitado)")
    lines.append("")
    lines.append(f"{'='*60}")

    return "\n".join(lines)

def main():
    ticker = sys.argv[1].upper() if len(sys.argv) > 1 else "COGN3"

    is_crypto = ticker in CRYPTO_IDS

    if is_crypto:
        output = analyze_crypto(ticker)
    else:
        output = analyze_b3(ticker)

    print(output)

    output_file = f"{OUTPUT_DIR}/{ticker.lower()}_output.txt"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"\n✅ Output salvo em: {output_file}")
        print(f"   John Galt: use file_read {output_file}")
    except Exception as e:
        print(f"\n⚠️  Não foi possível salvar arquivo: {e}")

if __name__ == "__main__":
    main()
