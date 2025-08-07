"""
Session API router for the financial product recommendation system.

This module provides REST endpoints for managing conversation sessions
and user context across different platforms.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.utils.session_manager import SessionManager, SessionInfo

logger = logging.getLogger(__name__)

router = APIRouter()

# Use the global session manager from main app
from src.utils.session_manager import session_manager


class CreateSessionRequest(BaseModel):
    """Request model for creating a session"""
    user_id: str
    platform: str


class SessionResponse(BaseModel):
    """Response model for session information"""
    session_id: str
    user_id: str
    platform: str
    start_time: str
    last_activity: str
    message_count: int
    is_active: bool


class SessionStatsResponse(BaseModel):
    """Response model for session statistics"""
    session_id: str
    user_id: str
    platform: str
    duration_seconds: float
    message_count: int
    is_active: bool
    start_time: str
    last_activity: str


async def get_session_manager():
    """Dependency to get session manager"""
    return session_manager


@router.post("/create", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """
    Create a new conversation session.
    
    Creates a new session for a user on a specific platform.
    """
    try:
        session_id = await session_mgr.create_session(request.user_id, request.platform)
        session_info = await session_mgr.get_session(session_id)
        
        if not session_info:
            raise HTTPException(status_code=500, detail="Failed to create session")
        
        return SessionResponse(
            session_id=session_info.session_id,
            user_id=session_info.user_id,
            platform=session_info.platform,
            start_time=session_info.start_time.isoformat(),
            last_activity=session_info.last_activity.isoformat(),
            message_count=session_info.message_count,
            is_active=session_info.is_active
        )
        
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """
    Get session information.
    
    Returns detailed information about a specific session.
    """
    try:
        session_info = await session_mgr.get_session(session_id)
        
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionResponse(
            session_id=session_info.session_id,
            user_id=session_info.user_id,
            platform=session_info.platform,
            start_time=session_info.start_time.isoformat(),
            last_activity=session_info.last_activity.isoformat(),
            message_count=session_info.message_count,
            is_active=session_info.is_active
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{session_id}/stats", response_model=SessionStatsResponse)
async def get_session_stats(
    session_id: str,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """
    Get session statistics.
    
    Returns detailed statistics for a specific session.
    """
    try:
        stats = await session_mgr.get_session_stats(session_id)
        
        if not stats:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionStatsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{session_id}/end")
async def end_session(
    session_id: str,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """
    End a conversation session.
    
    Marks a session as inactive and stops tracking it.
    """
    try:
        session_info = await session_mgr.get_session(session_id)
        
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        await session_mgr.end_session(session_id)
        
        return {
            "session_id": session_id,
            "ended": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/user/{user_id}/sessions")
async def get_user_sessions(
    user_id: str,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """
    Get all sessions for a user.
    
    Returns all active sessions for a specific user.
    """
    try:
        sessions = await session_mgr.get_user_sessions(user_id)
        
        return {
            "user_id": user_id,
            "sessions": [
                {
                    "session_id": session.session_id,
                    "platform": session.platform,
                    "start_time": session.start_time.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "message_count": session.message_count,
                    "is_active": session.is_active
                }
                for session in sessions
            ],
            "total_sessions": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"Error getting user sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/all/sessions")
async def get_all_sessions(
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """
    Get all active sessions.
    
    Returns all currently active sessions across all users.
    """
    try:
        sessions = await session_mgr.get_all_sessions()
        
        return {
            "sessions": [
                {
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "platform": session.platform,
                    "start_time": session.start_time.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "message_count": session.message_count,
                    "is_active": session.is_active
                }
                for session in sessions
            ],
            "total_sessions": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"Error getting all sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats/overview")
async def get_system_stats(
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """
    Get system-wide session statistics.
    
    Returns overview statistics for the entire system.
    """
    try:
        session_count = await session_mgr.get_session_count()
        user_count = await session_mgr.get_user_count()
        
        return {
            "total_active_sessions": session_count,
            "total_unique_users": user_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{session_id}/validate")
async def validate_session(
    session_id: str,
    user_id: str,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """
    Validate a session for a user.
    
    Checks if a session is valid for a specific user.
    """
    try:
        is_valid = await session_mgr.validate_session(session_id, user_id)
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "is_valid": is_valid,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error validating session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/cleanup/expired")
async def cleanup_expired_sessions(
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """
    Manually trigger cleanup of expired sessions.
    
    Removes sessions that have exceeded the timeout period.
    """
    try:
        await session_mgr.cleanup_expired_sessions()
        
        return {
            "cleanup_completed": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up expired sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
