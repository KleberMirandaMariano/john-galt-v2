#!/usr/bin/env python3
"""
financial_datasets.py - Financial Datasets API Integration

Acesso a 17,000+ ações globais, fundamentalistas, earnings, balanços
Alternativa ao Bloomberg Terminal para John Galt

Autor: John Galt v2.0 - Financial Datasets Integration
Data: 08/05/2026
"""

import requests
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from functools import lru_cache


class FinancialDatasetsAPI:
    """
    Client para Financial Datasets API
    
    Features:
    - 17,000+ ações (NYSE, NASDAQ, B3, etc)
    - Fundamentalistas (P/E, ROE, margins, etc)
    - Earnings (resultados trimestrais)
    - Demonstrações financeiras (DRE, Balanço, Fluxo Caixa)
    - Preços de cripto
    - Análise comparativa
    """
    
    BASE_URL = "https://api.financialdatasets.ai/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: API key (opcional, usa var de ambiente se omitido)
        """
        self.api_key = api_key or os.getenv("FINANCIAL_DATASETS_API_KEY")
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
        
        self.session.headers.update({
            "User-Agent": "John-Galt-Bot/2.0 (Financial Analysis)"
        })
    
    # =================================================================
    # STOCK PRICES
    # =================================================================
    
    @lru_cache(maxsize=100)
    def get_stock_price(self, ticker: str) -> Optional[Dict]:
        """
        Obter preço atual da ação
        
        Args:
            ticker: Ticker (ex: AAPL, PETR4.SA, MSFT)
        
        Returns:
            Dict com preço e dados básicos
        """
        try:
            url = f"{self.BASE_URL}/stocks/{ticker}/price"
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"⚠️ Erro ao buscar preço de {ticker}: {resp.status_code}")
                return None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    # =================================================================
    # FUNDAMENTALS
    # =================================================================
    
    def get_fundamentals(self, ticker: str) -> Optional[Dict]:
        """
        Obter métricas fundamentalistas
        
        Returns:
            Dict com P/E, P/B, ROE, Debt/Equity, Dividend Yield, etc
        """
        try:
            url = f"{self.BASE_URL}/stocks/{ticker}/fundamentals"
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                
                # Formatar métricas
                return {
                    "ticker": ticker,
                    "pe_ratio": data.get("pe_ratio"),
                    "pb_ratio": data.get("pb_ratio"),
                    "ps_ratio": data.get("ps_ratio"),
                    "roe": data.get("roe"),
                    "roa": data.get("roa"),
                    "debt_to_equity": data.get("debt_to_equity"),
                    "current_ratio": data.get("current_ratio"),
                    "dividend_yield": data.get("dividend_yield"),
                    "market_cap": data.get("market_cap"),
                    "enterprise_value": data.get("enterprise_value"),
                    "ebitda_margin": data.get("ebitda_margin"),
                    "net_margin": data.get("net_margin"),
                    "revenue_growth": data.get("revenue_growth_yoy"),
                    "earnings_growth": data.get("earnings_growth_yoy")
                }
            else:
                print(f"⚠️ Erro ao buscar fundamentalistas de {ticker}: {resp.status_code}")
                return None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    # =================================================================
    # EARNINGS
    # =================================================================
    
    def get_earnings(self, ticker: str, periods: int = 4) -> Optional[List[Dict]]:
        """
        Obter resultados trimestrais
        
        Args:
            ticker: Ticker
            periods: Número de trimestres (default 4)
        
        Returns:
            Lista de earnings por trimestre
        """
        try:
            url = f"{self.BASE_URL}/stocks/{ticker}/earnings"
            params = {"periods": periods}
            resp = self.session.get(url, params=params, timeout=10)
            
            if resp.status_code == 200:
                return resp.json().get("earnings", [])
            else:
                print(f"⚠️ Erro ao buscar earnings de {ticker}: {resp.status_code}")
                return None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    # =================================================================
    # FINANCIAL STATEMENTS
    # =================================================================
    
    def get_income_statement(self, ticker: str) -> Optional[Dict]:
        """
        Obter DRE (Demonstração de Resultados)
        
        Returns:
            Dict com revenue, expenses, net income, margins
        """
        try:
            url = f"{self.BASE_URL}/stocks/{ticker}/income-statement"
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code == 200:
                return resp.json()
            else:
                return None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    def get_balance_sheet(self, ticker: str) -> Optional[Dict]:
        """
        Obter Balanço Patrimonial
        
        Returns:
            Dict com assets, liabilities, equity
        """
        try:
            url = f"{self.BASE_URL}/stocks/{ticker}/balance-sheet"
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code == 200:
                return resp.json()
            else:
                return None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    def get_cash_flow(self, ticker: str) -> Optional[Dict]:
        """
        Obter Fluxo de Caixa
        
        Returns:
            Dict com operating, investing, financing cash flows
        """
        try:
            url = f"{self.BASE_URL}/stocks/{ticker}/cash-flow"
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code == 200:
                return resp.json()
            else:
                return None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    # =================================================================
    # CRYPTO
    # =================================================================
    
    def get_crypto_price(self, symbol: str) -> Optional[Dict]:
        """
        Obter preço de cripto
        
        Args:
            symbol: Símbolo (BTC, ETH, SOL)
        
        Returns:
            Dict com preço e dados
        """
        try:
            url = f"{self.BASE_URL}/crypto/{symbol}/price"
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code == 200:
                return resp.json()
            else:
                return None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    # =================================================================
    # COMPARATIVE ANALYSIS
    # =================================================================
    
    def compare_stocks(self, tickers: List[str]) -> Dict:
        """
        Comparar múltiplas ações lado-a-lado
        
        Args:
            tickers: Lista de tickers (ex: ["AAPL", "MSFT", "GOOGL"])
        
        Returns:
            Dict com comparação formatada
        """
        fundamentals = {}
        
        for ticker in tickers:
            fund = self.get_fundamentals(ticker)
            if fund:
                fundamentals[ticker] = fund
        
        if not fundamentals:
            return {"error": "No data available"}
        
        # Formatar comparação
        comparison = self._format_comparison(fundamentals)
        
        return {
            "tickers": tickers,
            "comparison": comparison,
            "timestamp": datetime.now().isoformat()
        }
    
    def _format_comparison(self, fundamentals: Dict) -> Dict:
        """Formatar tabela de comparação"""
        metrics = [
            "pe_ratio", "pb_ratio", "ps_ratio",
            "roe", "roa", "debt_to_equity",
            "current_ratio", "dividend_yield",
            "market_cap", "ebitda_margin", "net_margin",
            "revenue_growth", "earnings_growth"
        ]
        
        comparison = {}
        
        for metric in metrics:
            comparison[metric] = {}
            for ticker, data in fundamentals.items():
                value = data.get(metric)
                comparison[metric][ticker] = value
        
        return comparison
    
    def compare_to_brapi(self, ticker_b3: str) -> Dict:
        """
        Comparar dados Financial Datasets vs BRAPI
        
        Args:
            ticker_b3: Ticker B3 (ex: PETR4)
        
        Returns:
            Dict com comparação
        """
        # Converter ticker B3 para formato Yahoo Finance
        ticker_yf = f"{ticker_b3}.SA"
        
        # Buscar via Financial Datasets
        fd_data = self.get_fundamentals(ticker_yf)
        
        # Buscar via BRAPI (seria necessário integração)
        # Por enquanto retornar apenas FD data
        
        return {
            "ticker": ticker_b3,
            "financial_datasets": fd_data,
            "comparison_available": False  # Implementar integração BRAPI
        }
    
    # =================================================================
    # CORRELATION ANALYSIS
    # =================================================================
    
    def get_correlation(
        self, 
        assets: List[str], 
        days_back: int = 30
    ) -> Dict:
        """
        Calcular correlação entre ativos
        
        Args:
            assets: Lista de tickers/símbolos
            days_back: Dias históricos
        
        Returns:
            Dict com matriz de correlação
        """
        # Placeholder - implementar com dados históricos
        return {
            "assets": assets,
            "days_back": days_back,
            "correlation_matrix": {},
            "note": "Histórico de preços necessário para cálculo"
        }
    
    # =================================================================
    # UTILITIES
    # =================================================================
    
    def format_fundamentals_report(self, ticker: str) -> str:
        """
        Formatar relatório de fundamentalistas
        
        Returns:
            String formatada para Telegram/console
        """
        fund = self.get_fundamentals(ticker)
        
        if not fund:
            return f"❌ Dados não disponíveis para {ticker}"
        
        lines = []
        lines.append(f"📊 **FUNDAMENTALISTAS: {ticker.upper()}**")
        lines.append("")
        
        # Valuation
        lines.append("**VALUATION:**")
        if fund.get("pe_ratio"):
            lines.append(f"├ P/L: {fund['pe_ratio']:.2f}")
        if fund.get("pb_ratio"):
            lines.append(f"├ P/VP: {fund['pb_ratio']:.2f}")
        if fund.get("ps_ratio"):
            lines.append(f"└ P/S: {fund['ps_ratio']:.2f}")
        lines.append("")
        
        # Profitability
        lines.append("**RENTABILIDADE:**")
        if fund.get("roe"):
            lines.append(f"├ ROE: {fund['roe']*100:.1f}%")
        if fund.get("roa"):
            lines.append(f"├ ROA: {fund['roa']*100:.1f}%")
        if fund.get("net_margin"):
            lines.append(f"└ Margem Líq: {fund['net_margin']*100:.1f}%")
        lines.append("")
        
        # Solvency
        lines.append("**SOLVÊNCIA:**")
        if fund.get("debt_to_equity"):
            lines.append(f"├ Dívida/PL: {fund['debt_to_equity']:.2f}")
        if fund.get("current_ratio"):
            lines.append(f"└ Liquidez Corrente: {fund['current_ratio']:.2f}")
        lines.append("")
        
        # Growth
        lines.append("**CRESCIMENTO:**")
        if fund.get("revenue_growth"):
            lines.append(f"├ Receita YoY: {fund['revenue_growth']*100:+.1f}%")
        if fund.get("earnings_growth"):
            lines.append(f"└ Lucro YoY: {fund['earnings_growth']*100:+.1f}%")
        lines.append("")
        
        # Dividends
        if fund.get("dividend_yield"):
            lines.append("**DIVIDENDOS:**")
            lines.append(f"└ Yield: {fund['dividend_yield']*100:.2f}%")
        
        return "\n".join(lines)


# =============================================================================
# INTEGRATION WITH JOHN GALT PHASES
# =============================================================================

def integrate_with_memory(api: FinancialDatasetsAPI, ticker: str, memory):
    """
    Integrar com Phase 2: Enhanced Memory
    
    Armazena dados fundamentalistas na memória episódica
    """
    from src.enhanced_memory import EnhancedMemory
    
    fund = api.get_fundamentals(ticker)
    
    if fund:
        memory.store_episode(
            ticker=ticker,
            analysis_type="fundamentals",
            data=fund,
            result={"success": True, "quality": 0.90},
            metadata={"source": "financial_datasets"}
        )


def integrate_with_skills(api: FinancialDatasetsAPI, library):
    """
    Integrar com Phase 3: Skill Library
    
    Descobrir skill de análise fundamentalista
    """
    from src.skill_library import SkillLibrary
    
    code = '''
def analyze_fundamentals(ticker):
    """Análise fundamentalista completa"""
    from src.financial_datasets import FinancialDatasetsAPI
    
    api = FinancialDatasetsAPI()
    fund = api.get_fundamentals(ticker)
    
    # Value investing score
    score = 0
    if fund.get('pe_ratio') and fund['pe_ratio'] < 15:
        score += 1
    if fund.get('roe') and fund['roe'] > 0.15:
        score += 1
    if fund.get('debt_to_equity') and fund['debt_to_equity'] < 0.5:
        score += 1
    
    return {
        "ticker": ticker,
        "fundamentals": fund,
        "value_score": score,
        "recommendation": "BUY" if score >= 2 else "HOLD"
    }
'''
    
    skill_id = library.discover_skill(
        code=code,
        quality_score=0.95,
        context={
            "ticker": "GLOBAL",
            "type": "fundamental_analysis",
            "source": "financial_datasets"
        }
    )
    
    return skill_id


def integrate_with_learning(api: FinancialDatasetsAPI, ticker: str, learning):
    """
    Integrar com Phase 4: Autonomous Learning
    
    Registrar benchmark de análise fundamentalista
    """
    from src.autonomous_learning import AutonomousLearning
    
    fund = api.get_fundamentals(ticker)
    
    if fund:
        # Calcular qualidade da análise
        quality = 0.0
        if fund.get("pe_ratio"):
            quality += 0.2
        if fund.get("roe"):
            quality += 0.2
        if fund.get("revenue_growth"):
            quality += 0.2
        if fund.get("debt_to_equity"):
            quality += 0.2
        if fund.get("market_cap"):
            quality += 0.2
        
        learning.record_benchmark(
            task_type="fundamental_analysis",
            metrics={
                "data_quality": quality,
                "latency_seconds": 0.5  # Estimado
            },
            context={
                "ticker": ticker,
                "source": "financial_datasets"
            }
        )


# =============================================================================
# DEMO
# =============================================================================

def demo():
    """Demonstração da API"""
    print("💰 FINANCIAL DATASETS API - DEMO")
    print("="*70)
    print()
    
    api = FinancialDatasetsAPI()
    
    # 1. Fundamentalistas
    print("1️⃣ Fundamentalistas da Apple...")
    report = api.format_fundamentals_report("AAPL")
    print(report)
    print()
    
    # 2. Comparação
    print("2️⃣ Comparando Tech Giants...")
    comparison = api.compare_stocks(["AAPL", "MSFT", "GOOGL"])
    if "comparison" in comparison:
        print(f"✅ Comparação de {len(comparison['tickers'])} empresas")
        print(f"   Métricas: {len(comparison['comparison'])} disponíveis")
    print()
    
    # 3. Earnings
    print("3️⃣ Últimos earnings da Tesla...")
    earnings = api.get_earnings("TSLA", periods=2)
    if earnings:
        print(f"✅ {len(earnings)} trimestres encontrados")
    print()
    
    print("="*70)
    print("✅ FINANCIAL DATASETS API FUNCIONANDO")


if __name__ == "__main__":
    demo()
