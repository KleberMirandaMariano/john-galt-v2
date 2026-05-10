#!/usr/bin/env python3
"""
Reflection Engine for John Galt
Implements self-criticism and iterative improvement
Inspired by Reflexion paper: https://arxiv.org/pdf/2303.11366
"""

import os
from typing import Dict, List
import json
from datetime import datetime
import requests


class ReflectionEngine:
    """
    Sistema de reflexão e autocrítica para análises de opções

    Workflow:
    1. Gera análise inicial
    2. Auto-critica (identifica problemas)
    3. Refina análise com correções
    4. Repete até qualidade adequada (max 3 iterações)
    """

    def __init__(
        self,
        model: str = "anthropic/claude-sonnet-4-5",
        api_key: str = None,
        base_url: str = "https://openrouter.ai/api/v1"
    ):
        self.model = model
        self.max_iterations = 3
        self.quality_threshold = 0.85
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = base_url

        if not self.api_key:
            raise ValueError(
                "API key obrigatória. Defina OPENROUTER_API_KEY no arquivo .env"
            )

    def _call_claude(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 4000,
            "temperature": 0.3
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )

            response.raise_for_status()
            result = response.json()

            return result["choices"][0]["message"]["content"]

        except Exception as e:
            print(f"⚠️  API Error: {e}")
            return json.dumps({
                "issues_found": [],
                "suggestions": [],
                "needs_refinement": False,
                "quality_score": 0.5
            })

    def reflect_on_analysis(
        self,
        analysis: str,
        task: str,
        data_sources: Dict = None
    ) -> Dict:
        reflection_prompt = f"""
Você é um revisor CRÍTICO de análises quantitativas de opções.

TAREFA ORIGINAL:
{task}

ANÁLISE GERADA:
{analysis}

DADOS DISPONÍVEIS:
{json.dumps(data_sources, indent=2) if data_sources else "Não fornecidos"}

CRITÉRIOS DE AVALIAÇÃO (OBRIGATÓRIOS):

1. **Validação de Dados:**
   - ✓ Dados foram validados (freshness < 24h)?
   - ✓ Timestamp está presente?
   - ✓ Fonte dos dados está clara?

2. **Cálculos Matemáticos:**
   - ✓ Black-Scholes calculado corretamente?
   - ✓ Greeks (Delta, Theta, Vega, Gamma) presentes?
   - ✓ Valores estão dentro de ranges válidos?
     * Delta: -1 a +1
     * Theta: negativo para compras
     * Vega: positivo
     * IV: > 0

3. **Correlações e Contexto:**
   - ✓ Correlação BTC foi verificada (se cripto)?
   - ✓ Fear & Greed mencionado (se relevante)?
   - ✓ HV foi calculado e comparado com IV?

4. **Estruturas de Opções:**
   - ✓ Estratégias são apropriadas para contexto?
   - ✓ Risk/Reward calculado?
   - ✓ Break-even points identificados?
   - ✓ Cenários (alta/baixa/lateral) analisados?

5. **Warnings e Riscos:**
   - ✓ Riscos foram mencionados?
   - ✓ Theta decay explicado (se aplicável)?
   - ✓ Sizing sugerido (Kelly Criterion)?

6. **Formato e Clareza:**
   - ✓ Análise está estruturada?
   - ✓ Números estão formatados corretamente?
   - ✓ Recomendação final clara?

RESPONDA EM JSON (SEM MARKDOWN):
{{
    "issues_found": [
        "Descrição do problema 1",
        "Descrição do problema 2"
    ],
    "suggestions": [
        "Sugestão específica 1",
        "Sugestão específica 2"
    ],
    "needs_refinement": true/false,
    "quality_score": 0.0-1.0,
    "missing_validations": [
        "validação que falta"
    ],
    "calculation_errors": [
        "erro de cálculo encontrado"
    ]
}}

SEJA RIGOROSO. Se houver QUALQUER problema crítico, needs_refinement = true.
"""

        response = self._call_claude(reflection_prompt)

        try:
            reflection = json.loads(response.strip())
        except json.JSONDecodeError:
            reflection = {
                "issues_found": ["Failed to parse reflection response"],
                "suggestions": [],
                "needs_refinement": True,
                "quality_score": 0.5,
                "missing_validations": [],
                "calculation_errors": []
            }

        return reflection

    def refine_with_reflection(
        self,
        original: str,
        reflection: Dict,
        data_sources: Dict = None
    ) -> str:
        refinement_prompt = f"""
ANÁLISE ORIGINAL:
{original}

PROBLEMAS IDENTIFICADOS:
{json.dumps(reflection.get('issues_found', []), indent=2)}

SUGESTÕES DE MELHORIA:
{json.dumps(reflection.get('suggestions', []), indent=2)}

VALIDAÇÕES FALTANDO:
{json.dumps(reflection.get('missing_validations', []), indent=2)}

ERROS DE CÁLCULO:
{json.dumps(reflection.get('calculation_errors', []), indent=2)}

DADOS DISPONÍVEIS PARA USAR:
{json.dumps(data_sources, indent=2) if data_sources else "Não fornecidos"}

TAREFA:
Refine a análise corrigindo TODOS os problemas identificados.

INSTRUÇÕES:
1. Corrija TODOS os erros de cálculo
2. Adicione TODAS as validações faltando
3. Mantenha o formato e estrutura original
4. NÃO invente dados - use apenas os dados fornecidos
5. Se dados estão faltando, mencione explicitamente

Retorne APENAS a análise refinada (sem meta-comentários).
"""

        refined = self._call_claude(refinement_prompt)

        return refined.strip()

    def analyze_with_reflection(
        self,
        ticker: str,
        initial_analysis: str,
        data_sources: Dict = None
    ) -> Dict:
        analysis = initial_analysis
        iterations = []

        task = f"Análise quantitativa de opções para {ticker}"

        for i in range(self.max_iterations):
            print(f"\n{'='*60}")
            print(f"REFLEXION ITERATION {i+1}/{self.max_iterations}")
            print(f"{'='*60}")

            reflection = self.reflect_on_analysis(
                analysis,
                task,
                data_sources
            )

            iteration_info = {
                "iteration": i + 1,
                "quality_score": reflection['quality_score'],
                "issues_count": len(reflection['issues_found']),
                "needs_refinement": reflection['needs_refinement']
            }

            iterations.append(iteration_info)

            print(f"  Quality Score: {reflection['quality_score']:.2f}")
            print(f"  Issues Found: {len(reflection['issues_found'])}")
            print(f"  Needs Refinement: {reflection['needs_refinement']}")

            if not reflection['needs_refinement']:
                print(f"\n✅ ANALYSIS APPROVED!")
                break

            if i == self.max_iterations - 1:
                print(f"\n⚠️  Max iterations reached. Using best available.")
                break

            print(f"\n🔄 Refining analysis...")
            analysis = self.refine_with_reflection(
                analysis,
                reflection,
                data_sources
            )

        return {
            "final_analysis": analysis,
            "iterations": iterations,
            "total_iterations": len(iterations),
            "final_quality": iterations[-1]['quality_score']
        }


if __name__ == "__main__":
    engine = ReflectionEngine()

    sample_analysis = """
    SOL Options Analysis
    Spot: $88.88
    IV: 85%

    Strategy: Bull Call Spread
    - Buy Call $88
    - Sell Call $95
    Cost: $2.49
    """

    sample_data = {
        "spot": 88.88,
        "iv_atm": 85.0,
        "timestamp": datetime.now().isoformat()
    }

    result = engine.analyze_with_reflection(
        "SOL",
        sample_analysis,
        sample_data
    )

    print(f"\n{'='*60}")
    print(f"FINAL RESULT")
    print(f"{'='*60}")
    print(f"Total Iterations: {result['total_iterations']}")
    print(f"Final Quality: {result['final_quality']:.2f}")
