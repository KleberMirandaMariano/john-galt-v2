#!/usr/bin/env python3
"""
Integrated Workflow for John Galt - Phase 1
Combines: Agent Swarm + Reflection + Validation

Workflow:
1. Agent Swarm busca TODOS os dados em paralelo
2. Gera análise inicial com dados consolidados
3. Reflection Engine critica e refina
4. Auto Validator valida qualidade
5. Retorna análise aprovada ou erros
"""

import asyncio
import sys
import os
from typing import Dict
from datetime import datetime
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from latency_tracker import LatencyTracker
from agent_swarm_a2a import AgentSwarmA2A

from agent_swarm_analyzer import AgentSwarmAnalyzer
from reflection_engine import ReflectionEngine
from auto_validator import AutoValidator


class JohnGaltSuperIntelligence:
    """
    Sistema de Superinteligência Fase 1

    Características:
    - Agent Swarm A2A: agentes se comunicam via pub/sub e req/reply durante execução
    - Latência instrumentada por step com P50/P95 histórico
    - Autocrítica e refinamento (até 3 iterações)
    - Validação automática de qualidade
    """

    def __init__(self, use_a2a: bool = True):
        # use_a2a=True → AgentSwarmA2A (A2A); False → AgentSwarmAnalyzer original
        self.swarm = AgentSwarmA2A() if use_a2a else AgentSwarmAnalyzer()
        self.use_a2a = use_a2a
        self.reflection = ReflectionEngine()
        self.validator = AutoValidator()
    
    async def analyze_with_superintelligence(
        self,
        ticker: str,
        market: str = "cripto",
        user_query: str = None
    ) -> Dict:
        """
        Análise completa com superinteligência
        
        Args:
            ticker: Ticker para analisar
            market: "cripto" ou "b3"
            user_query: Query original do usuário (opcional)
        
        Returns:
            Dict com análise final validada
        """
        
        tracker = LatencyTracker()

        print("\n" + "="*70)
        print("🧠 JOHN GALT SUPERINTELLIGENCE - PHASE 1")
        print("="*70)
        print(f"Ticker: {ticker}")
        print(f"Market: {market}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")

        # STEP 1: Agent Swarm - Busca paralela de dados
        print("STEP 1: 🚀 AGENT SWARM - Parallel Data Fetching")
        print("-" * 70)

        with tracker.step("agent_swarm"):
            swarm_result = await self.swarm.analyze_parallel(ticker, market)
        data_sources = swarm_result["data"]

        print(f"  ✅ Data collected in {tracker.steps['agent_swarm']:.2f}s")
        print(f"  ✅ Completeness: {swarm_result['validation']['completeness']*100:.0f}%")

        if not swarm_result["validation"]["complete"]:
            print(f"  ⚠️  Missing: {swarm_result['validation']['missing_fields']}")

        # STEP 2: Gerar análise inicial
        print("\nSTEP 2: 📊 Generating Initial Analysis")
        print("-" * 70)

        with tracker.step("initial_analysis"):
            initial_analysis = self._generate_initial_analysis(
                ticker,
                data_sources,
                market
            )

        print(f"  ✅ Initial analysis generated in {tracker.steps['initial_analysis']:.2f}s")

        # STEP 3: Reflection Engine - Autocrítica e refinamento
        print("\nSTEP 3: 🔄 REFLECTION ENGINE - Self-Critique & Refinement")
        print("-" * 70)

        with tracker.step("reflection_engine"):
            reflection_result = self.reflection.analyze_with_reflection(
                ticker,
                initial_analysis,
                data_sources
            )

        final_analysis = reflection_result["final_analysis"]

        print(f"  ✅ Reflection completed in {tracker.steps['reflection_engine']:.2f}s")
        print(f"  ✅ Iterations: {reflection_result['total_iterations']}")
        print(f"  ✅ Final Quality: {reflection_result['final_quality']:.2f}")

        # STEP 4: Auto Validator - Validação final
        print("\nSTEP 4: ✅ AUTO VALIDATOR - Final Quality Check")
        print("-" * 70)

        analysis_dict = {
            "timestamp": datetime.now().isoformat(),
            **data_sources
        }

        with tracker.step("auto_validator"):
            validation = self.validator.validate(analysis_dict, market)

        print(f"  Status: {'✅ PASSED' if validation['valid'] else '❌ FAILED'}")
        print(f"  Score: {validation['score']:.2f}")
        print(f"  Checks: {validation['checks_passed']}/{validation['total_checks']}")

        if validation["errors"]:
            print(f"  🚨 Errors: {len(validation['errors'])}")
            for error in validation["errors"]:
                print(f"    - {error}")

        if validation["warnings"]:
            print(f"  ⚠️  Warnings: {len(validation['warnings'])}")
            for warning in validation["warnings"]:
                print(f"    - {warning}")

        # Latency report
        latency_record = tracker.flush(ticker, market, approved=validation["valid"])
        regressions = tracker.check_regressions(threshold=2.0)

        print("\n" + "="*70)
        print(tracker.summary())

        if regressions:
            print("\n  ⚠️  REGRESSÕES DE LATÊNCIA DETECTADAS:")
            for r in regressions:
                print(f"    - {r['step']}: {r['elapsed_s']:.2f}s ({r['ratio']}x P95={r['p95_s']:.2f}s)")

        print("\n" + "="*70)
        if validation["valid"]:
            print("✅ ANALYSIS APPROVED - Ready to send!")
        else:
            print("❌ ANALYSIS REJECTED - Fix errors before sending")
        print("="*70 + "\n")

        a2a_log = swarm_result.get("message_log", []) if self.use_a2a else []

        return {
            "ticker": ticker,
            "market": market,
            "timestamp": datetime.now().isoformat(),
            "analysis": final_analysis,
            "data_sources": data_sources,
            "reflection": {
                "iterations": reflection_result["iterations"],
                "total_iterations": reflection_result["total_iterations"],
                "final_quality": reflection_result["final_quality"]
            },
            "validation": validation,
            "latency": {
                "run_id": tracker.run_id,
                "steps": tracker.steps,
                "total_s": tracker.total,
                "regressions": regressions,
            },
            "a2a": {
                "enabled": self.use_a2a,
                "messages": len(a2a_log),
                "log": a2a_log,
                "vol_regime": data_sources.get("vol_regime"),
                "chain_depth": data_sources.get("chain_depth"),
            },
            "approved": validation["valid"]
        }
    
    def _generate_initial_analysis(
        self,
        ticker: str,
        data: Dict,
        market: str
    ) -> str:
        """
        Gera análise inicial com dados coletados
        
        Args:
            ticker: Ticker
            data: Dados consolidados do Agent Swarm
            market: Mercado
        
        Returns:
            String com análise inicial
        """
        
        # Aqui você integraria com Claude API para gerar análise
        # Por enquanto, vou gerar template
        
        analysis_parts = []
        
        # Header
        analysis_parts.append(f"# {ticker} Options Analysis")
        analysis_parts.append(f"Market: {market.upper()}")
        analysis_parts.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        analysis_parts.append("")
        
        # Market Data
        analysis_parts.append("## Market Data")
        analysis_parts.append(f"- Spot Price: ${data.get('spot_price', 'N/A'):.2f}")
        analysis_parts.append(f"- Historical Vol (30d): {data.get('historical_vol', 'N/A'):.1f}%")
        analysis_parts.append(f"- Implied Vol (ATM): {data.get('iv_atm', 'N/A'):.1f}%")
        
        if market == "cripto":
            analysis_parts.append(f"- BTC Correlation: {data.get('correlation_btc', 'N/A'):.2f}")
            analysis_parts.append(f"- Fear & Greed: {data.get('fear_greed_index', 'N/A')} ({data.get('fear_greed_status', 'N/A')})")
        
        analysis_parts.append("")
        
        # Volatility Analysis
        hv = data.get('historical_vol', 0)
        iv = data.get('iv_atm', 0)
        
        if hv and iv:
            iv_hv_ratio = iv / hv
            analysis_parts.append("## Volatility Analysis")
            analysis_parts.append(f"- IV/HV Ratio: {iv_hv_ratio:.2f}")
            
            if iv_hv_ratio > 1.2:
                analysis_parts.append("- **Vender volatilidade** (IV elevado)")
            elif iv_hv_ratio < 0.8:
                analysis_parts.append("- **Comprar volatilidade** (IV baixo)")
            else:
                analysis_parts.append("- Volatilidade neutra")
            
            analysis_parts.append("")
        
        # TODO: Adicionar Black-Scholes, Greeks, estruturas recomendadas
        
        return "\n".join(analysis_parts)


# Exemplo de uso
async def main():
    """Demo do sistema completo"""
    
    si = JohnGaltSuperIntelligence()
    
    # Análise SOL
    result = await si.analyze_with_superintelligence(
        ticker="SOL",
        market="cripto",
        user_query="Analise opções de SOL e sugira estratégias"
    )
    
    # Salvar resultado
    output_file = "/tmp/john_galt_analysis_sol.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n📄 Result saved to: {output_file}")
    
    # Mostrar análise final
    print("\n" + "="*70)
    print("FINAL ANALYSIS")
    print("="*70)
    print(result["analysis"])


if __name__ == "__main__":
    asyncio.run(main())
