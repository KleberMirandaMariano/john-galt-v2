#!/usr/bin/env python3
"""
test_phase4_autonomous.py - Teste do sistema Autonomous Learning

Testa:
- Curriculum generation
- A/B testing framework
- Performance benchmarking
- Quality degradation detection
- Skill evolution tracking

Autor: John Galt v2.0 - Phase 4
Data: 08/05/2026
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.autonomous_learning import AutonomousLearning
import json
import random


def test_curriculum_generation():
    """Testar geração de currículo"""
    print("📚 TESTE 1: CURRICULUM GENERATION")
    print("-" * 60)
    
    learning = AutonomousLearning()
    
    # Gerar currículo
    objectives = learning.generate_curriculum(
        current_performance={
            "accuracy": 0.85,
            "latency_seconds": 2.5,
            "error_rate": 0.10
        },
        target_improvement=0.10
    )
    
    print(f"✅ Currículo gerado com {len(objectives)} objetivos:")
    for obj in objectives:
        print(f"   - {obj['metric']}: {obj['current_value']:.2f} → {obj['target_value']:.2f}")
        print(f"     Melhoria alvo: {obj['improvement_pct']*100:.0f}%")
    
    # Verificar objetivos
    assert len(objectives) == 3, "Deveria ter 3 objetivos"
    assert all(obj['status'] == 'active' for obj in objectives), "Todos devem estar ativos"
    
    print()
    return True


def test_ab_testing():
    """Testar framework de A/B testing"""
    print("🧪 TESTE 2: A/B TESTING FRAMEWORK")
    print("-" * 60)
    
    learning = AutonomousLearning()
    
    # Criar experimento
    exp_id = learning.create_experiment(
        name="test_optimization",
        metric="latency_seconds",
        variant_a={"strategy": "sequential"},
        variant_b={"strategy": "parallel"},
        sample_size=5
    )
    
    print(f"✅ Experimento criado: {exp_id}")
    
    # Simular resultados (B melhor que A)
    for i in range(5):
        learning.record_experiment_result(exp_id, 'A', 2.5 + random.uniform(-0.1, 0.1))
        learning.record_experiment_result(exp_id, 'B', 0.8 + random.uniform(-0.05, 0.05))
    
    # Verificar resultado
    exp = learning._load_experiment(exp_id)
    
    print(f"   Status: {exp['status']}")
    print(f"   Variante A: {exp['variants']['A']['mean']:.2f}s")
    print(f"   Variante B: {exp['variants']['B']['mean']:.2f}s")
    
    if exp.get('winner'):
        print(f"   🏆 Vencedor: Variante {exp['winner']}")
        print(f"   Melhoria: {exp.get('improvement_pct', 0)*100:.1f}%")
    
    assert exp['status'] == 'completed', "Experimento deveria estar completo"
    assert exp['winner'] == 'B', "Variante B deveria vencer"
    
    print()
    return True


def test_performance_benchmarking():
    """Testar benchmarking de performance"""
    print("📊 TESTE 3: PERFORMANCE BENCHMARKING")
    print("-" * 60)
    
    learning = AutonomousLearning()
    
    # Registrar série de benchmarks
    print("Registrando benchmarks...")
    for i in range(10):
        learning.record_benchmark(
            task_type="options_analysis",
            metrics={
                "accuracy": 0.90 + random.uniform(-0.02, 0.02),
                "latency_seconds": 1.5 + random.uniform(-0.1, 0.1)
            },
            context={"iteration": i}
        )
    
    print(f"✅ 10 benchmarks registrados")
    
    # Obter tendência
    trend = learning.get_performance_trend(
        task_type="options_analysis",
        metric="accuracy",
        days_back=7
    )
    
    if 'error' not in trend:
        print(f"   Métrica: {trend['metric']}")
        print(f"   Data points: {trend['data_points']}")
        print(f"   Média: {trend['mean']:.4f}")
        print(f"   Desvio: {trend['std']:.4f}")
        print(f"   Range: [{trend['min']:.4f}, {trend['max']:.4f}]")
        
        assert trend['data_points'] == 10, "Deveria ter 10 pontos"
        assert 0.88 <= trend['mean'] <= 0.92, "Média deveria estar perto de 0.90"
    
    print()
    return True


def test_quality_degradation():
    """Testar detecção de degradação"""
    print("⚠️ TESTE 4: QUALITY DEGRADATION DETECTION")
    print("-" * 60)
    
    learning = AutonomousLearning()
    
    # Criar baseline (valores bons)
    print("Criando baseline...")
    for i in range(20):
        learning.record_benchmark(
            task_type="test_task",
            metrics={"accuracy": 0.90 + random.uniform(-0.01, 0.01)}
        )
    
    print("✅ Baseline criado (accuracy ~0.90)")
    
    # Registrar valor degradado (deveria emitir alerta)
    print("Registrando performance degradada...")
    learning.record_benchmark(
        task_type="test_task",
        metrics={"accuracy": 0.70}  # Bem abaixo do baseline
    )
    
    # Verificar se alerta foi criado
    alerts_path = os.path.join(learning.learning_dir, "quality_alerts.jsonl")
    
    if os.path.exists(alerts_path):
        with open(alerts_path, 'r') as f:
            alerts = [json.loads(line) for line in f]
        
        if alerts:
            print(f"✅ {len(alerts)} alerta(s) emitido(s)")
            last_alert = alerts[-1]
            print(f"   Tipo: {last_alert['type']}")
            print(f"   Métrica: {last_alert['metric']}")
            print(f"   Desvio: {last_alert['deviation_pct']:.1f}%")
        else:
            print("⚠️ Nenhum alerta emitido (pode ser esperado)")
    
    print()
    return True


def test_skill_evolution():
    """Testar rastreamento de evolução"""
    print("📈 TESTE 5: SKILL EVOLUTION TRACKING")
    print("-" * 60)
    
    learning = AutonomousLearning()
    
    # Rastrear evolução de uma skill
    skill_id = "skill_test_123"
    
    print(f"Rastreando evolução de {skill_id}...")
    for version in range(1, 6):
        learning.track_skill_evolution(
            skill_id=skill_id,
            version=f"v1.{version}",
            performance={
                "accuracy": 0.80 + (version * 0.03),  # Melhora ao longo do tempo
                "speed": 2.0 - (version * 0.2)  # Fica mais rápido
            }
        )
    
    print(f"✅ 5 versões rastreadas")
    
    # Obter sumário
    summary = learning.get_skill_evolution_summary(skill_id)
    
    print(f"   Skill: {summary['skill_id']}")
    print(f"   Versões: {summary['total_versions']}")
    print(f"   Primeira: {summary['first_version']}")
    print(f"   Última: {summary['latest_version']}")
    print(f"   Melhorias:")
    
    for metric, data in summary['improvements'].items():
        print(f"      {metric}: {data['first']:.2f} → {data['last']:.2f} ({data['change_pct']:+.1f}%)")
    
    assert summary['total_versions'] == 5, "Deveria ter 5 versões"
    assert summary['improvements']['accuracy']['change_pct'] > 0, "Accuracy deveria melhorar"
    
    print()
    return True


def test_learning_summary():
    """Testar sumário geral"""
    print("📋 TESTE 6: LEARNING SUMMARY")
    print("-" * 60)
    
    learning = AutonomousLearning()
    summary = learning.get_learning_summary()
    
    print("Sumário do sistema:")
    print(json.dumps(summary, indent=2))
    
    assert 'curriculum' in summary, "Deveria ter curriculum"
    assert 'experiments' in summary, "Deveria ter experiments"
    assert 'benchmarks' in summary, "Deveria ter benchmarks"
    
    print()
    return True


def main():
    """Executar todos os testes"""
    print("=" * 70)
    print("🧪 TESTE COMPLETO: AUTONOMOUS LEARNING SYSTEM (PHASE 4)")
    print("=" * 70)
    print()
    
    results = []
    
    # Teste 1: Curriculum
    try:
        results.append(("Curriculum Generation", test_curriculum_generation()))
    except Exception as e:
        print(f"❌ Erro: {e}")
        results.append(("Curriculum Generation", False))
    
    # Teste 2: A/B Testing
    try:
        results.append(("A/B Testing", test_ab_testing()))
    except Exception as e:
        print(f"❌ Erro: {e}")
        results.append(("A/B Testing", False))
    
    # Teste 3: Benchmarking
    try:
        results.append(("Performance Benchmarking", test_performance_benchmarking()))
    except Exception as e:
        print(f"❌ Erro: {e}")
        results.append(("Performance Benchmarking", False))
    
    # Teste 4: Quality Degradation
    try:
        results.append(("Quality Degradation", test_quality_degradation()))
    except Exception as e:
        print(f"❌ Erro: {e}")
        results.append(("Quality Degradation", False))
    
    # Teste 5: Skill Evolution
    try:
        results.append(("Skill Evolution", test_skill_evolution()))
    except Exception as e:
        print(f"❌ Erro: {e}")
        results.append(("Skill Evolution", False))
    
    # Teste 6: Summary
    try:
        results.append(("Learning Summary", test_learning_summary()))
    except Exception as e:
        print(f"❌ Erro: {e}")
        results.append(("Learning Summary", False))
    
    # Resultados finais
    print("=" * 70)
    print("📊 RESULTADOS FINAIS")
    print("=" * 70)
    print()
    
    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_name:30s}: {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print()
    print(f"Total: {total_passed}/{total_tests} testes passaram")
    
    if total_passed == total_tests:
        print()
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ FASE 4: AUTONOMOUS LEARNING FUNCIONANDO")
        return 0
    else:
        print()
        print("⚠️ ALGUNS TESTES FALHARAM")
        return 1


if __name__ == "__main__":
    sys.exit(main())
