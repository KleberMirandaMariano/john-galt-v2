#!/usr/bin/env python3
"""
validate_options_b3.py — Validador genérico para análise de opções B3
Corrige os 9 erros encontrados na validação Cowork para QUALQUER ativo
"""

import numpy as np
from scipy.stats import norm
from datetime import datetime, timedelta
import json
import sys

class OptionsValidatorB3:
    """
    Validador genérico para análise quantitativa de opções B3
    
    Funciona para QUALQUER ativo: COGN3, PETR4, VALE3, ITUB4, etc.
    """
    
    def __init__(self, ticker, spot_price, strike, days_to_expiry, rf_rate, volatility):
        self.ticker = ticker.upper()
        self.S = spot_price
        self.K = strike
        self.T = days_to_expiry / 252
        self.r = rf_rate
        self.sigma = volatility
        self.errors = []
        self.warnings = []
    
    # ========================================================================
    # ERRO 1: Validar Série de Opção (Nomenclatura B3)
    # ========================================================================
    
    def validate_option_series(self, series_code, analysis_date):
        """
        Valida nomenclatura B3 para QUALQUER ticker
        
        Formato: [TICKER][MÊS][STRIKE]
        Ex: COGNE335, PETRJ45, VALEF30, ITUBK25
        
        Mês: A=jan, B=fev, C=mar, D=abr, E=mai, F=jun,
             G=jul, H=ago, I=set, J=out, K=nov, L=dez
        """
        month_codes = {
            'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6,
            'G': 7, 'H': 8, 'I': 9, 'J': 10, 'K': 11, 'L': 12
        }
        
        # Extrair ticker base (pode ter 4 ou 5 caracteres: PETR4, COGN3, VALE3)
        ticker_base = series_code[:len(self.ticker)]
        
        if ticker_base != self.ticker:
            self.errors.append({
                "tipo": "🔴 CRÍTICO",
                "erro": f"Ticker da série ({ticker_base}) difere do ativo ({self.ticker})",
                "correção": f"Verificar se série é realmente do ativo {self.ticker}"
            })
            return None
        
        # Extrair código do mês
        month_letter = series_code[len(self.ticker)]
        
        if month_letter not in month_codes:
            self.errors.append({
                "tipo": "🔴 CRÍTICO",
                "erro": f"Código de mês inválido: {month_letter}",
                "correção": "Usar A=jan, B=fev, C=mar, D=abr, E=mai, F=jun, G=jul, H=ago, I=set, J=out, K=nov, L=dez"
            })
            return None
        
        month = month_codes[month_letter]
        year = analysis_date.year
        
        # Calcular 3ª sexta-feira do mês (vencimento B3)
        first_day = datetime(year, month, 1)
        first_friday = first_day + timedelta(days=(4 - first_day.weekday()) % 7)
        third_friday = first_friday + timedelta(weeks=2)
        
        # CRÍTICO: Verificar se série já expirou
        if third_friday < analysis_date:
            next_month_code = list(month_codes.keys())[month % 12]
            self.errors.append({
                "tipo": "🔴 CRÍTICO - SÉRIE EXPIRADA",
                "erro": f"Série {series_code} expirou em {third_friday.strftime('%d/%m/%Y')}",
                "análise_feita": analysis_date.strftime('%d/%m/%Y'),
                "dias_atrasado": (analysis_date - third_friday).days,
                "correção": f"Usar série do próximo mês: {self.ticker}{next_month_code}"
            })
            return None
        
        return {
            "ticker": self.ticker,
            "series": series_code,
            "expiry": third_friday,
            "days_to_expiry": (third_friday - analysis_date).days,
            "is_valid": True
        }
    
    # ========================================================================
    # ERROS 2 e 3: Delta e P(ITM) - Black-Scholes Correto
    # ========================================================================
    
    def calculate_black_scholes_greeks(self):
        """Calcula gregas Black-Scholes para QUALQUER ativo"""
        
        if self.T <= 0:
            self.errors.append({
                "tipo": "🔴 CRÍTICO",
                "erro": "Opção já expirada (T ≤ 0)"
            })
            return None
        
        # Black-Scholes
        d1 = (np.log(self.S / self.K) + (self.r + 0.5 * self.sigma**2) * self.T) / (self.sigma * np.sqrt(self.T))
        d2 = d1 - self.sigma * np.sqrt(self.T)
        
        delta = norm.cdf(d1)
        p_itm = norm.cdf(d2)
        
        # Theta SEMPRE negativo para long call
        theta = (
            -self.S * norm.pdf(d1) * self.sigma / (2 * np.sqrt(self.T))
            - self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
        ) / 252
        
        gamma = norm.pdf(d1) / (self.S * self.sigma * np.sqrt(self.T))
        vega = self.S * norm.pdf(d1) * np.sqrt(self.T) / 100
        
        # Validar theta
        if theta > 0:
            self.errors.append({
                "tipo": "🔴 CRÍTICO - THETA POSITIVO",
                "erro": "Theta positivo é impossível para long call",
                "valor_incorreto": f"+{abs(theta):.4f}",
                "valor_correto": f"{theta:.4f} (negativo)"
            })
        
        return {
            "delta": delta,
            "p_itm": p_itm,
            "theta": theta,
            "gamma": gamma,
            "vega": vega
        }
    
    # ========================================================================
    # ERRO 5: Break-even Correto
    # ========================================================================
    
    def calculate_breakeven(self, premium):
        """Break-even CORRETO: Strike + Premium (NÃO Spot + Premium!)"""
        return self.K + premium
    
    # ========================================================================
    # ERRO 6: Classificação ATM/OTM/ITM
    # ========================================================================
    
    def classify_moneyness(self):
        """Classifica corretamente para QUALQUER strike"""
        moneyness_pct = ((self.S - self.K) / self.K) * 100
        
        if abs(moneyness_pct) < 2:
            classification = "ATM"
        elif moneyness_pct > 0:
            classification = "ITM"
        else:
            classification = "OTM"
        
        return {
            "classification": classification,
            "moneyness_pct": moneyness_pct,
            "is_deep": abs(moneyness_pct) > 10
        }
    
    # ========================================================================
    # ERRO 7: P&L Correto
    # ========================================================================
    
    def calculate_pnl(self, target_price, premium, n_contracts):
        """P&L correto para long call de QUALQUER ativo"""
        intrinsic_value = max(0, target_price - self.K)
        pnl_per_option = intrinsic_value - premium
        total_pnl = pnl_per_option * n_contracts * 100
        
        return {
            "intrinsic_value": intrinsic_value,
            "pnl_per_option": pnl_per_option,
            "total_pnl": total_pnl,
            "roi_pct": (pnl_per_option / premium * 100) if premium > 0 else 0
        }
    
    # ========================================================================
    # ERRO 8: Kelly Criterion Correto
    # ========================================================================
    
    def calculate_kelly(self, p_success, gain, loss):
        """Kelly genérico para QUALQUER trade"""
        q = 1 - p_success
        b = gain / loss if loss > 0 else 0
        
        f_star = (p_success * b - q) / b if b > 0 else 0
        f_quarter = f_star / 4
        
        return {
            "f_star": f_star,
            "f_quarter": f_quarter,
            "p_success": p_success,
            "expected_value": p_success * gain - q * loss
        }
    
    # ========================================================================
    # GERAR RELATÓRIO COMPLETO
    # ========================================================================
    
    def generate_report(self, series_code, analysis_date, premium, target_price, n_contracts):
        """Gerar análise completa validada para QUALQUER ativo B3"""
        
        print(f"\n{'='*70}")
        print(f"ANÁLISE QUANTITATIVA VALIDADA — {self.ticker}")
        print(f"{'='*70}")
        
        # 1. Validar série
        print(f"\n📋 SÉRIE DE OPÇÃO:")
        series_info = self.validate_option_series(series_code, analysis_date)
        if series_info:
            print(f"   Série: {series_info['series']}")
            print(f"   Vencimento: {series_info['expiry'].strftime('%d/%m/%Y')} ({series_info['days_to_expiry']} dias)")
        else:
            print(f"   ❌ SÉRIE INVÁLIDA!")
        
        # 2. Gregas
        print(f"\n📊 GREGAS (BLACK-SCHOLES):")
        greeks = self.calculate_black_scholes_greeks()
        if greeks:
            print(f"   Delta: {greeks['delta']:.4f}")
            print(f"   P(ITM): {greeks['p_itm']*100:.1f}%")
            print(f"   Theta: {greeks['theta']:.4f}/dia")
            print(f"   Gamma: {greeks['gamma']:.4f}")
            print(f"   Vega: {greeks['vega']:.4f}")
        
        # 3. Classificação
        print(f"\n🎯 CLASSIFICAÇÃO:")
        moneyness = self.classify_moneyness()
        print(f"   Tipo: {moneyness['classification']}")
        print(f"   Moneyness: {moneyness['moneyness_pct']:+.1f}%")
        print(f"   Spot: R$ {self.S:.2f}")
        print(f"   Strike: R$ {self.K:.2f}")
        
        # 4. Break-even
        print(f"\n💰 BREAK-EVEN:")
        be = self.calculate_breakeven(premium)
        print(f"   Break-even: R$ {be:.3f}")
        print(f"   Fórmula: Strike + Premium = {self.K:.2f} + {premium:.3f}")
        
        # 5. P&L
        print(f"\n📈 P&L NO ALVO (R$ {target_price:.2f}):")
        pnl = self.calculate_pnl(target_price, premium, n_contracts)
        print(f"   Ganho por opção: R$ {pnl['pnl_per_option']:.3f}")
        print(f"   Ganho total ({n_contracts} contratos): R$ {pnl['total_pnl']:.2f}")
        print(f"   ROI: {pnl['roi_pct']:.1f}%")
        
        # 6. Kelly
        if greeks and pnl['pnl_per_option'] > 0:
            print(f"\n🎲 KELLY CRITERION:")
            kelly = self.calculate_kelly(greeks['p_itm'], pnl['pnl_per_option'], premium)
            print(f"   Kelly Full (f*): {kelly['f_star']*100:.1f}%")
            print(f"   Kelly 1/4: {kelly['f_quarter']*100:.1f}%")
            print(f"   Valor Esperado: R$ {kelly['expected_value']:.3f}")
        
        # 7. Erros
        if self.errors:
            print(f"\n{'='*70}")
            print(f"⚠️ ERROS ENCONTRADOS: {len(self.errors)}")
            print(f"{'='*70}")
            for i, err in enumerate(self.errors, 1):
                print(f"\n{err['tipo']} #{i}:")
                for key, value in err.items():
                    if key != 'tipo':
                        print(f"   {key}: {value}")
        else:
            print(f"\n✅ Nenhum erro encontrado!")
        
        return {
            "ticker": self.ticker,
            "series_info": series_info,
            "greeks": greeks,
            "moneyness": moneyness,
            "breakeven": be,
            "pnl": pnl,
            "errors": self.errors
        }

# ============================================================================
# USO: python3 validate_options_b3.py TICKER SPOT STRIKE DAYS RATE VOL SERIES DATE PREMIUM TARGET CONTRACTS
# ============================================================================

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Uso: python3 validate_options_b3.py [TICKER] [SPOT] [STRIKE] [DAYS] [RATE] [VOL] [SERIES] [DATE] [PREMIUM] [TARGET] [CONTRACTS]")
        print("\nExemplo COGN3:")
        print("python3 validate_options_b3.py COGN3 2.97 3.35 23 0.1475 0.65 COGND335 2026-04-24 0.085 3.80 10")
        print("\nExemplo PETR4:")
        print("python3 validate_options_b3.py PETR4 38.50 40.00 30 0.1475 0.45 PETRJ40 2026-05-15 1.20 42.00 5")
        sys.exit(1)
    
    # Parsear argumentos
    ticker = sys.argv[1] if len(sys.argv) > 1 else "COGN3"
    spot = float(sys.argv[2]) if len(sys.argv) > 2 else 2.97
    strike = float(sys.argv[3]) if len(sys.argv) > 3 else 3.35
    days = int(sys.argv[4]) if len(sys.argv) > 4 else 23
    rate = float(sys.argv[5]) if len(sys.argv) > 5 else 0.1475
    vol = float(sys.argv[6]) if len(sys.argv) > 6 else 0.65
    series = sys.argv[7] if len(sys.argv) > 7 else "COGND335"
    date_str = sys.argv[8] if len(sys.argv) > 8 else "2026-04-24"
    premium = float(sys.argv[9]) if len(sys.argv) > 9 else 0.085
    target = float(sys.argv[10]) if len(sys.argv) > 10 else 3.80
    contracts = int(sys.argv[11]) if len(sys.argv) > 11 else 10
    
    analysis_date = datetime.strptime(date_str, "%Y-%m-%d")
    
    # Criar validador
    validator = OptionsValidatorB3(
        ticker=ticker,
        spot_price=spot,
        strike=strike,
        days_to_expiry=days,
        rf_rate=rate,
        volatility=vol
    )
    
    # Gerar relatório
    report = validator.generate_report(
        series_code=series,
        analysis_date=analysis_date,
        premium=premium,
        target_price=target,
        n_contracts=contracts
    )
    
    # Salvar JSON
    output_file = f"/tmp/{ticker.lower()}_validation_{date_str}.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n{'='*70}")
    print(f"✅ Relatório salvo: {output_file}")
    print(f"{'='*70}\n")

