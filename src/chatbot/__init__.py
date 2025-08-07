"""
Chatbot integration package for the financial product recommendation system.

This package contains adapters for different chatbot platforms including
Discord, Telegram, and other messaging platforms.
"""

from .base_adapter import BaseChatbotAdapter
from .discord_adapter import DiscordAdapter
from .manager import ChatbotManager, ChatbotManagerFactory

__all__ = [
    "BaseChatbotAdapter",
    "DiscordAdapter",
    "ChatbotManager",
    "ChatbotManagerFactory"
] 