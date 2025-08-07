"""
Session Manager for the financial product recommendation system.

This module provides session management functionality for tracking
conversation sessions and user context across the system.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass

from src.data.models import ConversationSession, ConversationMessage, UserProfile


@dataclass
class SessionInfo:
    """Session information"""
    session_id: str
    user_id: str
    platform: str
    start_time: datetime
    last_activity: datetime
    message_count: int
    is_active: bool


class SessionManager:
    """
    Manages conversation sessions and user context.
    
    Provides functionality for creating, tracking, and managing
    conversation sessions across different platforms.
    """
    
    def __init__(self):
        self._sessions: Dict[str, SessionInfo] = {}
        self._conversation_manager = ConversationManager()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._user_sessions: Dict[str, List[str]] = {}
        self._session_timeout = timedelta(hours=24)  # 24 hour timeout
        self._logger = logging.getLogger(__name__)
    
    async def start(self):
        """Start the session manager with background cleanup"""
        self._cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
        self._logger.info("Session manager started with background cleanup task")
    
    async def stop(self):
        """Stop the session manager"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        self._logger.info("Session manager stopped")
    
    async def create_session(self, user_id: str, platform: str) -> str:
        """
        Create a new conversation session.
        
        Args:
            user_id: User identifier
            platform: Chat platform (discord, telegram, etc.)
            
        Returns:
            str: Session identifier
        """
        session_id = f"{platform}_{user_id}_{uuid.uuid4().hex[:8]}"
        
        session_info = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            platform=platform,
            start_time=datetime.now(timezone.utc),
            last_activity=datetime.now(timezone.utc),
            message_count=0,
            is_active=True
        )
        
        self._sessions[session_id] = session_info
        
        # Track user sessions
        if user_id not in self._user_sessions:
            self._user_sessions[user_id] = []
        self._user_sessions[user_id].append(session_id)
        
        self._logger.info(f"Created session {session_id} for user {user_id} on {platform}")
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """
        Get session information.
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionInfo if session exists, None otherwise
        """
        session = self._sessions.get(session_id)
        if session and session.is_active:
            return session
        return None
    
    async def validate_session(self, session_id: str, user_id: str) -> bool:
        """
        Validate a session for a user.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            bool: True if session is valid, False otherwise
        """
        session = await self.get_session(session_id)
        if session and session.user_id == user_id:
            # Update last activity
            session.last_activity = datetime.now(timezone.utc)
            return True
        return False
    
    async def update_session_activity(self, session_id: str):
        """
        Update session activity timestamp.
        
        Args:
            session_id: Session identifier
        """
        session = self._sessions.get(session_id)
        if session:
            session.last_activity = datetime.now(timezone.utc)
            session.message_count += 1
    
    async def end_session(self, session_id: str):
        """
        End a conversation session.
        
        Args:
            session_id: Session identifier
        """
        session = self._sessions.get(session_id)
        if session:
            session.is_active = False
            self._logger.info(f"Ended session {session_id}")
    
    async def get_user_sessions(self, user_id: str) -> List[SessionInfo]:
        """
        Get all active sessions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List[SessionInfo]: List of active sessions
        """
        session_ids = self._user_sessions.get(user_id, [])
        sessions = []
        
        for session_id in session_ids:
            session = await self.get_session(session_id)
            if session:
                sessions.append(session)
        
        return sessions
    
    async def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Get statistics for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict[str, Any]: Session statistics
        """
        session = await self.get_session(session_id)
        if not session:
            return {}
        
        duration = datetime.now(timezone.utc) - session.start_time
        
        return {
            "session_id": session_id,
            "user_id": session.user_id,
            "platform": session.platform,
            "duration_seconds": duration.total_seconds(),
            "message_count": session.message_count,
            "is_active": session.is_active,
            "start_time": session.start_time.isoformat(),
            "last_activity": session.last_activity.isoformat()
        }
    
    async def cleanup_expired_sessions(self):
        """
        Clean up expired sessions.
        
        Removes sessions that have exceeded the timeout period.
        """
        current_time = datetime.now(timezone.utc)
        expired_sessions = []
        
        for session_id, session in self._sessions.items():
            if session.is_active and (current_time - session.last_activity) > self._session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            await self.end_session(session_id)
            self._logger.info(f"Cleaned up expired session {session_id}")
    
    async def _cleanup_expired_sessions(self):
        """Background task to clean up expired sessions"""
        while True:
            try:
                await self.cleanup_expired_sessions()
                await asyncio.sleep(3600)  # Run every hour
            except Exception as e:
                self._logger.error(f"Error in session cleanup: {e}")
                await asyncio.sleep(3600)  # Continue after error
    
    async def get_all_sessions(self) -> List[SessionInfo]:
        """
        Get all active sessions.
        
        Returns:
            List[SessionInfo]: List of all active sessions
        """
        return [session for session in self._sessions.values() if session.is_active]
    
    async def get_session_count(self) -> int:
        """
        Get the total number of active sessions.
        
        Returns:
            int: Number of active sessions
        """
        return len([s for s in self._sessions.values() if s.is_active])
    
    async def get_user_count(self) -> int:
        """
        Get the total number of unique users with active sessions.
        
        Returns:
            int: Number of unique users
        """
        active_users = set()
        for session in self._sessions.values():
            if session.is_active:
                active_users.add(session.user_id)
        return len(active_users)


class ConversationManager:
    """
    Manages conversation messages within sessions.
    
    Provides functionality for storing and retrieving conversation
    messages for a given session.
    """
    
    def __init__(self):
        self._conversations: Dict[str, List[ConversationMessage]] = {}
        self._logger = logging.getLogger(__name__)
    
    async def add_message(self, session_id: str, message: ConversationMessage):
        """
        Add a message to a conversation session.
        
        Args:
            session_id: Session identifier
            message: Conversation message
        """
        if session_id not in self._conversations:
            self._conversations[session_id] = []
        
        self._conversations[session_id].append(message)
        self._logger.debug(f"Added message to session {session_id}")
    
    async def get_conversation(self, session_id: str) -> List[ConversationMessage]:
        """
        Get all messages for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List[ConversationMessage]: List of conversation messages
        """
        return self._conversations.get(session_id, [])
    
    async def clear_conversation(self, session_id: str):
        """
        Clear all messages for a session.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self._conversations:
            del self._conversations[session_id]
            self._logger.info(f"Cleared conversation for session {session_id}")
    
    async def get_message_count(self, session_id: str) -> int:
        """
        Get the number of messages in a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            int: Number of messages
        """
        return len(self._conversations.get(session_id, []))
    
    async def get_last_message(self, session_id: str) -> Optional[ConversationMessage]:
        """
        Get the last message in a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            ConversationMessage if exists, None otherwise
        """
        messages = self._conversations.get(session_id, [])
        return messages[-1] if messages else None


# Global instances
session_manager = SessionManager()
conversation_manager = ConversationManager()

# Initialize session manager when module is imported
async def initialize_session_manager():
    """Initialize the global session manager."""
    await session_manager.start()

# Note: The session manager will be started when the FastAPI app starts
# via the lifespan context manager in src/api/main.py
