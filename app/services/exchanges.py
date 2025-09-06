"""
Clientes de API para exchanges de criptomoedas
"""

import httpx
import asyncio
from typing import Dict, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BaseExchangeClient:
    """Cliente base para exchanges"""
    
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.client = None
    
    async def _get_client(self):
        """Obter cliente HTTP de forma lazy"""
        if self.client is None:
            try:
                self.client = httpx.AsyncClient(timeout=10.0)
            except Exception as e:
                logger.warning(f"Failed to create HTTP client for {self.name}: {e}")
                return None
        return self.client
    
    async def get_price(self, symbol: str) -> Optional[float]:
        """Método abstrato para obter preço"""
        raise NotImplementedError
    
    async def close(self):
        """Fechar cliente HTTP"""
        if self.client:
            await self.client.aclose()
            self.client = None

class BinanceClient(BaseExchangeClient):
    """Cliente para Binance API"""
    
    def __init__(self):
        super().__init__("binance", "https://api.binance.com")
    
    async def get_price(self, symbol: str) -> Optional[float]:
        """Obter preço da Binance"""
        try:
            client = await self._get_client()
            if not client:
                return None
                
            # Converter símbolo para formato Binance (ex: BTC -> BTCUSDT)
            if not symbol.endswith('USDT'):
                symbol = f"{symbol}USDT"
            
            url = f"{self.base_url}/api/v3/ticker/price"
            params = {"symbol": symbol}
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return float(data["price"])
            
        except Exception as e:
            logger.error(f"Erro ao obter preço da Binance para {symbol}: {e}")
            return None

class CoinbaseClient(BaseExchangeClient):
    """Cliente para Coinbase Pro API"""
    
    def __init__(self):
        super().__init__("coinbase", "https://api.exchange.coinbase.com")
    
    async def get_price(self, symbol: str) -> Optional[float]:
        """Obter preço da Coinbase"""
        try:
            client = await self._get_client()
            if not client:
                return None
                
            # Converter símbolo para formato Coinbase (ex: BTC -> BTC-USD)
            if not symbol.endswith('-USD'):
                symbol = f"{symbol}-USD"
            
            url = f"{self.base_url}/products/{symbol}/ticker"
            
            response = await client.get(url)
            response.raise_for_status()
            
            data = response.json()
            return float(data["price"])
            
        except Exception as e:
            logger.error(f"Erro ao obter preço da Coinbase para {symbol}: {e}")
            return None

class KrakenClient(BaseExchangeClient):
    """Cliente para Kraken API"""
    
    def __init__(self):
        super().__init__("kraken", "https://api.kraken.com")
    
    async def get_price(self, symbol: str) -> Optional[float]:
        """Obter preço da Kraken"""
        try:
            client = await self._get_client()
            if not client:
                return None
                
            # Converter símbolo para formato Kraken (ex: BTC -> XXBTZUSD)
            symbol_mapping = {
                "BTC": "XXBTZUSD",
                "ETH": "XETHZUSD",
                "BTCUSDT": "XXBTZUSD",
                "ETHUSDT": "XETHZUSD"
            }
            
            kraken_symbol = symbol_mapping.get(symbol, symbol)
            
            url = f"{self.base_url}/0/public/Ticker"
            params = {"pair": kraken_symbol}
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "result" in data and kraken_symbol in data["result"]:
                ticker_data = data["result"][kraken_symbol]
                # Usar preço de venda (ask) como referência
                return float(ticker_data["a"][0])
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter preço da Kraken para {symbol}: {e}")
            return None

class ExchangeManager:
    """Gerenciador de exchanges"""
    
    def __init__(self):
        self.exchanges = {}
        self._initialized = False
    
    def _initialize_exchanges(self):
        """Inicializar exchanges apenas quando necessário"""
        if not self._initialized:
            try:
                self.exchanges = {
                    "binance": BinanceClient(),
                    "coinbase": CoinbaseClient(),
                    "kraken": KrakenClient()
                }
                self._initialized = True
                logger.info("✅ All exchanges initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize some exchanges: {e}")
                # Inicializar apenas as que funcionam
                self.exchanges = {}
                try:
                    self.exchanges["binance"] = BinanceClient()
                    logger.info("✅ Binance client initialized")
                except Exception as e:
                    logger.warning(f"❌ Failed to initialize Binance: {e}")
                    
                try:
                    self.exchanges["coinbase"] = CoinbaseClient()
                    logger.info("✅ Coinbase client initialized")
                except Exception as e:
                    logger.warning(f"❌ Failed to initialize Coinbase: {e}")
                    
                try:
                    self.exchanges["kraken"] = KrakenClient()
                    logger.info("✅ Kraken client initialized")
                except Exception as e:
                    logger.warning(f"❌ Failed to initialize Kraken: {e}")
                    
                self._initialized = True
    
    async def get_all_prices(self, symbol: str) -> Dict[str, Optional[float]]:
        """Obter preços de todas as exchanges simultaneamente"""
        self._initialize_exchanges()
        
        if not self.exchanges:
            logger.warning("No exchanges available")
            return {}
        
        tasks = []
        exchange_names = []
        
        for name, client in self.exchanges.items():
            tasks.append(client.get_price(symbol))
            exchange_names.append(name)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        prices = {}
        for i, result in enumerate(results):
            exchange_name = exchange_names[i]
            if isinstance(result, Exception):
                logger.error(f"Erro na exchange {exchange_name}: {result}")
                prices[exchange_name] = None
            else:
                prices[exchange_name] = result
        
        return prices
    
    async def close_all(self):
        """Fechar todas as conexões"""
        for client in self.exchanges.values():
            await client.close()

# Instância global do gerenciador (inicialização lazy)
exchange_manager = ExchangeManager()