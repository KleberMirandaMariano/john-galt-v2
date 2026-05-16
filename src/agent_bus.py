#!/usr/bin/env python3
"""
agent_bus.py - Barramento de mensagens in-process para Agent2Agent (A2A).

Três padrões suportados:
  1. Pub/Sub   — publish(topic, payload) → todos os subscribers recebem
  2. Direct    — send(recipient, payload) → agente específico
  3. Req/Reply — request(recipient, payload) → aguarda resposta (com timeout)

Uso mínimo:
    bus = AgentBus()
    a = BaseAgent("agente_a", bus, capabilities=["market_data"])
    b = BaseAgent("agente_b", bus)
    b.subscribe("market_ready")

    await a.publish("market_ready", {"spot": 91.83})
    msg = await b.receive(timeout=2.0)

Sem dependências externas — só asyncio + stdlib.
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set


@dataclass
class AgentMessage:
    sender: str
    payload: Any
    message_id: str = field(default_factory=lambda: uuid.uuid4().hex[:10])
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    topic: Optional[str] = None      # pub/sub
    recipient: Optional[str] = None  # direct / req-reply
    reply_to: Optional[str] = None   # ID da request original


class AgentBus:
    """
    Barramento central in-process.

    Estado interno:
    - _queues: fila asyncio por agente
    - _subscriptions: topic → conjunto de agentes subscritos
    - _capabilities: agente → lista de capacidades anunciadas
    - _pending: message_id → Future aguardando reply
    - _log: histórico de mensagens (para debug/auditoria)
    """

    def __init__(self):
        self._queues: Dict[str, asyncio.Queue] = {}
        self._subscriptions: Dict[str, Set[str]] = {}
        self._capabilities: Dict[str, List[str]] = {}
        self._pending: Dict[str, asyncio.Future] = {}
        self._log: List[Dict] = []

    # ------------------------------------------------------------------
    # Registro
    # ------------------------------------------------------------------

    def register(self, agent_name: str, capabilities: List[str] = None):
        """Registra agente e cria sua fila."""
        if agent_name not in self._queues:
            self._queues[agent_name] = asyncio.Queue()
        self._capabilities[agent_name] = capabilities or []

    def subscribe(self, agent_name: str, topics: List[str]):
        """Subscreve agente a um ou mais topics."""
        for topic in topics:
            self._subscriptions.setdefault(topic, set()).add(agent_name)

    # ------------------------------------------------------------------
    # Pub/Sub
    # ------------------------------------------------------------------

    async def publish(self, sender: str, topic: str, payload: Any) -> str:
        """
        Publica em um topic. Todos os subscribers (exceto o sender) recebem.
        Retorna message_id.
        """
        msg = AgentMessage(sender=sender, topic=topic, payload=payload)
        subscribers = self._subscriptions.get(topic, set()) - {sender}
        for agent in subscribers:
            if agent in self._queues:
                await self._queues[agent].put(msg)
        self._log.append({
            "type": "publish", "sender": sender, "topic": topic,
            "subscribers": sorted(subscribers), "msg_id": msg.message_id,
            "ts": msg.timestamp,
        })
        return msg.message_id

    # ------------------------------------------------------------------
    # Direct
    # ------------------------------------------------------------------

    async def send(self, sender: str, recipient: str, payload: Any) -> str:
        """Envia mensagem direta para um agente. Retorna message_id."""
        self._assert_registered(recipient)
        msg = AgentMessage(sender=sender, recipient=recipient, payload=payload)
        await self._queues[recipient].put(msg)
        self._log.append({
            "type": "send", "sender": sender, "recipient": recipient,
            "msg_id": msg.message_id, "ts": msg.timestamp,
        })
        return msg.message_id

    # ------------------------------------------------------------------
    # Request / Reply
    # ------------------------------------------------------------------

    async def request(
        self,
        sender: str,
        recipient: str,
        payload: Any,
        timeout: float = 10.0,
    ) -> Any:
        """
        Envia request e bloqueia até receber reply (ou timeout).
        O recipient deve chamar bus.reply(message_id, payload).
        """
        self._assert_registered(recipient)
        loop = asyncio.get_event_loop()
        future: asyncio.Future = loop.create_future()
        msg = AgentMessage(sender=sender, recipient=recipient, payload=payload)
        self._pending[msg.message_id] = future
        await self._queues[recipient].put(msg)
        self._log.append({
            "type": "request", "sender": sender, "recipient": recipient,
            "msg_id": msg.message_id, "ts": msg.timestamp,
        })
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            self._pending.pop(msg.message_id, None)
            raise TimeoutError(
                f"request de '{sender}' para '{recipient}' excedeu {timeout}s"
            )

    def reply(self, message_id: str, payload: Any):
        """Responde a uma request pendente identificada por message_id."""
        future = self._pending.pop(message_id, None)
        if future and not future.done():
            future.set_result(payload)

    # ------------------------------------------------------------------
    # Recepção
    # ------------------------------------------------------------------

    async def receive(
        self, agent_name: str, timeout: Optional[float] = None
    ) -> Optional[AgentMessage]:
        """
        Retira próxima mensagem da fila do agente.
        timeout=None → não bloqueia (get_nowait).
        timeout=N    → aguarda até N segundos.
        """
        if agent_name not in self._queues:
            return None
        try:
            if timeout is None:
                return self._queues[agent_name].get_nowait()
            return await asyncio.wait_for(
                self._queues[agent_name].get(), timeout=timeout
            )
        except (asyncio.TimeoutError, asyncio.QueueEmpty):
            return None

    async def drain(self, agent_name: str) -> List[AgentMessage]:
        """Retorna todas as mensagens pendentes na fila (sem bloquear)."""
        msgs = []
        while True:
            msg = await self.receive(agent_name)
            if msg is None:
                break
            msgs.append(msg)
        return msgs

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def get_registered_agents(self) -> Dict[str, List[str]]:
        return dict(self._capabilities)

    def get_message_log(self) -> List[Dict]:
        return list(self._log)

    def summary(self) -> str:
        agents = len(self._queues)
        msgs = len(self._log)
        lines = [f"  AgentBus  agents={agents}  messages={msgs}"]
        for agent, caps in self._capabilities.items():
            cap_str = ", ".join(caps) if caps else "—"
            lines.append(f"    {agent:<28} caps=[{cap_str}]")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _assert_registered(self, name: str):
        if name not in self._queues:
            raise KeyError(f"Agente '{name}' não registrado no bus.")


class BaseAgent:
    """
    Classe base para agentes A2A.

    Herdar desta classe dá ao agente:
    - Registro automático no bus
    - send / publish / request / reply / receive / subscribe como métodos
    - Override de run() para lógica própria
    """

    def __init__(self, name: str, bus: AgentBus, capabilities: List[str] = None):
        self.name = name
        self.bus = bus
        self.capabilities = capabilities or []
        bus.register(name, self.capabilities)

    # Atalhos que encapsulam o nome do agente
    async def send(self, recipient: str, payload: Any) -> str:
        return await self.bus.send(self.name, recipient, payload)

    async def publish(self, topic: str, payload: Any) -> str:
        return await self.bus.publish(self.name, topic, payload)

    async def request(self, recipient: str, payload: Any, timeout: float = 10.0) -> Any:
        return await self.bus.request(self.name, recipient, payload, timeout=timeout)

    def reply(self, message_id: str, payload: Any):
        self.bus.reply(message_id, payload)

    def subscribe(self, *topics: str):
        self.bus.subscribe(self.name, list(topics))

    async def receive(self, timeout: Optional[float] = None) -> Optional[AgentMessage]:
        return await self.bus.receive(self.name, timeout=timeout)

    async def drain(self) -> List[AgentMessage]:
        return await self.bus.drain(self.name)

    async def run(self, **kwargs) -> Any:
        raise NotImplementedError(f"{self.name}.run() não implementado")
