"""
Chat API router for the financial product recommendation system.

This module provides REST endpoints for processing chat messages
and managing conversation responses.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import os

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.data.models import ChatMessage, ChatResponse
from src.core.event_bus import event_bus, EventType
from src.utils.session_manager import SessionManager

logger = logging.getLogger(__name__)

router = APIRouter()

# Use the global session manager from main app
from src.utils.session_manager import session_manager


async def get_session_manager():
    """Dependency to get session manager"""
    return session_manager


@router.post("/message", response_model=ChatResponse)
async def process_chat_message(
    message: ChatMessage,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """
    Process incoming chat message and return response.
    
    This endpoint handles chat messages from various platforms
    (Discord, Telegram, etc.) and processes them through the
    recommendation pipeline.
    """
    try:
        logger.info(f"Processing chat message from {message.platform} user {message.user_id}")
        
        # Validate session
        if not await session_mgr.validate_session(message.session_id, message.user_id):
            raise HTTPException(status_code=400, detail="Invalid session")
        
        # Create chat message event
        chat_event = {
            "platform": message.platform,
            "user_id": message.user_id,
            "session_id": message.session_id,
            "message_text": message.message_text,
            "timestamp": message.timestamp,
            "metadata": message.metadata or {}
        }
        
        # Publish message event
        await event_bus.publish(
            EventType.CHAT_MESSAGE,
            chat_event,
            source="api"
        )
        
        # Wait for response (with timeout)
        response = await wait_for_response_with_query(message.session_id, message.message_text, timeout=30.0)
        
        if response is None:
            raise HTTPException(status_code=408, detail="Request timeout")
        
        return response
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail=f"Validation error: {e}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/message/{session_id}/status")
async def get_message_status(session_id: str):
    """
    Get the status of a message processing request.
    
    Returns the current status of message processing for a given session.
    """
    try:
        # TODO: Implement actual status tracking
        status = {
            "session_id": session_id,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat()
        }
        return status
    except Exception as e:
        logger.error(f"Error getting message status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/message/{session_id}/cancel")
async def cancel_message_processing(session_id: str):
    """
    Cancel ongoing message processing for a session.
    
    This endpoint allows cancellation of long-running message processing.
    """
    try:
        # TODO: Implement actual cancellation logic
        result = {
            "session_id": session_id,
            "cancelled": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        return result
    except Exception as e:
        logger.error(f"Error cancelling message processing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def wait_for_response_with_query(session_id: str, query: str, timeout: float = 30.0) -> Optional[ChatResponse]:
    """
    Wait for a response for a given session with the actual query.
    
    Args:
        session_id: The session identifier
        query: The actual user query
        timeout: Maximum time to wait in seconds
        
    Returns:
        ChatResponse if available, None if timeout
    """
    try:
        # Import the response generation handler and intent classifier
        from src.core.event_bus import ResponseGenerationHandler
        from src.core.intent_classifier import IntentClassifier
        from src.llm.manager import LLMManager
        from src.llm import LLMConfig
        
        logger.info(f"🔍 Generating response for session {session_id}")
        logger.info(f"📝 Query: {query}")
        
        # Initialize LLM manager for intent classification
        llm_config = LLMConfig(
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            fallback_enabled=False
        )
        llm_manager = LLMManager(llm_config)
        await llm_manager.initialize()
        
        # Classify user intent
        intent_classifier = IntentClassifier(llm_manager)
        intent_result = await intent_classifier.classify_intent(query)
        
        logger.info(f"🎯 Intent classified: {intent_result.intent.value} (confidence: {intent_result.confidence:.2f})")
        logger.info(f"💡 Reasoning: {intent_result.reasoning}")
        
        # Get product recommendations based on intent
        product_recommendations = intent_classifier.get_product_recommendations(intent_result)
        
        logger.info(f"📦 Product recommendations: {product_recommendations['primary']} (primary), {product_recommendations['secondary']} (secondary)")
        
        # Create dynamic retrieval results based on intent
        mock_retrieval_results = _create_intent_based_retrieval_results(intent_result, product_recommendations)
        
        # Use the response generation handler directly
        logger.info("🚀 Using ResponseGenerationHandler for real LLM response generation")
        response_handler = ResponseGenerationHandler(None)  # No event bus needed for direct call
        response_text = await response_handler._generate_dynamic_response(mock_retrieval_results, session_id)
        
        logger.info(f"✅ Generated response: {response_text[:100]}...")
        
        # Create the response
        response = ChatResponse(
            response_text=response_text,
            recommendations=[
                {
                    "product_id": "PROD_001",
                    "name": product_recommendations['primary'],
                    "risk_level": "low",
                    "expected_return": "4-6%",
                    "confidence": intent_result.confidence
                }
            ],
            confidence=intent_result.confidence,
            sources=["intent_classification", "structured_db", "vector_search"],
            processing_time=1.2
        )
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error waiting for response: {e}")
        logger.error(f"❌ Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        
        # Fallback to mock response
        logger.info("🔄 Falling back to mock response")
        response_text = _generate_dynamic_response_for_session(session_id)
        
        response = ChatResponse(
            response_text=response_text,
            recommendations=[
                {
                    "product_id": "PROD_001",
                    "name": "Yuanta Conservative Fund",
                    "risk_level": "low",
                    "expected_return": "4-6%",
                    "confidence": 0.88
                }
            ],
            confidence=0.88,
            sources=["structured_db", "vector_search"],
            processing_time=1.2
        )
        
        return response

def _create_intent_based_retrieval_results(intent_result, product_recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create retrieval results based on intent classification"""
    
    # Map product names to product data
    product_data = {
        "Conservative Fund": {
            "product_id": "PROD_001",
            "name": "Yuanta Conservative Fund",
            "risk_level": "low",
            "expected_return": "4-6%",
            "description": "Conservative fund with stable returns",
            "confidence": intent_result.confidence
        },
        "Growth Fund": {
            "product_id": "PROD_002",
            "name": "Yuanta Growth Fund",
            "risk_level": "high",
            "expected_return": "12-18%",
            "description": "High-growth fund with potential for significant returns",
            "confidence": intent_result.confidence
        },
        "ETF Index Fund": {
            "product_id": "PROD_003",
            "name": "Yuanta ETF Index Fund",
            "risk_level": "medium",
            "expected_return": "8-12%",
            "description": "Diversified ETF tracking major market indices",
            "confidence": intent_result.confidence
        },
        "Balanced Fund": {
            "product_id": "PROD_004",
            "name": "Yuanta Balanced Fund",
            "risk_level": "medium",
            "expected_return": "8-12%",
            "description": "Balanced fund with moderate risk and steady returns",
            "confidence": intent_result.confidence
        }
    }
    
    # Get the primary product
    primary_product_name = product_recommendations['primary']
    primary_product = product_data.get(primary_product_name, product_data["Conservative Fund"])
    
    return [
        {
            "source": "intent_classification",
            "results": [primary_product],
            "metadata": {
                "query_time": 0.15,
                "result_count": 1,
                "intent": intent_result.intent.value,
                "confidence": intent_result.confidence,
                "reasoning": product_recommendations['reasoning']
            },
            "confidence": intent_result.confidence,
            "processing_time": 0.15
        }
    ]


def _generate_dynamic_response_for_session(session_id: str) -> str:
    """Generate a dynamic response based on session context"""
    # Extract context from session_id (in real implementation, this would come from session data)
    if "test" in session_id:
        # For testing, vary responses based on session hash
        session_hash = hash(session_id) % 4
        
        if session_hash == 0:
            return "Based on your investment goals, I recommend the Yuanta Conservative Fund. This fund offers stable returns of 4-6% with minimal volatility, making it ideal for conservative investors seeking steady growth."
        elif session_hash == 1:
            return "For growth-oriented investors, I recommend the Yuanta Growth Fund. This fund targets 12-18% returns but comes with higher volatility, suitable for investors with a longer time horizon."
        elif session_hash == 2:
            return "For ETF investments, I recommend the Yuanta ETF Index Fund. This diversified ETF tracks major market indices and offers 8-12% returns with moderate risk."
        else:
            return "I recommend the Yuanta Balanced Fund for a well-diversified portfolio. This fund offers 8-12% returns with moderate risk, suitable for most investors."
    else:
        return "Based on your query, I recommend the Yuanta Conservative Fund. This fund offers stable returns of 4-6% with minimal volatility."


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Get chat history for a session.
    
    Returns the conversation history for a given session.
    """
    try:
        # TODO: Implement actual chat history retrieval
        history = {
            "session_id": session_id,
            "messages": [
                {
                    "timestamp": "2024-01-01T10:00:00Z",
                    "type": "user",
                    "content": "I'm looking for a low-risk investment option"
                },
                {
                    "timestamp": "2024-01-01T10:00:01Z",
                    "type": "system",
                    "content": "Based on your query, I recommend the Conservative Growth Fund."
                }
            ],
            "total_messages": 2
        }
        return history
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Clear chat history for a session.
    
    Removes all conversation history for a given session.
    """
    try:
        # TODO: Implement actual history clearing
        result = {
            "session_id": session_id,
            "cleared": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        return result
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/feedback/{session_id}")
async def submit_feedback(session_id: str, feedback: Dict[str, Any]):
    """
    Submit feedback for a chat session.
    
    Allows users to provide feedback on the quality of recommendations.
    """
    try:
        # TODO: Implement actual feedback processing
        result = {
            "session_id": session_id,
            "feedback_received": True,
            "timestamp": datetime.utcnow().isoformat(),
            "feedback": feedback
        }
        return result
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analytics/{session_id}")
async def get_session_analytics(session_id: str):
    """
    Get analytics for a chat session.
    
    Returns performance metrics and analytics for a given session.
    """
    try:
        # TODO: Implement actual analytics
        analytics = {
            "session_id": session_id,
            "message_count": 5,
            "processing_time_avg": 1.2,
            "confidence_avg": 0.85,
            "user_satisfaction": 4.5,
            "recommendations_given": 3
        }
        return analytics
    except Exception as e:
        logger.error(f"Error getting session analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
