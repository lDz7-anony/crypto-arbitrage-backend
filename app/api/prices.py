"""
Endpoints da API para preços e arbitragem
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, List
from datetime import datetime
import json
import asyncio
import logging

from app.models.price import Price, ArbitrageOpportunity, PriceComparison
from app.services.price_monitor import price_monitor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["prices"])

# Armazenar conexões WebSocket ativas
active_connections: List[WebSocket] = []

async def broadcast_message(message: dict):
    """Enviar mensagem para todas as conexões WebSocket ativas"""
    if active_connections:
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in active_connections:
            try:
                await connection.send_text(message_str)
            except:
                disconnected.append(connection)
        
        # Remover conexões desconectadas
        for connection in disconnected:
            active_connections.remove(connection)

@router.get("/prices/{symbol}")
async def get_prices(symbol: str) -> Dict[str, List[Price]]:
    """Obter preços de um símbolo específico de todas as exchanges"""
    try:
        symbol = symbol.upper()
        logger.info(f"Getting prices for {symbol}")
        
        # Obter preços de todas as exchanges para o símbolo
        from app.services.exchanges import exchange_manager
        prices_dict = await exchange_manager.get_all_prices(symbol)
        
        # Converter para lista de objetos Price
        prices = []
        for exchange, price_value in prices_dict.items():
            if price_value is not None:
                price = Price(
                    exchange=exchange,
                    symbol=symbol,
                    price=price_value
                )
                prices.append(price)
        
        logger.info(f"Retrieved {len(prices)} prices for {symbol}")
        return {"symbol": symbol, "prices": prices}
        
    except Exception as e:
        logger.error(f"Erro ao obter preços para {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter preços: {str(e)}")

@router.get("/prices")
async def get_all_prices() -> Dict[str, List[Price]]:
    """Obter preços de todos os símbolos suportados"""
    try:
        logger.info("Getting all prices")
        all_prices = await price_monitor.get_all_prices()
        return all_prices
        
    except Exception as e:
        logger.error(f"Erro ao obter todos os preços: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter preços: {str(e)}")

@router.get("/arbitrage")
async def get_arbitrage_opportunities() -> List[ArbitrageOpportunity]:
    """Obter todas as oportunidades de arbitragem atuais"""
    try:
        logger.info("Getting arbitrage opportunities")
        opportunities = await price_monitor.get_all_arbitrage_opportunities()
        return opportunities
        
    except Exception as e:
        logger.error(f"Erro ao obter oportunidades de arbitragem: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter oportunidades: {str(e)}")

@router.get("/arbitrage/{symbol}")
async def get_arbitrage_opportunities_for_symbol(symbol: str) -> List[ArbitrageOpportunity]:
    """Obter oportunidades de arbitragem para um símbolo específico"""
    try:
        symbol = symbol.upper()
        logger.info(f"Getting arbitrage opportunities for {symbol}")
        opportunities = await price_monitor.find_arbitrage_opportunities(symbol)
        return opportunities
        
    except Exception as e:
        logger.error(f"Erro ao obter oportunidades de arbitragem para {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter oportunidades: {str(e)}")

@router.get("/compare/{symbol}")
async def compare_prices(symbol: str) -> PriceComparison:
    """Comparar preços de um símbolo entre todas as exchanges"""
    try:
        symbol = symbol.upper()
        logger.info(f"Comparing prices for {symbol}")
        comparison = await price_monitor.get_price_comparison(symbol)
        
        if not comparison:
            raise HTTPException(status_code=404, detail=f"Não foi possível obter preços para {symbol}")
        
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao comparar preços para {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao comparar preços: {str(e)}")

@router.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """WebSocket para atualizações de preços em tempo real"""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info("WebSocket connection established for prices")
    
    try:
        while True:
            # Enviar atualizações a cada 30 segundos
            await asyncio.sleep(30)
            
            # Obter preços atuais
            all_prices = await price_monitor.get_all_prices()
            
            # Enviar para o cliente
            await websocket.send_json({
                "type": "price_update",
                "data": all_prices,
                "timestamp": datetime.utcnow().isoformat()
            })
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)

@router.websocket("/ws/arbitrage")
async def websocket_arbitrage(websocket: WebSocket):
    """WebSocket para atualizações de arbitragem em tempo real"""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info("WebSocket connection established for arbitrage")
    
    try:
        while True:
            # Enviar atualizações a cada 30 segundos
            await asyncio.sleep(30)
            
            # Obter oportunidades de arbitragem
            opportunities = await price_monitor.get_all_arbitrage_opportunities()
            
            # Enviar para o cliente
            await websocket.send_json({
                "type": "arbitrage_update",
                "data": opportunities,
                "timestamp": datetime.utcnow().isoformat()
            })
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)