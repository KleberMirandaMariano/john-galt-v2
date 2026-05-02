#!/usr/bin/env python3
"""
YFinance Global Indices Fetcher
Busca dados de 8 índices globais em tempo real via yfinance
"""

import asyncio
import json
import logging
from datetime import datetime
import yfinance as yf
import pandas as pd

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
    INDICES = {
        "^GSPC": {"name": "S&P 500", "country": "US", "currency": "USD"},
        "^DJI": {"name": "Dow Jones", "country": "US", "currency": "USD"},
        "^IXIC": {"name": "Nasdaq", "country": "US", "currency": "USD"},
        "^FTSE": {"name": "FTSE 100", "country": "UK", "currency": "GBP"},
        "^N225": {"name": "Nikkei 225", "country": "JP", "currency": "JPY"},
        "^TWII": {"name": "Taiwan", "country": "TW", "currency": "TWD"},
        "^HSI": {"name": "Hang Seng", "country": "HK", "currency": "HKD"},
        "^BVSP": {"name": "Ibovespa", "country": "BR", "currency": "BRL"},
    }
    
    def __init__(self):
        self.data = {"timestamp": None, "indices": {}, "statistics": {}}
    
    async def fetch_index_data(self, ticker: str) -> dict:
        try:
            logger.info(f"Buscando {ticker}...")
            
            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(
                None,
                lambda: yf.download(ticker, period="1y", progress=False, threads=False)
            )
            
            if df is None or df.empty:
                logger.warning(f"⚠️ {ticker}: Sem dados")
                return None
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            logger.info(f"✅ {ticker}: {len(df)} dias")
            
            last = df.iloc[-1]
            close = float(last["Close"])
            open_p = float(last["Open"])
            high = float(last["High"])
            low = float(last["Low"])
            
            data = {
                "ticker": ticker,
                "name": self.INDICES[ticker]["name"],
                "country": self.INDICES[ticker]["country"],
                "currency": self.INDICES[ticker]["currency"],
                "close": close,
                "open": open_p,
                "high": high,
                "low": low,
                "days": len(df),
                "date": str(df.index[-1].date())
            }
            
            if len(df) > 1:
                prev = float(df.iloc[-2]["Close"])
                data["change"] = close - prev
                data["change_pct"] = (data["change"] / prev * 100) if prev else 0
            else:
                data["change"] = 0
                data["change_pct"] = 0
            
            returns = df["Close"].pct_change().dropna()
            data["volatility"] = float(returns.std() * 100) if len(returns) > 0 else 0
            
            return data
        
        except Exception as e:
            logger.error(f"❌ {ticker}: {e}")
            return None
    
    async def fetch_all_indices(self):
        logger.info("=" * 80)
        logger.info("🌍 YFINANCE GLOBAL INDICES FETCHER")
        logger.info("=" * 80 + "\n")
        
        tasks = [self.fetch_index_data(ticker) for ticker in self.INDICES.keys()]
        results = await asyncio.gather(*tasks)
        
        self.data["indices"] = {r["ticker"]: r for r in results if r}
        self.data["timestamp"] = datetime.now().isoformat()
        valid = len(self.data["indices"])
        
        self.data["statistics"] = {
            "total": len(self.INDICES),
            "successful": valid,
            "failed": len(self.INDICES) - valid
        }
        
        logger.info(f"\n✅ {valid}/{len(self.INDICES)}")
        return self.data
    
    async def save_results(self):
        try:
            with open("/tmp/yfinance_indices.json", "w") as f:
                json.dump(self.data, f, indent=2)
            logger.info("💾 Salvos em /tmp/yfinance_indices.json")
        except Exception as e:
            logger.error(f"Erro ao salvar: {e}")

async def main():
    fetcher = YFinanceIndicesFetcher()
    await fetcher.fetch_all_indices()
    await fetcher.save_results()
    
    print("\n" + "=" * 80)
    print("📊 RESUMO DOS ÍNDICES")
    print("=" * 80 + "\n")
    
    for ticker, info in sorted(fetcher.data["indices"].items()):
        emoji = "📈" if info["change_pct"] >= 0 else "📉"
        print(f"{emoji} {info['name']:25} {info['close']:>10,.2f} {info['currency']:3} ({info['change_pct']:>+6.2f}%) | Vol: {info['volatility']:.2f}%")
    
    print("\n" + "=" * 80)
    print(f"✅ Total: {fetcher.data['statistics']['successful']}/{fetcher.data['statistics']['total']}")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
