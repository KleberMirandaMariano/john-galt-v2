#!/usr/bin/env python3
"""
read_cache.py — Carregar dados de cache do VPS cron para análise ZeroClaw
Lê resultado de cripto_daily.sh, fng_alert.sh, b3_update.sh, news_scraper.py
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

WORKSPACE = os.getenv('ZEROCLAW_WORKSPACE', '/root/.zeroclaw/workspace')
DEFAULT_MAX_CACHE_AGE_MINUTES = 60


class CacheReader:
    """Gerenciador de cache para dados coletados via cron"""

    def __init__(self, max_age_minutes: int = DEFAULT_MAX_CACHE_AGE_MINUTES):
        self.workspace = Path(WORKSPACE)
        self.max_age_minutes = max_age_minutes

    def _is_stale(self, file_path: Path) -> bool:
        """Verifica se o arquivo de cache está desatualizado."""
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            age = datetime.now() - mtime
            if age > timedelta(minutes=self.max_age_minutes):
                logger.warning("Cache %s está desatualizado (%.0f min)", file_path.name, age.total_seconds() / 60)
                return True
            return False
        except OSError:
            return True

    def load_cripto_cache(self):
        """Carrega dados de criptográficas coletados por cripto_daily.sh"""
        cache_file = self.workspace / ".cripto_cache.json"

        if not cache_file.exists():
            logger.info("Cache cripto não encontrado: %s", cache_file)
            return {
                "status": "No cache",
                "message": "cripto_daily.sh ainda não foi executado",
                "timestamp": None
            }

        if self._is_stale(cache_file):
            return {
                "status": "Stale",
                "message": f"Cache mais antigo que {self.max_age_minutes} minutos",
                "timestamp": datetime.fromtimestamp(cache_file.stat().st_mtime).isoformat()
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
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("Erro ao ler cache cripto: %s", e)
            return {"status": "Error", "error": str(e)}

    def load_fng_cache(self):
        """Carrega Fear & Greed Index coletado por fng_alert.sh"""
        cache_file = self.workspace / ".fng_cache.json"

        if not cache_file.exists():
            logger.info("Cache FNG não encontrado: %s", cache_file)
            return {
                "status": "No cache",
                "message": "fng_alert.sh ainda não foi executado",
                "timestamp": None
            }

        if self._is_stale(cache_file):
            return {
                "status": "Stale",
                "message": f"Cache mais antigo que {self.max_age_minutes} minutos",
                "timestamp": datetime.fromtimestamp(cache_file.stat().st_mtime).isoformat()
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
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("Erro ao ler cache FNG: %s", e)
            return {"status": "Error", "error": str(e)}

    def load_b3_cache(self):
        """Carrega cotações B3 de b3_cotacoes.txt"""
        cache_file = self.workspace / "b3_cotacoes.txt"

        if not cache_file.exists():
            logger.info("Cache B3 não encontrado: %s", cache_file)
            return {
                "status": "No cache",
                "message": "b3_update.sh ainda não foi executado",
                "tickers": []
            }

        if self._is_stale(cache_file):
            return {
                "status": "Stale",
                "message": f"Cache mais antigo que {self.max_age_minutes} minutos",
                "timestamp": datetime.fromtimestamp(cache_file.stat().st_mtime).isoformat()
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
        except OSError as e:
            logger.error("Erro ao ler cache B3: %s", e)
            return {"status": "Error", "error": str(e)}

    def load_news_cache(self):
        """Carrega notícias de noticias.txt"""
        cache_file = self.workspace / "noticias.txt"

        if not cache_file.exists():
            logger.info("Cache de notícias não encontrado: %s", cache_file)
            return {
                "status": "No cache",
                "message": "news_scraper.py ainda não foi executado",
                "news_count": 0
            }

        if self._is_stale(cache_file):
            return {
                "status": "Stale",
                "message": f"Cache mais antigo que {self.max_age_minutes} minutos",
                "timestamp": datetime.fromtimestamp(cache_file.stat().st_mtime).isoformat()
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
        except OSError as e:
            logger.error("Erro ao ler cache de notícias: %s", e)
            return {"status": "Error", "error": str(e)}

    def get_all_cache(self):
        """Carrega todo o cache disponível"""
        return {
            "timestamp": datetime.now().isoformat(),
            "workspace": str(self.workspace),
            "max_age_minutes": self.max_age_minutes,
            "cripto": self.load_cripto_cache(),
            "fng": self.load_fng_cache(),
            "b3": self.load_b3_cache(),
            "news": self.load_news_cache()
        }


cache_reader = CacheReader()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    import pprint
    print("=" * 60)
    print("CACHE STATUS")
    print("=" * 60)
    pprint.pprint(cache_reader.get_all_cache())
