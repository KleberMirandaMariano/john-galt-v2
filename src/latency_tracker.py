#!/usr/bin/env python3
"""
latency_tracker.py - Instrumentação de latência por step do pipeline.

Uso:
    tracker = LatencyTracker()
    with tracker.step("agent_swarm"):
        result = await swarm.analyze_parallel(...)
    tracker.flush(ticker, market, approved=True)
    print(tracker.summary())
"""

import json
import os
import statistics
import time
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, List, Optional

LATENCY_FILE = "/root/.zeroclaw/metrics/latency.jsonl"


class LatencyTracker:
    """
    Mede e persiste a latência de cada step do pipeline.

    Funcionalidades:
    - Context manager síncrono compatível com código async
    - Persistência em JSONL (append-only, consistente com padrão do projeto)
    - Percentis P50/P95 por step (últimos N runs)
    - Detecção de regressão: step atual > threshold × P95 histórico
    """

    def __init__(self, run_id: str = None, latency_file: str = LATENCY_FILE):
        self.run_id = run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.latency_file = latency_file
        self.steps: Dict[str, float] = {}
        os.makedirs(os.path.dirname(latency_file), exist_ok=True)

    @contextmanager
    def step(self, name: str):
        """Context manager para medir um step. Funciona com await no corpo."""
        start = time.perf_counter()
        try:
            yield
        finally:
            self.steps[name] = round(time.perf_counter() - start, 3)

    @property
    def total(self) -> float:
        return round(sum(self.steps.values()), 3)

    def flush(self, ticker: str, market: str, approved: bool) -> Dict:
        """Persiste métricas da execução atual e retorna o record."""
        record = {
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat(),
            "ticker": ticker,
            "market": market,
            "approved": approved,
            "steps": self.steps,
            "total_s": self.total,
        }
        with open(self.latency_file, "a") as f:
            f.write(json.dumps(record) + "\n")
        return record

    def get_stats(self, step_name: Optional[str] = None, last_n: int = 50) -> Dict:
        """
        Calcula P50/P95/mean/min/max por step nos últimos N runs.

        Args:
            step_name: Filtrar por step específico (None = todos).
            last_n: Janela de runs para cálculo.

        Returns:
            Dict step → {"p50", "p95", "mean", "min", "max", "n"}
        """
        if not os.path.exists(self.latency_file):
            return {}

        records = []
        with open(self.latency_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        records = records[-last_n:]

        step_times: Dict[str, List[float]] = {}
        for rec in records:
            for sname, elapsed in rec.get("steps", {}).items():
                if step_name and sname != step_name:
                    continue
                step_times.setdefault(sname, []).append(elapsed)

        stats = {}
        for sname, times in step_times.items():
            n = len(times)
            sorted_t = sorted(times)
            stats[sname] = {
                "p50": round(sorted_t[max(0, int(n * 0.50) - 1)], 3),
                "p95": round(sorted_t[max(0, int(n * 0.95) - 1)], 3),
                "mean": round(statistics.mean(times), 3),
                "min": round(min(times), 3),
                "max": round(max(times), 3),
                "n": n,
            }
        return stats

    def check_regressions(self, threshold: float = 2.0) -> List[Dict]:
        """
        Compara steps atuais com P95 histórico.

        Returns:
            Lista de dicts para steps que excedem threshold × P95.
        """
        hist = self.get_stats()
        regressions = []
        for sname, elapsed in self.steps.items():
            if sname not in hist:
                continue
            p95 = hist[sname]["p95"]
            if p95 > 0 and elapsed > threshold * p95:
                regressions.append({
                    "step": sname,
                    "elapsed_s": elapsed,
                    "p95_s": p95,
                    "ratio": round(elapsed / p95, 2),
                })
        return regressions

    def summary(self) -> str:
        """Tabela formatada com tempos e percentuais da execução atual."""
        if not self.steps:
            return "  [LatencyTracker] Nenhum step registrado."
        total = self.total
        lines = [f"  Latency Report  run={self.run_id}"]
        lines.append(f"  {'Step':<28} {'Tempo':>8}  {'%':>6}")
        lines.append("  " + "-" * 46)
        for name, elapsed in self.steps.items():
            pct = (elapsed / total * 100) if total else 0
            lines.append(f"  {name:<28} {elapsed:>7.2f}s  {pct:>5.1f}%")
        lines.append("  " + "-" * 46)
        lines.append(f"  {'TOTAL':<28} {total:>7.2f}s  100.0%")
        return "\n".join(lines)
