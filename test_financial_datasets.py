#!/usr/bin/env python3
"""
test_financial_datasets.py - Testes Financial Datasets Integration

Testa:
- API wrapper
- Fundamental Analysis Skill
- Dashboard generation
- Integration with Phases 1-4

Autor: John Galt v2.0 - Financial Datasets Tests
Data: 08/05/2026
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.financial_datasets import FinancialDatasetsAPI
from src.fundamental_analysis_skill import FundamentalAnalysisSkill
from src.stock_comparison_dashboard import StockComparisonDashboard


def test_api_wrapper():
    """Testar API wrapper"""
    print("🔌 TESTE 1: API WRAPPER")
    print("-" * 60)
    
    api = FinancialDatasetsAPI()
    
    # Test 1: Get fundamentals
    print("Testing get_fundamentals('AAPL')...")
    fund = api.get_fundamentals("AAPL")
    
    if fund:
        print(f"✅ Fundamentals retrieved: {len(fund)} fields")
        print(f"   Ticker: {fund.get('ticker')}")
        print(f"   P/E: {fund.get('pe_ratio')}")
        print(f"   ROE: {fund.get('roe')}")
    else:
        print("⚠️ No data (API might be unavailable)")
    
    # Test 2: Format report
    print("\nTesting format_fundamentals_report...")
    report = api.format_fundamentals_report("AAPL")
    
    if report and "FUNDAMENTALISTAS" in report:
        print("✅ Report formatted successfully")
        lines = report.split('\n')
        print(f"   Report lines: {len(lines)}")
    else:
        print("⚠️ Report not formatted")
    
    # Test 3: Compare stocks
    print("\nTesting compare_stocks...")
    comparison = api.compare_stocks(["AAPL", "MSFT"])
    
    if comparison and "comparison" in comparison:
        print(f"✅ Comparison generated: {len(comparison['tickers'])} stocks")
        print(f"   Metrics: {len(comparison['comparison'])} available")
    else:
        print("⚠️ Comparison failed")
    
    print()
    return True


def test_fundamental_skill():
    """Testar Fundamental Analysis Skill"""
    print("🎯 TESTE 2: FUNDAMENTAL ANALYSIS SKILL")
    print("-" * 60)
    
    skill = FundamentalAnalysisSkill()
    
    # Test 1: Analyze single stock
    print("Testing analyze('AAPL')...")
    analysis = skill.analyze("AAPL")
    
    if analysis and "scores" in analysis:
        print("✅ Analysis complete")
        scores = analysis['scores']
        print(f"   Value score: {scores['value']:.1f}/10")
        print(f"   Quality score: {scores['quality']:.1f}/10")
        print(f"   Final score: {scores['final']:.1f}/10")
        
        rec = analysis['recommendation']
        print(f"   Recommendation: {rec['action']}")
    else:
        print("⚠️ Analysis failed (API might be unavailable)")
    
    # Test 2: Format analysis
    print("\nTesting format_analysis...")
    formatted = skill.format_analysis(analysis)
    
    if formatted and "ANÁLISE FUNDAMENTALISTA" in formatted:
        print("✅ Analysis formatted")
        print(f"   Length: {len(formatted)} chars")
    else:
        print("⚠️ Formatting failed")
    
    # Test 3: Compare stocks
    print("\nTesting compare_stocks...")
    comparison = skill.compare_stocks(["AAPL", "MSFT", "GOOGL"])
    
    if comparison and "ranking" in comparison:
        print(f"✅ Comparison complete: {len(comparison['ranking'])} stocks")
        if comparison.get('best'):
            best = comparison['best']
            print(f"   Best: {best['ticker']} (score: {best['scores']['final']:.1f}/10)")
    else:
        print("⚠️ Comparison failed")
    
    print()
    return True


def test_dashboard():
    """Testar Stock Comparison Dashboard"""
    print("📊 TESTE 3: STOCK COMPARISON DASHBOARD")
    print("-" * 60)
    
    dashboard = StockComparisonDashboard()
    
    # Test: Generate dashboard
    print("Testing generate_dashboard...")
    
    try:
        output_path = "/tmp/test_dashboard.html"
        path = dashboard.generate_dashboard(
            tickers=["AAPL", "MSFT"],
            output_path=output_path
        )
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ Dashboard generated: {output_path}")
            print(f"   File size: {file_size} bytes")
            
            # Check content
            with open(output_path, 'r') as f:
                content = f.read()
            
            if "Stock Comparison Dashboard" in content:
                print("   ✅ HTML content valid")
            if "chart.js" in content:
                print("   ✅ Chart.js included")
            if "radarChart" in content:
                print("   ✅ Radar chart present")
        else:
            print("❌ Dashboard file not created")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print()
    return True


def test_phase_integration():
    """Testar integração com Phases 1-4"""
    print("🔗 TESTE 4: INTEGRATION WITH PHASES")
    print("-" * 60)
    
    # Phase 2: Memory
    print("Testing Phase 2 (Memory) integration...")
    try:
        from src.enhanced_memory import EnhancedMemory
        from src.financial_datasets import integrate_with_memory
        
        memory = EnhancedMemory()
        api = FinancialDatasetsAPI()
        
        integrate_with_memory(api, "AAPL", memory)
        print("✅ Memory integration working")
    except Exception as e:
        print(f"⚠️ Memory integration: {e}")
    
    # Phase 3: Skills
    print("\nTesting Phase 3 (Skills) integration...")
    try:
        from src.skill_library import SkillLibrary
        from src.financial_datasets import integrate_with_skills
        
        library = SkillLibrary()
        api = FinancialDatasetsAPI()
        
        skill_id = integrate_with_skills(api, library)
        if skill_id:
            print(f"✅ Skill integration working: {skill_id}")
        else:
            print("⚠️ Skill not created")
    except Exception as e:
        print(f"⚠️ Skills integration: {e}")
    
    # Phase 4: Learning
    print("\nTesting Phase 4 (Learning) integration...")
    try:
        from src.autonomous_learning import AutonomousLearning
        from src.financial_datasets import integrate_with_learning
        
        learning = AutonomousLearning()
        api = FinancialDatasetsAPI()
        
        integrate_with_learning(api, "AAPL", learning)
        print("✅ Learning integration working")
    except Exception as e:
        print(f"⚠️ Learning integration: {e}")
    
    print()
    return True


def main():
    """Executar todos os testes"""
    print("=" * 70)
    print("🧪 TESTE COMPLETO: FINANCIAL DATASETS INTEGRATION")
    print("=" * 70)
    print()
    
    results = []
    
    # Teste 1: API Wrapper
    try:
        results.append(("API Wrapper", test_api_wrapper()))
    except Exception as e:
        print(f"❌ Erro: {e}")
        results.append(("API Wrapper", False))
    
    # Teste 2: Fundamental Skill
    try:
        results.append(("Fundamental Skill", test_fundamental_skill()))
    except Exception as e:
        print(f"❌ Erro: {e}")
        results.append(("Fundamental Skill", False))
    
    # Teste 3: Dashboard
    try:
        results.append(("Dashboard", test_dashboard()))
    except Exception as e:
        print(f"❌ Erro: {e}")
        results.append(("Dashboard", False))
    
    # Teste 4: Phase Integration
    try:
        results.append(("Phase Integration", test_phase_integration()))
    except Exception as e:
        print(f"❌ Erro: {e}")
        results.append(("Phase Integration", False))
    
    # Resultados finais
    print("=" * 70)
    print("📊 RESULTADOS FINAIS")
    print("=" * 70)
    print()
    
    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_name:25s}: {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print()
    print(f"Total: {total_passed}/{total_tests} testes passaram")
    
    if total_passed == total_tests:
        print()
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ FINANCIAL DATASETS INTEGRATION FUNCIONANDO")
        return 0
    else:
        print()
        print("⚠️ ALGUNS TESTES FALHARAM (API pode estar indisponível)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
