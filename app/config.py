"""
Configurações do Sistema de Arbitragem de Criptomoedas
"""

import os
from typing import Optional

class Settings:
    """Configurações da aplicação"""
    
    def __init__(self):
        # Configurações gerais
        self.app_name = os.getenv("APP_NAME", "Crypto Arbitrage Monitor")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Configurações do servidor
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", 8000))
        
        # Configurações de CORS
        self.allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
        
        # Configurações de logging
        self.log_level = os.getenv("LOG_LEVEL", "info")
        
        # Configurações de arbitragem
        self.min_profit_percentage = float(os.getenv("MIN_PROFIT_PERCENTAGE", "0.5"))
        self.max_price_difference = float(os.getenv("MAX_PRICE_DIFFERENCE", "10.0"))
        self.update_interval = int(os.getenv("UPDATE_INTERVAL", "30"))
        
        # Configurações das exchanges (opcional)
        self.binance_api_key = os.getenv("BINANCE_API_KEY")
        self.binance_secret_key = os.getenv("BINANCE_SECRET_KEY")
        self.coinbase_api_key = os.getenv("COINBASE_API_KEY")
        self.coinbase_secret_key = os.getenv("COINBASE_SECRET_KEY")
        self.kraken_api_key = os.getenv("KRAKEN_API_KEY")
        self.kraken_secret_key = os.getenv("KRAKEN_SECRET_KEY")
        
        # Configurações de notificações (opcional)
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

# Instância global das configurações
settings = Settings()