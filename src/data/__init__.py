"""
Data models and utilities for the financial recommendation system.
"""

from .models import ChatResponse, ConversationMessage, MessageType, UserProfile
from .product_database import ProductDatabase, Product
from .market_data_simulator import MarketDataSimulator

__all__ = [
    'ChatResponse',
    'ConversationMessage', 
    'MessageType',
    'UserProfile',
    'ProductDatabase',
    'Product',
    'MarketDataSimulator'
]
