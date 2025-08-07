"""
Discord chatbot adapter for the financial product recommendation system.

This module provides integration with Discord's bot API for handling
messages and responses on Discord servers.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .base_adapter import BaseChatbotAdapter
from src.data.models import ChatResponse


class DiscordAdapter(BaseChatbotAdapter):
    """
    Discord chatbot adapter implementation.
    
    Handles Discord bot integration including message processing,
    response delivery, and session management.
    """
    
    def __init__(self, event_bus, session_manager, bot_token: str = None):
        """
        Initialize the Discord adapter.
        
        Args:
            event_bus: Event bus for publishing messages
            session_manager: Session manager for user sessions
            bot_token: Discord bot token (optional for testing)
        """
        super().__init__(event_bus, session_manager)
        self.bot_token = bot_token
        self._bot = None
        self._logger = logging.getLogger(__name__)
        
        # Mock Discord client for testing (replace with actual discord.py)
        self._mock_client = MockDiscordClient() if not bot_token else None
    
    @property
    def platform_name(self) -> str:
        """Return the platform name"""
        return "discord"
    
    async def start(self):
        """Start the Discord bot"""
        try:
            if self.bot_token:
                # Note: Using mock implementation for API testing
                # For actual Discord integration, uncomment and implement:
                # self._bot = discord.Client()
                # await self._bot.start(self.bot_token)
                self._logger.info("Discord bot started with token")
            else:
                # Use mock client for testing
                await self._mock_client.start()
                self._logger.info("Discord adapter started in mock mode")
            
            self._running = True
            self._logger.info("Discord adapter started successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to start Discord adapter: {e}")
            raise
    
    async def stop(self):
        """Stop the Discord bot"""
        try:
            if self._bot:
                await self._bot.close()
            elif self._mock_client:
                await self._mock_client.stop()
            
            self._running = False
            self._logger.info("Discord adapter stopped successfully")
            
        except Exception as e:
            self._logger.error(f"Error stopping Discord adapter: {e}")
    
    async def send_message(self, user_id: str, message: str, session_id: str):
        """
        Send a message to a Discord user.
        
        Args:
            user_id: Discord user ID
            message: Message content to send
            session_id: Session identifier
        """
        try:
            if self._bot:
                # Note: Using mock implementation for API testing
                # For actual Discord integration, uncomment and implement:
                # user = await self._bot.fetch_user(int(user_id))
                # await user.send(message)
                self._logger.info(f"Sent Discord message to {user_id}: {message[:50]}...")
            elif self._mock_client:
                await self._mock_client.send_message(user_id, message)
                self._logger.info(f"Sent mock Discord message to {user_id}: {message[:50]}...")
            else:
                self._logger.warning("No Discord client available")
                
        except Exception as e:
            self._logger.error(f"Error sending Discord message: {e}")
            raise
    
    async def process_discord_message(self, user_id: str, message_text: str, 
                                    channel_id: str = None, guild_id: str = None):
        """
        Process a message from Discord.
        
        Args:
            user_id: Discord user ID
            message_text: Message content
            channel_id: Discord channel ID
            guild_id: Discord guild (server) ID
        """
        metadata = {
            "channel_id": channel_id,
            "guild_id": guild_id,
            "platform": "discord"
        }
        
        await self.process_incoming_message(user_id, message_text, metadata)
    
    async def handle_response(self, response: ChatResponse):
        """
        Handle a response from the system for Discord.
        
        Args:
            response: Chat response to send to user
        """
        try:
            # Extract user_id from session_id
            user_id = self._extract_user_id_from_session(response.session_id)
            
            # Format the response for Discord
            formatted_message = self._format_response_for_discord(response)
            
            # Send the response
            await self.send_message(user_id, formatted_message, response.session_id)
            
            self._logger.info(f"Sent Discord response to {user_id}")
            
        except Exception as e:
            self._logger.error(f"Error handling Discord response: {e}")
    
    def _format_response_for_discord(self, response: ChatResponse) -> str:
        """
        Format a response for Discord display.
        
        Args:
            response: Chat response to format
            
        Returns:
            str: Formatted message for Discord
        """
        # Start with the main response text
        formatted = f"🤖 **Financial Advisor Response**\n\n{response.response_text}\n"
        
        # Add recommendations if available
        if response.recommendations:
            formatted += "\n📊 **Recommendations:**\n"
            for i, rec in enumerate(response.recommendations, 1):
                formatted += f"{i}. **{rec.get('name', 'Unknown')}**\n"
                formatted += f"   • Risk Level: {rec.get('risk_level', 'Unknown')}\n"
                formatted += f"   • Expected Return: {rec.get('expected_return', 'Unknown')}\n"
        
        # Add confidence and sources
        formatted += f"\n🎯 **Confidence:** {response.confidence:.1%}\n"
        formatted += f"📚 **Sources:** {', '.join(response.sources)}\n"
        formatted += f"⏱️ **Processing Time:** {response.processing_time:.2f}s"
        
        return formatted
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the Discord adapter.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        base_health = await super().health_check()
        base_health.update({
            "bot_connected": self._bot is not None or self._mock_client is not None,
            "token_configured": self.bot_token is not None
        })
        return base_health


class MockDiscordClient:
    """
    Mock Discord client for testing purposes.
    
    Simulates Discord bot functionality without requiring
    actual Discord API integration.
    """
    
    def __init__(self):
        self._running = False
        self._messages = []
        self._logger = logging.getLogger(__name__)
    
    async def start(self):
        """Start the mock Discord client"""
        self._running = True
        self._logger.info("Mock Discord client started")
    
    async def stop(self):
        """Stop the mock Discord client"""
        self._running = False
        self._logger.info("Mock Discord client stopped")
    
    async def send_message(self, user_id: str, message: str):
        """
        Send a mock message to a user.
        
        Args:
            user_id: User ID
            message: Message content
        """
        if not self._running:
            raise RuntimeError("Mock Discord client not running")
        
        self._messages.append({
            "user_id": user_id,
            "message": message,
            "timestamp": datetime.now()
        })
        
        self._logger.info(f"Mock Discord message sent to {user_id}: {message[:50]}...")
    
    def get_messages(self) -> list:
        """Get all sent messages"""
        return self._messages.copy()
    
    def clear_messages(self):
        """Clear all messages"""
        self._messages.clear() 