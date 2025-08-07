"""
Chatbot integration tests for the financial product recommendation system.

This module contains tests to verify the chatbot adapters and manager
are working correctly with the event-driven architecture.
"""

import pytest
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any

from src.chatbot import (
    BaseChatbotAdapter, DiscordAdapter,
    ChatbotManager, ChatbotManagerFactory
)
from src.core.event_bus import EventBus, EventType
from src.utils.session_manager import SessionManager
from src.data.models import ChatResponse


class TestChatbotAdapters:
    """Test individual chatbot adapters"""
    
    @pytest.fixture
    def event_bus(self):
        """Create a test event bus"""
        return EventBus()
    
    @pytest.fixture
    def session_manager(self):
        """Create a test session manager"""
        return SessionManager()
    
    @pytest.mark.asyncio
    async def test_discord_adapter_creation(self, event_bus, session_manager):
        """Test creating a Discord adapter"""
        adapter = DiscordAdapter(event_bus, session_manager)
        
        assert adapter.platform_name == "discord"
        assert adapter.is_running == False
        assert adapter.bot_token is None
    
    @pytest.mark.asyncio
    async def test_discord_adapter_start_stop(self, event_bus, session_manager):
        """Test starting and stopping Discord adapter"""
        adapter = DiscordAdapter(event_bus, session_manager)
        
        # Start adapter
        await adapter.start()
        assert adapter.is_running == True
        
        # Stop adapter
        await adapter.stop()
        assert adapter.is_running == False
    
    @pytest.mark.asyncio
    async def test_discord_message_processing(self, event_bus, session_manager):
        """Test processing messages through Discord adapter"""
        await event_bus.start()
        await session_manager.start()
        
        adapter = DiscordAdapter(event_bus, session_manager)
        await adapter.start()
        
        # Process a message
        await adapter.process_discord_message(
            user_id="123456",
            message_text="I need investment advice",
            channel_id="789012",
            guild_id="345678"
        )
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        # Check that session was created
        user_sessions = await session_manager.get_user_sessions("123456")
        assert len(user_sessions) > 0
        
        # Cleanup
        await adapter.stop()
        await session_manager.stop()
        await event_bus.stop()
    



class TestChatbotManager:
    """Test the chatbot manager"""
    
    @pytest.fixture
    def event_bus(self):
        """Create a test event bus"""
        return EventBus()
    
    @pytest.fixture
    def session_manager(self):
        """Create a test session manager"""
        return SessionManager()
    
    @pytest.mark.asyncio
    async def test_manager_creation(self, event_bus, session_manager):
        """Test creating a chatbot manager"""
        manager = ChatbotManager(event_bus, session_manager)
        
        assert manager.is_running == False
        assert len(manager.get_platforms()) == 0
    
    @pytest.mark.asyncio
    async def test_manager_with_adapters(self, event_bus, session_manager):
        """Test manager with registered adapters"""
        manager = ChatbotManager(event_bus, session_manager)
        
        # Register adapters
        discord_adapter = DiscordAdapter(event_bus, session_manager)
        
        manager.register_adapter(discord_adapter)
        
        assert len(manager.get_platforms()) == 1
        assert "discord" in manager.get_platforms()
    
    @pytest.mark.asyncio
    async def test_manager_start_stop(self, event_bus, session_manager):
        """Test starting and stopping the manager"""
        await event_bus.start()
        await session_manager.start()
        
        manager = ChatbotManager(event_bus, session_manager)
        
        # Register adapters
        discord_adapter = DiscordAdapter(event_bus, session_manager)
        
        manager.register_adapter(discord_adapter)
        
        # Start manager
        await manager.start()
        assert manager.is_running == True
        
        # Check that adapters are running
        assert discord_adapter.is_running == True
        
        # Stop manager
        await manager.stop()
        assert manager.is_running == False
        
        # Cleanup
        await session_manager.stop()
        await event_bus.stop()
    
    @pytest.mark.asyncio
    async def test_manager_health_check(self, event_bus, session_manager):
        """Test manager health check"""
        await event_bus.start()
        await session_manager.start()
        
        manager = ChatbotManager(event_bus, session_manager)
        
        # Register adapters
        discord_adapter = DiscordAdapter(event_bus, session_manager)
        
        manager.register_adapter(discord_adapter)
        
        await manager.start()
        
        # Perform health check
        health_data = await manager.health_check()
        
        assert health_data["manager_running"] == True
        assert "discord" in health_data["adapters"]
        
        # Cleanup
        await manager.stop()
        await session_manager.stop()
        await event_bus.stop()


class TestChatbotManagerFactory:
    """Test the chatbot manager factory"""
    
    @pytest.fixture
    def event_bus(self):
        """Create a test event bus"""
        return EventBus()
    
    @pytest.fixture
    def session_manager(self):
        """Create a test session manager"""
        return SessionManager()
    
    @pytest.mark.asyncio
    async def test_factory_create_manager(self, event_bus, session_manager):
        """Test creating manager with factory"""
        manager = ChatbotManagerFactory.create_manager(event_bus, session_manager)
        
        assert isinstance(manager, ChatbotManager)
        assert len(manager.get_platforms()) == 2  # discord and test
        assert "discord" in manager.get_platforms()
        assert "test" in manager.get_platforms()
    
    @pytest.mark.asyncio
    async def test_factory_create_manager_specific_platforms(self, event_bus, session_manager):
        """Test creating manager with specific platforms"""
        manager = ChatbotManagerFactory.create_manager(
            event_bus, session_manager, platforms=["discord"]
        )
        
        assert isinstance(manager, ChatbotManager)
        assert len(manager.get_platforms()) == 1
        assert "discord" in manager.get_platforms()
        assert "telegram" not in manager.get_platforms()


class TestChatbotIntegration:
    """Test end-to-end chatbot integration"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_chatbot_flow(self):
        """Test complete chatbot message flow"""
        # Setup components
        event_bus = EventBus()
        session_manager = SessionManager()
        
        await event_bus.start()
        await session_manager.start()
        
        # Create chatbot manager
        manager = ChatbotManagerFactory.create_manager(event_bus, session_manager)
        await manager.start()
        
        # Get Discord adapter
        discord_adapter = manager.get_adapter("discord")
        assert discord_adapter is not None
        
        # Process a message
        await discord_adapter.process_discord_message(
            user_id="test_user_123",
            message_text="I want to invest in low-risk options",
            channel_id="test_channel",
            guild_id="test_guild"
        )
        
        # Wait for processing
        await asyncio.sleep(0.2)
        
        # Check that session was created
        user_sessions = await session_manager.get_user_sessions("test_user_123")
        assert len(user_sessions) > 0
        
        # Test response handling
        response = ChatResponse(
            response_text="Based on your request, I recommend the Conservative Growth Fund.",
            recommendations=[
                {
                    "product_id": "PROD_001",
                    "name": "Conservative Growth Fund",
                    "risk_level": "low",
                    "expected_return": "3-5%"
                }
            ],
            confidence=0.88,
            sources=["structured_db", "vector_search"],
            processing_time=1.2
        )
        
        # Handle response (this would normally come from the event bus)
        await discord_adapter.handle_response(response)
        
        # Cleanup
        await manager.stop()
        await session_manager.stop()
        await event_bus.stop()


if __name__ == "__main__":
    # Run chatbot integration tests
    pytest.main([__file__, "-v"]) 