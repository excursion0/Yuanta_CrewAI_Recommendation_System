"""
Base chatbot adapter for the financial product recommendation system.

This module provides the base interface that all chatbot platform adapters
must implement, ensuring consistent behavior across different platforms.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.data.models import ChatMessage, ChatResponse
from src.core.event_bus import EventBus, EventType
from src.utils.session_manager import SessionManager


class BaseChatbotAdapter(ABC):
    """
    Base class for chatbot platform adapters.
    
    Provides a common interface for different chatbot platforms
    and handles message processing, session management, and response delivery.
    """
    
    def __init__(self, event_bus: EventBus, session_manager: SessionManager):
        """
        Initialize the chatbot adapter.
        
        Args:
            event_bus: Event bus for publishing messages
            session_manager: Session manager for user sessions
        """
        self.event_bus = event_bus
        self.session_manager = session_manager
        self._logger = logging.getLogger(self.__class__.__name__)
        self._running = False
        self._response_handlers: Dict[str, callable] = {}
        
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Return the platform name (e.g., 'discord', 'telegram')"""
        pass
    
    @abstractmethod
    async def start(self):
        """Start the chatbot adapter"""
        pass
    
    @abstractmethod
    async def stop(self):
        """Stop the chatbot adapter"""
        pass
    
    @abstractmethod
    async def send_message(self, user_id: str, message: str, session_id: str):
        """Send a message to a user on the platform"""
        pass
    
    async def process_incoming_message(self, user_id: str, message_text: str, 
                                     metadata: Optional[Dict[str, Any]] = None):
        """
        Process an incoming message from the platform.
        
        Args:
            user_id: User identifier on the platform
            message_text: Message content
            metadata: Platform-specific metadata
        """
        try:
            # Get or create session for user
            session_id = await self._get_or_create_session(user_id)
            
            # Create chat message
            chat_message = ChatMessage(
                platform=self.platform_name,
                user_id=user_id,
                session_id=session_id,
                message_text=message_text,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            
            # Publish to event bus
            await self.event_bus.publish(
                EventType.CHAT_MESSAGE,
                chat_message.model_dump()
            )
            
            self._logger.info(f"Processed message from {user_id} on {self.platform_name}")
            
        except Exception as e:
            self._logger.error(f"Error processing message: {e}")
            await self._send_error_response(user_id, "Sorry, I encountered an error processing your message.")
    
    async def handle_response(self, response: ChatResponse):
        """
        Handle a response from the system.
        
        Args:
            response: Chat response to send to user
        """
        try:
            # Extract user_id from session_id (format: platform_userid_session)
            session_id = response.session_id
            user_id = self._extract_user_id_from_session(session_id)
            
            # Send the response
            await self.send_message(user_id, response.response_text, session_id)
            
            # Log the response
            self._logger.info(f"Sent response to {user_id} on {self.platform_name}")
            
        except Exception as e:
            self._logger.error(f"Error handling response: {e}")
    
    async def _get_or_create_session(self, user_id: str) -> str:
        """
        Get or create a session for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            str: Session identifier
        """
        # Check for existing active sessions
        user_sessions = await self.session_manager.get_user_sessions(user_id)
        
        # If user has active sessions, use the most recent one
        if user_sessions:
            # Sort by last activity and use the most recent
            sorted_sessions = sorted(
                user_sessions, 
                key=lambda s: s.last_activity, 
                reverse=True
            )
            return sorted_sessions[0].session_id
        
        # Create new session
        session_id = await self.session_manager.create_session(user_id, self.platform_name)
        return session_id
    
    def _extract_user_id_from_session(self, session_id: str) -> str:
        """
        Extract user ID from session ID.
        
        Session ID format: platform_userid_session
        Example: discord_123456_abc123
        
        Args:
            session_id: Session identifier
            
        Returns:
            str: User identifier
        """
        try:
            # Split by underscore and get the user_id part
            parts = session_id.split('_')
            if len(parts) >= 3:
                return parts[1]  # user_id is the second part
            else:
                # Fallback: return the session_id as user_id
                return session_id
        except Exception:
            # Fallback: return the session_id as user_id
            return session_id
    
    async def _send_error_response(self, user_id: str, error_message: str):
        """
        Send an error response to a user.
        
        Args:
            user_id: User identifier
            error_message: Error message to send
        """
        try:
            await self.send_message(user_id, error_message, "error_session")
        except Exception as e:
            self._logger.error(f"Failed to send error response: {e}")
    
    def register_response_handler(self, handler: callable):
        """
        Register a response handler.
        
        Args:
            handler: Function to handle responses
        """
        self._response_handlers[self.platform_name] = handler
    
    async def _notify_response_handlers(self, response: ChatResponse):
        """
        Notify registered response handlers.
        
        Args:
            response: Chat response
        """
        for handler in self._response_handlers.values():
            try:
                await handler(response)
            except Exception as e:
                self._logger.error(f"Error in response handler: {e}")
    
    @property
    def is_running(self) -> bool:
        """Check if the adapter is running"""
        return self._running
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the adapter.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        return {
            "platform": self.platform_name,
            "running": self._running,
            "status": "healthy" if self._running else "stopped"
        } 