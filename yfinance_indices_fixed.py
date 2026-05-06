#!/usr/bin/env python3
"""YFinance Global Indices Fetcher - VERSÃO CORRIGIDA"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import yfinance as yf

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('/tmp/yfinance_indices.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class YFinanceIndicesFetcher:
    """Busca dados de índices globais via yfinance"""
    
    INDICES = {
        "^GSPC": {"name": "S&P 500", "region": "EUA", "country": "US", "currency": "USD"},
        "^DJI": {"name": "Dow Jones", "region": "EUA", "country": "US", "currency": "USD"},
        "^IXIC": {"name": "Nasdaq", "region": "EUA", "country": "US", "currency": "USD"},
        "^FTSE": {"name": "FTSE 100", "region": "UK", "country": "UK", "currency": "GBP"},
        "^N225": {"name": "Nikkei 225", "region": "Japão", "country": "JP", "currency": "JPY"},
        "^TWII": {"name": "Taiwan", "region": "Taiwan", "country": "TW", "currency": "TWD"},
        "^HSI": {"name": "Hang Seng", "region": "HK", "country": "HK", "currency": "HKD"},
        "^BVSP": {"name": "Ibovespa", "region": "Brasil", "country": "BR", "currency": "BRL"},
    }
    
    def __init__(self):
        self.data = {"timestamp": None, "indices": {}, "statistics": {}}
    
    async def fetch_index_data(self, ticker: str, days: int = 365) -> Optional[dict]:
        """Buscar dados de índice via yfinance"""
        try:
            logger.info(f"Buscando {ticker}...")
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(
                None,
                lambda: yf.download(ticker, start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"), progress=False)
            )
            
            if df is not None and not df.empty:
                logger.info(f"✅ {ticker}: {len(df)} dias")
                
                # Extrair dados da última linha
                last = df.iloc[-1]
                data = {
                    "ticker": ticker,
                    "name": self.INDICES[ticker]["name"],
                    "country": self.INDICES[ticker]["country"],
                    "currency": self.INDICES[ticker]["currency"],
                    "close": float(last["Close"]),
                    "open": float(last["Open"]),
                    "high": float(last["High"]),
                    "low": float(last["Low"]),
                    "volume": float(last.get("Volume", 0)),
                    "days_data": len(df),
                    "date": str(df.index[-1].date())
                }
                
                # Calcular mudanças
                if len(df) > 1:
                    prev_close = float(df.iloc[-2]["Close"])
                    data["change"] = data["close"] - prev_close
                    data["change_pct"] = (data["change"] / prev_close * 100) if prev_close else 0
                else:
                    data["change"] = 0
                    data["change_pct"] = 0
                
                # Volatilidade
                returns = df["Close"].pct_change().dropna()
                data["volatility"] = float(returns.std() * 100) if len(returns) > 0 else 0
                
                return data
            else:
                logger.warning(f"⚠️ {ticker}: Sem dados")
                return None
        
        except Exception as e:
            logger.error(f"❌ {ticker}: {e}")
            return None
    
    async def fetch_all_indices(self) -> Dict[str, Any]:
        """Buscar todos os índices"""
        logger.info("=" * 80)
        logger.info("🌍 YFINANCE GLOBAL INDICES FETCHER")
        logger.info("=" * 80 + "\n")
        
        # Fetch paralelo
        tasks = [self.fetch_index_data(ticker) for ticker in self.INDICES.keys()]
        results = await asyncio.gather(*tasks)
        
        # Consolidar resultados
        self.data["indices"] = {r["ticker"]: r for r in results if r is not None}
        self.data["timestamp"] = datetime.now().isoformat()
        
        valid = len(self.data["indices"])
        self.data["statistics"] = {
            "total": len(self.INDICES),
            "successful": valid,
            "failed": len(self.INDICES) - valid
        }
        
        logger.info(f"\n✅ Análise concluída: {valid}/{len(self.INDICES)}")
        return self.data
    
    async def save_results(self):
        """Salvar em JSON"""
        try:
            with open("/tmp/yfinance_indices.json", "w") as f:
                json.dump(self.data, f, indent=2)
            logger.info("💾 Resultados salvos")
        except Exception as e:
            logger.error(f"Erro ao salvar: {e}")

async def main():
    fetcher = YFinanceIndicesFetcher()
    data = await fetcher.fetch_all_indices()
    await fetcher.save_results()
    
    print("\n" + "=" * 80)
    print("📊 RESUMO")
    print("=" * 80 + "\n")
    
    for ticker, info in data["indices"].items():
        emoji = "📈" if info["change_pct"] >= 0 else "📉"
        print(f"{emoji} {info['name']:20} {info['close']:>10,.2f} {info['currency']:3} ({info['change_pct']:>+6.2f}%)")
    
    print("\n" + "=" * 80)
    print(f"Total: {data['statistics']['successful']}/{data['statistics']['total']}")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
