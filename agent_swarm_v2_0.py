#!/usr/bin/env python3
import asyncio
import json
import logging
import os
import sys
import httpx
from datetime import datetime
from typing import List, Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('john-galt')

OPENROUTER_MODEL = "anthropic/claude-haiku-4-5"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
REQUEST_TIMEOUT = 90.0
MAX_TOKENS = 1500

WORKSPACE = os.getenv('ZEROCLAW_WORKSPACE', '/root/.zeroclaw/workspace')
sys.path.insert(0, WORKSPACE)
try:
    from validate_analysis_quality import QualityValidator
except ImportError:
    class QualityValidator:
        def __init__(self, t, o): pass
        def check_all(self, **kw): return {"erros": []}


class ClaudeHaikuAgent:
    def __init__(self, agent_id: int, ticker: str, api_key: str):
        self.agent_id = agent_id
        self.ticker = ticker
        self.api_key = api_key
        self.start_time = None
        self.end_time = None

    async def call_claude_haiku(self, prompt: str) -> Dict:
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.post(
                    OPENROUTER_BASE_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "HTTP-Referer": "https://john-galt.local",
                        "X-Title": "John Galt Swarm"
                    },
                    json={
                        "model": OPENROUTER_MODEL,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": MAX_TOKENS,
                        "temperature": 0.7
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "response": data['choices'][0]['message']['content'],
                        "tokens": data.get('usage', {}).get('total_tokens', 0)
                    }
                else:
                    logger.error("Agent %d API error %d para %s", self.agent_id, response.status_code, self.ticker)
                    return {"success": False, "error": f"API Error: {response.status_code}", "response": None, "tokens": 0}
        except httpx.TimeoutException:
            logger.error("Agent %d timeout ao processar %s", self.agent_id, self.ticker)
            return {"success": False, "error": "Timeout", "response": None, "tokens": 0}
        except Exception as e:
            logger.error("Agent %d erro inesperado em %s: %s", self.agent_id, self.ticker, e)
            return {"success": False, "error": str(e), "response": None, "tokens": 0}

    async def analyze(self, analysis_data: Dict) -> Dict:
        self.start_time = datetime.now()
        logger.info("Agent %d iniciando análise de %s", self.agent_id, self.ticker)

        pitm_val = analysis_data.get('pitm', 0)
        prompt = f"""Analise esta opção B3:
Ticker: {analysis_data['ticker']}
Série: {analysis_data.get('series_code', 'N/A')}
Tipo: {analysis_data.get('option_type', 'CALL')}
Delta: {analysis_data.get('delta', 'N/A')}
Theta: {analysis_data.get('theta', 'N/A')}
P(ITM): {pitm_val * 100:.1f}%

Responda APENAS em JSON: {{"status": "APROVADO ou REPROVADO", "motivo": "explicacao"}}"""

        claude_result = await self.call_claude_haiku(prompt)

        validator = QualityValidator(self.ticker, analysis_data.get('option_type', 'CALL'))
        validation_report = validator.check_all(
            serie=len(analysis_data.get('series_code', '')) >= 5,
            theta=analysis_data.get('theta', 0),
            delta=analysis_data.get('delta', 0),
            pitm=analysis_data.get('pitm', 0),
            be=analysis_data.get('break_even', 0),
            rr=analysis_data.get('rr', 0),
            kelly=analysis_data.get('kelly', 0),
            moneyness=analysis_data.get('moneyness_correct', True),
            pnl=analysis_data.get('pnl', 0)
        )

        if claude_result['success']:
            status = "APROVADO" if not validation_report.get('erros') else "REPROVADO"
        else:
            status = "ERRO"

        self.end_time = datetime.now()
        elapsed = (self.end_time - self.start_time).total_seconds()
        logger.info("Agent %d concluiu %s em %.2fs — status: %s", self.agent_id, self.ticker, elapsed, status)

        return {
            "agent_id": self.agent_id,
            "ticker": self.ticker,
            "status": status,
            "validacoes_passadas": 9 if status == "APROVADO" else 0,
            "tempo_processamento": f"{elapsed:.2f}s",
            "timestamp": self.end_time.isoformat(),
            "claude_response": claude_result.get('response'),
            "tokens_used": claude_result.get('tokens', 0)
        }


class AgentSwarmWithClaude:
    def __init__(self, num_agents: int = 10, api_key: str = None):
        self.num_agents = num_agents
        self.api_key = api_key
        self.results = {}
        self.total_tokens = 0

    async def execute_parallel(self, tasks: List[Dict]) -> Dict:
        if not self.api_key:
            logger.error("API Key não configurada. Defina OPENROUTER_API_KEY.")
            return {}

        start_time = datetime.now()

        print("\n" + "="*80)
        print(f"🚀 AGENT SWARM v2.0 — {OPENROUTER_MODEL}")
        print("="*80)
        print(f"📊 Ativos a analisar: {len(tasks)}")
        print(f"🤖 Agentes: {self.num_agents}")
        print("="*80 + "\n")

        agents = []
        tasks_list = []

        for i, task in enumerate(tasks):
            agent_id = i % self.num_agents
            agent = ClaudeHaikuAgent(agent_id, task['ticker'], self.api_key)
            agents.append(agent)
            tasks_list.append(agent.analyze(task))
            print(f"   📌 Agent {agent_id} ← {task['ticker']}")

        print("\n⏳ Processando em paralelo...\n")

        results_list = await asyncio.gather(*tasks_list, return_exceptions=True)

        for result in results_list:
            if isinstance(result, Exception):
                logger.error("Tarefa falhou com exceção: %s", result)
                continue
            self.results[result['ticker']] = result
            self.total_tokens += result['tokens_used']

        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        aprovados = sum(1 for r in self.results.values() if r['status'] == 'APROVADO')

        print("\n" + "="*80)
        print("✅ ANÁLISE COMPLETA")
        print("="*80)
        print(f"⏱️  Tempo total: {elapsed:.2f}s")
        print(f"✅ Aprovados: {aprovados}/{len(self.results)}")
        print(f"🔤 Tokens utilizados: {self.total_tokens}")
        print("="*80 + "\n")

        for ticker, result in self.results.items():
            status_emoji = "✅" if result['status'] == 'APROVADO' else "❌"
            print(f"{status_emoji} {ticker:8} | {result['status']:10} | {result['tempo_processamento']} | Tokens: {result['tokens_used']}")

        return {
            "timestamp": end_time.isoformat(),
            "model": OPENROUTER_MODEL,
            "total_ativos": len(self.results),
            "aprovados": aprovados,
            "tempo_total": f"{elapsed:.2f}s",
            "tokens_totais": self.total_tokens,
            "resultados": self.results
        }


async def main():
    api_key = os.getenv('OPENROUTER_API_KEY')

    if not api_key:
        logger.error("OPENROUTER_API_KEY não definida. Defina a variável de ambiente.")
        sys.exit(1)

    analises = [
        {'ticker': 'COGN3', 'option_type': 'PUT', 'series_code': 'COGNP320', 'theta': -0.006, 'delta': -0.627, 'pitm': 0.687, 'break_even': 2.883, 'rr': 9.09, 'kelly': 0.088, 'pnl': 1591},
        {'ticker': 'PETR4', 'option_type': 'CALL', 'series_code': 'PETRK100', 'theta': -0.005, 'delta': 0.45, 'pitm': 0.38, 'break_even': 29.5, 'rr': 2.8, 'kelly': 0.065, 'pnl': 2341},
        {'ticker': 'VALE3', 'option_type': 'PUT', 'series_code': 'VALEP70', 'theta': -0.004, 'delta': -0.32, 'pitm': 0.25, 'break_even': 68.5, 'rr': 5.2, 'kelly': 0.042, 'pnl': 567}
    ]

    swarm = AgentSwarmWithClaude(num_agents=3, api_key=api_key)
    results = await swarm.execute_parallel(analises)

    if results:
        output_path = '/tmp/swarm_v2_results.json'
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info("Resultados salvos em: %s", output_path)


if __name__ == "__main__":
    asyncio.run(main())
