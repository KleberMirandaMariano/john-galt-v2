#!/usr/bin/env python3
"""
autonomous_learning.py - Phase 4: Autonomous Learning System

Sistema de aprendizado autônomo completo:
1. Self-Improvement Curriculum
2. Performance Benchmarking
3. A/B Testing Framework
4. Self-Fine-Tuning Loops
5. Skill Evolution Tracking
6. Quality Degradation Detection

Autor: John Galt v2.0 - Phase 4
Data: 08/05/2026
"""

import json
import os
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import hashlib


class AutonomousLearning:
    """
    Sistema de aprendizado autônomo para John Galt
    
    Features:
    1. Curriculum Generation - Define objetivos de melhoria
    2. Experiment Execution - Executa testes A/B
    3. Performance Tracking - Monitora métricas continuamente
    4. Auto-Adjustment - Ajusta estratégias automaticamente
    5. Quality Guards - Detecta e previne degradação
    """
    
    def __init__(self, learning_dir: str = "/root/.zeroclaw/learning"):
        """
        Args:
            learning_dir: Diretório para dados de aprendizado
        """
        self.learning_dir = learning_dir
        self.curriculum_path = os.path.join(learning_dir, "curriculum.json")
        self.experiments_path = os.path.join(learning_dir, "experiments.jsonl")
        self.benchmarks_path = os.path.join(learning_dir, "benchmarks.jsonl")
        self.evolution_path = os.path.join(learning_dir, "evolution.json")
        
        # Criar diretórios
        os.makedirs(learning_dir, exist_ok=True)
        
        # Carregar estado
        self.curriculum = self._load_curriculum()
        self.evolution = self._load_evolution()
        
        # Performance tracking (sliding window)
        self.performance_window = deque(maxlen=100)
    
    # =================================================================
    # SELF-IMPROVEMENT CURRICULUM
    # =================================================================
    
    def generate_curriculum(
        self, 
        current_performance: Dict[str, float],
        target_improvement: float = 0.10
    ) -> List[Dict]:
        """
        Gerar currículo de auto-aperfeiçoamento
        
        Args:
            current_performance: Performance atual por métrica
            target_improvement: Melhoria alvo (0.10 = 10%)
        
        Returns:
            Lista de objetivos de aprendizado
        """
        objectives = []
        
        for metric, current_value in current_performance.items():
            # Calcular target
            if metric in ['accuracy', 'success_rate', 'quality_score']:
                # Métricas que devem aumentar
                target = current_value * (1 + target_improvement)
                target = min(target, 1.0)  # Cap em 100%
            elif metric in ['error_rate', 'latency_seconds']:
                # Métricas que devem diminuir
                target = current_value * (1 - target_improvement)
                target = max(target, 0.0)  # Floor em 0
            else:
                continue
            
            # Criar objetivo
            objective = {
                "id": self._generate_id(f"obj_{metric}"),
                "metric": metric,
                "current_value": current_value,
                "target_value": target,
                "improvement_pct": target_improvement,
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "experiments": [],
                "best_result": None
            }
            
            objectives.append(objective)
        
        # Salvar currículo
        self.curriculum = {
            "objectives": objectives,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        self._save_curriculum()
        
        return objectives
    
    def suggest_improvements(
        self, 
        metric: str, 
        current_value: float
    ) -> List[Dict]:
        """
        Sugerir melhorias específicas para uma métrica
        
        Args:
            metric: Nome da métrica
            current_value: Valor atual
        
        Returns:
            Lista de sugestões de melhoria
        """
        suggestions = []
        
        # Sugestões baseadas na métrica
        if metric == 'accuracy':
            if current_value < 0.90:
                suggestions.append({
                    "type": "improve_validation",
                    "description": "Add more validation steps",
                    "expected_gain": 0.05
                })
                suggestions.append({
                    "type": "enhance_data_quality",
                    "description": "Improve data collection quality",
                    "expected_gain": 0.03
                })
        
        elif metric == 'latency_seconds':
            if current_value > 2.0:
                suggestions.append({
                    "type": "optimize_parallel",
                    "description": "Increase parallelism in data fetching",
                    "expected_gain": -0.5  # Redução de 0.5s
                })
                suggestions.append({
                    "type": "cache_results",
                    "description": "Implement caching layer",
                    "expected_gain": -1.0
                })
        
        elif metric == 'success_rate':
            if current_value < 0.95:
                suggestions.append({
                    "type": "add_error_handling",
                    "description": "Improve error recovery",
                    "expected_gain": 0.05
                })
        
        return suggestions
    
    # =================================================================
    # A/B TESTING FRAMEWORK
    # =================================================================
    
    def create_experiment(
        self,
        name: str,
        metric: str,
        variant_a: Dict,
        variant_b: Dict,
        sample_size: int = 20
    ) -> str:
        """
        Criar experimento A/B
        
        Args:
            name: Nome do experimento
            metric: Métrica a otimizar
            variant_a: Configuração baseline
            variant_b: Configuração experimental
            sample_size: Tamanho da amostra por variante
        
        Returns:
            ID do experimento
        """
        experiment_id = self._generate_id(f"exp_{name}")
        
        experiment = {
            "id": experiment_id,
            "name": name,
            "metric": metric,
            "status": "running",
            "created_at": datetime.now().isoformat(),
            "variants": {
                "A": {
                    "config": variant_a,
                    "results": [],
                    "mean": None,
                    "std": None
                },
                "B": {
                    "config": variant_b,
                    "results": [],
                    "mean": None,
                    "std": None
                }
            },
            "sample_size": sample_size,
            "current_samples": 0,
            "winner": None,
            "confidence": None
        }
        
        # Salvar experimento
        with open(self.experiments_path, 'a') as f:
            f.write(json.dumps(experiment) + '\n')
        
        return experiment_id
    
    def record_experiment_result(
        self,
        experiment_id: str,
        variant: str,
        result_value: float
    ):
        """
        Registrar resultado de experimento
        
        Args:
            experiment_id: ID do experimento
            variant: 'A' ou 'B'
            result_value: Valor da métrica
        """
        # Carregar experimento
        experiment = self._load_experiment(experiment_id)
        
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        # Adicionar resultado
        experiment['variants'][variant]['results'].append(result_value)
        experiment['current_samples'] += 1
        
        # Atualizar estatísticas
        results = experiment['variants'][variant]['results']
        experiment['variants'][variant]['mean'] = statistics.mean(results)
        
        if len(results) > 1:
            experiment['variants'][variant]['std'] = statistics.stdev(results)
        
        # Verificar se experimento está completo
        if experiment['current_samples'] >= experiment['sample_size'] * 2:
            self._finalize_experiment(experiment)
        
        # Salvar
        self._update_experiment(experiment)
    
    def _finalize_experiment(self, experiment: Dict):
        """Finalizar experimento e determinar vencedor"""
        variant_a = experiment['variants']['A']
        variant_b = experiment['variants']['B']
        
        mean_a = variant_a['mean']
        mean_b = variant_b['mean']
        
        metric = experiment['metric']
        
        # Determinar vencedor baseado no tipo de métrica
        # Para métricas onde MENOR é melhor (latency, error_rate)
        if metric in ['latency_seconds', 'error_rate', 'time']:
            if mean_b < mean_a:
                experiment['winner'] = 'B'
                improvement = (mean_a - mean_b) / mean_a
            else:
                experiment['winner'] = 'A'
                improvement = (mean_b - mean_a) / mean_b
        
        # Para métricas onde MAIOR é melhor (accuracy, quality)
        else:
            if mean_b > mean_a:
                experiment['winner'] = 'B'
                improvement = (mean_b - mean_a) / mean_a
            else:
                experiment['winner'] = 'A'
                improvement = (mean_a - mean_b) / mean_b
        
        experiment['improvement_pct'] = improvement
        experiment['status'] = 'completed'
        experiment['completed_at'] = datetime.now().isoformat()
        
        # Calcular confidence (simplificado)
        if variant_a.get('std') and variant_b.get('std'):
            # Heurística simples de confiança
            pooled_std = (variant_a['std'] + variant_b['std']) / 2
            effect_size = abs(mean_b - mean_a) / pooled_std
            
            if effect_size > 0.8:
                experiment['confidence'] = 0.95
            elif effect_size > 0.5:
                experiment['confidence'] = 0.80
            else:
                experiment['confidence'] = 0.60
        else:
            experiment['confidence'] = 0.50
    
    # =================================================================
    # PERFORMANCE BENCHMARKING
    # =================================================================
    
    def record_benchmark(
        self,
        task_type: str,
        metrics: Dict[str, float],
        context: Optional[Dict] = None
    ) -> str:
        """
        Registrar benchmark de performance
        
        Args:
            task_type: Tipo de tarefa (options, macro, etc)
            metrics: Métricas medidas
            context: Contexto adicional
        
        Returns:
            ID do benchmark
        """
        benchmark_id = self._generate_id(f"bench_{task_type}")
        
        benchmark = {
            "id": benchmark_id,
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
            "metrics": metrics,
            "context": context or {}
        }
        
        # Salvar
        with open(self.benchmarks_path, 'a') as f:
            f.write(json.dumps(benchmark) + '\n')
        
        # Adicionar à janela de performance
        self.performance_window.append(benchmark)
        
        # Verificar degradação
        self._check_quality_degradation(task_type, metrics)
        
        return benchmark_id
    
    def get_performance_trend(
        self,
        task_type: str,
        metric: str,
        days_back: int = 7
    ) -> Dict:
        """
        Obter tendência de performance
        
        Args:
            task_type: Tipo de tarefa
            metric: Métrica a analisar
            days_back: Dias para trás
        
        Returns:
            Dict com tendência
        """
        cutoff = datetime.now() - timedelta(days=days_back)
        values = []
        timestamps = []
        
        # Ler benchmarks
        if os.path.exists(self.benchmarks_path):
            with open(self.benchmarks_path, 'r') as f:
                for line in f:
                    bench = json.loads(line.strip())
                    bench_time = datetime.fromisoformat(bench['timestamp'])
                    
                    if (bench['task_type'] == task_type and
                        bench_time >= cutoff and
                        metric in bench['metrics']):
                        values.append(bench['metrics'][metric])
                        timestamps.append(bench_time)
        
        if not values:
            return {"error": "No data"}
        
        # Calcular tendência
        trend = {
            "metric": metric,
            "task_type": task_type,
            "data_points": len(values),
            "mean": statistics.mean(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0,
            "min": min(values),
            "max": max(values),
            "latest": values[-1],
            "trend_direction": None
        }
        
        # Calcular direção da tendência (primeira vs última metade)
        if len(values) >= 4:
            mid = len(values) // 2
            first_half_mean = statistics.mean(values[:mid])
            second_half_mean = statistics.mean(values[mid:])
            
            change = (second_half_mean - first_half_mean) / first_half_mean
            
            if abs(change) < 0.05:
                trend['trend_direction'] = 'stable'
            elif change > 0:
                trend['trend_direction'] = 'improving'
            else:
                trend['trend_direction'] = 'degrading'
        
        return trend
    
    # =================================================================
    # QUALITY DEGRADATION DETECTION
    # =================================================================
    
    def _check_quality_degradation(
        self,
        task_type: str,
        current_metrics: Dict[str, float]
    ):
        """
        Verificar degradação de qualidade
        
        Compara métricas atuais com baseline
        Emite alerta se degradação detectada
        """
        # Obter baseline (média dos últimos 30 dias)
        baseline = self._get_baseline_metrics(task_type, days=30)
        
        if not baseline:
            return  # Sem baseline ainda
        
        # Verificar cada métrica
        for metric, current_value in current_metrics.items():
            if metric not in baseline:
                continue
            
            baseline_value = baseline[metric]['mean']
            baseline_std = baseline[metric]['std']
            
            # Calcular z-score
            if baseline_std > 0:
                z_score = (current_value - baseline_value) / baseline_std
            else:
                z_score = 0
            
            # Alertar se degradação significativa
            # Para métricas que devem ser altas (accuracy, quality)
            if metric in ['accuracy', 'quality_score', 'success_rate']:
                if z_score < -2.0:  # Mais de 2 desvios abaixo
                    self._emit_quality_alert(
                        task_type, 
                        metric, 
                        current_value, 
                        baseline_value,
                        "degradation"
                    )
            
            # Para métricas que devem ser baixas (latency, error_rate)
            elif metric in ['latency_seconds', 'error_rate']:
                if z_score > 2.0:  # Mais de 2 desvios acima
                    self._emit_quality_alert(
                        task_type, 
                        metric, 
                        current_value, 
                        baseline_value,
                        "degradation"
                    )
    
    def _emit_quality_alert(
        self,
        task_type: str,
        metric: str,
        current: float,
        baseline: float,
        alert_type: str
    ):
        """Emitir alerta de qualidade"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "task_type": task_type,
            "metric": metric,
            "current_value": current,
            "baseline_value": baseline,
            "deviation_pct": abs((current - baseline) / baseline) * 100
        }
        
        # Log alerta
        alerts_path = os.path.join(self.learning_dir, "quality_alerts.jsonl")
        with open(alerts_path, 'a') as f:
            f.write(json.dumps(alert) + '\n')
        
        print(f"⚠️ QUALITY ALERT: {task_type}/{metric}")
        print(f"   Current: {current:.4f}")
        print(f"   Baseline: {baseline:.4f}")
        print(f"   Deviation: {alert['deviation_pct']:.1f}%")
    
    def _get_baseline_metrics(
        self,
        task_type: str,
        days: int = 30
    ) -> Dict:
        """Obter métricas baseline"""
        cutoff = datetime.now() - timedelta(days=days)
        metrics_data = defaultdict(list)
        
        if os.path.exists(self.benchmarks_path):
            with open(self.benchmarks_path, 'r') as f:
                for line in f:
                    bench = json.loads(line.strip())
                    bench_time = datetime.fromisoformat(bench['timestamp'])
                    
                    if bench['task_type'] == task_type and bench_time >= cutoff:
                        for metric, value in bench['metrics'].items():
                            metrics_data[metric].append(value)
        
        # Calcular estatísticas
        baseline = {}
        for metric, values in metrics_data.items():
            if len(values) >= 5:  # Mínimo de 5 samples
                baseline[metric] = {
                    "mean": statistics.mean(values),
                    "std": statistics.stdev(values) if len(values) > 1 else 0,
                    "count": len(values)
                }
        
        return baseline
    
    # =================================================================
    # SKILL EVOLUTION TRACKING
    # =================================================================
    
    def track_skill_evolution(
        self,
        skill_id: str,
        version: str,
        performance: Dict[str, float]
    ):
        """
        Rastrear evolução de uma skill
        
        Args:
            skill_id: ID da skill
            version: Versão da skill
            performance: Métricas de performance
        """
        if skill_id not in self.evolution:
            self.evolution[skill_id] = {
                "created_at": datetime.now().isoformat(),
                "versions": []
            }
        
        # Adicionar versão
        version_data = {
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "performance": performance
        }
        
        self.evolution[skill_id]["versions"].append(version_data)
        
        # Limitar histórico (últimas 50 versões)
        if len(self.evolution[skill_id]["versions"]) > 50:
            self.evolution[skill_id]["versions"] = self.evolution[skill_id]["versions"][-50:]
        
        # Salvar
        self._save_evolution()
    
    def get_skill_evolution_summary(self, skill_id: str) -> Dict:
        """Sumário da evolução de uma skill"""
        if skill_id not in self.evolution:
            return {"error": "Skill not found"}
        
        versions = self.evolution[skill_id]["versions"]
        
        if not versions:
            return {"error": "No versions"}
        
        # Comparar primeira vs última versão
        first = versions[0]
        last = versions[-1]
        
        improvements = {}
        for metric in first['performance']:
            if metric in last['performance']:
                first_val = first['performance'][metric]
                last_val = last['performance'][metric]
                change = (last_val - first_val) / first_val if first_val != 0 else 0
                improvements[metric] = {
                    "first": first_val,
                    "last": last_val,
                    "change_pct": change * 100
                }
        
        return {
            "skill_id": skill_id,
            "total_versions": len(versions),
            "first_version": first['version'],
            "latest_version": last['version'],
            "improvements": improvements,
            "created_at": self.evolution[skill_id]["created_at"]
        }
    
    # =================================================================
    # AUTO-ADJUSTMENT
    # =================================================================
    
    def suggest_auto_adjustment(
        self,
        task_type: str,
        current_performance: Dict[str, float]
    ) -> List[Dict]:
        """
        Sugerir ajustes automáticos baseados em performance
        
        Returns:
            Lista de ajustes sugeridos
        """
        adjustments = []
        
        # Obter tendência
        for metric in current_performance:
            trend = self.get_performance_trend(task_type, metric, days_back=7)
            
            if trend.get('trend_direction') == 'degrading':
                # Sugerir rollback
                adjustments.append({
                    "type": "rollback",
                    "reason": f"{metric} is degrading",
                    "metric": metric,
                    "action": "Revert to previous version",
                    "priority": "high"
                })
            
            elif trend.get('trend_direction') == 'improving':
                # Continuar com estratégia atual
                adjustments.append({
                    "type": "continue",
                    "reason": f"{metric} is improving",
                    "metric": metric,
                    "action": "Maintain current approach",
                    "priority": "low"
                })
        
        return adjustments
    
    # =================================================================
    # UTILITIES
    # =================================================================
    
    def _generate_id(self, prefix: str) -> str:
        """Gerar ID único"""
        timestamp = datetime.now().isoformat()
        content = f"{prefix}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _load_curriculum(self) -> Dict:
        """Carregar currículo"""
        if os.path.exists(self.curriculum_path):
            with open(self.curriculum_path, 'r') as f:
                return json.load(f)
        return {"objectives": [], "created_at": None}
    
    def _save_curriculum(self):
        """Salvar currículo"""
        with open(self.curriculum_path, 'w') as f:
            json.dump(self.curriculum, f, indent=2)
    
    def _load_evolution(self) -> Dict:
        """Carregar evolução"""
        if os.path.exists(self.evolution_path):
            with open(self.evolution_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_evolution(self):
        """Salvar evolução"""
        with open(self.evolution_path, 'w') as f:
            json.dump(self.evolution, f, indent=2)
    
    def _load_experiment(self, experiment_id: str) -> Optional[Dict]:
        """Carregar experimento específico"""
        if not os.path.exists(self.experiments_path):
            return None
        
        with open(self.experiments_path, 'r') as f:
            for line in f:
                exp = json.loads(line.strip())
                if exp['id'] == experiment_id:
                    return exp
        
        return None
    
    def _update_experiment(self, experiment: Dict):
        """Atualizar experimento"""
        # Ler todos os experimentos
        experiments = []
        if os.path.exists(self.experiments_path):
            with open(self.experiments_path, 'r') as f:
                for line in f:
                    exp = json.loads(line.strip())
                    if exp['id'] == experiment['id']:
                        experiments.append(experiment)
                    else:
                        experiments.append(exp)
        
        # Reescrever arquivo
        with open(self.experiments_path, 'w') as f:
            for exp in experiments:
                f.write(json.dumps(exp) + '\n')
    
    def get_learning_summary(self) -> Dict:
        """Sumário geral do sistema de aprendizado"""
        # Contar experimentos
        total_experiments = 0
        completed_experiments = 0
        
        if os.path.exists(self.experiments_path):
            with open(self.experiments_path, 'r') as f:
                for line in f:
                    exp = json.loads(line.strip())
                    total_experiments += 1
                    if exp.get('status') == 'completed':
                        completed_experiments += 1
        
        # Contar benchmarks
        total_benchmarks = 0
        if os.path.exists(self.benchmarks_path):
            with open(self.benchmarks_path, 'r') as f:
                total_benchmarks = sum(1 for _ in f)
        
        # Contar alertas
        total_alerts = 0
        alerts_path = os.path.join(self.learning_dir, "quality_alerts.jsonl")
        if os.path.exists(alerts_path):
            with open(alerts_path, 'r') as f:
                total_alerts = sum(1 for _ in f)
        
        return {
            "curriculum": {
                "objectives": len(self.curriculum.get('objectives', [])),
                "active": sum(
                    1 for obj in self.curriculum.get('objectives', [])
                    if obj.get('status') == 'active'
                )
            },
            "experiments": {
                "total": total_experiments,
                "completed": completed_experiments,
                "running": total_experiments - completed_experiments
            },
            "benchmarks": {
                "total": total_benchmarks
            },
            "quality_alerts": {
                "total": total_alerts
            },
            "skill_evolution": {
                "tracked_skills": len(self.evolution)
            }
        }


# =============================================================================
# DEMONSTRAÇÃO
# =============================================================================

def demo():
    """Demonstração do sistema de aprendizado autônomo"""
    print("🤖 AUTONOMOUS LEARNING SYSTEM - PHASE 4")
    print("="*70)
    print()
    
    # Inicializar
    learning = AutonomousLearning()
    
    # 1. Gerar currículo
    print("1️⃣ Gerando currículo de auto-aperfeiçoamento...")
    objectives = learning.generate_curriculum({
        "accuracy": 0.85,
        "latency_seconds": 2.5,
        "success_rate": 0.90
    }, target_improvement=0.10)
    
    print(f"✅ {len(objectives)} objetivos criados:")
    for obj in objectives:
        print(f"   - {obj['metric']}: {obj['current_value']:.2f} → {obj['target_value']:.2f}")
    print()
    
    # 2. Criar experimento A/B
    print("2️⃣ Criando experimento A/B...")
    exp_id = learning.create_experiment(
        name="test_parallel_fetching",
        metric="latency_seconds",
        variant_a={"parallel": False},
        variant_b={"parallel": True},
        sample_size=10
    )
    print(f"✅ Experimento criado: {exp_id}")
    
    # Simular resultados
    import random
    for i in range(10):
        learning.record_experiment_result(exp_id, 'A', 2.5 + random.uniform(-0.2, 0.2))
        learning.record_experiment_result(exp_id, 'B', 0.8 + random.uniform(-0.1, 0.1))
    
    exp = learning._load_experiment(exp_id)
    if exp.get('winner'):
        print(f"   Vencedor: Variante {exp['winner']}")
        print(f"   Melhoria: {exp['improvement_pct']*100:.1f}%")
    print()
    
    # 3. Registrar benchmarks
    print("3️⃣ Registrando benchmarks...")
    for i in range(5):
        learning.record_benchmark(
            task_type="options",
            metrics={
                "accuracy": 0.90 + random.uniform(-0.02, 0.02),
                "latency_seconds": 1.5 + random.uniform(-0.1, 0.1)
            }
        )
    print(f"✅ 5 benchmarks registrados")
    print()
    
    # 4. Rastrear evolução de skill
    print("4️⃣ Rastreando evolução de skill...")
    skill_id = "skill_black_scholes"
    for version in range(1, 4):
        learning.track_skill_evolution(
            skill_id=skill_id,
            version=f"v1.{version}",
            performance={
                "accuracy": 0.85 + (version * 0.03),
                "speed": 1.0 - (version * 0.1)
            }
        )
    
    summary = learning.get_skill_evolution_summary(skill_id)
    print(f"✅ Skill: {summary['skill_id']}")
    print(f"   Versões: {summary['total_versions']}")
    print(f"   Melhorias:")
    for metric, data in summary['improvements'].items():
        print(f"      {metric}: {data['change_pct']:+.1f}%")
    print()
    
    # 5. Sumário geral
    print("5️⃣ Sumário do sistema...")
    summary = learning.get_learning_summary()
    print(json.dumps(summary, indent=2))
    print()
    
    print("="*70)
    print("✅ FASE 4: AUTONOMOUS LEARNING IMPLEMENTADA")


if __name__ == "__main__":
    demo()
