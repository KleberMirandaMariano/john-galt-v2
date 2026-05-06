#!/usr/bin/env python3
"""
Stooq Global Indices Fetcher
Baixa dados de índices (S&P 500, Ibovespa, Nikkei, etc) em CSV
SEM API KEY - apenas download direto de CSV

Tickers suportados:
- IBOV: Ibovespa (Brasil)
- ^GSPC: S&P 500 (EUA)
- ^DJI: Dow Jones (EUA)
- ^IXIC: Nasdaq (EUA)
- ^FTSE: FTSE 100 (UK)
- ^N225: Nikkei 225 (Japão)
- ^TWII: Taiwan Weighted (Taiwan)
- ^HSI: Hang Seng (Hong Kong)
- ^BVSP: Bovespa (Brasil) [alternativa]
"""

import asyncio
import io
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import httpx
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('/tmp/stooq_indices.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StooqIndicesFetcher:
    """Busca dados de índices globais do Stooq"""
    
    # Mapping de ticker → nome amigável + região
    INDICES = {
        "IBOV": {"name": "Ibovespa", "region": "Brasil", "country": "BR"},
        "^GSPC": {"name": "S&P 500", "region": "EUA", "country": "US"},
        "^DJI": {"name": "Dow Jones Industrial Average", "region": "EUA", "country": "US"},
        "^IXIC": {"name": "Nasdaq Composite", "region": "EUA", "country": "US"},
        "^FTSE": {"name": "FTSE 100", "region": "Reino Unido", "country": "UK"},
        "^N225": {"name": "Nikkei 225", "region": "Japão", "country": "JP"},
        "^TWII": {"name": "Taiwan Weighted", "region": "Taiwan", "country": "TW"},
        "^HSI": {"name": "Hang Seng", "region": "Hong Kong", "country": "HK"},
    }
    
    def __init__(self):
        self.client = None
        self.data = {
            "timestamp": None,
            "indices": {},
            "statistics": {}
        }
    
    async def init(self):
        """Inicializar cliente HTTP"""
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Fechar cliente HTTP"""
        if self.client:
            await self.client.aclose()
    
    async def fetch_index_csv(self, ticker: str, days: int = 60) -> Optional[pd.DataFrame]:
        """Buscar dados de índice em CSV do Stooq"""
        try:
            logger.info(f"Buscando dados de {ticker}...")
            
            # URL do Stooq para download CSV
            # Formato: https://stooq.com/q/d/l/?s=TICKER&d1=YYYYMMDD&d2=YYYYMMDD&i=d&o=csv
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            d1 = start_date.strftime("%Y%m%d")
            d2 = end_date.strftime("%Y%m%d")
            
            url = f"https://stooq.com/q/d/l/"
            params = {
                "s": ticker,
                "d1": d1,
                "d2": d2,
                "i": "d",  # Daily data
                "o": "csv"
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200 and len(response.text) > 100:
                # Ler CSV
                df = pd.read_csv(io.StringIO(response.text))
                
                # Converter coluna Data para datetime
                if "Data" in df.columns:
                    df["Data"] = pd.to_datetime(df["Data"], format="%Y-%m-%d")
                
                logger.info(f"✅ {ticker}: {len(df)} dias de dados carregados")
                return df
            else:
                logger.warning(f"⚠️ {ticker}: Nenhum dado encontrado ou erro na requisição")
                return None
        
        except Exception as e:
            logger.error(f"❌ {ticker}: Erro ao buscar dados: {e}")
            return None
    
    def analyze_index(self, ticker: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisar dados de um índice"""
        try:
            info = self.INDICES.get(ticker, {"name": ticker, "region": "Unknown", "country": "XX"})
            
            if df is None or len(df) == 0:
                return None
            
            # Dados mais recentes
            latest = df.iloc[0]  # Primeiro registro (mais recente)
            
            close_price = latest.get("Zamknięcie", latest.get("Close", 0))
            open_price = latest.get("Otwarcie", latest.get("Open", 0))
            high_price = latest.get("Maksimum", latest.get("High", 0))
            low_price = latest.get("Minimum", latest.get("Low", 0))
            volume = latest.get("Wolumin", latest.get("Volume", 0))
            
            # Calcular mudanças
            if len(df) > 1:
                prev_close = df.iloc[-1].get("Zamknięcie", df.iloc[-1].get("Close", close_price))
            else:
                prev_close = close_price
            
            change = close_price - prev_close
            change_pct = (change / prev_close * 100) if prev_close != 0 else 0
            
            # Calcular média móvel (20 dias)
            ma20 = df["Zamknięcie"].mean() if "Zamknięcie" in df.columns else df["Close"].mean()
            
            # Calcular volatilidade (desvio padrão dos retornos diários)
            close_col = "Zamknięcie" if "Zamknięcie" in df.columns else "Close"
            returns = df[close_col].pct_change().dropna()
            volatility = returns.std() * 100  # Em percentagem
            
            return {
                "ticker": ticker,
                "name": info["name"],
                "region": info["region"],
                "country": info["country"],
                "current_price": close_price,
                "open_price": open_price,
                "high_price": high_price,
                "low_price": low_price,
                "change": change,
                "change_pct": change_pct,
                "volume": volume,
                "ma20": ma20,
                "volatility_daily": volatility,
                "days_of_data": len(df),
                "latest_date": str(df.iloc[0]["Data"]) if "Data" in df.columns else "N/A"
            }
        
        except Exception as e:
            logger.error(f"❌ Erro ao analisar {ticker}: {e}")
            return None
    
    async def fetch_all_indices(self) -> Dict[str, Any]:
        """Buscar e analisar TODOS os índices"""
        logger.info("=" * 80)
        logger.info("🌍 STOOQ GLOBAL INDICES FETCHER")
        logger.info("=" * 80)
        
        print("\n⏳ Baixando dados de índices em paralelo...\n")
        
        # Usar asyncio para paralelizar downloads
        tasks = []
        for ticker in self.INDICES.keys():
            task = self.fetch_index_csv(ticker, days=90)
            tasks.append((ticker, task))
        
        # Executar todas as requisições em paralelo
        results = []
        for ticker, task in tasks:
            df = await task
            results.append((ticker, df))
        
        # Analisar cada índice
        self.data["indices"] = {}
        valid_indices = 0
        
        for ticker, df in results:
            analysis = self.analyze_index(ticker, df)
            if analysis:
                self.data["indices"][ticker] = analysis
                valid_indices += 1
        
        self.data["timestamp"] = datetime.now().isoformat()
        
        # Calcular estatísticas
        if valid_indices > 0:
            self.data["statistics"] = {
                "total_indices": len(self.INDICES),
                "successful_fetches": valid_indices,
                "failed_fetches": len(self.INDICES) - valid_indices
            }
        
        logger.info(f"\n✅ Análise concluída!")
        logger.info(f"✅ Índices com sucesso: {valid_indices}/{len(self.INDICES)}")
        
        return self.data
    
    async def save_results(self, filename: str = "/tmp/stooq_indices.json"):
        """Salvar resultados em JSON"""
        try:
            # Converter valores numpy/pandas para JSON-serializable
            data_clean = json.loads(json.dumps(self.data, default=str))
            
            with open(filename, 'w') as f:
                json.dump(data_clean, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Resultados salvos em: {filename}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar resultados: {e}")

async def main():
    fetcher = StooqIndicesFetcher()
    
    try:
        await fetcher.init()
        data = await fetcher.fetch_all_indices()
        await fetcher.save_results()
        
        # Exibir resumo
        print("\n" + "=" * 80)
        print("📊 RESUMO DOS ÍNDICES")
        print("=" * 80 + "\n")
        
        for ticker, info in data["indices"].items():
            change_emoji = "📈" if info["change"] >= 0 else "📉"
            print(f"{change_emoji} {info['name']:30} ({info['country']})")
            print(f"   Preço: {info['current_price']:>10,.2f}")
            print(f"   Mudança: {info['change']:>10,.2f} ({info['change_pct']:>+6.2f}%)")
            print(f"   Volatilidade: {info['volatility_daily']:>6.2f}%")
            print(f"   Dados: {info['days_of_data']} dias")
            print()
        
    finally:
        await fetcher.close()

if __name__ == "__main__":
    asyncio.run(main())
