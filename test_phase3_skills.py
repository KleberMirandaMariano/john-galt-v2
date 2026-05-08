#!/usr/bin/env python3
"""
test_phase3_skills.py - Teste do sistema Skill Library

Testa:
- Pattern extraction
- Skill discovery
- Skill retrieval
- Skill composition

Autor: John Galt v2.0 - Phase 3
Data: 08/05/2026
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.skill_library import SkillLibrary
import json


def test_pattern_extraction():
    """Testar extração de padrões"""
    print("🔍 TESTE 1: PATTERN EXTRACTION")
    print("-" * 60)
    
    library = SkillLibrary()
    
    # Código de exemplo
    code = '''
import requests
from scipy.stats import norm

def calculate_iv(price, S, K, T, r):
    """Calculate implied volatility"""
    # Implementation here
    return iv

def fetch_data(ticker):
    """Fetch market data"""
    url = f"https://api.example.com/data/{ticker}"
    return requests.get(url).json()
'''
    
    context = {"ticker": "SOL", "type": "options"}
    
    # Extrair padrões
    code_patterns = library.extract_patterns_from_code(code, context)
    api_patterns = library.extract_api_patterns(code, context)
    
    print(f"✅ Padrões de código: {len(code_patterns)}")
    for p in code_patterns:
        if p['type'] == 'function':
            print(f"   - Função: {p['name']}() com {len(p['args'])} args")
        elif p['type'] in ['import', 'import_from']:
            print(f"   - Import: {p.get('module', 'N/A')}")
    
    print(f"✅ Padrões de API: {len(api_patterns)}")
    for p in api_patterns:
        print(f"   - API: {p['api_type']} ({p['url'][:50]}...)")
    
    print()
    return True


def test_skill_discovery():
    """Testar descoberta de skills"""
    print("🎯 TESTE 2: SKILL DISCOVERY")
    print("-" * 60)
    
    library = SkillLibrary()
    
    # Código de análise bem-sucedida
    code = '''
def analyze_option_spread(spot, strike_long, strike_short, iv, days):
    """Analyze bull call spread"""
    from scipy.stats import norm
    import numpy as np
    
    T = days / 365
    r = 0.05
    
    # Calculate prices
    # ... implementation ...
    
    return {
        'cost': cost,
        'max_gain': max_gain,
        'roi': roi
    }
'''
    
    # Descobrir skill
    skill_id = library.discover_skill(
        code=code,
        quality_score=0.90,
        context={
            "ticker": "SOL",
            "type": "options",
            "approach": "black_scholes"
        }
    )
    
    if skill_id:
        print(f"✅ Skill descoberta: {skill_id}")
        
        # Ver estatísticas
        stats = library.get_skill_stats(skill_id)
        print(f"   Nome: {stats['name']}")
        print(f"   Qualidade: {stats['quality_score']:.2f}")
        print(f"   Padrões: {stats['pattern_count']}")
    else:
        print("❌ Nenhuma skill descoberta")
        return False
    
    print()
    return True


def test_skill_retrieval():
    """Testar busca de skills relevantes"""
    print("🔎 TESTE 3: SKILL RETRIEVAL")
    print("-" * 60)
    
    library = SkillLibrary()
    
    # Criar algumas skills de teste
    for i in range(3):
        code = f'''
def test_function_{i}():
    """Test function {i}"""
    return {i}
'''
        library.discover_skill(
            code=code,
            quality_score=0.85 + (i * 0.02),
            context={
                "ticker": "SOL" if i % 2 == 0 else "PETR4",
                "type": "options"
            }
        )
    
    # Buscar skills relevantes
    relevant = library.find_relevant_skills("SOL", "options", limit=5)
    
    print(f"✅ Skills relevantes encontradas: {len(relevant)}")
    for skill in relevant:
        print(f"   - {skill['name']}")
        print(f"     Relevância: {skill['relevance']:.2f}")
        print(f"     Qualidade: {skill['quality_score']:.2f}")
    
    print()
    return True


def test_skill_composition():
    """Testar composição de skills"""
    print("🧩 TESTE 4: SKILL COMPOSITION")
    print("-" * 60)
    
    library = SkillLibrary()
    
    # Criar skill com código
    code = '''
import numpy as np
from scipy.stats import norm

def black_scholes(S, K, T, r, sigma):
    """Black-Scholes pricing"""
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    return S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d1 - sigma*np.sqrt(T))
'''
    
    skill_id = library.discover_skill(
        code=code,
        quality_score=0.95,
        context={"ticker": "SOL", "type": "options"}
    )
    
    if not skill_id:
        print("❌ Não foi possível criar skill para teste")
        return False
    
    # Compor código
    composed = library.compose_skills([skill_id])
    
    if composed:
        lines = composed.split('\n')
        print(f"✅ Código composto ({len(lines)} linhas)")
        print("   Primeiras linhas:")
        for line in lines[:5]:
            print(f"   {line}")
    else:
        print("❌ Nenhum código composto")
        return False
    
    print()
    return True


def test_library_summary():
    """Testar sumário da biblioteca"""
    print("📊 TESTE 5: LIBRARY SUMMARY")
    print("-" * 60)
    
    library = SkillLibrary()
    summary = library.get_library_summary()
    
    print("Sumário da biblioteca:")
    print(f"   Total de skills: {summary['total_skills']}")
    print(f"   Por tipo: {summary['by_type']}")
    print(f"   Por ticker: {summary['by_ticker']}")
    print(f"   Total de padrões: {summary['total_patterns']}")
    
    if summary['top_skills']:
        print(f"   Top skill: {summary['top_skills'][0]['name']}")
    
    print()
    return True


def main():
    """Executar todos os testes"""
    print("=" * 70)
    print("🧪 TESTE COMPLETO: SKILL LIBRARY SYSTEM (PHASE 3)")
    print("=" * 70)
    print()
    
    results = []
    
    # Teste 1: Pattern Extraction
    try:
        results.append(("Pattern Extraction", test_pattern_extraction()))
    except Exception as e:
        print(f"❌ Erro: {e}")
        results.append(("Pattern Extraction", False))
    
    # Teste 2: Skill Discovery
    try:
        results.append(("Skill Discovery", test_skill_discovery()))
    except Exception as e:
        print(f"❌ Erro: {e}")
        results.append(("Skill Discovery", False))
    
    # Teste 3: Skill Retrieval
    try:
        results.append(("Skill Retrieval", test_skill_retrieval()))
    except Exception as e:
        print(f"❌ Erro: {e}")
        results.append(("Skill Retrieval", False))
    
    # Teste 4: Skill Composition
    try:
        results.append(("Skill Composition", test_skill_composition()))
    except Exception as e:
        print(f"❌ Erro: {e}")
        results.append(("Skill Composition", False))
    
    # Teste 5: Library Summary
    try:
        results.append(("Library Summary", test_library_summary()))
    except Exception as e:
        print(f"❌ Erro: {e}")
        results.append(("Library Summary", False))
    
    # Resultados finais
    print("=" * 70)
    print("📊 RESULTADOS FINAIS")
    print("=" * 70)
    print()
    
    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_name:20s}: {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print()
    print(f"Total: {total_passed}/{total_tests} testes passaram")
    
    if total_passed == total_tests:
        print()
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ FASE 3: SKILL LIBRARY FUNCIONANDO")
        return 0
    else:
        print()
        print("⚠️ ALGUNS TESTES FALHARAM")
        return 1


if __name__ == "__main__":
    sys.exit(main())
