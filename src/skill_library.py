#!/usr/bin/env python3
"""
skill_library.py - Phase 3: Skill Library System

Extrai padrões de código de análises bem-sucedidas
Cria biblioteca de funções reutilizáveis
Auto-descoberta de novas skills

Autor: John Galt v2.0 - Phase 3
Data: 08/05/2026
"""

import json
import os
import ast
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from collections import defaultdict, Counter
import re


class SkillLibrary:
    """
    Biblioteca de skills extraídas automaticamente de análises bem-sucedidas
    
    Features:
    1. Pattern Extraction: Extrai padrões de código de episódios
    2. Skill Discovery: Identifica novas skills automaticamente
    3. Code Reuse: Biblioteca de funções reutilizáveis
    4. Skill Composition: Combina skills para tarefas complexas
    """
    
    def __init__(self, library_dir: str = "/root/.zeroclaw/skills"):
        """
        Args:
            library_dir: Diretório para armazenar skills
        """
        self.library_dir = library_dir
        self.skills_path = os.path.join(library_dir, "skills.json")
        self.patterns_path = os.path.join(library_dir, "patterns.json")
        self.metadata_path = os.path.join(library_dir, "metadata.json")
        
        # Criar diretórios
        os.makedirs(library_dir, exist_ok=True)
        os.makedirs(os.path.join(library_dir, "code"), exist_ok=True)
        
        # Carregar biblioteca
        self.skills = self._load_skills()
        self.patterns = self._load_patterns()
        self.metadata = self._load_metadata()
    
    # =================================================================
    # PATTERN EXTRACTION
    # =================================================================
    
    def extract_patterns_from_code(self, code: str, context: Dict) -> List[Dict]:
        """
        Extrair padrões de código Python
        
        Args:
            code: Código Python
            context: Contexto da análise (ticker, tipo, resultado)
        
        Returns:
            Lista de padrões extraídos
        """
        patterns = []
        
        try:
            tree = ast.parse(code)
            
            # Extrair funções
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    pattern = self._extract_function_pattern(node, code, context)
                    if pattern:
                        patterns.append(pattern)
                
                # Extrair imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        patterns.append({
                            "type": "import",
                            "module": alias.name,
                            "context": context
                        })
                
                elif isinstance(node, ast.ImportFrom):
                    patterns.append({
                        "type": "import_from",
                        "module": node.module,
                        "names": [alias.name for alias in node.names],
                        "context": context
                    })
        
        except SyntaxError:
            # Código inválido, ignorar
            pass
        
        return patterns
    
    def _extract_function_pattern(
        self, 
        node: ast.FunctionDef, 
        code: str, 
        context: Dict
    ) -> Optional[Dict]:
        """Extrair padrão de uma função"""
        # Pegar código fonte da função
        try:
            func_code = ast.get_source_segment(code, node)
            if not func_code:
                return None
            
            # Extrair assinatura
            args = [arg.arg for arg in node.args.args]
            
            # Calcular hash do código
            code_hash = hashlib.md5(func_code.encode()).hexdigest()[:12]
            
            return {
                "type": "function",
                "name": node.name,
                "args": args,
                "code": func_code,
                "hash": code_hash,
                "docstring": ast.get_docstring(node),
                "context": context,
                "line_count": func_code.count('\n') + 1
            }
        except:
            return None
    
    def extract_api_patterns(self, code: str, context: Dict) -> List[Dict]:
        """
        Extrair padrões de chamadas de API
        
        Returns:
            Lista de padrões de API
        """
        patterns = []
        
        # Regex para URLs de API
        url_pattern = r'https?://[^\s"\'\)]+(?:/[^\s"\'\)]*)?'
        urls = re.findall(url_pattern, code)
        
        for url in urls:
            # Identificar tipo de API
            api_type = "unknown"
            if "coingecko" in url.lower():
                api_type = "coingecko"
            elif "okx.com" in url.lower():
                api_type = "okx"
            elif "bcb.gov.br" in url.lower():
                api_type = "bcb"
            elif "brapi.dev" in url.lower():
                api_type = "brapi"
            
            patterns.append({
                "type": "api_call",
                "api_type": api_type,
                "url": url,
                "context": context
            })
        
        return patterns
    
    # =================================================================
    # SKILL DISCOVERY
    # =================================================================
    
    def discover_skill(
        self, 
        code: str, 
        quality_score: float,
        context: Dict
    ) -> Optional[str]:
        """
        Descobrir nova skill a partir de código bem-sucedido
        
        Args:
            code: Código da análise
            quality_score: Score de qualidade (0-1)
            context: Contexto (ticker, tipo, etc)
        
        Returns:
            ID da skill descoberta ou None
        """
        if quality_score < 0.85:
            return None  # Só descobrir de análises de alta qualidade
        
        # Extrair padrões
        code_patterns = self.extract_patterns_from_code(code, context)
        api_patterns = self.extract_api_patterns(code, context)
        
        all_patterns = code_patterns + api_patterns
        
        if not all_patterns:
            return None
        
        # Gerar ID da skill
        skill_id = self._generate_skill_id(context)
        
        # Criar skill
        skill = {
            "id": skill_id,
            "name": self._generate_skill_name(context),
            "description": f"Extracted from {context.get('type', 'unknown')} analysis",
            "patterns": all_patterns,
            "quality_score": quality_score,
            "context": context,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0,
            "success_rate": 1.0  # Inicial
        }
        
        # Armazenar skill
        self.skills[skill_id] = skill
        
        # Armazenar código (se tiver funções)
        functions = [p for p in code_patterns if p['type'] == 'function']
        if functions:
            code_path = os.path.join(self.library_dir, "code", f"{skill_id}.py")
            with open(code_path, 'w') as f:
                f.write(f"# Skill: {skill['name']}\n")
                f.write(f"# Created: {skill['created_at']}\n")
                f.write(f"# Quality: {quality_score:.2f}\n\n")
                for func in functions:
                    f.write(func['code'] + "\n\n")
        
        # Salvar
        self._save_skills()
        
        return skill_id
    
    def _generate_skill_id(self, context: Dict) -> str:
        """Gerar ID único para skill"""
        timestamp = datetime.now().isoformat()
        content = f"{context.get('ticker', 'unknown')}_{context.get('type', 'unknown')}_{timestamp}"
        return "skill_" + hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _generate_skill_name(self, context: Dict) -> str:
        """Gerar nome descritivo para skill"""
        ticker = context.get('ticker', 'unknown')
        analysis_type = context.get('type', 'unknown')
        return f"{ticker}_{analysis_type}_skill"
    
    # =================================================================
    # SKILL RETRIEVAL & COMPOSITION
    # =================================================================
    
    def find_relevant_skills(
        self, 
        ticker: str, 
        analysis_type: str,
        min_quality: float = 0.85,
        limit: int = 5
    ) -> List[Dict]:
        """
        Encontrar skills relevantes para uma análise
        
        Args:
            ticker: Ticker atual
            analysis_type: Tipo de análise
            min_quality: Qualidade mínima
            limit: Máximo de skills a retornar
        
        Returns:
            Lista de skills relevantes
        """
        relevant = []
        
        for skill_id, skill in self.skills.items():
            ctx = skill.get('context', {})
            
            # Filtrar por qualidade
            if skill.get('quality_score', 0) < min_quality:
                continue
            
            # Match exato: mesmo ticker e tipo
            if ctx.get('ticker') == ticker and ctx.get('type') == analysis_type:
                relevant.append({
                    **skill,
                    "relevance": 1.0
                })
            
            # Match parcial: mesmo tipo
            elif ctx.get('type') == analysis_type:
                relevant.append({
                    **skill,
                    "relevance": 0.7
                })
            
            # Match fraco: mesmo ticker
            elif ctx.get('ticker') == ticker:
                relevant.append({
                    **skill,
                    "relevance": 0.5
                })
        
        # Ordenar por relevância e qualidade
        relevant.sort(
            key=lambda x: (x['relevance'], x['quality_score']), 
            reverse=True
        )
        
        return relevant[:limit]
    
    def compose_skills(self, skill_ids: List[str]) -> str:
        """
        Compor múltiplas skills em um código único
        
        Args:
            skill_ids: Lista de IDs de skills
        
        Returns:
            Código composto
        """
        composed_code = []
        imports = set()
        functions = []
        
        for skill_id in skill_ids:
            skill = self.skills.get(skill_id)
            if not skill:
                continue
            
            # Coletar imports
            for pattern in skill.get('patterns', []):
                if pattern['type'] == 'import':
                    imports.add(f"import {pattern['module']}")
                elif pattern['type'] == 'import_from':
                    names = ', '.join(pattern['names'])
                    imports.add(f"from {pattern['module']} import {names}")
            
            # Coletar funções
            code_path = os.path.join(self.library_dir, "code", f"{skill_id}.py")
            if os.path.exists(code_path):
                with open(code_path, 'r') as f:
                    code = f.read()
                    # Remover comentários de header
                    code = re.sub(r'^#.*\n', '', code, flags=re.MULTILINE)
                    functions.append(code.strip())
        
        # Montar código composto
        if imports:
            composed_code.append('\n'.join(sorted(imports)))
            composed_code.append('')
        
        if functions:
            composed_code.extend(functions)
        
        return '\n'.join(composed_code)
    
    # =================================================================
    # SKILL ANALYTICS
    # =================================================================
    
    def get_skill_stats(self, skill_id: str) -> Dict:
        """Estatísticas de uma skill"""
        skill = self.skills.get(skill_id)
        if not skill:
            return {"error": "Skill not found"}
        
        return {
            "id": skill_id,
            "name": skill['name'],
            "quality_score": skill.get('quality_score', 0),
            "usage_count": skill.get('usage_count', 0),
            "success_rate": skill.get('success_rate', 0),
            "created_at": skill.get('created_at'),
            "pattern_count": len(skill.get('patterns', [])),
            "context": skill.get('context', {})
        }
    
    def get_library_summary(self) -> Dict:
        """Sumário da biblioteca"""
        total_skills = len(self.skills)
        
        # Skills por tipo
        by_type = defaultdict(int)
        for skill in self.skills.values():
            ctx = skill.get('context', {})
            by_type[ctx.get('type', 'unknown')] += 1
        
        # Skills por ticker
        by_ticker = defaultdict(int)
        for skill in self.skills.values():
            ctx = skill.get('context', {})
            by_ticker[ctx.get('ticker', 'unknown')] += 1
        
        # Top skills por qualidade
        top_skills = sorted(
            self.skills.items(),
            key=lambda x: x[1].get('quality_score', 0),
            reverse=True
        )[:5]
        
        return {
            "total_skills": total_skills,
            "by_type": dict(by_type),
            "by_ticker": dict(by_ticker),
            "top_skills": [
                {
                    "id": skill_id,
                    "name": skill['name'],
                    "quality": skill.get('quality_score', 0)
                }
                for skill_id, skill in top_skills
            ],
            "total_patterns": sum(
                len(s.get('patterns', [])) for s in self.skills.values()
            )
        }
    
    def update_skill_metrics(
        self, 
        skill_id: str, 
        success: bool
    ):
        """
        Atualizar métricas de uma skill
        
        Args:
            skill_id: ID da skill
            success: Se o uso foi bem-sucedido
        """
        skill = self.skills.get(skill_id)
        if not skill:
            return
        
        # Atualizar contadores
        skill['usage_count'] = skill.get('usage_count', 0) + 1
        
        # Atualizar success rate (média móvel)
        current_rate = skill.get('success_rate', 1.0)
        usage_count = skill['usage_count']
        
        # Média móvel exponencial
        alpha = 0.1  # Peso do novo resultado
        new_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * current_rate
        skill['success_rate'] = new_rate
        
        # Salvar
        self._save_skills()
    
    # =================================================================
    # PERSISTENCE
    # =================================================================
    
    def _load_skills(self) -> Dict:
        """Carregar skills"""
        if os.path.exists(self.skills_path):
            with open(self.skills_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_skills(self):
        """Salvar skills"""
        with open(self.skills_path, 'w') as f:
            json.dump(self.skills, f, indent=2)
    
    def _load_patterns(self) -> Dict:
        """Carregar padrões"""
        if os.path.exists(self.patterns_path):
            with open(self.patterns_path, 'r') as f:
                return json.load(f)
        return {"common_patterns": [], "rare_patterns": []}
    
    def _save_patterns(self):
        """Salvar padrões"""
        with open(self.patterns_path, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def _load_metadata(self) -> Dict:
        """Carregar metadados"""
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'r') as f:
                return json.load(f)
        return {
            "last_updated": None,
            "total_discoveries": 0,
            "total_compositions": 0
        }
    
    def _save_metadata(self):
        """Salvar metadados"""
        self.metadata["last_updated"] = datetime.now().isoformat()
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)


# =============================================================================
# INTEGRATION WITH ENHANCED MEMORY
# =============================================================================

def integrate_with_memory(library: SkillLibrary, memory_dir: str):
    """
    Integrar Skill Library com Enhanced Memory
    
    Lê episódios bem-sucedidos e descobre skills automaticamente
    
    Args:
        library: Instância de SkillLibrary
        memory_dir: Diretório de memória episódica
    """
    episodic_path = os.path.join(memory_dir, "episodic.jsonl")
    
    if not os.path.exists(episodic_path):
        return
    
    discovered = 0
    
    # Ler episódios
    with open(episodic_path, 'r') as f:
        for line in f:
            try:
                episode = json.loads(line.strip())
                
                # Verificar se tem código
                metadata = episode.get('metadata', {})
                code = metadata.get('code')
                
                if not code:
                    continue
                
                # Verificar qualidade
                result = episode.get('result', {})
                quality = result.get('quality', 0.0)
                
                if quality < 0.85:
                    continue
                
                # Descobrir skill
                context = {
                    "ticker": episode.get('ticker'),
                    "type": episode.get('type'),
                    "episode_id": episode.get('id')
                }
                
                skill_id = library.discover_skill(code, quality, context)
                
                if skill_id:
                    discovered += 1
            
            except:
                continue
    
    print(f"✅ Discovered {discovered} new skills from memory")


# =============================================================================
# DEMONSTRAÇÃO
# =============================================================================

def demo():
    """Demonstração do sistema de skills"""
    print("🧰 SKILL LIBRARY SYSTEM - PHASE 3")
    print("="*70)
    print()
    
    # Inicializar
    library = SkillLibrary()
    
    # Exemplo: Código de análise bem-sucedida
    sample_code = '''
def calculate_black_scholes(S, K, T, r, sigma, option_type='call'):
    """Calculate Black-Scholes option price"""
    from scipy.stats import norm
    import numpy as np
    
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    
    if option_type == 'call':
        price = S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
    else:
        price = K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)
    
    return price

def fetch_spot_price(ticker):
    """Fetch spot price from CoinGecko"""
    import requests
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ticker}&vs_currencies=usd"
    resp = requests.get(url)
    return resp.json()[ticker]['usd']
'''
    
    print("1️⃣ Descobrindo skill de código bem-sucedido...")
    skill_id = library.discover_skill(
        code=sample_code,
        quality_score=0.92,
        context={
            "ticker": "SOL",
            "type": "options",
            "approach": "black_scholes"
        }
    )
    print(f"✅ Skill descoberta: {skill_id}")
    print()
    
    # Estatísticas
    print("2️⃣ Estatísticas da skill...")
    stats = library.get_skill_stats(skill_id)
    print(json.dumps(stats, indent=2))
    print()
    
    # Buscar skills relevantes
    print("3️⃣ Buscando skills relevantes para SOL options...")
    relevant = library.find_relevant_skills("SOL", "options")
    print(f"✅ Encontradas {len(relevant)} skills relevantes")
    if relevant:
        print(f"   Top skill: {relevant[0]['name']} (relevance: {relevant[0]['relevance']:.2f})")
    print()
    
    # Compor skills
    print("4️⃣ Compondo código de skills...")
    if skill_id:
        composed = library.compose_skills([skill_id])
        lines = composed.split('\n')
        print(f"✅ Código composto ({len(lines)} linhas):")
        print(composed[:200] + "..." if len(composed) > 200 else composed)
    print()
    
    # Sumário da biblioteca
    print("5️⃣ Sumário da biblioteca...")
    summary = library.get_library_summary()
    print(json.dumps(summary, indent=2))
    print()
    
    print("="*70)
    print("✅ FASE 3: SKILL LIBRARY IMPLEMENTADA")


if __name__ == "__main__":
    demo()
