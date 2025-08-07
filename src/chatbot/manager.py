"""
Chatbot manager for the financial product recommendation system.

This module provides centralized management of all chatbot platform adapters,
including startup, shutdown, message routing, and response handling.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.core.event_bus import EventBus, EventType
from src.utils.session_manager import SessionManager
from src.data.models import ChatResponse
from .base_adapter import BaseChatbotAdapter
from .discord_adapter import DiscordAdapter


class ChatbotManager:
    """
    Central manager for all chatbot platform adapters.
    
    Coordinates startup, shutdown, message routing, and response handling
    across multiple chatbot platforms.
    """
    
    def __init__(self, event_bus: EventBus, session_manager: SessionManager):
        """
        Initialize the chatbot manager.
        
        Args:
            event_bus: Event bus for publishing messages
            session_manager: Session manager for user sessions
        """
        self.event_bus = event_bus
        self.session_manager = session_manager
        self._logger = logging.getLogger(__name__)
        
        # Store adapters by platform name
        self._adapters: Dict[str, BaseChatbotAdapter] = {}
        self._running = False
        
        # Subscribe to response events
        self.event_bus.subscribe(EventType.CHAT_RESPONSE, self._handle_response)
    
    async def start(self):
        """Start all chatbot adapters"""
        try:
            self._logger.info("Starting chatbot manager...")
            
            # Start all registered adapters
            for platform, adapter in self._adapters.items():
                try:
                    await adapter.start()
                    self._logger.info(f"Started {platform} adapter")
                except Exception as e:
                    self._logger.error(f"Failed to start {platform} adapter: {e}")
            
            self._running = True
            self._logger.info("Chatbot manager started successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to start chatbot manager: {e}")
            raise
    
    async def stop(self):
        """Stop all chatbot adapters"""
        try:
            self._logger.info("Stopping chatbot manager...")
            
            # Stop all adapters
            for platform, adapter in self._adapters.items():
                try:
                    await adapter.stop()
                    self._logger.info(f"Stopped {platform} adapter")
                except Exception as e:
                    self._logger.error(f"Error stopping {platform} adapter: {e}")
            
            self._running = False
            self._logger.info("Chatbot manager stopped successfully")
            
        except Exception as e:
            self._logger.error(f"Error stopping chatbot manager: {e}")
    
    def register_adapter(self, adapter: BaseChatbotAdapter):
        """
        Register a chatbot adapter.
        
        Args:
            adapter: Chatbot adapter to register
        """
        platform = adapter.platform_name
        self._adapters[platform] = adapter
        self._logger.info(f"Registered {platform} adapter")
    
    def get_adapter(self, platform: str) -> Optional[BaseChatbotAdapter]:
        """
        Get a specific adapter by platform name.
        
        Args:
            platform: Platform name (e.g., 'discord', 'telegram')
            
        Returns:
            BaseChatbotAdapter if found, None otherwise
        """
        return self._adapters.get(platform)
    
    def get_all_adapters(self) -> Dict[str, BaseChatbotAdapter]:
        """
        Get all registered adapters.
        
        Returns:
            Dict[str, BaseChatbotAdapter]: All registered adapters
        """
        return self._adapters.copy()
    
    async def _handle_response(self, response_data: Dict[str, Any]):
        """
        Handle a response from the system.
        
        Args:
            response_data: Response data from the event bus
        """
        try:
            # Parse the response as ChatResponseEvent (which has session_id)
            from src.data.models import ChatResponseEvent
            response_event = ChatResponseEvent(**response_data)
            
            # Extract platform from session_id
            platform = self._extract_platform_from_session(response_event.session_id)
            
            # Get the appropriate adapter
            adapter = self.get_adapter(platform)
            if adapter:
                # Convert ChatResponseEvent to ChatResponse for the adapter
                from src.data.models import ChatResponse
                chat_response = ChatResponse(
                    response_text=response_event.response_text,
                    recommendations=response_event.recommendations,
                    confidence=response_event.confidence,
                    sources=response_event.sources,
                    processing_time=response_event.processing_time
                )
                await adapter.handle_response(chat_response)
            else:
                self._logger.warning(f"No adapter found for platform: {platform}")
                
        except Exception as e:
            self._logger.error(f"Error handling response: {e}")
    
    def _extract_platform_from_session(self, session_id: str) -> str:
        """
        Extract platform name from session ID.
        
        Session ID format: platform_userid_session
        Example: discord_123456_abc123
        
        Args:
            session_id: Session identifier
            
        Returns:
            str: Platform name
        """
        try:
            parts = session_id.split('_')
            if len(parts) >= 3:
                return parts[0]  # platform is the first part
            else:
                return "unknown"
        except Exception:
            return "unknown"
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on all adapters.
        
        Returns:
            Dict[str, Any]: Health check results for all adapters
        """
        health_results = {
            "manager_running": self._running,
            "adapters": {}
        }
        
        for platform, adapter in self._adapters.items():
            try:
                adapter_health = await adapter.health_check()
                health_results["adapters"][platform] = adapter_health
            except Exception as e:
                health_results["adapters"][platform] = {
                    "error": str(e),
                    "status": "unhealthy"
                }
        
        return health_results
    
    def get_platforms(self) -> List[str]:
        """
        Get list of all registered platforms.
        
        Returns:
            List[str]: List of platform names
        """
        return list(self._adapters.keys())
    
    @property
    def is_running(self) -> bool:
        """Check if the manager is running"""
        return self._running


class ChatbotManagerFactory:
    """
    Factory for creating and configuring chatbot managers.
    
    Provides convenient methods for setting up chatbot managers
    with different platform configurations.
    """
    
    @staticmethod
    def create_manager(event_bus: EventBus, session_manager: SessionManager,
                      platforms: List[str] = None) -> ChatbotManager:
        """
        Create a chatbot manager with specified platforms.
        
        Args:
            event_bus: Event bus for publishing messages
            session_manager: Session manager for user sessions
            platforms: List of platforms to enable (default: all)
            
        Returns:
            ChatbotManager: Configured chatbot manager
        """
        manager = ChatbotManager(event_bus, session_manager)
        
        # Default to Discord platform if none specified
        if platforms is None:
            platforms = ["discord", "test"]
        
        # Create and register adapters
        for platform in platforms:
            adapter = ChatbotManagerFactory._create_adapter(
                platform, event_bus, session_manager
            )
            if adapter:
                manager.register_adapter(adapter)
        
        return manager
    
    @staticmethod
    def _create_adapter(platform: str, event_bus: EventBus, 
                       session_manager: SessionManager) -> Optional[BaseChatbotAdapter]:
        """
        Create an adapter for a specific platform.
        
        Args:
            platform: Platform name
            event_bus: Event bus
            session_manager: Session manager
            
        Returns:
            BaseChatbotAdapter if platform is supported, None otherwise
        """
        if platform == "discord":
            return DiscordAdapter(event_bus, session_manager)
        elif platform == "test":
            # Create a simple test adapter that just logs responses
            from .base_adapter import BaseChatbotAdapter
            
            class TestAdapter(BaseChatbotAdapter):
                def __init__(self, event_bus, session_manager):
                    super().__init__(event_bus, session_manager)
                    self._logger = logging.getLogger(__name__)
                
                @property
                def platform_name(self) -> str:
                    """Return the platform name"""
                    return "test"
                
                async def start(self):
                    """Start the test adapter"""
                    self._running = True
                    self._logger.info("Test adapter started")
                
                async def stop(self):
                    """Stop the test adapter"""
                    self._running = False
                    self._logger.info("Test adapter stopped")
                
                async def send_message(self, user_id: str, message: str, session_id: str = None):
                    """Send message for test platform (just log it)"""
                    self._logger.info(f"TEST PLATFORM - Sending message to {user_id}: {message}")
                    return True
                
                async def get_user_info(self, user_id: str):
                    """Get user info for test platform"""
                    return {"user_id": user_id, "platform": "test", "name": f"Test User {user_id}"}
            
            return TestAdapter(event_bus, session_manager)
        else:
            logging.warning(f"Unsupported platform: {platform}")
            return None 