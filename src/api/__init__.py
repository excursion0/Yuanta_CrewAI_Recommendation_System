"""
API layer for the financial product recommendation system.

This module provides the FastAPI application and REST endpoints
for the chatbot integration.
"""

from .main import app
from .chat import router as chat_router
from .session import router as session_router

__all__ = [
    "app",
    "chat_router", 
    "session_router"
]
