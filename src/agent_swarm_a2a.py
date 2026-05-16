#!/usr/bin/env python3
"""
agent_swarm_a2a.py - Agent Swarm com comunicação Agent2Agent real.

Diferença vs AgentSwarmAnalyzer original:
  - Agentes não só rodam em paralelo — eles se comunicam durante a execução
  - market_data_agent publica regime de volatilidade → options_agent reage
  - options_agent pode solicitar spot_price via request/reply ao market_data_agent
  - Se um agente falha, broadcast de alerta → outros ajustam comportamento

Topologia de mensagens:
  market_data_agent  →[pub: volatility_regime]→  options_agent
  market_data_agent  →[pub: volatility_regime]→  correlation_agent
  options_agent      →[req: spot_price?]      →  market_data_agent  (req/reply)
  qualquer_agente    →[pub: agent_failed]     →  synthesis_agent
  todos              →[pub: agent_ready]      →  synthesis_agent
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from agent_bus import AgentBus, AgentMessage, BaseAgent


# ============================================================================
# AGENTS
# ============================================================================

class MarketDataAgent(BaseAgent):
    """
    Busca spot price + HV. Publica regime de volatilidade para outros agentes.
    Responde a requests de spot_price (req/reply).
    """

    def __init__(self, bus: AgentBus):
        super().__init__(
            "market_data_agent", bus,
            capabilities=["spot_price", "historical_volatility", "vol_regime"]
        )
        self._spot_cache: Optional[float] = None

    async def run(self, ticker: str, market: str) -> Dict:
        print(f"  [market_data] buscando spot + HV para {ticker}...")
        await asyncio.sleep(0.4)  # simula fetch (BRAPI / CoinGecko)

        spot = 88.88
        hv = 92.5
        self._spot_cache = spot

        result = {
            "spot_price": spot,
            "historical_volatility": hv,
            "source": "brapi" if market == "b3" else "coingecko",
            "timestamp": datetime.now().isoformat(),
        }

        # Determinar regime de volatilidade e publicar para outros agentes
        regime = "high" if hv > 80 else ("low" if hv < 30 else "normal")
        await self.publish("volatility_regime", {
            "regime": regime,
            "hv": hv,
            "ticker": ticker,
        })

        # Publicar que está pronto
        await self.publish("agent_ready", {
            "agent": self.name,
            "outputs": list(result.keys()),
        })

        # Ficar disponível para responder requests de spot_price enquanto outros rodam
        asyncio.create_task(self._handle_spot_requests())

        print(f"  [market_data] pronto  spot={spot}  hv={hv}  regime={regime}")
        return result

    async def _handle_spot_requests(self):
        """Responde requests de spot_price vindos de outros agentes."""
        for _ in range(10):  # janela de tempo para receber requests
            msg = await self.receive(timeout=0.2)
            if msg is None:
                break
            if msg.payload.get("request") == "spot_price":
                self.reply(msg.message_id, {"spot_price": self._spot_cache})


class OptionsAgent(BaseAgent):
    """
    Busca options chain + IV ATM.
    Reage ao regime de volatilidade publicado pelo market_data_agent.
    Pode solicitar spot_price via request/reply.
    """

    def __init__(self, bus: AgentBus):
        super().__init__(
            "options_agent", bus,
            capabilities=["implied_volatility", "options_chain"]
        )
        self.subscribe("volatility_regime")

    async def run(self, ticker: str, market: str) -> Dict:
        print(f"  [options] aguardando regime de vol antes de buscar chain...")

        # Aguarda sinal do market_data_agent (A2A: dep dinâmica)
        regime_msg: Optional[AgentMessage] = await self.receive(timeout=3.0)
        regime = "normal"
        if regime_msg and regime_msg.topic == "volatility_regime":
            regime = regime_msg.payload.get("regime", "normal")
            print(f"  [options] regime recebido via bus: {regime}")

        # Ajusta profundidade da chain com base no regime
        chain_depth = "deep_otm" if regime == "high" else "atm_only"
        print(f"  [options] buscando chain ({chain_depth}) para {ticker}...")
        await asyncio.sleep(0.5)

        # Solicita spot atual via request/reply (para garantir consistência)
        try:
            spot_resp = await self.request(
                "market_data_agent",
                {"request": "spot_price"},
                timeout=2.0,
            )
            spot = spot_resp.get("spot_price", 88.88)
        except TimeoutError:
            spot = 88.88

        result = {
            "implied_volatility": 85.0,
            "options_chain": {
                "calls": [
                    {"strike": round(spot * 0.95, 2), "price": 5.20},
                    {"strike": round(spot, 2),        "price": 2.45},
                    {"strike": round(spot * 1.05, 2), "price": 0.85},
                ],
                "puts": [
                    {"strike": round(spot * 0.95, 2), "price": 3.10},
                    {"strike": round(spot * 0.90, 2), "price": 1.50},
                    {"strike": round(spot * 0.85, 2), "price": 0.45},
                ],
            },
            "chain_depth": chain_depth,
            "vol_regime_received": regime,
            "source": "okx_api",
            "timestamp": datetime.now().isoformat(),
        }

        await self.publish("agent_ready", {"agent": self.name, "outputs": ["iv", "chain"]})
        print(f"  [options] pronto  iv=85.0  chain_depth={chain_depth}")
        return result


class CorrelationAgent(BaseAgent):
    """
    Calcula correlação ticker-BTC.
    Subscreve volatility_regime para ajustar janela de cálculo.
    """

    def __init__(self, bus: AgentBus):
        super().__init__(
            "correlation_agent", bus,
            capabilities=["btc_correlation"]
        )
        self.subscribe("volatility_regime")

    async def run(self, ticker: str, market: str) -> Dict:
        if market != "cripto":
            return {}

        # Consome regime se já chegou (não bloqueia)
        regime_msg = await self.receive(timeout=0.5)
        window = 14 if (regime_msg and regime_msg.payload.get("regime") == "high") else 30
        print(f"  [correlation] calculando {ticker}-BTC (janela {window}d)...")
        await asyncio.sleep(0.3)

        result = {
            "btc_correlation": 0.78,
            "period_days": window,
            "source": "coingecko",
            "timestamp": datetime.now().isoformat(),
        }
        await self.publish("agent_ready", {"agent": self.name, "outputs": ["btc_correlation"]})
        print(f"  [correlation] pronto  corr=0.78  janela={window}d")
        return result


class SentimentAgent(BaseAgent):
    """Busca Fear & Greed Index. Independente, sem sub/pub de regime."""

    def __init__(self, bus: AgentBus):
        super().__init__(
            "sentiment_agent", bus,
            capabilities=["fear_greed_index"]
        )

    async def run(self, ticker: str, market: str) -> Dict:
        if market != "cripto":
            return {}
        print(f"  [sentiment] buscando Fear & Greed...")
        await asyncio.sleep(0.2)
        result = {
            "fear_greed_index": 65,
            "status": "Greed",
            "source": "alternative.me",
            "timestamp": datetime.now().isoformat(),
        }
        await self.publish("agent_ready", {"agent": self.name, "outputs": ["fear_greed"]})
        print(f"  [sentiment] pronto  fg=65 (Greed)")
        return result


# ============================================================================
# ORCHESTRATOR
# ============================================================================

class AgentSwarmA2A:
    """
    Versão A2A do Agent Swarm.

    Substitui o AgentSwarmAnalyzer simples por agentes que:
    - Publicam descobertas intermediárias via bus
    - Reagem a informações de outros agentes durante a execução
    - Usam request/reply para dados pontuais on-demand
    """

    def __init__(self):
        self.bus = AgentBus()
        self.market_data = MarketDataAgent(self.bus)
        self.options     = OptionsAgent(self.bus)
        self.correlation = CorrelationAgent(self.bus)
        self.sentiment   = SentimentAgent(self.bus)

    async def analyze_parallel(self, ticker: str, market: str = "cripto") -> Dict:
        """
        Executa o swarm A2A e retorna resultado consolidado.

        Ordem de execução:
          market_data_agent inicia → publica volatility_regime →
          options_agent e correlation_agent reagem →
          sentiment_agent corre independente →
          todos consolidam
        """
        print(f"\n{'='*60}")
        print(f"AGENT SWARM A2A  ticker={ticker}  market={market}")
        print(f"{'='*60}")

        start = datetime.now()

        # Lançar todos em paralelo — a comunicação via bus cria a coordenação
        results = await asyncio.gather(
            self.market_data.run(ticker, market),
            self.options.run(ticker, market),
            self.correlation.run(ticker, market),
            self.sentiment.run(ticker, market),
            return_exceptions=True,
        )

        elapsed = (datetime.now() - start).total_seconds()

        md_result   = results[0] if not isinstance(results[0], Exception) else {}
        opt_result  = results[1] if not isinstance(results[1], Exception) else {}
        corr_result = results[2] if not isinstance(results[2], Exception) else {}
        sent_result = results[3] if not isinstance(results[3], Exception) else {}

        consolidated = self._consolidate(
            ticker, market, md_result, opt_result, corr_result, sent_result
        )
        validation = self._validate(consolidated, market)

        print(f"\n✅ Swarm A2A completou em {elapsed:.2f}s")
        print(self.bus.summary())

        return {
            "ticker": ticker,
            "market": market,
            "timestamp": datetime.now().isoformat(),
            "data": consolidated,
            "validation": validation,
            "execution_time_seconds": elapsed,
            "message_log": self.bus.get_message_log(),
        }

    def _consolidate(
        self, ticker, market, md, opt, corr, sent
    ) -> Dict:
        out: Dict[str, Any] = {"ticker": ticker, "market": market}
        out["spot_price"]      = md.get("spot_price")
        out["historical_vol"]  = md.get("historical_volatility")
        out["iv_atm"]          = opt.get("implied_volatility")
        out["options_chain"]   = opt.get("options_chain")
        out["chain_depth"]     = opt.get("chain_depth")
        out["vol_regime"]      = opt.get("vol_regime_received")
        if market == "cripto":
            out["correlation_btc"]    = corr.get("btc_correlation")
            out["fear_greed_index"]   = sent.get("fear_greed_index")
            out["fear_greed_status"]  = sent.get("status")
        return out

    def _validate(self, data: Dict, market: str) -> Dict:
        required = {
            "cripto": ["spot_price", "historical_vol", "iv_atm",
                       "correlation_btc", "fear_greed_index", "options_chain"],
            "b3":     ["spot_price", "historical_vol", "iv_atm", "options_chain"],
        }
        fields = required.get(market, [])
        missing = [f for f in fields if not data.get(f)]
        present = len(fields) - len(missing)
        return {
            "complete": len(missing) == 0,
            "completeness": round(present / len(fields), 2) if fields else 1.0,
            "required_fields": len(fields),
            "present_fields": present,
            "missing_fields": missing,
        }


# ============================================================================
# DEMO
# ============================================================================

async def demo():
    swarm = AgentSwarmA2A()
    result = await swarm.analyze_parallel("SOL", market="cripto")

    print("\n--- MESSAGE LOG (A2A) ---")
    for entry in result["message_log"]:
        t = entry["type"]
        if t == "publish":
            print(f"  publish  {entry['sender']:20} → topic={entry['topic']}  subs={entry['subscribers']}")
        elif t == "send":
            print(f"  send     {entry['sender']:20} → {entry['recipient']}")
        elif t == "request":
            print(f"  request  {entry['sender']:20} → {entry['recipient']}  id={entry['msg_id']}")

    print(f"\nCompleteness: {result['validation']['completeness']*100:.0f}%")
    print(f"vol_regime:   {result['data'].get('vol_regime')}")
    print(f"chain_depth:  {result['data'].get('chain_depth')}")


if __name__ == "__main__":
    asyncio.run(demo())
