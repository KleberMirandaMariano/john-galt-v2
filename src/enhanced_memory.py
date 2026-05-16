#!/usr/bin/env python3
"""
enhanced_memory.py - Phase 2: Enhanced Memory System

Integra com zeroclaw_dream.py para memória persistente
Implementa três tipos de memória:
- Episódica: Análises específicas passadas
- Semântica: Conhecimento geral acumulado
- Procedural: Procedimentos e padrões de sucesso

Autor: John Galt v2.0 - Phase 2
Data: 06/05/2026
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib
import math


class EnhancedMemory:
    """
    Sistema de memória aprimorado para John Galt
    
    Três tipos de memória:
    1. Episódica: Análises passadas específicas (O QUE aconteceu)
    2. Semântica: Conhecimento geral (O QUE significa)
    3. Procedural: Como fazer (COMO fazer)
    """
    
    def __init__(self, memory_dir: str = "/root/.zeroclaw/memory"):
        """
        Args:
            memory_dir: Diretório para armazenar memórias
        """
        self.memory_dir = memory_dir
        self.episodic_path = os.path.join(memory_dir, "episodic.jsonl")
        self.semantic_path = os.path.join(memory_dir, "semantic.json")
        self.procedural_path = os.path.join(memory_dir, "procedural.json")
        self.vectors_path = os.path.join(memory_dir, "vectors.jsonl")

        # Criar diretório se não existir
        os.makedirs(memory_dir, exist_ok=True)

        # Carregar memórias
        self.semantic = self._load_semantic()
        self.procedural = self._load_procedural()
    
    # =================================================================
    # MEMÓRIA EPISÓDICA: "O QUE ACONTECEU"
    # =================================================================
    
    def store_episode(
        self,
        ticker: str,
        analysis_type: str,
        data: Dict,
        result: Dict,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Armazenar episódio de análise
        
        Args:
            ticker: Ticker analisado (SOL, PETR4, etc)
            analysis_type: Tipo de análise (options, macro, cripto)
            data: Dados usados na análise
            result: Resultado da análise
            metadata: Metadados adicionais
        
        Returns:
            ID do episódio
        """
        episode_id = self._generate_episode_id(ticker, analysis_type)
        
        episode = {
            "id": episode_id,
            "timestamp": datetime.now().isoformat(),
            "ticker": ticker.upper(),
            "type": analysis_type,
            "data": data,
            "result": result,
            "metadata": metadata or {}
        }
        
        # Append ao arquivo JSONL
        with open(self.episodic_path, 'a') as f:
            f.write(json.dumps(episode) + '\n')

        # Indexar vetor para busca semântica
        vector = self._build_vector(episode)
        self._index_episode_vector(episode_id, vector)

        # Atualizar memória semântica
        self._update_semantic_from_episode(episode)

        # Atualizar memória procedural se foi bem-sucedido
        if result.get('success', False):
            self._update_procedural_from_episode(episode)

        return episode_id
    
    def retrieve_similar_episodes(
        self,
        ticker: str,
        analysis_type: str,
        days_back: int = 30,
        limit: int = 5
    ) -> List[Dict]:
        """
        Recuperar episódios similares
        
        Args:
            ticker: Ticker atual
            analysis_type: Tipo de análise
            days_back: Quantos dias olhar para trás
            limit: Máximo de episódios a retornar
        
        Returns:
            Lista de episódios similares
        """
        if not os.path.exists(self.episodic_path):
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        episodes = []
        
        # Ler JSONL e filtrar
        with open(self.episodic_path, 'r') as f:
            for line in f:
                try:
                    ep = json.loads(line.strip())
                    ep_date = datetime.fromisoformat(ep['timestamp'])
                    
                    # Filtrar por ticker, tipo e data
                    if (ep['ticker'] == ticker.upper() and
                        ep['type'] == analysis_type and
                        ep_date >= cutoff_date):
                        episodes.append(ep)
                except:
                    continue
        
        # Ordenar por timestamp (mais recente primeiro)
        episodes.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return episodes[:limit]
    
    def get_episode_stats(self, ticker: str) -> Dict:
        """
        Estatísticas de episódios para um ticker
        
        Returns:
            Dict com estatísticas
        """
        if not os.path.exists(self.episodic_path):
            return {"total": 0, "by_type": {}}
        
        stats = {
            "total": 0,
            "by_type": defaultdict(int),
            "success_rate": 0.0,
            "first_seen": None,
            "last_seen": None
        }
        
        successes = 0
        total = 0
        
        with open(self.episodic_path, 'r') as f:
            for line in f:
                try:
                    ep = json.loads(line.strip())
                    if ep['ticker'] != ticker.upper():
                        continue
                    
                    stats["total"] += 1
                    stats["by_type"][ep['type']] += 1
                    
                    # Atualizar datas
                    ep_date = ep['timestamp']
                    if stats["first_seen"] is None or ep_date < stats["first_seen"]:
                        stats["first_seen"] = ep_date
                    if stats["last_seen"] is None or ep_date > stats["last_seen"]:
                        stats["last_seen"] = ep_date
                    
                    # Contar sucessos
                    total += 1
                    if ep.get('result', {}).get('success', False):
                        successes += 1
                except:
                    continue
        
        if total > 0:
            stats["success_rate"] = successes / total
        
        stats["by_type"] = dict(stats["by_type"])
        return stats
    
    # =================================================================
    # MEMÓRIA SEMÂNTICA: "O QUE SIGNIFICA"
    # =================================================================
    
    def _load_semantic(self) -> Dict:
        """Carregar memória semântica"""
        if os.path.exists(self.semantic_path):
            with open(self.semantic_path, 'r') as f:
                return json.load(f)
        
        return {
            "tickers": {},      # Conhecimento por ticker
            "concepts": {},     # Conceitos gerais
            "patterns": {},     # Padrões identificados
            "rules": [],        # Regras aprendidas
            "last_updated": None
        }
    
    def _save_semantic(self):
        """Salvar memória semântica"""
        self.semantic["last_updated"] = datetime.now().isoformat()
        with open(self.semantic_path, 'w') as f:
            json.dump(self.semantic, f, indent=2)
    
    def _update_semantic_from_episode(self, episode: Dict):
        """Atualizar conhecimento semântico a partir de episódio"""
        ticker = episode['ticker']
        
        # Atualizar conhecimento do ticker
        if ticker not in self.semantic["tickers"]:
            self.semantic["tickers"][ticker] = {
                "typical_iv": [],
                "typical_price_range": [],
                "typical_volume": [],
                "correlation_with_btc": [],
                "observations": []
            }
        
        # Extrair dados do episódio
        data = episode.get('data', {})
        result = episode.get('result', {})
        
        # Armazenar IVs
        if 'iv' in data:
            self.semantic["tickers"][ticker]["typical_iv"].append(data['iv'])
        
        # Armazenar preços
        if 'spot_price' in data:
            self.semantic["tickers"][ticker]["typical_price_range"].append(data['spot_price'])
        
        # Armazenar correlação com BTC (para cripto)
        if 'btc_correlation' in data:
            self.semantic["tickers"][ticker]["correlation_with_btc"].append(data['btc_correlation'])
        
        # Limitar tamanho dos arrays (manter últimos 100)
        for key in ["typical_iv", "typical_price_range", "correlation_with_btc"]:
            if len(self.semantic["tickers"][ticker][key]) > 100:
                self.semantic["tickers"][ticker][key] = self.semantic["tickers"][ticker][key][-100:]
        
        # Salvar
        self._save_semantic()
    
    def get_semantic_knowledge(self, ticker: str) -> Dict:
        """
        Recuperar conhecimento semântico sobre um ticker
        
        Returns:
            Dict com conhecimento acumulado
        """
        if ticker.upper() not in self.semantic["tickers"]:
            return {"error": f"No knowledge about {ticker}"}
        
        ticker_data = self.semantic["tickers"][ticker.upper()]
        
        # Calcular médias
        import statistics
        
        knowledge = {
            "ticker": ticker.upper(),
            "data_points": {}
        }
        
        if ticker_data["typical_iv"]:
            knowledge["data_points"]["avg_iv"] = statistics.mean(ticker_data["typical_iv"])
            knowledge["data_points"]["std_iv"] = statistics.stdev(ticker_data["typical_iv"]) if len(ticker_data["typical_iv"]) > 1 else 0
        
        if ticker_data["typical_price_range"]:
            knowledge["data_points"]["avg_price"] = statistics.mean(ticker_data["typical_price_range"])
            knowledge["data_points"]["price_range"] = {
                "min": min(ticker_data["typical_price_range"]),
                "max": max(ticker_data["typical_price_range"])
            }
        
        if ticker_data["correlation_with_btc"]:
            knowledge["data_points"]["avg_btc_correlation"] = statistics.mean(ticker_data["correlation_with_btc"])
        
        knowledge["observations_count"] = len(ticker_data.get("observations", []))
        
        return knowledge
    
    # =================================================================
    # MEMÓRIA PROCEDURAL: "COMO FAZER"
    # =================================================================
    
    def _load_procedural(self) -> Dict:
        """Carregar memória procedural"""
        if os.path.exists(self.procedural_path):
            with open(self.procedural_path, 'r') as f:
                return json.load(f)
        
        return {
            "successful_patterns": [],
            "failed_patterns": [],
            "best_practices": [],
            "last_updated": None
        }
    
    def _save_procedural(self):
        """Salvar memória procedural"""
        self.procedural["last_updated"] = datetime.now().isoformat()
        with open(self.procedural_path, 'w') as f:
            json.dump(self.procedural, f, indent=2)
    
    def _update_procedural_from_episode(self, episode: Dict):
        """Atualizar memória procedural a partir de episódio bem-sucedido"""
        # Extrair padrão de sucesso
        pattern = {
            "type": episode['type'],
            "ticker": episode['ticker'],
            "approach": episode.get('metadata', {}).get('approach', 'unknown'),
            "success_timestamp": episode['timestamp'],
            "quality_score": episode.get('result', {}).get('quality', 0.0)
        }
        
        # Adicionar aos sucessos
        self.procedural["successful_patterns"].append(pattern)
        
        # Limitar tamanho (manter últimos 50)
        if len(self.procedural["successful_patterns"]) > 50:
            self.procedural["successful_patterns"] = self.procedural["successful_patterns"][-50:]
        
        # Salvar
        self._save_procedural()
    
    def get_best_practices(self, analysis_type: str) -> List[str]:
        """
        Recuperar melhores práticas para um tipo de análise
        
        Args:
            analysis_type: Tipo de análise
        
        Returns:
            Lista de melhores práticas
        """
        # Filtrar padrões bem-sucedidos por tipo
        relevant_patterns = [
            p for p in self.procedural["successful_patterns"]
            if p['type'] == analysis_type and p.get('quality_score', 0) >= 0.85
        ]
        
        if not relevant_patterns:
            return []
        
        # Extrair approaches únicos
        approaches = list(set(p['approach'] for p in relevant_patterns))
        
        best_practices = [
            f"Use '{approach}' approach (success rate from patterns)"
            for approach in approaches
        ]
        
        # Adicionar best practices fixas se existirem
        best_practices.extend(self.procedural.get("best_practices", []))
        
        return best_practices
    
    # =================================================================
    # BUSCA VETORIAL: SIMILARIDADE SEMÂNTICA
    # =================================================================

    def _build_vector(self, episode: Dict) -> Dict[str, float]:
        """
        Constrói vetor TF esparso a partir do conteúdo de um episódio.

        Campos utilizados (com pesos):
        - ticker (×3), analysis_type (×2): identidade do episódio
        - chaves e valores textuais de data/result/metadata
        - buckets numéricos (iv_high, price_low, etc.)
        """
        tokens: List[str] = []

        tokens.extend([episode.get("ticker", "").lower()] * 3)
        tokens.extend([episode.get("type", "").lower()] * 2)

        def _tokenize_dict(d: Dict, depth: int = 0):
            if depth > 2:
                return
            for key, val in d.items():
                key_tok = key.lower().replace("-", "_")
                tokens.append(key_tok)
                if isinstance(val, str):
                    tokens.extend(val.lower().split())
                elif isinstance(val, (int, float)) and val != 0:
                    bucket = "high" if val > 0.5 else "low"
                    tokens.append(f"{key_tok}_{bucket}")
                elif isinstance(val, list):
                    for item in val:
                        if isinstance(item, str):
                            tokens.extend(item.lower().split())
                elif isinstance(val, dict):
                    _tokenize_dict(val, depth + 1)

        _tokenize_dict(episode.get("data", {}))
        _tokenize_dict(episode.get("result", {}))
        _tokenize_dict(episode.get("metadata", {}))

        # Normalizar tokens: manter apenas alfanuméricos ≥ 2 chars
        clean: List[str] = []
        for t in tokens:
            t = "".join(c for c in t if c.isalnum() or c == "_")
            if len(t) >= 2:
                clean.append(t)

        # Term frequency normalizado
        tf: Dict[str, float] = {}
        for t in clean:
            tf[t] = tf.get(t, 0) + 1
        total = sum(tf.values())
        if total:
            tf = {k: v / total for k, v in tf.items()}

        return tf

    def _cosine_similarity(
        self, v1: Dict[str, float], v2: Dict[str, float]
    ) -> float:
        """Similaridade coseno entre dois vetores TF esparsos."""
        common = set(v1) & set(v2)
        if not common:
            return 0.0
        dot = sum(v1[k] * v2[k] for k in common)
        norm1 = math.sqrt(sum(x * x for x in v1.values()))
        norm2 = math.sqrt(sum(x * x for x in v2.values()))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def _query_to_vector(
        self,
        query: str,
        ticker: Optional[str] = None,
        analysis_type: Optional[str] = None,
    ) -> Dict[str, float]:
        """Converte texto livre + campos opcionais em vetor TF."""
        tokens: List[str] = []

        for word in query.lower().split():
            word = "".join(c for c in word if c.isalnum() or c == "_")
            if len(word) >= 2:
                tokens.append(word)

        if ticker:
            tokens.extend([ticker.lower()] * 3)
        if analysis_type:
            tokens.extend([analysis_type.lower()] * 2)

        tf: Dict[str, float] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        total = sum(tf.values())
        if total:
            tf = {k: v / total for k, v in tf.items()}
        return tf

    def _index_episode_vector(self, episode_id: str, vector: Dict[str, float]):
        """Persiste o vetor do episódio em vectors.jsonl."""
        record = {"episode_id": episode_id, "vector": vector}
        with open(self.vectors_path, "a") as f:
            f.write(json.dumps(record) + "\n")

    def search_by_query(
        self,
        query: str,
        ticker: Optional[str] = None,
        analysis_type: Optional[str] = None,
        top_k: int = 5,
        min_similarity: float = 0.1,
    ) -> List[Dict]:
        """
        Busca episódios semanticamente similares à query.

        Difere de retrieve_similar_episodes: não filtra por ticker/tipo exatos —
        encontra o que for mais parecido pelo conteúdo, ideal para queries livres.

        Args:
            query: Texto livre (ex: "SOL opções bull spread IV alto")
            ticker: Peso adicional para um ticker específico (opcional)
            analysis_type: Peso adicional para tipo (opcional)
            top_k: Máximo de episódios retornados
            min_similarity: Similaridade mínima para incluir (0-1)

        Returns:
            Lista de dicts com episódio + "similarity" score, ordenada desc.
        """
        if not os.path.exists(self.vectors_path):
            return []

        q_vec = self._query_to_vector(query, ticker, analysis_type)
        if not q_vec:
            return []

        # Carregar vetores e calcular similaridades
        scored: List[Tuple[str, float]] = []
        with open(self.vectors_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    sim = self._cosine_similarity(q_vec, rec["vector"])
                    if sim >= min_similarity:
                        scored.append((rec["episode_id"], sim))
                except (json.JSONDecodeError, KeyError):
                    continue

        if not scored:
            return []

        # Top-K por similaridade
        scored.sort(key=lambda x: x[1], reverse=True)
        top_ids = {eid: sim for eid, sim in scored[:top_k]}

        # Recuperar episódios completos do JSONL episódico
        results: List[Dict] = []
        if os.path.exists(self.episodic_path):
            with open(self.episodic_path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        ep = json.loads(line)
                        if ep["id"] in top_ids:
                            ep["similarity"] = round(top_ids[ep["id"]], 4)
                            results.append(ep)
                    except (json.JSONDecodeError, KeyError):
                        continue

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results

    # =================================================================
    # UTILIDADES
    # =================================================================
    
    def _generate_episode_id(self, ticker: str, analysis_type: str) -> str:
        """Gerar ID único para episódio"""
        timestamp = datetime.now().isoformat()
        content = f"{ticker}_{analysis_type}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def get_memory_summary(self) -> Dict:
        """
        Obter sumário de todas as memórias
        
        Returns:
            Dict com estatísticas gerais
        """
        # Contar episódios e vetores
        episode_count = 0
        if os.path.exists(self.episodic_path):
            with open(self.episodic_path) as f:
                episode_count = sum(1 for _ in f)

        vector_count = 0
        if os.path.exists(self.vectors_path):
            with open(self.vectors_path) as f:
                vector_count = sum(1 for _ in f)

        return {
            "episodic": {
                "total_episodes": episode_count,
                "file": self.episodic_path,
            },
            "vector_index": {
                "indexed_episodes": vector_count,
                "file": self.vectors_path,
            },
            "semantic": {
                "tickers_tracked": len(self.semantic.get("tickers", {})),
                "concepts": len(self.semantic.get("concepts", {})),
                "patterns": len(self.semantic.get("patterns", {})),
                "rules": len(self.semantic.get("rules", [])),
                "last_updated": self.semantic.get("last_updated")
            },
            "procedural": {
                "successful_patterns": len(self.procedural.get("successful_patterns", [])),
                "failed_patterns": len(self.procedural.get("failed_patterns", [])),
                "best_practices": len(self.procedural.get("best_practices", [])),
                "last_updated": self.procedural.get("last_updated")
            }
        }
    
    def clear_old_episodes(self, days: int = 90):
        """
        Limpar episódios mais antigos que X dias
        
        Args:
            days: Número de dias para manter
        """
        if not os.path.exists(self.episodic_path):
            return
        
        cutoff_date = datetime.now() - timedelta(days=days)
        kept_episodes = []
        
        with open(self.episodic_path, 'r') as f:
            for line in f:
                try:
                    ep = json.loads(line.strip())
                    ep_date = datetime.fromisoformat(ep['timestamp'])
                    
                    if ep_date >= cutoff_date:
                        kept_episodes.append(line)
                except:
                    continue
        
        # Reescrever arquivo
        with open(self.episodic_path, 'w') as f:
            f.writelines(kept_episodes)
        
        print(f"✅ Cleaned {len(kept_episodes)} episodes (kept last {days} days)")


# =============================================================================
# INTEGRAÇÃO COM ZEROCLAW_DREAM.PY
# =============================================================================

def integrate_with_dream(memory: EnhancedMemory, dream_output: Dict):
    """
    Integrar com saída do zeroclaw_dream.py
    
    O zeroclaw_dream.py consolida memórias periodicamente.
    Esta função extrai insights e os adiciona à memória semântica.
    
    Args:
        memory: Instância de EnhancedMemory
        dream_output: Output do zeroclaw_dream.py
    """
    # Extrair insights do dream
    insights = dream_output.get('insights', [])
    
    for insight in insights:
        # Adicionar à memória semântica
        if insight.get('type') == 'pattern':
            pattern_id = f"pattern_{len(memory.semantic['patterns'])}"
            memory.semantic['patterns'][pattern_id] = {
                "description": insight.get('description'),
                "confidence": insight.get('confidence', 0.0),
                "source": "zeroclaw_dream",
                "timestamp": datetime.now().isoformat()
            }
        
        elif insight.get('type') == 'rule':
            memory.semantic['rules'].append({
                "rule": insight.get('description'),
                "confidence": insight.get('confidence', 0.0),
                "source": "zeroclaw_dream",
                "timestamp": datetime.now().isoformat()
            }
)
    
    # Salvar
    memory._save_semantic()


# =============================================================================
# DEMONSTRAÇÃO
# =============================================================================

def demo():
    """Demonstração do sistema de memória"""
    print("🧠 ENHANCED MEMORY SYSTEM - PHASE 2")
    print("="*70)
    print()
    
    # Inicializar
    memory = EnhancedMemory()
    
    # Exemplo: Armazenar episódio
    print("1️⃣ Armazenando episódio de análise SOL...")
    episode_id = memory.store_episode(
        ticker="SOL",
        analysis_type="options",
        data={
            "spot_price": 91.83,
            "iv": 0.85,
            "btc_correlation": 0.72
        },
        result={
            "success": True,
            "quality": 0.92,
            "recommendations": ["Bull call spread $91/$98"]
        },
        metadata={
            "approach": "black_scholes_greeks",
            "duration_seconds": 2.5
        }
    )
    print(f"✅ Episódio armazenado: {episode_id}")
    print()
    
    # Recuperar episódios similares
    print("2️⃣ Recuperando episódios similares...")
    similar = memory.retrieve_similar_episodes("SOL", "options", days_back=30)
    print(f"✅ Encontrados {len(similar)} episódios similares")
    print()
    
    # Conhecimento semântico
    print("3️⃣ Conhecimento semântico sobre SOL...")
    knowledge = memory.get_semantic_knowledge("SOL")
    print(json.dumps(knowledge, indent=2))
    print()
    
    # Melhores práticas
    print("4️⃣ Melhores práticas para análise de opções...")
    practices = memory.get_best_practices("options")
    for i, practice in enumerate(practices, 1):
        print(f"  {i}. {practice}")
    print()
    
    # Sumário geral
    print("5️⃣ Sumário da memória...")
    summary = memory.get_memory_summary()
    print(json.dumps(summary, indent=2))
    print()
    
    print("="*70)
    print("✅ FASE 2: ENHANCED MEMORY IMPLEMENTADA")


if __name__ == "__main__":
    demo()
