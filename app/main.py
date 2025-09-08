"""
Sistema de Monitoramento de Arbitragem de Criptomoedas
FastAPI Backend
"""

import os
import logging
import time
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.user import UserCreate, UserResponse
from datetime import datetime, timedelta
from jose import JWTError, jwt
import uvicorn

# JWT Configuration
SECRET_KEY = "crypto-arbitrage-secret-key-2024"
ALGORITHM = "HS256"
security = HTTPBearer()

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

# Configurar CORS para permitir requisições de qualquer domínio
# Especialmente importante para v0.dev e outros domínios de preview
logger.info("🔗 Configurando CORS para permitir todas as origens")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens (incluindo v0.dev)
    allow_credentials=True,  # Permite cookies e headers de autenticação
    allow_methods=["*"],  # Permite todos os métodos HTTP
    allow_headers=["*"],  # Permite todos os headers
)

logger.info("✅ CORS configurado com sucesso - permitindo todas as origens")

# Middleware personalizado para logging de requisições CORS
@app.middleware("http")
async def cors_logging_middleware(request: Request, call_next):
    """Middleware para logging de requisições CORS"""
    start_time = time.time()
    
    # Log da requisição recebida
    origin = request.headers.get("origin", "unknown")
    method = request.method
    path = request.url.path
    
    logger.info(f"🌐 Requisição recebida: {method} {path} de origem: {origin}")
    
    # Processar a requisição
    response = await call_next(request)
    
    # Calcular tempo de processamento
    process_time = time.time() - start_time
    
    # Log da resposta
    logger.info(f"✅ Resposta enviada: {response.status_code} em {process_time:.3f}s para {origin}")
    
    # Adicionar headers CORS explícitos para garantir compatibilidade
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

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

@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    """Register a new user"""
    logger.info(f"User registration attempt for email: {user.email}")
    return UserResponse(
        id="temp-123",
        email=user.email, 
        name=user.name,
        created_at=datetime.now().isoformat()
    )

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/auth/login")
async def login(email: str, password: str):
    """Login with email and password - returns JWT token"""
    logger.info(f"Login attempt for email: {email}")
    
    # Simple mock authentication
    if email == "teste@exemplo.com" and password == "senha123":
        token_data = {"sub": email, "exp": datetime.utcnow() + timedelta(hours=24)}
        token = create_access_token(token_data)
        logger.info(f"Login successful for email: {email}")
        return {"access_token": token, "token_type": "bearer"}
    
    logger.warning(f"Login failed for email: {email}")
    return {"error": "Invalid credentials"}

@app.get("/auth/verify")
async def verify_auth(current_user: str = Depends(verify_token)):
    """Verify JWT token and return user info"""
    logger.info(f"Token verification for user: {current_user}")
    return {
        "email": current_user,
        "authenticated": True,
        "message": "Token is valid"
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
        "cors_enabled": True,
        "cors_origins": ["*"],
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "auth_register": "/auth/register",
            "auth_login": "/auth/login",
            "auth_verify": "/auth/verify",
            "prices": "/api/v1/prices",
            "arbitrage": "/api/v1/arbitrage",
            "websocket_prices": "/api/v1/ws/prices",
            "websocket_arbitrage": "/api/v1/ws/arbitrage",
            "cors_test": "/api/v1/cors-test"
        },
        "supported_symbols": ["BTC", "ETH"],
        "exchanges": ["binance", "coinbase", "kraken"]
    }

@app.get("/api/v1/cors-test")
async def cors_test():
    """Endpoint para testar CORS"""
    return {
        "message": "CORS funcionando corretamente!",
        "cors_headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true"
        },
        "timestamp": "2025-01-06T22:30:00Z"
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