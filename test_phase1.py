#!/usr/bin/env python3
"""
Test Script for John Galt Superintelligence - Phase 1

Testa:
1. Agent Swarm Analyzer
2. Reflection Engine
3. Auto Validator
4. Integrated Workflow
"""

import asyncio
import sys
from datetime import datetime

# Add workspace to path
sys.path.insert(0, '/root/.zeroclaw/workspace')

from agent_swarm_analyzer import AgentSwarmAnalyzer
from reflection_engine import ReflectionEngine
from auto_validator import AutoValidator
from john_galt_superintelligence import JohnGaltSuperIntelligence


async def test_agent_swarm():
    """Test 1: Agent Swarm Analyzer"""
    
    print("\n" + "="*70)
    print("TEST 1: AGENT SWARM ANALYZER")
    print("="*70)
    
    analyzer = AgentSwarmAnalyzer()
    
    # Test SOL (cripto)
    result = await analyzer.analyze_parallel("SOL", market="cripto")
    
    print("\n✅ Test SOL completed")
    print(f"Execution time: {result['execution_time_seconds']:.2f}s")
    print(f"Completeness: {result['validation']['completeness']*100:.0f}%")
    
    # Test PETR4 (B3)
    result_b3 = await analyzer.analyze_parallel("PETR4", market="b3")
    
    print("\n✅ Test PETR4 completed")
    print(f"Execution time: {result_b3['execution_time_seconds']:.2f}s")
    print(f"Completeness: {result_b3['validation']['completeness']*100:.0f}%")
    
    return True


def test_reflection_engine():
    """Test 2: Reflection Engine"""
    
    print("\n" + "="*70)
    print("TEST 2: REFLECTION ENGINE")
    print("="*70)
    
    engine = ReflectionEngine()
    
    # Sample analysis
    sample_analysis = """
    SOL Options Analysis
    
    Spot: $88.88
    IV: 85%
    HV: 92%
    
    Strategy: Bull Call Spread
    - Buy Call $88
    - Sell Call $95
    Cost: $2.49
    """
    
    sample_data = {
        "spot_price": 88.88,
        "iv_atm": 85.0,
        "historical_vol": 92.0,
        "timestamp": datetime.now().isoformat()
    }
    
    result = engine.analyze_with_reflection(
        "SOL",
        sample_analysis,
        sample_data
    )
    
    print("\n✅ Reflection completed")
    print(f"Iterations: {result['total_iterations']}")
    print(f"Final Quality: {result['final_quality']:.2f}")
    
    return True


def test_auto_validator():
    """Test 3: Auto Validator"""
    
    print("\n" + "="*70)
    print("TEST 3: AUTO VALIDATOR")
    print("="*70)
    
    validator = AutoValidator()
    
    # Test 1: Valid analysis
    valid_analysis = {
        "timestamp": datetime.now().isoformat(),
        "spot_price": 88.88,
        "iv_atm": 85.0,
        "historical_vol": 92.5,
        "correlation_btc": 0.78,
        "fear_greed_index": 65,
        "black_scholes": {
            "call_price": 3.45,
            "put_price": 2.89,
            "iv": 85.0
        },
        "greeks": {
            "delta": 0.55,
            "theta": -0.12,
            "vega": 0.18,
            "gamma": 0.025
        },
        "recommended_structures": [
            {
                "name": "Bull Call Spread",
                "risk_reward": 2.5,
                "break_even": 90.50,
                "scenarios": {}
            }
        ]
    }
    
    validation = validator.validate(valid_analysis, market="cripto")
    
    print("\n✅ Validation completed")
    print(f"Valid: {validation['valid']}")
    print(f"Score: {validation['score']:.2f}")
    print(f"Errors: {len(validation['errors'])}")
    print(f"Warnings: {len(validation['warnings'])}")
    
    # Test 2: Invalid analysis (missing data)
    invalid_analysis = {
        "timestamp": datetime.now().isoformat(),
        "spot_price": 88.88
        # Missing required fields
    }
    
    validation_invalid = validator.validate(invalid_analysis, market="cripto")
    
    print("\n✅ Validation (invalid data) completed")
    print(f"Valid: {validation_invalid['valid']}")
    print(f"Score: {validation_invalid['score']:.2f}")
    print(f"Errors: {len(validation_invalid['errors'])}")
    
    return True


async def test_integrated_workflow():
    """Test 4: Integrated Workflow"""
    
    print("\n" + "="*70)
    print("TEST 4: INTEGRATED WORKFLOW")
    print("="*70)
    
    si = JohnGaltSuperIntelligence()
    
    # Test complete workflow
    result = await si.analyze_with_superintelligence(
        ticker="SOL",
        market="cripto",
        user_query="Analise opções de SOL"
    )
    
    print("\n✅ Integrated workflow completed")
    print(f"Approved: {result['approved']}")
    print(f"Reflection iterations: {result['reflection']['total_iterations']}")
    print(f"Reflection quality: {result['reflection']['final_quality']:.2f}")
    print(f"Validation score: {result['validation']['score']:.2f}")
    print(f"Swarm execution time: {result['swarm_execution_time']:.2f}s")
    
    return True


async def run_all_tests():
    """Run all tests"""
    
    print("\n" + "="*70)
    print("🧪 JOHN GALT SUPERINTELLIGENCE - PHASE 1 TESTS")
    print("="*70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    tests = [
        ("Agent Swarm", test_agent_swarm()),
        ("Reflection Engine", test_reflection_engine()),
        ("Auto Validator", test_auto_validator()),
        ("Integrated Workflow", test_integrated_workflow())
    ]
    
    results = []
    
    for name, test_coro in tests:
        try:
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
            results.append((name, "✅ PASSED", None))
        except Exception as e:
            results.append((name, "❌ FAILED", str(e)))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for name, status, error in results:
        print(f"{status} {name}")
        if error:
            print(f"  Error: {error}")
    
    passed = sum(1 for _, status, _ in results if status == "✅ PASSED")
    total = len(results)
    
    print("\n" + "="*70)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("="*70)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
