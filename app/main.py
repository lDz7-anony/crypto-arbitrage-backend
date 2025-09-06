"""
Sistema de Monitoramento de Arbitragem de Criptomoedas
FastAPI Backend
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar rotas apenas quando necessário para evitar problemas de inicialização

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

# Incluir rotas (importação lazy para evitar problemas de startup)
try:
    from app.api.prices import router as prices_router
    app.include_router(prices_router)
    logger.info("Price routes loaded successfully")
except Exception as e:
    logger.warning(f"Failed to load price routes: {e}")
    # Criar rotas básicas se houver falha
    @app.get("/api/v1/prices/{symbol}")
    async def fallback_prices(symbol: str):
        return {"error": "Price service temporarily unavailable", "symbol": symbol}
    
    @app.get("/api/v1/arbitrage")
    async def fallback_arbitrage():
        return {"error": "Arbitrage service temporarily unavailable"}

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
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "service": "crypto-arbitrage-monitor",
        "version": "1.0.0",
        "timestamp": "2025-01-06T22:30:00Z"
    }

@app.on_event("startup")
async def startup_event():
    """Evento de inicialização da aplicação"""
    logger.info("🚀 Application starting up...")
    logger.info("📊 Crypto Arbitrage Monitor API")
    logger.info("🔗 Health endpoint available at /health")
    logger.info("📚 API documentation available at /docs")
    
    # Verificar variáveis de ambiente
    port = os.getenv("PORT", "8000")
    host = os.getenv("HOST", "0.0.0.0")
    logger.info(f"🌐 Starting server on {host}:{port}")
    
    # Verificar se as rotas foram carregadas
    try:
        from app.api.prices import router as prices_router
        logger.info("✅ Price monitoring routes loaded")
    except Exception as e:
        logger.warning(f"⚠️ Price routes not available: {e}")
    
    logger.info("✅ Application startup completed successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de encerramento da aplicação"""
    logger.info("🛑 Application shutting down...")
    logger.info("✅ Shutdown completed")

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
    
    logger.info(f"🚀 Starting Crypto Arbitrage Monitor")
    logger.info(f"🌐 Host: {host}")
    logger.info(f"🔌 Port: {port}")
    logger.info(f"🐛 Debug: {debug}")
    logger.info(f"📝 Log Level: {log_level}")
    
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=debug,
            log_level=log_level
        )
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        raise