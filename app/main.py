"""
Sistema de Monitoramento de Arbitragem de Criptomoedas
FastAPI Backend
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api.prices import router as prices_router

# Criar instância do FastAPI
app = FastAPI(
    title="Crypto Arbitrage Monitor",
    description="Sistema de monitoramento de oportunidades de arbitragem em criptomoedas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
# Obter origens permitidas das variáveis de ambiente
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
if allowed_origins == ["*"]:
    # Em produção, usar origens específicas se definidas
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(prices_router)

@app.get("/")
async def root():
    """Endpoint raiz - informações básicas da API"""
    return {
        "message": "Crypto Arbitrage Monitor API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "crypto-arbitrage-monitor",
        "version": "1.0.0"
    }

@app.get("/api/v1/status")
async def api_status():
    """Status da API"""
    return {
        "api_status": "operational",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "prices": "/api/v1/prices",
            "arbitrage": "/api/v1/arbitrage",
            "websocket_prices": "/api/v1/ws/prices",
            "websocket_arbitrage": "/api/v1/ws/arbitrage"
        },
        "supported_symbols": ["BTC", "ETH"],
        "exchanges": ["binance", "coinbase", "kraken"]
    }

if __name__ == "__main__":
    # Obter configurações das variáveis de ambiente
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level=log_level
    )