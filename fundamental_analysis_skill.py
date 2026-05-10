#!/usr/bin/env python3
"""
fundamental_analysis_skill.py - Skill de Análise Fundamentalista

Análise completa de métricas fundamentalistas usando Financial Datasets API
Integra com Phases 1-4 do John Galt

Autor: John Galt v2.0 - Fundamental Analysis Skill
Data: 08/05/2026
"""

from typing import Dict, List, Optional
from financial_datasets import FinancialDatasetsAPI
import statistics


class FundamentalAnalysisSkill:
    """
    Skill de análise fundamentalista completa
    
    Features:
    - Value investing score
    - Quality score
    - Growth score
    - Risk score
    - Recomendação final
    """
    
    def __init__(self):
        self.api = FinancialDatasetsAPI()
    
    def analyze(self, ticker: str) -> Dict:
        """
        Análise fundamentalista completa
        
        Returns:
            Dict com scores, recomendação e detalhes
        """
        # Buscar dados
        fund = self.api.get_fundamentals(ticker)
        
        if not fund:
            return {
                "error": f"Dados não disponíveis para {ticker}",
                "ticker": ticker
            }
        
        # Calcular scores
        value_score = self._calculate_value_score(fund)
        quality_score = self._calculate_quality_score(fund)
        growth_score = self._calculate_growth_score(fund)
        risk_score = self._calculate_risk_score(fund)
        
        # Score final (média ponderada)
        final_score = (
            value_score * 0.30 +
            quality_score * 0.30 +
            growth_score * 0.25 +
            risk_score * 0.15
        )
        
        # Recomendação
        recommendation = self._get_recommendation(final_score)
        
        return {
            "ticker": ticker,
            "fundamentals": fund,
            "scores": {
                "value": value_score,
                "quality": quality_score,
                "growth": growth_score,
                "risk": risk_score,
                "final": final_score
            },
            "recommendation": recommendation,
            "analysis_timestamp": self._get_timestamp()
        }
    
    def _calculate_value_score(self, fund: Dict) -> float:
        """
        Calcular score de valuation (0-10)
        
        Critérios:
        - P/L baixo (< 15 = bom)
        - P/VP baixo (< 3 = bom)
        - Dividend Yield alto (> 3% = bom)
        """
        score = 5.0  # Neutro
        
        # P/L
        pe = fund.get("pe_ratio")
        if pe:
            if pe < 10:
                score += 2.0
            elif pe < 15:
                score += 1.0
            elif pe > 25:
                score -= 1.0
            elif pe > 40:
                score -= 2.0
        
        # P/VP
        pb = fund.get("pb_ratio")
        if pb:
            if pb < 1.0:
                score += 1.5
            elif pb < 3.0:
                score += 0.5
            elif pb > 5.0:
                score -= 1.0
        
        # Dividend Yield
        dy = fund.get("dividend_yield")
        if dy:
            if dy > 0.05:  # > 5%
                score += 1.5
            elif dy > 0.03:  # > 3%
                score += 0.5
        
        return max(0, min(10, score))
    
    def _calculate_quality_score(self, fund: Dict) -> float:
        """
        Calcular score de qualidade (0-10)
        
        Critérios:
        - ROE alto (> 15% = bom)
        - ROA alto (> 10% = bom)
        - Margem líquida alta (> 10% = bom)
        """
        score = 5.0
        
        # ROE
        roe = fund.get("roe")
        if roe:
            if roe > 0.20:  # > 20%
                score += 2.0
            elif roe > 0.15:  # > 15%
                score += 1.0
            elif roe < 0.05:  # < 5%
                score -= 2.0
        
        # ROA
        roa = fund.get("roa")
        if roa:
            if roa > 0.10:  # > 10%
                score += 1.5
            elif roa > 0.05:  # > 5%
                score += 0.5
        
        # Margem Líquida
        margin = fund.get("net_margin")
        if margin:
            if margin > 0.15:  # > 15%
                score += 1.5
            elif margin > 0.10:  # > 10%
                score += 0.5
            elif margin < 0:  # Prejuízo
                score -= 2.0
        
        return max(0, min(10, score))
    
    def _calculate_growth_score(self, fund: Dict) -> float:
        """
        Calcular score de crescimento (0-10)
        
        Critérios:
        - Crescimento de receita (> 15% YoY = bom)
        - Crescimento de lucro (> 15% YoY = bom)
        """
        score = 5.0
        
        # Crescimento de receita
        revenue_growth = fund.get("revenue_growth")
        if revenue_growth:
            if revenue_growth > 0.20:  # > 20%
                score += 2.5
            elif revenue_growth > 0.15:  # > 15%
                score += 1.5
            elif revenue_growth > 0.10:  # > 10%
                score += 0.5
            elif revenue_growth < 0:  # Negativo
                score -= 2.0
        
        # Crescimento de lucro
        earnings_growth = fund.get("earnings_growth")
        if earnings_growth:
            if earnings_growth > 0.20:
                score += 2.5
            elif earnings_growth > 0.15:
                score += 1.5
            elif earnings_growth > 0.10:
                score += 0.5
            elif earnings_growth < 0:
                score -= 2.0
        
        return max(0, min(10, score))
    
    def _calculate_risk_score(self, fund: Dict) -> float:
        """
        Calcular score de risco (0-10, maior = menos risco)
        
        Critérios:
        - Dívida/PL baixo (< 0.5 = bom)
        - Liquidez corrente alta (> 1.5 = bom)
        """
        score = 5.0
        
        # Dívida/PL
        debt_equity = fund.get("debt_to_equity")
        if debt_equity is not None:
            if debt_equity < 0.3:
                score += 2.5
            elif debt_equity < 0.5:
                score += 1.0
            elif debt_equity > 1.0:
                score -= 1.5
            elif debt_equity > 2.0:
                score -= 3.0
        
        # Liquidez Corrente
        current_ratio = fund.get("current_ratio")
        if current_ratio:
            if current_ratio > 2.0:
                score += 2.5
            elif current_ratio > 1.5:
                score += 1.0
            elif current_ratio < 1.0:
                score -= 2.0
        
        return max(0, min(10, score))
    
    def _get_recommendation(self, final_score: float) -> Dict:
        """
        Gerar recomendação baseada no score final
        
        Returns:
            Dict com ação, confiança e justificativa
        """
        if final_score >= 7.5:
            return {
                "action": "STRONG_BUY",
                "confidence": 0.90,
                "rationale": "Fundamentalistas sólidos em todas as dimensões"
            }
        elif final_score >= 6.5:
            return {
                "action": "BUY",
                "confidence": 0.75,
                "rationale": "Fundamentalistas acima da média"
            }
        elif final_score >= 5.5:
            return {
                "action": "HOLD",
                "confidence": 0.60,
                "rationale": "Fundamentalistas neutros"
            }
        elif final_score >= 4.0:
            return {
                "action": "SELL",
                "confidence": 0.70,
                "rationale": "Fundamentalistas abaixo da média"
            }
        else:
            return {
                "action": "STRONG_SELL",
                "confidence": 0.85,
                "rationale": "Fundamentalistas fracos"
            }
    
    def _get_timestamp(self) -> str:
        """Timestamp ISO 8601"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def format_analysis(self, analysis: Dict) -> str:
        """
        Formatar análise para Telegram/console
        
        Returns:
            String formatada
        """
        if "error" in analysis:
            return f"❌ {analysis['error']}"
        
        lines = []
        lines.append(f"📊 **ANÁLISE FUNDAMENTALISTA: {analysis['ticker'].upper()}**")
        lines.append("")
        
        # Scores
        scores = analysis['scores']
        lines.append("**SCORES:**")
        lines.append(f"├ Value: {scores['value']:.1f}/10 {self._get_emoji(scores['value'])}")
        lines.append(f"├ Quality: {scores['quality']:.1f}/10 {self._get_emoji(scores['quality'])}")
        lines.append(f"├ Growth: {scores['growth']:.1f}/10 {self._get_emoji(scores['growth'])}")
        lines.append(f"├ Risk: {scores['risk']:.1f}/10 {self._get_emoji(scores['risk'])}")
        lines.append(f"└ **FINAL: {scores['final']:.1f}/10** {self._get_emoji(scores['final'])}")
        lines.append("")
        
        # Recomendação
        rec = analysis['recommendation']
        lines.append("**RECOMENDAÇÃO:**")
        lines.append(f"├ Ação: **{rec['action']}**")
        lines.append(f"├ Confiança: {rec['confidence']*100:.0f}%")
        lines.append(f"└ Motivo: {rec['rationale']}")
        lines.append("")
        
        # Fundamentalistas
        fund = analysis['fundamentals']
        lines.append("**FUNDAMENTALISTAS:**")
        
        if fund.get("pe_ratio"):
            lines.append(f"├ P/L: {fund['pe_ratio']:.2f}")
        if fund.get("roe"):
            lines.append(f"├ ROE: {fund['roe']*100:.1f}%")
        if fund.get("debt_to_equity"):
            lines.append(f"├ Dívida/PL: {fund['debt_to_equity']:.2f}")
        if fund.get("revenue_growth"):
            lines.append(f"└ Crescimento: {fund['revenue_growth']*100:+.1f}%")
        
        return "\n".join(lines)
    
    def _get_emoji(self, score: float) -> str:
        """Emoji baseado no score"""
        if score >= 7.5:
            return "🟢"
        elif score >= 6.0:
            return "🟡"
        elif score >= 4.0:
            return "🟠"
        else:
            return "🔴"
    
    def compare_stocks(self, tickers: List[str]) -> Dict:
        """
        Comparar múltiplas ações
        
        Returns:
            Dict com análises e ranking
        """
        analyses = []
        
        for ticker in tickers:
            analysis = self.analyze(ticker)
            if "error" not in analysis:
                analyses.append(analysis)
        
        # Ordenar por score final
        analyses.sort(key=lambda x: x['scores']['final'], reverse=True)
        
        return {
            "tickers": tickers,
            "analyses": analyses,
            "ranking": [a['ticker'] for a in analyses],
            "best": analyses[0] if analyses else None,
            "worst": analyses[-1] if analyses else None
        }


# =============================================================================
# DEMO
# =============================================================================

def demo():
    """Demonstração da skill"""
    print("🎯 FUNDAMENTAL ANALYSIS SKILL - DEMO")
    print("="*70)
    print()
    
    skill = FundamentalAnalysisSkill()
    
    # 1. Análise individual
    print("1️⃣ Analisando Apple...")
    analysis = skill.analyze("AAPL")
    formatted = skill.format_analysis(analysis)
    print(formatted)
    print()
    
    # 2. Comparação
    print("2️⃣ Comparando Tech Giants...")
    comparison = skill.compare_stocks(["AAPL", "MSFT", "GOOGL"])
    
    if comparison.get("best"):
        best = comparison['best']
        print(f"✅ Melhor: {best['ticker']} (score: {best['scores']['final']:.1f}/10)")
        print(f"   Recomendação: {best['recommendation']['action']}")
    print()
    
    print("="*70)
    print("✅ FUNDAMENTAL ANALYSIS SKILL FUNCIONANDO")


if __name__ == "__main__":
    demo()
