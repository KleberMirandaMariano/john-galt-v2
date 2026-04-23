#!/usr/bin/env python3
"""
read_cache.py — Carregar dados de cache do VPS cron para análise ZeroClaw
Lê resultado de cripto_daily.sh, fng_alert.sh, b3_update.sh, news_scraper.py
"""

import json
import os
from datetime import datetime
from pathlib import Path

WORKSPACE = "/root/.zeroclaw/workspace"

class CacheReader:
    """Gerenciador de cache para dados coletados via cron"""
    
    def __init__(self):
        self.workspace = Path(WORKSPACE)
    
    def load_cripto_cache(self):
        """Carrega dados de criptográficas coletados por cripto_daily.sh"""
        cache_file = self.workspace / ".cripto_cache.json"
        
        if not cache_file.exists():
            return {
                "status": "No cache",
                "message": "cripto_daily.sh ainda não foi executado",
                "timestamp": None
            }
        
        try:
            with open(cache_file) as f:
                data = json.load(f)
            
            return {
                "status": "OK",
                "btc_price": data.get('bitcoin', {}).get('usd'),
                "btc_24h": data.get('bitcoin', {}).get('usd_24h_change'),
                "eth_price": data.get('ethereum', {}).get('usd'),
                "eth_24h": data.get('ethereum', {}).get('usd_24h_change'),
                "sol_price": data.get('solana', {}).get('usd'),
                "sol_24h": data.get('solana', {}).get('usd_24h_change'),
                "data": data
            }
        except Exception as e:
            return {"status": "Error", "error": str(e)}
    
    def load_fng_cache(self):
        """Carrega Fear & Greed Index coletado por fng_alert.sh"""
        cache_file = self.workspace / ".fng_cache.json"
        
        if not cache_file.exists():
            return {
                "status": "No cache",
                "message": "fng_alert.sh ainda não foi executado",
                "timestamp": None
            }
        
        try:
            with open(cache_file) as f:
                data = json.load(f)
            
            return {
                "status": "OK",
                "fng_value": data.get('value'),
                "fng_label": data.get('value_classification'),
                "timestamp": data.get('timestamp'),
                "data": data
            }
        except Exception as e:
            return {"status": "Error", "error": str(e)}
    
    def load_b3_cache(self):
        """Carrega cotações B3 de b3_cotacoes.txt"""
        cache_file = self.workspace / "b3_cotacoes.txt"
        
        if not cache_file.exists():
            return {
                "status": "No cache",
                "message": "b3_update.sh ainda não foi executado",
                "tickers": []
            }
        
        try:
            tickers = {}
            with open(cache_file) as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    parts = line.strip().split('|')
                    if len(parts) >= 2:
                        ticker = parts[0]
                        tickers[ticker] = {
                            "raw_line": line.strip(),
                            "fields": parts
                        }
            
            return {
                "status": "OK",
                "count": len(tickers),
                "tickers": tickers,
                "data": tickers
            }
        except Exception as e:
            return {"status": "Error", "error": str(e)}
    
    def load_news_cache(self):
        """Carrega notícias de noticias.txt"""
        cache_file = self.workspace / "noticias.txt"
        
        if not cache_file.exists():
            return {
                "status": "No cache",
                "message": "news_scraper.py ainda não foi executado",
                "news_count": 0
            }
        
        try:
            with open(cache_file) as f:
                content = f.read()
            
            lines = [l.strip() for l in content.split('\n') if l.strip()]
            
            return {
                "status": "OK",
                "news_count": len(lines),
                "raw_content": content,
                "lines": lines
            }
        except Exception as e:
            return {"status": "Error", "error": str(e)}
    
    def get_all_cache(self):
        """Carrega todo o cache disponível"""
        return {
            "timestamp": datetime.now().isoformat(),
            "workspace": str(self.workspace),
            "cripto": self.load_cripto_cache(),
            "fng": self.load_fng_cache(),
            "b3": self.load_b3_cache(),
            "news": self.load_news_cache()
        }


# Export para ZeroClaw usar
cache_reader = CacheReader()

if __name__ == "__main__":
    # Teste local
    import pprint
    print("=" * 60)
    print("CACHE STATUS")
    print("=" * 60)
    pprint.pprint(cache_reader.get_all_cache())

