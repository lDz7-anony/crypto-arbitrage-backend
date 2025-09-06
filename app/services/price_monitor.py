"""
Serviço de monitoramento de preços e detecção de arbitragem
"""

import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import logging

from app.models.price import Price, ArbitrageOpportunity, PriceComparison
from app.services.exchanges import exchange_manager

logger = logging.getLogger(__name__)

class PriceMonitorService:
    """Serviço para monitoramento de preços e detecção de arbitragem"""
    
    def __init__(self, min_profit_percentage: float = 0.5):
        self.min_profit_percentage = min_profit_percentage
        self.supported_symbols = ["BTC", "ETH"]
    
    async def get_price_comparison(self, symbol: str) -> Optional[PriceComparison]:
        """Obter comparação de preços entre todas as exchanges"""
        try:
            # Obter preços de todas as exchanges
            prices_dict = await exchange_manager.get_all_prices(symbol)
            
            # Criar objetos Price
            prices = []
            for exchange, price_value in prices_dict.items():
                if price_value is not None:
                    price = Price(
                        exchange=exchange,
                        symbol=symbol,
                        price=price_value,
                        timestamp=datetime.utcnow()
                    )
                    prices.append(price)
            
            if len(prices) < 2:
                logger.warning(f"Preços insuficientes para {symbol}: {len(prices)} exchanges")
                return None
            
            # Encontrar maior e menor preço
            highest_price = max(prices, key=lambda p: p.price)
            lowest_price = min(prices, key=lambda p: p.price)
            
            # Calcular diferenças
            price_difference = highest_price.price - lowest_price.price
            price_difference_percentage = (price_difference / lowest_price.price) * 100
            
            return PriceComparison(
                symbol=symbol,
                prices=prices,
                highest_price=highest_price,
                lowest_price=lowest_price,
                price_difference=price_difference,
                price_difference_percentage=price_difference_percentage,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Erro ao obter comparação de preços para {symbol}: {e}")
            return None
    
    async def find_arbitrage_opportunities(self, symbol: str) -> List[ArbitrageOpportunity]:
        """Encontrar oportunidades de arbitragem para um símbolo"""
        opportunities = []
        
        try:
            price_comparison = await self.get_price_comparison(symbol)
            
            if not price_comparison:
                return opportunities
            
            # Verificar se a diferença de preço é significativa
            if price_comparison.price_difference_percentage < self.min_profit_percentage:
                return opportunities
            
            # Criar oportunidade de arbitragem
            # Comprar na exchange com menor preço, vender na com maior preço
            opportunity = ArbitrageOpportunity(
                symbol=symbol,
                buy_exchange=price_comparison.lowest_price.exchange,
                sell_exchange=price_comparison.highest_price.exchange,
                buy_price=price_comparison.lowest_price.price,
                sell_price=price_comparison.highest_price.price,
                profit_percentage=price_comparison.price_difference_percentage,
                profit_amount=price_comparison.price_difference,
                timestamp=datetime.utcnow()
            )
            
            opportunities.append(opportunity)
            
        except Exception as e:
            logger.error(f"Erro ao encontrar oportunidades de arbitragem para {symbol}: {e}")
        
        return opportunities
    
    async def get_all_arbitrage_opportunities(self) -> List[ArbitrageOpportunity]:
        """Obter todas as oportunidades de arbitragem para todos os símbolos suportados"""
        all_opportunities = []
        
        # Processar todos os símbolos simultaneamente
        tasks = [self.find_arbitrage_opportunities(symbol) for symbol in self.supported_symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Erro ao processar {self.supported_symbols[i]}: {result}")
            else:
                all_opportunities.extend(result)
        
        # Ordenar por percentual de lucro (maior primeiro)
        all_opportunities.sort(key=lambda x: x.profit_percentage, reverse=True)
        
        return all_opportunities
    
    async def get_all_prices(self) -> Dict[str, List[Price]]:
        """Obter preços de todos os símbolos de todas as exchanges"""
        all_prices = {}
        
        for symbol in self.supported_symbols:
            try:
                prices_dict = await exchange_manager.get_all_prices(symbol)
                prices = []
                
                for exchange, price_value in prices_dict.items():
                    if price_value is not None:
                        price = Price(
                            exchange=exchange,
                            symbol=symbol,
                            price=price_value,
                            timestamp=datetime.utcnow()
                        )
                        prices.append(price)
                
                all_prices[symbol] = prices
                
            except Exception as e:
                logger.error(f"Erro ao obter preços para {symbol}: {e}")
                all_prices[symbol] = []
        
        return all_prices

# Instância global do serviço
price_monitor = PriceMonitorService()