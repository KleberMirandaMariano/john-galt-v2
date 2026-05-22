#!/usr/bin/env python3
"""
analyze_ticker.py — Análise quantitativa completa via APIs públicas
Salva output em /root/.zeroclaw/workspace/{ticker}_output.txt
John Galt lê o arquivo com file_read após execução.

Uso (na VPS, o repo fica em /root/.zeroclaw/workspace/):
  python3 /root/.zeroclaw/workspace/analyze_ticker.py COGN3
  python3 /root/.zeroclaw/workspace/analyze_ticker.py PETR4
  python3 /root/.zeroclaw/workspace/analyze_ticker.py SOL
  python3 /root/.zeroclaw/workspace/analyze_ticker.py BTC
"""

import sys
import os
import json
import math
import requests
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from cotahist import CotahistClient
try:
    from bayesian_signals import (
        BayesianUpdater, MarketRegime,
        SIGNALS_B3, SIGNALS_CRIPTO,
        bayesian_kelly,
    )
    _BAYES_OK = True
except ImportError:
    _BAYES_OK = False

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

def implied_vol(market_price, S, K, T, r, tipo="CALL", tol=1e-5, max_iter=100):
    """Bisecção para back-solve IV a partir do prêmio de mercado real."""
    if market_price <= 0 or T <= 0 or S <= 0 or K <= 0:
        return None
    lo, hi = 0.001, 10.0
    for _ in range(max_iter):
        mid = (lo + hi) / 2
        price, _ = black_scholes(S, K, T, r, mid, tipo)
        if price is None:
            return None
        diff = price - market_price
        if abs(diff) < tol:
            return round(mid, 4)
        if diff > 0:
            hi = mid
        else:
            lo = mid
    return round((lo + hi) / 2, 4)

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
    # BCB PTAX Série 1 — oficial, sem rate limit
    try:
        r = requests.get(
            "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados/ultimos/2?formato=json",
            timeout=10,
        )
        data = r.json()
        if data and len(data) >= 1:
            return float(data[-1]["valor"])
    except Exception:
        pass
    # Fallback: CoinGecko USDT/BRL
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=brl",
            timeout=10,
        )
        return float(r.json()["tether"]["brl"])
    except Exception:
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

    # Fontes em paralelo
    q     = fetch_b3(ticker)        # BRAPI: fundamentais
    selic = fetch_selic()
    usd   = fetch_usdbrl()

    # COTAHIST: spot real + opções reais
    cotahist = CotahistClient()
    cota_quote   = cotahist.get_quote(ticker)
    cota_options = cotahist.get_options(ticker, max_vencimentos=2)

    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"📊 ANÁLISE B3 — {ticker}")
    lines.append(f"{'='*60}")
    lines.append(f"📅 Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')} BRT")
    lines.append(f"🏦 Selic: {selic:.2f}% a.a.")
    if usd:
        lines.append(f"💱 USD/BRL: R$ {usd:.4f}")
    lines.append("")

    # Preço: COTAHIST tem prioridade (fonte oficial B3), fallback BRAPI
    if cota_quote:
        preco = cota_quote["preco"]
        vol_brl = cota_quote["volume"]
        lines.append(f"💰 COTAÇÃO (COTAHIST — {cota_quote['data_ref']})")
        lines.append(f"   Preço:   R$ {preco:.2f}")
        lines.append(f"   Volume:  R$ {vol_brl/1e6:.1f}M")
        if q:
            var = q.get("regularMarketChangePercent", 0)
            lines.append(f"   Variação: {var:+.2f}% hoje (BRAPI)")
    elif q:
        preco = q.get("regularMarketPrice", 0)
        lines.append(f"💰 COTAÇÃO (BRAPI — sem COTAHIST hoje)")
        lines.append(f"   Preço:    R$ {preco:.2f}")
        var = q.get("regularMarketChangePercent", 0)
        lines.append(f"   Variação: {var:+.2f}% hoje")
    else:
        lines.append(f"❌ Dados não encontrados para {ticker}.")
        return "\n".join(lines)

    if q:
        mcap = q.get("marketCap")
        if mcap:
            lines.append(f"   Market Cap: R$ {mcap/1e9:.2f}B")
    lines.append("")

    # Fundamentais: BRAPI
    if q:
        pl  = q.get("priceEarnings")
        lpa = q.get("earningsPerShare")
        vpa = q.get("bookValue")
        dy  = q.get("dividendYield")
        nome = q.get("longName", ticker)
        lines.append(f"🏢 {nome}")
        lines.append(f"📈 FUNDAMENTALISTA (BRAPI)")
        if pl:  lines.append(f"   P/L:  {pl:.1f}x")
        if lpa: lines.append(f"   LPA:  R$ {lpa:.4f}")
        if vpa:
            lines.append(f"   VPA:  R$ {vpa:.2f}")
            pvpa = preco / vpa if vpa else None
            if pvpa: lines.append(f"   P/VPA: {pvpa:.2f}x")
        if dy:  lines.append(f"   DY:   {dy:.2f}%")
        g = graham(lpa, vpa) if lpa and vpa else None
        if g:
            upside = (g / preco - 1) * 100
            lines.append(f"   Graham: R$ {g:.2f} (upside: {upside:+.1f}%)")
        lines.append("")

    # Opções: COTAHIST (reais) ou Black-Scholes estimado (fallback)
    r_anual = selic / 100
    T_base  = 30 / 365

    if cota_options:
        lines.append(f"📊 OPÇÕES REAIS B3 (COTAHIST — {cotahist._date_ref})")
        lines.append(f"   Spot de referência: R$ {preco:.2f} | Selic: {selic:.2f}%")
        lines.append("")

        # Agrupar por tipo e vencimento
        from itertools import groupby
        opts_sorted = sorted(cota_options, key=lambda x: (x["tipo"], x["vencimento"], x["strike"]))
        for tipo, grupo_tipo in groupby(opts_sorted, key=lambda x: x["tipo"]):
            for venc, grupo_venc in groupby(grupo_tipo, key=lambda x: x["vencimento"]):
                opts_venc = list(grupo_venc)
                # Filtrar strikes próximos ao ATM (±30%)
                atm_opts = [o for o in opts_venc
                            if 0.70 * preco <= o["strike"] <= 1.30 * preco][:8]
                if not atm_opts:
                    atm_opts = opts_venc[:5]

                # Calcular DTE
                try:
                    dte_days = (datetime.strptime(venc, "%Y-%m-%d") - datetime.now()).days
                except Exception:
                    dte_days = 30
                T = max(dte_days, 1) / 365

                lines.append(f"   {tipo}S — venc {venc} ({dte_days}d)")
                lines.append(f"   {'Strike':>8}  {'Prêmio':>8}  {'IV impl':>8}  {'Volume':>10}  {'Δ':>7}")
                lines.append(f"   {'-'*52}")
                for o in atm_opts:
                    iv = implied_vol(o["preco"], preco, o["strike"], T, r_anual, tipo)
                    _, greeks = black_scholes(preco, o["strike"], T, r_anual, iv or 0.45, tipo)
                    delta_str = f"{greeks['delta']:+.3f}" if greeks else "  —  "
                    iv_str    = f"{iv*100:.1f}%" if iv else "  —  "
                    atm_mark  = " ←ATM" if abs(o["strike"] - preco) / preco < 0.02 else ""
                    lines.append(
                        f"   R${o['strike']:>7.2f}  R${o['preco']:>6.4f}  {iv_str:>7}  "
                        f"R${o['volume']/1e3:>7.0f}K  {delta_str}{atm_mark}"
                    )
                lines.append("")

    else:
        # Fallback: Black-Scholes com IV estimada
        lines.append(f"📊 OPÇÕES ESTIMADAS (Black-Scholes — sem COTAHIST)")
        sigma_est = 0.45
        T = T_base
        K_atm = round(preco, 2)
        call_price, call_greeks = black_scholes(preco, K_atm, T, r_anual, sigma_est, "CALL")
        put_price,  put_greeks  = black_scholes(preco, K_atm, T, r_anual, sigma_est, "PUT")
        lines.append(f"   Parâmetros: Spot={preco:.2f} | Strike ATM={K_atm:.2f} | DTE=30d")
        lines.append(f"   IV estimada: {sigma_est*100:.0f}% | Selic: {selic:.2f}%")
        if call_price:
            lines.append(f"   Call ATM: R$ {call_price:.4f} | Δ={call_greeks['delta']} θ={call_greeks['theta']}")
        if put_price:
            lines.append(f"   Put  ATM: R$ {put_price:.4f} | Δ={put_greeks['delta']} θ={put_greeks['theta']}")
        lines.append("")

    if _BAYES_OK:
        updater = BayesianUpdater(prior=0.50)
        regime  = MarketRegime()
        applied = []

        if selic >= 12.0:
            updater.update_from_library("selic_restrictive", SIGNALS_B3)
            regime.update("selic_restrictive")
            applied.append("selic_restrictive")

        if q:
            var_pct = q.get("regularMarketChangePercent", 0) or 0
            if var_pct > 0:
                updater.update_from_library("ibov_positive", SIGNALS_B3)
                regime.update("ibov_positive")
                applied.append("ibov_positive")

        if cota_options:
            # Usa IV mediana das opções para estimar IV/HV
            ivs = []
            for o in cota_options[:10]:
                if 0.80 * preco <= o["strike"] <= 1.20 * preco:
                    T_opt = max((datetime.strptime(o["vencimento"], "%Y-%m-%d") - datetime.now()).days, 1) / 365
                    iv = implied_vol(o["preco"], preco, o["strike"], T_opt, selic / 100, o["tipo"])
                    if iv:
                        ivs.append(iv)
            if ivs:
                iv_med = sorted(ivs)[len(ivs) // 2]
                hv_est = 0.40
                ratio  = iv_med / hv_est
                if ratio > 1.2:
                    updater.update_from_library("iv_hv_high", SIGNALS_B3)
                    regime.update("iv_hv_high")
                    applied.append(f"iv_hv_high (IV/HV={ratio:.2f})")
                elif ratio < 0.8:
                    updater.update_from_library("iv_hv_low", SIGNALS_B3)
                    regime.update("iv_hv_low")
                    applied.append(f"iv_hv_low (IV/HV={ratio:.2f})")

        posterior = updater.posterior
        f_full, f_quarter, f_capped = bayesian_kelly(posterior, ganho=0.10, perda=0.05, risk_type="defined")

        lines.append(f"🧠 ANÁLISE BAYESIANA")
        lines.append(f"   Prior: 0.50 → Posterior: {posterior:.1%}")
        if applied:
            lines.append(f"   Sinais: {', '.join(applied)}")
        lines.append(f"   LR acumulado: {updater.cumulative_lr():.2f}×")
        lines.append(f"   Regime estimado: {regime.dominant().upper()} → {regime.strategy_hint()}")
        lines.append(f"")
        lines.append(f"🎯 KELLY BAYESIANO")
        lines.append(f"   f* = {f_full:.2%} | 1/4 Kelly = {f_quarter:.2%} | Cap aplicado = {f_capped:.2%}")
        lines.append(f"   Máx capital: 2% (OTM) | 5% (spread RR>2:1)")
    else:
        f_full, f_cons = kelly(0.55, 0.10, 0.05)
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

    if _BAYES_OK:
        updater = BayesianUpdater(prior=0.50)
        regime  = MarketRegime()
        applied = []

        if fng_val is not None:
            if fng_val < 25:
                updater.update_from_library("fng_extreme_fear", SIGNALS_CRIPTO)
                regime.update("fng_extreme_fear")
                applied.append(f"fng_extreme_fear (FNG={fng_val})")
            elif fng_val > 75:
                updater.update_from_library("fng_extreme_greed", SIGNALS_CRIPTO)
                regime.update("fng_extreme_greed")
                applied.append(f"fng_extreme_greed (FNG={fng_val})")
            elif 45 <= fng_val <= 55:
                updater.update_from_library("fng_neutral", SIGNALS_CRIPTO)
                applied.append(f"fng_neutral (FNG={fng_val})")

        if sigma_est > 0.80:
            updater.update_from_library("hv_high", SIGNALS_CRIPTO)
            regime.update("hv_high")
            applied.append(f"hv_high (HV~{sigma_est*100:.0f}%)")
        elif sigma_est < 0.40:
            updater.update_from_library("hv_low", SIGNALS_CRIPTO)
            regime.update("hv_low")
            applied.append(f"hv_low (HV~{sigma_est*100:.0f}%)")

        posterior = updater.posterior
        f_full, f_quarter, f_capped = bayesian_kelly(posterior, ganho=0.15, perda=0.08, risk_type="high")

        lines.append(f"")
        lines.append(f"🧠 ANÁLISE BAYESIANA")
        lines.append(f"   Prior: 0.50 → Posterior: {posterior:.1%}")
        if applied:
            lines.append(f"   Sinais: {', '.join(applied)}")
        lines.append(f"   LR acumulado: {updater.cumulative_lr():.2f}×")
        lines.append(f"   Regime estimado: {regime.dominant().upper()} → {regime.strategy_hint()}")
        lines.append(f"")
        lines.append(f"🎯 KELLY BAYESIANO")
        lines.append(f"   f* = {f_full:.2%} | 1/4 Kelly = {f_quarter:.2%} | Cap = {f_capped:.2%}")
        lines.append(f"   Máx: 2% capital (OTM) | 5% (spread RR>2:1)")
    else:
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
