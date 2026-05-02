#!/usr/bin/env python3
"""
Deribit BTC Options Fetcher
Busca dados de 946 opções BTC em tempo real via API pública Deribit
"""

import asyncio
import json
import logging
from datetime import datetime
import httpx

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('/tmp/deribit_btc_options.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DeribitBTCFetcher:
    BASE_URL = "https://www.deribit.com/api/v2"
    
    def __init__(self):
        self.data = {
            "timestamp": None,
            "btc_price": None,
            "options": [],
            "statistics": {}
        }
    
    async def fetch_btc_price(self) -> float:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.BASE_URL}/public/get_index_price?index_name=btc_usd")
                data = resp.json()
                price = data.get("result", {}).get("index_price", 0)
                logger.info(f"✅ BTC Price: ${price:,.2f}")
                return price
        except Exception as e:
            logger.error(f"❌ Erro ao buscar preço BTC: {e}")
            return 0
    
    async def fetch_instruments(self) -> list:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{self.BASE_URL}/public/get_instruments?currency=BTC&kind=option"
                )
                data = resp.json()
                instruments = data.get("result", [])
                logger.info(f"✅ {len(instruments)} opções BTC encontradas")
                return instruments
        except Exception as e:
            logger.error(f"❌ Erro ao buscar instrumentos: {e}")
            return []
    
    async def fetch_ticker(self, instrument_name: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{self.BASE_URL}/public/ticker?instrument_name={instrument_name}"
                )
                data = resp.json()
                result = data.get("result", {})
                
                if result:
                    return {
                        "instrument": instrument_name,
                        "bid": result.get("best_bid_price", 0),
                        "ask": result.get("best_ask_price", 0),
                        "last_price": result.get("last_price", 0),
                        "iv": result.get("mark_iv", 0),
                        "open_interest": result.get("open_interest", 0),
                        "mark_price": result.get("mark_price", 0),
                        "delta": result.get("greeks", {}).get("delta", 0),
                        "gamma": result.get("greeks", {}).get("gamma", 0),
                        "vega": result.get("greeks", {}).get("vega", 0),
                        "theta": result.get("greeks", {}).get("theta", 0),
                        "rho": result.get("greeks", {}).get("rho", 0),
                    }
        except Exception as e:
            logger.error(f"❌ Erro ao buscar {instrument_name}: {e}")
        
        return {}
    
    async def fetch_all_options(self, instruments: list) -> list:
        logger.info(f"\n⏳ Processando {len(instruments)} opções em paralelo...")
        
        all_options = []
        batch_size = 50
        
        for i in range(0, len(instruments), batch_size):
            batch = instruments[i:i+batch_size]
            logger.info(f"📦 Batch {i//batch_size + 1}: {len(batch)} opções")
            
            tasks = [self.fetch_ticker(inst["instrument_name"]) for inst in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, dict) and result:
                    all_options.append(result)
        
        logger.info(f"✅ {len(all_options)} opções processadas com sucesso")
        return all_options
    
    async def run(self):
        logger.info("=" * 80)
        logger.info("🚀 DERIBIT BTC OPTIONS FETCHER")
        logger.info("=" * 80 + "\n")
        
        self.data["btc_price"] = await self.fetch_btc_price()
        instruments = await self.fetch_instruments()
        
        if not instruments:
            logger.error("❌ Nenhum instrumento encontrado")
            return
        
        self.data["options"] = await self.fetch_all_options(instruments)
        self.data["timestamp"] = datetime.now().isoformat()
        self.data["statistics"] = {
            "total_instruments": len(instruments),
            "options_fetched": len(self.data["options"]),
            "success_rate": f"{len(self.data['options'])/len(instruments)*100:.1f}%"
        }
        
        logger.info(f"\n✅ Total: {len(self.data['options'])} opções coletadas")
        logger.info(f"📊 Taxa de sucesso: {self.data['statistics']['success_rate']}")
    
    async def save_results(self):
        try:
            with open("/tmp/deribit_btc_options.json", "w") as f:
                json.dump(self.data, f, indent=2)
            logger.info("💾 Resultados salvos em /tmp/deribit_btc_options.json")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar: {e}")

async def main():
    fetcher = DeribitBTCFetcher()
    await fetcher.run()
    await fetcher.save_results()
    
    print("\n" + "=" * 80)
    print("📊 RESUMO - OPÇÕES BTC")
    print("=" * 80)
    print(f"\n💰 BTC Price: ${fetcher.data['btc_price']:,.2f}")
    print(f"📈 Opções coletadas: {len(fetcher.data['options'])}")
    print(f"✅ Taxa de sucesso: {fetcher.data['statistics']['success_rate']}")
    print(f"⏰ Timestamp: {fetcher.data['timestamp']}")
    print("\n💾 Arquivo: /tmp/deribit_btc_options.json")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
