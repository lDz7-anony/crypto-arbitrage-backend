"""
Modelos de dados para preços e oportunidades de arbitragem
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class Price(BaseModel):
    """Modelo para preço de criptomoeda"""
    exchange: str = Field(..., description="Nome da exchange")
    symbol: str = Field(..., description="Símbolo da criptomoeda (ex: BTCUSDT)")
    price: float = Field(..., description="Preço atual")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp do preço")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ArbitrageOpportunity(BaseModel):
    """Modelo para oportunidade de arbitragem"""
    symbol: str = Field(..., description="Símbolo da criptomoeda")
    buy_exchange: str = Field(..., description="Exchange para compra")
    sell_exchange: str = Field(..., description="Exchange para venda")
    buy_price: float = Field(..., description="Preço de compra")
    sell_price: float = Field(..., description="Preço de venda")
    profit_percentage: float = Field(..., description="Percentual de lucro")
    profit_amount: float = Field(..., description="Valor do lucro")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp da oportunidade")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PriceComparison(BaseModel):
    """Modelo para comparação de preços entre exchanges"""
    symbol: str = Field(..., description="Símbolo da criptomoeda")
    prices: List[Price] = Field(..., description="Lista de preços por exchange")
    highest_price: Price = Field(..., description="Maior preço encontrado")
    lowest_price: Price = Field(..., description="Menor preço encontrado")
    price_difference: float = Field(..., description="Diferença absoluta de preço")
    price_difference_percentage: float = Field(..., description="Diferença percentual de preço")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp da comparação")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }