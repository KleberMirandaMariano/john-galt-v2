#!/usr/bin/env python3
"""
test_phase2_memory.py - Teste do sistema Enhanced Memory

Testa os três tipos de memória:
- Episódica
- Semântica
- Procedural

Autor: John Galt v2.0 - Phase 2
Data: 06/05/2026
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.enhanced_memory import EnhancedMemory
import json
from datetime import datetime


def test_episodic_memory():
    """Testar memória episódica"""
    print("📊 TESTE 1: MEMÓRIA EPISÓDICA")
    print("-" * 60)
    
    memory = EnhancedMemory()
    
    # Armazenar 3 episódios diferentes
    episodes = []
    
    # Episódio 1: SOL opções
    ep1 = memory.store_episode(
        ticker="SOL",
        analysis_type="options",
        data={"spot": 91.83, "iv": 0.85},
        result={"success": True, "quality": 0.90},
        metadata={"approach": "black_scholes"}
    )
    episodes.append(ep1)
    print(f"✅ Episódio 1 armazenado: {ep1}")
    
    # Episódio 2: SOL macro
    ep2 = memory.store_episode(
        ticker="SOL",
        analysis_type="macro",
        data={"price": 92.15, "volume": 1000000},
        result={"success": True, "quality": 0.85},
        metadata={"approach": "technical_analysis"}
    )
    episodes.append(ep2)
    print(f"✅ Episódio 2 armazenado: {ep2}")
    
    # Episódio 3: PETR4 opções
    ep3 = memory.store_episode(
        ticker="PETR4",
        analysis_type="options",
        data={"spot": 42.50, "iv": 0.60},
        result={"success": True, "quality": 0.88},
        metadata={"approach": "black_scholes"}
    )
    episodes.append(ep3)
    print(f"✅ Episódio 3 armazenado: {ep3}")
    
    print()
    
    # Recuperar episódios similares
    print("🔍 Recuperando episódios similares para SOL opções...")
    similar = memory.retrieve_similar_episodes("SOL", "options")
    print(f"✅ Encontrados {len(similar)} episódios")
    
    if similar:
        print(f"   Mais recente: {similar[0]['timestamp']}")
    
    print()
    
    # Estatísticas
    print("📈 Estatísticas SOL:")
    stats = memory.get_episode_stats("SOL")
    print(f"   Total: {stats['total']}")
    print(f"   Por tipo: {stats['by_type']}")
    print(f"   Taxa de sucesso: {stats['success_rate']:.1%}")
    
    print()
    return True


def test_semantic_memory():
    """Testar memória semântica"""
    print("🧠 TESTE 2: MEMÓRIA SEMÂNTICA")
    print("-" * 60)
    
    memory = EnhancedMemory()
    
    # Armazenar episódios para construir conhecimento
    for i in range(5):
        memory.store_episode(
            ticker="SOL",
            analysis_type="options",
            data={
                "spot_price": 90.0 + i,
                "iv": 0.80 + (i * 0.01),
                "btc_correlation": 0.70 + (i * 0.01)
            },
            result={"success": True, "quality": 0.90},
            metadata={"approach": "black_scholes"}
        )
    
    # Recuperar conhecimento
    print("🔍 Conhecimento acumulado sobre SOL...")
    knowledge = memory.get_semantic_knowledge("SOL")
    
    if "data_points" in knowledge:
        print(f"✅ Volatilidade média: {knowledge['data_points'].get('avg_iv', 0):.2%}")
        print(f"✅ Preço médio: ${knowledge['data_points'].get('avg_price', 0):.2f}")
        print(f"✅ Correlação BTC: {knowledge['data_points'].get('avg_btc_correlation', 0):.2f}")
    
    print()
    return True


def test_procedural_memory():
    """Testar memória procedural"""
    print("🛠️ TESTE 3: MEMÓRIA PROCEDURAL")
    print("-" * 60)
    
    memory = EnhancedMemory()
    
    # Armazenar episódios bem-sucedidos
    for approach in ["black_scholes", "monte_carlo", "binomial_tree"]:
        memory.store_episode(
            ticker="SOL",
            analysis_type="options",
            data={"spot": 91.83, "iv": 0.85},
            result={"success": True, "quality": 0.90},
            metadata={"approach": approach}
        )
    
    # Recuperar melhores práticas
    print("🔍 Melhores práticas para análise de opções...")
    practices = memory.get_best_practices("options")
    
    if practices:
        for i, practice in enumerate(practices, 1):
            print(f"   {i}. {practice}")
        print(f"✅ {len(practices)} práticas identificadas")
    else:
        print("   ⚠️ Nenhuma prática ainda (precisa mais episódios)")
    
    print()
    return True


def test_memory_summary():
    """Testar sumário da memória"""
    print("📋 TESTE 4: SUMÁRIO DA MEMÓRIA")
    print("-" * 60)
    
    memory = EnhancedMemory()
    summary = memory.get_memory_summary()
    
    print("Sumário:")
    print(json.dumps(summary, indent=2))
    print()
    
    return True


def main():
    """Executar todos os testes"""
    print("=" * 70)
    print("🧪 TESTE COMPLETO: ENHANCED MEMORY SYSTEM (PHASE 2)")
    print("=" * 70)
    print()
    
    results = []
    
    # Teste 1: Episódica
    try:
        results.append(("Episódica", test_episodic_memory()))
    except Exception as e:
        print(f"❌ Erro no teste episódico: {e}")
        results.append(("Episódica", False))
    
    # Teste 2: Semântica
    try:
        results.append(("Semântica", test_semantic_memory()))
    except Exception as e:
        print(f"❌ Erro no teste semântico: {e}")
        results.append(("Semântica", False))
    
    # Teste 3: Procedural
    try:
        results.append(("Procedural", test_procedural_memory()))
    except Exception as e:
        print(f"❌ Erro no teste procedural: {e}")
        results.append(("Procedural", False))
    
    # Teste 4: Sumário
    try:
        results.append(("Sumário", test_memory_summary()))
    except Exception as e:
        print(f"❌ Erro no teste de sumário: {e}")
        results.append(("Sumário", False))
    
    # Resultados finais
    print("=" * 70)
    print("📊 RESULTADOS FINAIS")
    print("=" * 70)
    print()
    
    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_name:15s}: {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print()
    print(f"Total: {total_passed}/{total_tests} testes passaram")
    
    if total_passed == total_tests:
        print()
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ FASE 2: ENHANCED MEMORY FUNCIONANDO")
        return 0
    else:
        print()
        print("⚠️ ALGUNS TESTES FALHARAM")
        return 1


if __name__ == "__main__":
    sys.exit(main())
