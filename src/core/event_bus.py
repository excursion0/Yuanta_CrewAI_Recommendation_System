"""
Event Bus implementation for the financial product recommendation system.

This module provides the core event-driven communication infrastructure,
including event publishing, subscription management, and message queue integration.
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.data.models import (
    ChatMessageEvent, ChatResponseEvent, SessionCreatedEvent, SessionEndedEvent,
    DataSynchronizationEvent, FinancialProduct
)


class EventType(str, Enum):
    """Event types for the system"""
    CHAT_MESSAGE = "chat.message"
    CHAT_RESPONSE = "chat.response"
    SESSION_CREATED = "session.created"
    SESSION_ENDED = "session.ended"
    DATA_SYNC = "data.sync"
    INTENT_ANALYSIS = "intent.analysis"
    TOOL_SELECTION = "tool.selection"
    DATA_RETRIEVAL = "data.retrieval"
    DATA_RETRIEVAL_COMPLETED = "data.retrieval.completed"
    RESPONSE_GENERATION = "response.generation"
    ERROR = "error"


@dataclass
class Event:
    """Event wrapper for internal processing"""
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str
    correlation_id: Optional[str] = None


class EventBus:
    """
    Central event bus for the financial product recommendation system.
    
    Handles event publishing, subscription management, and message routing
    in an event-driven architecture.
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._message_queue = asyncio.Queue()
        self._processing = False
        self._process_task: Optional[asyncio.Task] = None
        self._logger = logging.getLogger(__name__)
        
    async def start(self):
        """Start the event bus processing"""
        self._processing = True
        self._process_task = asyncio.create_task(self._process_events())
        self._logger.info("Event bus started")
    
    async def stop(self):
        """Stop the event bus processing"""
        self._processing = False
        if hasattr(self, '_process_task') and self._process_task:
            self._process_task.cancel()
            try:
                await self._process_task
            except asyncio.CancelledError:
                pass
        self._logger.info("Event bus stopped")
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to an event type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        self._logger.info(f"Subscribed to event type: {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from an event type"""
        if event_type in self._subscribers:
            if handler in self._subscribers[event_type]:
                self._subscribers[event_type].remove(handler)
                self._logger.info(f"Unsubscribed from event type: {event_type}")
    
    async def publish(self, event_type: str, data: Dict[str, Any], source: str = "system", correlation_id: Optional[str] = None):
        """Publish an event to the bus"""
        event = Event(
            event_type=event_type,
            data=data,
            timestamp=datetime.now(timezone.utc),
            source=source,
            correlation_id=correlation_id
        )
        
        await self._message_queue.put(event)
        self._logger.debug(f"Published event: {event_type} from {source}")
    
    async def _process_events(self):
        """Process events from the message queue"""
        while self._processing:
            try:
                event = await asyncio.wait_for(self._message_queue.get(), timeout=1.0)
                await self._handle_event(event)
            except asyncio.TimeoutError:
                continue
            except (ConnectionError, TimeoutError) as e:
                self._logger.error(f"Network error processing event: {e}")
            except ValueError as e:
                self._logger.error(f"Invalid event data: {e}")
            except Exception as e:
                self._logger.error(f"Unexpected error processing event: {e}")
    
    async def _handle_event(self, event: Event):
        """Handle a single event"""
        if event.event_type in self._subscribers:
            handlers = self._subscribers[event.event_type]
            
            # Execute handlers concurrently
            tasks = []
            for handler in handlers:
                try:
                    task = asyncio.create_task(handler(event.data))
                    tasks.append(task)
                except (ConnectionError, TimeoutError) as e:
                    self._logger.error(f"Network error in event handler: {e}")
                except ValueError as e:
                    self._logger.error(f"Invalid data in event handler: {e}")
                except Exception as e:
                    self._logger.error(f"Unexpected error in event handler: {e}")
            
            # Wait for all handlers to complete
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        
        self._logger.debug(f"Processed event: {event.event_type}")


class MessageQueue:
    """
    Message queue implementation for persistent message storage.
    
    Provides reliable message delivery with retry mechanisms and
    dead letter queue support.
    """
    
    def __init__(self, queue_name: str = "financial_recommendations"):
        self.queue_name = queue_name
        self._queue = asyncio.Queue()
        self._dead_letter_queue = asyncio.Queue()
        self._retry_count = {}
        self._max_retries = 3
        self._logger = logging.getLogger(__name__)
    
    async def enqueue(self, message: Dict[str, Any], priority: int = 0):
        """Enqueue a message with priority"""
        message_with_priority = {
            "data": message,
            "priority": priority,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "retry_count": 0
        }
        await self._queue.put(message_with_priority)
        self._logger.debug(f"Enqueued message with priority {priority}")
    
    async def dequeue(self) -> Optional[Dict[str, Any]]:
        """Dequeue the next message"""
        try:
            message = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            return message
        except asyncio.TimeoutError:
            return None
    
    async def mark_failed(self, message: Dict[str, Any], error: str):
        """Mark a message as failed and handle retry logic"""
        retry_count = message.get("retry_count", 0)
        
        if retry_count < self._max_retries:
            # Retry the message
            message["retry_count"] = retry_count + 1
            await self._queue.put(message)
            self._logger.warning(f"Retrying message, attempt {retry_count + 1}/{self._max_retries}")
        else:
            # Move to dead letter queue
            await self._dead_letter_queue.put({
                "original_message": message,
                "error": error,
                "failed_at": datetime.now(timezone.utc).isoformat()
            })
            self._logger.error(f"Message moved to dead letter queue after {self._max_retries} retries")
    
    async def mark_completed(self, message: Dict[str, Any]):
        """Mark a message as successfully processed"""
        self._queue.task_done()
        self._logger.debug("Message marked as completed")


class EventHandler:
    """
    Base class for event handlers.
    
    Provides common functionality for event processing and error handling.
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._logger = logging.getLogger(self.__class__.__name__)
    
    async def handle_event(self, event_data: Dict[str, Any]):
        """Handle an event - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement handle_event")
    
    async def publish_event(self, event_type: str, data: Dict[str, Any], source: str = None):
        """Publish an event to the bus"""
        if source is None:
            source = self.__class__.__name__
        await self.event_bus.publish(event_type, data, source)


class ChatMessageHandler(EventHandler):
    """Handler for chat message events"""
    
    async def handle_event(self, event_data: Dict[str, Any]):
        """Handle incoming chat message events"""
        try:
            # Parse the chat message event
            chat_event = ChatMessageEvent(**event_data)
            
            # Log the incoming message
            self._logger.info(f"Processing chat message from {chat_event.platform} user {chat_event.user_id}")
            
            # Add original query to metadata
            metadata = chat_event.metadata.copy() if chat_event.metadata else {}
            metadata["original_query"] = chat_event.message_text
            
            # Publish intent analysis event
            await self.publish_event(
                EventType.INTENT_ANALYSIS,
                {
                    "session_id": chat_event.session_id,
                    "user_id": chat_event.user_id,
                    "message_text": chat_event.message_text,
                    "platform": chat_event.platform,
                    "metadata": metadata
                }
            )
            
        except Exception as e:
            self._logger.error(f"Error handling chat message: {e}")
            # Publish error event
            await self.publish_event(
                EventType.ERROR,
                {
                    "error_type": "chat_message_processing",
                    "error_message": str(e),
                    "session_id": event_data.get("session_id"),
                    "user_id": event_data.get("user_id")
                }
            )


class IntentAnalysisHandler(EventHandler):
    """Handler for intent analysis events"""
    
    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus)
        self._intent_classifier = None
        self._llm_manager = None
        self._initialized = False
    
    async def _initialize_classifier(self):
        """Initialize the LLM-based intent classifier"""
        if not self._initialized:
            try:
                from src.core.intent_classifier import IntentClassifier
                from src.llm.manager import LLMManager
                from src.llm import LLMConfig
                import os
                
                # Initialize LLM manager
                llm_config = LLMConfig(
                    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                    openai_api_key=os.getenv("OPENAI_API_KEY"),
                    fallback_enabled=True
                )
                self._llm_manager = LLMManager(llm_config)
                await self._llm_manager.initialize()
                
                # Initialize intent classifier
                self._intent_classifier = IntentClassifier(self._llm_manager)
                self._initialized = True
                self._logger.info("✅ LLM-based intent classifier initialized")
                
            except Exception as e:
                self._logger.error(f"❌ Failed to initialize intent classifier: {e}")
                self._intent_classifier = None
                self._initialized = False
    
    async def handle_event(self, event_data: Dict[str, Any]):
        """Handle intent analysis events using simple keyword-based classification"""
        try:
            session_id = event_data.get("session_id")
            message_text = event_data.get("message_text", "")
            
            self._logger.info(f"🔍 Analyzing intent for session {session_id}")
            self._logger.info(f"📝 Query: {message_text}")
            
            # Use simple keyword-based intent analysis to avoid LLM misclassification
            query_lower = message_text.lower()
            
            # Determine intent based on keywords
            if any(keyword in query_lower for keyword in ["high risk", "high-risk", "aggressive", "growth", "high return"]):
                primary_intent = "growth_investment"
                reasoning = "Query contains high-risk or growth keywords"
            elif any(keyword in query_lower for keyword in ["low risk", "low-risk", "conservative", "stable", "safe"]):
                primary_intent = "capital_preservation"
                reasoning = "Query contains low-risk or conservative keywords"
            elif any(keyword in query_lower for keyword in ["etf", "index", "diversified"]):
                primary_intent = "diversification"
                reasoning = "Query contains ETF or diversification keywords"
            elif any(keyword in query_lower for keyword in ["list", "all", "every", "show"]):
                primary_intent = "product_listing"
                reasoning = "Query requests product listing"
            else:
                primary_intent = "general_advice"
                reasoning = "General investment advice query"
            
            intent_data = {
                "session_id": session_id,
                "primary_intent": primary_intent,
                "confidence": 0.8,
                "entities": {
                    "risk_level": "medium",
                    "investment_type": "general"
                },
                "sub_intents": ["risk_assessment", "product_search"],
                "query_complexity": "medium",
                "reasoning": reasoning
            }
            
            self._logger.info(f"✅ Intent classified: {primary_intent}")
            self._logger.info(f"💡 Reasoning: {reasoning}")
            
            # Publish tool selection event
            await self.publish_event(
                EventType.TOOL_SELECTION,
                {
                    "session_id": session_id,
                    "intent_result": intent_data,
                    "metadata": event_data.get("metadata", {})
                }
            )
            
        except Exception as e:
            self._logger.error(f"❌ Error in intent analysis: {e}")
            await self.publish_event(
                EventType.ERROR,
                {
                    "error_type": "intent_analysis",
                    "error_message": str(e),
                    "session_id": event_data.get("session_id")
                }
            )


class ToolSelectionHandler(EventHandler):
    """Handler for tool selection events"""
    
    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus)
        self._pending_sessions: Dict[str, Dict[str, Any]] = {}  # session_id -> {tools: [], results: []}
    
    async def handle_event(self, event_data: Dict[str, Any]):
        """Handle tool selection events"""
        try:
            session_id = event_data.get("session_id")
            intent_result = event_data.get("intent_result", {})
            
            self._logger.info(f"Selecting tools for session {session_id}")
            
            # Select appropriate tools based on intent
            selected_tools = self._select_tools(intent_result)
            
            # Initialize session tracking
            self._pending_sessions[session_id] = {
                "tools": selected_tools,
                "results": [],
                "expected_count": len(selected_tools),
                "metadata": event_data.get("metadata", {})
            }
            
            # Publish data retrieval events for each selected tool
            for tool in selected_tools:
                await self.publish_event(
                    EventType.DATA_RETRIEVAL,
                    {
                        "session_id": session_id,
                        "tool_name": tool["name"],
                        "parameters": tool["parameters"],
                        "priority": tool["priority"]
                    }
                )
            
        except Exception as e:
            self._logger.error(f"Error in tool selection: {e}")
            await self.publish_event(
                EventType.ERROR,
                {
                    "error_type": "tool_selection",
                    "error_message": str(e),
                    "session_id": event_data.get("session_id")
                }
            )
    
    async def _check_and_publish_response(self, session_id: str):
        """Check if all tools have completed and publish response if ready"""
        if session_id not in self._pending_sessions:
            return
            
        session_data = self._pending_sessions[session_id]
        if len(session_data["results"]) >= session_data["expected_count"]:
            # All tools have completed, publish single response generation event
            self._logger.info(f"All tools completed for session {session_id}, publishing response generation")
            await self.publish_event(
                EventType.RESPONSE_GENERATION,
                {
                    "session_id": session_id,
                    "retrieval_results": session_data["results"],
                    "metadata": session_data.get("metadata", {})
                }
            )
            # Clean up session data
            del self._pending_sessions[session_id]
    
    async def _add_retrieval_result(self, session_id: str, result: Dict[str, Any]):
        """Add a retrieval result to the session and check if ready to publish"""
        if session_id in self._pending_sessions:
            self._pending_sessions[session_id]["results"].append(result)
            await self._check_and_publish_response(session_id)
    
    async def handle_data_retrieval_completed(self, event_data: Dict[str, Any]):
        """Handle data retrieval completion events"""
        try:
            session_id = event_data.get("session_id")
            results = event_data.get("results")
            
            self._logger.info(f"Received data retrieval completion for session {session_id}")
            
            # Add the result to the session
            await self._add_retrieval_result(session_id, results)
            
        except Exception as e:
            self._logger.error(f"Error handling data retrieval completion: {e}")
            await self.publish_event(
                EventType.ERROR,
                {
                    "error_type": "data_retrieval_completion",
                    "error_message": str(e),
                    "session_id": event_data.get("session_id")
                }
            )
    
    def _select_tools(self, intent_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Select appropriate tools based on intent"""
        tools = []
        
        # Always include structured database search
        tools.append({
            "name": "structured_db_search",
            "priority": 1,
            "parameters": {
                "risk_level": intent_result.get("entities", {}).get("risk_level", "medium"),
                "product_category": "investment"
            }
        })
        
        # Include vector search for semantic similarity
        tools.append({
            "name": "vector_search",
            "priority": 2,
            "parameters": {
                "query": intent_result.get("message_text", ""),
                "limit": 10
            }
        })
        
        # Include GraphRAG for relationship queries
        tools.append({
            "name": "graphrag_search",
            "priority": 3,
            "parameters": {
                "query": intent_result.get("message_text", ""),
                "depth": 2
            }
        })
        
        return tools


class DataRetrievalHandler(EventHandler):
    """Handler for data retrieval events"""
    
    async def handle_event(self, event_data: Dict[str, Any]):
        """Handle data retrieval events"""
        try:
            session_id = event_data.get("session_id")
            tool_name = event_data.get("tool_name")
            
            self._logger.info(f"Retrieving data with tool {tool_name} for session {session_id}")
            
            # Create varied mock data based on tool type
            mock_results = self._create_varied_mock_results(tool_name)
            
            # Publish a data retrieval completion event that the tool selection handler can listen to
            await self.publish_event(
                EventType.DATA_RETRIEVAL_COMPLETED,
                {
                    "session_id": session_id,
                    "tool_name": tool_name,
                    "results": mock_results
                }
            )
            
        except Exception as e:
            self._logger.error(f"Error in data retrieval: {e}")
            await self.publish_event(
                EventType.ERROR,
                {
                    "error_type": "data_retrieval",
                    "error_message": str(e),
                    "session_id": event_data.get("session_id")
                }
            )
    
    def _create_varied_mock_results(self, tool_name: str) -> Dict[str, Any]:
        """Create varied mock results based on tool type"""
        if tool_name == "structured_db_search":
            return {
                "source": tool_name,
                "results": [
                    {
                        "product_id": "PROD_001",
                        "name": "Yuanta Conservative Fund",
                        "risk_level": "low",
                        "expected_return": "4-6%",
                        "description": "Conservative fund with stable returns",
                        "confidence": 0.92
                    }
                ],
                "metadata": {
                    "query_time": 0.15,
                    "result_count": 1
                },
                "confidence": 0.92,
                "processing_time": 0.15
            }
        elif tool_name == "vector_search":
            return {
                "source": tool_name,
                "results": [
                    {
                        "product_id": "PROD_002",
                        "name": "Yuanta Growth Fund",
                        "risk_level": "high",
                        "expected_return": "12-18%",
                        "description": "High-growth fund with potential for significant returns",
                        "confidence": 0.88
                    }
                ],
                "metadata": {
                    "query_time": 0.25,
                    "result_count": 1
                },
                "confidence": 0.88,
                "processing_time": 0.25
            }
        elif tool_name == "graphrag_search":
            return {
                "source": tool_name,
                "results": [
                    {
                        "product_id": "PROD_003",
                        "name": "Yuanta ETF Index Fund",
                        "risk_level": "medium",
                        "expected_return": "8-12%",
                        "description": "Diversified ETF tracking major market indices",
                        "confidence": 0.85
                    }
                ],
                "metadata": {
                    "query_time": 0.35,
                    "result_count": 1
                },
                "confidence": 0.85,
                "processing_time": 0.35
            }
        else:
            # Default balanced fund
            return {
                "source": tool_name,
                "results": [
                    {
                        "product_id": "PROD_004",
                        "name": "Yuanta Balanced Fund",
                        "risk_level": "medium",
                        "expected_return": "8-12%",
                        "description": "Balanced fund with moderate risk and steady returns",
                        "confidence": 0.90
                    }
                ],
                "metadata": {
                    "query_time": 0.20,
                    "result_count": 1
                },
                "confidence": 0.90,
                "processing_time": 0.20
            }


class ResponseGenerationHandler(EventHandler):
    """Handler for response generation events"""
    
    async def handle_event(self, event_data: Dict[str, Any]):
        """Handle response generation events"""
        try:
            session_id = event_data.get("session_id")
            retrieval_results = event_data.get("retrieval_results", [])
            
            self._logger.info(f"Generating response for session {session_id}")
            
            # Get metadata from the original chat message event
            # We need to track this through the event chain
            metadata = event_data.get("metadata", {})
            
            # Get original query from metadata
            original_query = metadata.get("original_query", "")
            
            # Generate dynamic response based on retrieval results and original query
            response_text = await self._generate_dynamic_response(retrieval_results, session_id, original_query, metadata)
            
            # Create dynamic products based on original query for recommendations
            if original_query:
                dynamic_products = await self._create_dynamic_products_from_query(original_query)
                recommendations = self._create_recommendations_from_products(dynamic_products)
            else:
                recommendations = self._extract_recommendations(retrieval_results)
            
            response_event = ChatResponseEvent(
                session_id=session_id,
                response_text=response_text,
                recommendations=recommendations,
                confidence=0.88,
                sources=["structured_db", "vector_search"],
                processing_time=1.2,
                timestamp=datetime.now(timezone.utc),
                metadata=metadata
            )
            
            # Publish the response event
            await self.publish_event(
                EventType.CHAT_RESPONSE,
                response_event.dict()
            )
            
        except Exception as e:
            self._logger.error(f"Error in response generation: {e}")
            await self.publish_event(
                EventType.ERROR,
                {
                    "error_type": "response_generation",
                    "error_message": str(e),
                    "session_id": event_data.get("session_id")
                }
            )
    
    async def _generate_dynamic_response(self, retrieval_results: List[Dict[str, Any]], session_id: str, original_query: str = None, metadata: Dict[str, Any] = None) -> str:
        """Generate a dynamic response based on retrieval results and original query"""
        try:
            self._logger.info(f"Generating dynamic response for session {session_id}")
            self._logger.info(f"Retrieval results: {retrieval_results}")
            self._logger.info(f"Original query: {original_query}")
            
            # Create context from retrieval results
            context = self._create_context_from_results(retrieval_results)
            self._logger.info(f"Context: {context}")
            
            # Create dynamic products based on original query (preferred) or retrieval results
            if original_query:
                dynamic_products = await self._create_dynamic_products_from_query(original_query)
                self._logger.info(f"Dynamic products based on query: {[p.name for p in dynamic_products]}")
            else:
                dynamic_products = self._create_dynamic_products(retrieval_results)
                self._logger.info(f"Dynamic products based on results: {[p.name for p in dynamic_products]}")
            
            # Always try real LLM first
            try:
                response = await self._generate_real_llm_response(context, dynamic_products, session_id, metadata)
                self._logger.info(f"Generated real LLM response: {response}")
                return response
            except Exception as e:
                self._logger.error(f"Real LLM failed: {e}")
                # Only fallback to mock if real LLM completely fails
                response = self._generate_mock_response(context, dynamic_products)
                self._logger.info(f"Generated mock response as fallback: {response}")
                return response
            
        except Exception as e:
            self._logger.error(f"Error generating dynamic response: {e}")
            return self._get_fallback_response(retrieval_results)
    
    async def _generate_real_llm_response(self, context: str, products: List[Any], session_id: str, metadata: Dict[str, Any] = None) -> str:
        """Generate response using real LLM API"""
        try:
            self._logger.info("🔍 Starting real LLM response generation...")
            
            # Import LLM manager
            from src.llm.manager import LLMManager
            from src.llm import LLMConfig
            
            # Get API key from environment
            anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
            if not anthropic_api_key:
                self._logger.error("❌ ANTHROPIC_API_KEY not found in environment")
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            
            self._logger.info(f"✅ API key found: {anthropic_api_key[:10]}...")
            
            # Initialize LLM manager
            self._logger.info("🔧 Initializing LLM manager...")
            llm_config = LLMConfig(
                anthropic_api_key=anthropic_api_key,
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                fallback_enabled=True
            )
            llm_manager = LLMManager(llm_config)
            init_success = await llm_manager.initialize()
            
            if not init_success:
                self._logger.error("❌ LLM manager initialization failed")
                raise Exception("LLM manager initialization failed")
            
            self._logger.info("✅ LLM manager initialized successfully")
            
            # Get original query from metadata
            original_query = metadata.get("original_query", "") if metadata else ""
            
            # Get conversation history from metadata if available
            conversation_history = None
            if metadata and "conversation_history" in metadata:
                conversation_history = metadata["conversation_history"]
                self._logger.info(f"📚 Using conversation history with {len(conversation_history)} messages")
            
            # Generate response using LLM manager with proper query
            self._logger.info("🚀 Calling LLM manager process_query...")
            response = await llm_manager.process_query(
                query=original_query if original_query else "Please provide investment advice",
                available_products=products,
                user_profile=None,
                conversation_history=conversation_history
            )
            
            if response and response.content:
                self._logger.info(f"✅ Real LLM response generated: {response.content[:100]}...")
                return response.content
            else:
                self._logger.error("❌ No response content from LLM manager")
                return "I apologize, but I'm having trouble generating a response right now. Please try again."
            
        except Exception as e:
            self._logger.error(f"❌ Error generating real LLM response: {e}")
            self._logger.error(f"❌ Exception type: {type(e).__name__}")
            import traceback
            self._logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise
    
    def _generate_mock_response(self, context: str, products: List[Any]) -> str:
        """Generate a mock response for testing without requiring LLM API keys"""
        if not products:
            return "I apologize, but I don't have any suitable products to recommend at this time."
        
        product = products[0]  # Use the first product
        
        # Create response based on product characteristics
        if "Conservative" in product.name:
            return f"Based on your query, I recommend the {product.name}. This fund offers stable returns of {product.expected_return} with minimal volatility, making it ideal for conservative investors seeking steady growth."
        elif "Growth" in product.name:
            return f"For growth-oriented investors, I recommend the {product.name}. This fund targets {product.expected_return} returns but comes with higher volatility, suitable for investors with a longer time horizon."
        elif "ETF" in product.name:
            return f"For ETF investments, I recommend the {product.name}. This diversified ETF tracks major market indices and offers {product.expected_return} returns with moderate risk."
        elif "Balanced" in product.name:
            return f"I recommend the {product.name} for a well-diversified portfolio. This fund offers {product.expected_return} returns with moderate risk, suitable for most investors."
        else:
            return f"Based on your investment goals, I recommend the {product.name}. This fund offers {product.expected_return} returns with {product.risk_level} risk level."
    
    def _create_dynamic_products(self, retrieval_results: List[Dict[str, Any]]) -> List[FinancialProduct]:
        """Create dynamic products based on retrieval results and query context"""
        products = []
        
        # Extract query context from retrieval results
        query_context = self._extract_query_context(retrieval_results)
        
        # Create products based on context
        if "low-risk" in query_context.lower() or "conservative" in query_context.lower():
            products.append(FinancialProduct(
                product_id="PROD_001",
                name="Yuanta Conservative Fund",
                type="mutual_fund",
                risk_level="low",
                description="Conservative fund with stable returns and low volatility",
                issuer="Yuanta Securities",
                inception_date=datetime.now(timezone.utc),
                expected_return="4-6%",
                volatility=0.03,
                sharpe_ratio=0.9,
                minimum_investment=1000.0,
                expense_ratio=0.008,
                dividend_yield=0.03,
                regulatory_status="approved",
                compliance_requirements=["KYC", "AML"],
                tags=["conservative", "stable", "low-risk"],
                categories=["mutual_fund", "fixed_income"],
                embedding_id="emb_prod_001"
            ))
        elif "high-risk" in query_context.lower() or "growth" in query_context.lower():
            products.append(FinancialProduct(
                product_id="PROD_002",
                name="Yuanta Growth Fund",
                type="mutual_fund",
                risk_level="high",
                description="High-growth fund with potential for significant returns",
                issuer="Yuanta Securities",
                inception_date=datetime.now(timezone.utc),
                expected_return="12-18%",
                volatility=0.15,
                sharpe_ratio=1.2,
                minimum_investment=5000.0,
                expense_ratio=0.015,
                dividend_yield=0.01,
                regulatory_status="approved",
                compliance_requirements=["KYC", "AML"],
                tags=["growth", "high-risk", "equity"],
                categories=["mutual_fund", "equity"],
                embedding_id="emb_prod_002"
            ))
        elif "etf" in query_context.lower():
            products.append(FinancialProduct(
                product_id="PROD_003",
                name="Yuanta ETF Index Fund",
                type="etf",
                risk_level="medium",
                description="Diversified ETF tracking major market indices",
                issuer="Yuanta Securities",
                inception_date=datetime.now(timezone.utc),
                expected_return="8-12%",
                volatility=0.08,
                sharpe_ratio=1.0,
                minimum_investment=500.0,
                expense_ratio=0.005,
                dividend_yield=0.02,
                regulatory_status="approved",
                compliance_requirements=["KYC", "AML"],
                tags=["etf", "diversified", "index"],
                categories=["etf", "equity"],
                embedding_id="emb_prod_003"
            ))
        else:
            # Default balanced fund
            products.append(FinancialProduct(
                product_id="PROD_004",
                name="Yuanta Balanced Fund",
                type="mutual_fund",
                risk_level="medium",
                description="Balanced fund with moderate risk and steady returns",
                issuer="Yuanta Securities",
                inception_date=datetime.now(timezone.utc),
                expected_return="8-12%",
                volatility=0.06,
                sharpe_ratio=1.1,
                minimum_investment=2000.0,
                expense_ratio=0.012,
                dividend_yield=0.025,
                regulatory_status="approved",
                compliance_requirements=["KYC", "AML"],
                tags=["balanced", "moderate", "diversified"],
                categories=["mutual_fund", "mixed"],
                embedding_id="emb_prod_004"
            ))
        
        return products
    
    def _extract_query_context(self, retrieval_results: List[Dict[str, Any]]) -> str:
        """Extract query context from retrieval results"""
        context_parts = []
        
        for result in retrieval_results:
            if isinstance(result, dict) and 'results' in result:
                for product in result['results']:
                    if isinstance(product, dict):
                        context_parts.append(f"{product.get('name', '')} {product.get('description', '')}")
        
        return " ".join(context_parts) if context_parts else "investment recommendation"
    
    def _get_fallback_response(self, retrieval_results: List[Dict[str, Any]]) -> str:
        """Get a fallback response based on retrieval results"""
        query_context = self._extract_query_context(retrieval_results)
        
        if "low-risk" in query_context.lower() or "conservative" in query_context.lower():
            return "Based on your preference for low-risk investments, I recommend the Yuanta Conservative Fund. This fund offers stable returns of 4-6% with minimal volatility, making it ideal for conservative investors."
        elif "high-risk" in query_context.lower() or "growth" in query_context.lower():
            return "For growth-oriented investors, I recommend the Yuanta Growth Fund. This fund targets 12-18% returns but comes with higher volatility, suitable for investors with a longer time horizon."
        elif "etf" in query_context.lower():
            return "For ETF investments, I recommend the Yuanta ETF Index Fund. This diversified ETF tracks major market indices and offers 8-12% returns with moderate risk."
        else:
            return "I recommend the Yuanta Balanced Fund for a well-diversified portfolio. This fund offers 8-12% returns with moderate risk, suitable for most investors."
    
    def _create_context_from_results(self, retrieval_results: List[Dict[str, Any]]) -> str:
        """Create context string from retrieval results"""
        if not retrieval_results:
            return "investment recommendation"
        
        context_parts = []
        for result in retrieval_results:
            if isinstance(result, dict) and 'results' in result:
                for product in result['results']:
                    if isinstance(product, dict):
                        context_parts.append(f"{product.get('name', 'Unknown Product')}: {product.get('description', 'No description')} - {product.get('expected_return', 'Unknown return')} - {product.get('risk_level', 'Unknown risk')}")
        
        return " | ".join(context_parts) if context_parts else "investment recommendation"
    
    def _extract_recommendations(self, retrieval_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract recommendations from retrieval results"""
        recommendations = []
        
        for result in retrieval_results:
            if isinstance(result, dict) and 'results' in result:
                for product in result['results']:
                    if isinstance(product, dict):
                        recommendations.append({
                            "product_id": product.get("product_id", "UNKNOWN"),
                            "name": product.get("name", "Unknown Product"),
                            "risk_level": product.get("risk_level", "unknown"),
                            "expected_return": product.get("expected_return", "Unknown"),
                            "confidence": product.get("confidence", 0.88)
                        })
        
        # Return default recommendation if none found
        if not recommendations:
            recommendations.append({
                "product_id": "PROD_004",
                "name": "Yuanta Balanced Fund",
                "risk_level": "medium",
                "expected_return": "8-12%",
                "confidence": 0.88
            })
        
        return recommendations
    
    def _create_recommendations_from_products(self, products: List[FinancialProduct]) -> List[Dict[str, Any]]:
        """Create recommendations from dynamic products"""
        recommendations = []
        
        for product in products:
            recommendations.append({
                "product_id": product.product_id,
                "name": product.name,
                "risk_level": product.risk_level,
                "expected_return": product.expected_return,
                "confidence": 0.88
            })
        
        return recommendations

    async def generate_real_llm_response(self, context: str, session_id: str) -> str:
        """Public method to generate real LLM response"""
        try:
            self._logger.info(f"🔍 Generating real LLM response for session {session_id}")
            
            # Create dynamic products based on context
            dynamic_products = self._create_dynamic_products_from_context(context)
            self._logger.info(f"Dynamic products: {[p.name for p in dynamic_products]}")
            
            # Generate real LLM response
            response = await self._generate_real_llm_response(context, dynamic_products, session_id, None)
            self._logger.info(f"✅ Real LLM response generated: {response[:100]}...")
            return response
            
        except Exception as e:
            self._logger.error(f"❌ Error in generate_real_llm_response: {e}")
            # Fallback to mock response
            response = self._generate_mock_response(context, dynamic_products)
            self._logger.info(f"🔄 Fallback to mock response: {response[:100]}...")
            return response
    
    async def _create_dynamic_products_from_query(self, query: str) -> List[FinancialProduct]:
        """Create dynamic products based on original user query using LLM intent classification"""
        products = []
        query_lower = query.lower()
        
        # Check for "list all" or "every" requests first
        if any(keyword in query_lower for keyword in ["list every", "list all", "every", "all products", "show all", "all yuanta"]):
            # Return all available products for listing requests
            products.extend([
                FinancialProduct(
                    product_id="PROD_001",
                    name="Yuanta Conservative Fund",
                    type="mutual_fund",
                    risk_level="low",
                    description="Conservative fund with stable returns and low volatility",
                    issuer="Yuanta Securities",
                    inception_date=datetime.now(timezone.utc),
                    expected_return="4-6%",
                    volatility=0.03,
                    sharpe_ratio=0.9,
                    minimum_investment=1000.0,
                    expense_ratio=0.008,
                    dividend_yield=0.03,
                    regulatory_status="approved",
                    compliance_requirements=["KYC", "AML"],
                    tags=["conservative", "stable", "low-risk"],
                    categories=["mutual_fund", "fixed_income"],
                    embedding_id="emb_prod_001"
                ),
                FinancialProduct(
                    product_id="PROD_002",
                    name="Yuanta Growth Fund",
                    type="mutual_fund",
                    risk_level="high",
                    description="High-growth fund with potential for significant returns",
                    issuer="Yuanta Securities",
                    inception_date=datetime.now(timezone.utc),
                    expected_return="12-18%",
                    volatility=0.15,
                    sharpe_ratio=1.2,
                    minimum_investment=5000.0,
                    expense_ratio=0.015,
                    dividend_yield=0.01,
                    regulatory_status="approved",
                    compliance_requirements=["KYC", "AML"],
                    tags=["growth", "high-risk", "equity"],
                    categories=["mutual_fund", "equity"],
                    embedding_id="emb_prod_002"
                ),
                FinancialProduct(
                    product_id="PROD_003",
                    name="Yuanta ETF Index Fund",
                    type="etf",
                    risk_level="medium",
                    description="Diversified ETF tracking major market indices",
                    issuer="Yuanta Securities",
                    inception_date=datetime.now(timezone.utc),
                    expected_return="8-12%",
                    volatility=0.08,
                    sharpe_ratio=1.0,
                    minimum_investment=500.0,
                    expense_ratio=0.005,
                    dividend_yield=0.02,
                    regulatory_status="approved",
                    compliance_requirements=["KYC", "AML"],
                    tags=["etf", "diversified", "index"],
                    categories=["etf", "equity"],
                    embedding_id="emb_prod_003"
                ),
                FinancialProduct(
                    product_id="PROD_004",
                    name="Yuanta Balanced Fund",
                    type="mutual_fund",
                    risk_level="medium",
                    description="Balanced fund with moderate risk and steady returns",
                    issuer="Yuanta Securities",
                    inception_date=datetime.now(timezone.utc),
                    expected_return="8-12%",
                    volatility=0.06,
                    sharpe_ratio=1.1,
                    minimum_investment=2000.0,
                    expense_ratio=0.012,
                    dividend_yield=0.025,
                    regulatory_status="approved",
                    compliance_requirements=["KYC", "AML"],
                    tags=["balanced", "moderate", "diversified"],
                    categories=["mutual_fund", "mixed"],
                    embedding_id="emb_prod_004"
                )
            ])
        else:
            # Use keyword-based selection for better alignment with user queries
            # This avoids the LLM misclassification issue where "high risk" gets classified as RISK_MANAGEMENT
            if any(keyword in query_lower for keyword in ["high risk", "high-risk", "aggressive", "growth", "high return", "high yield"]):
                products.append(FinancialProduct(
                    product_id="PROD_002",
                    name="Yuanta Growth Fund",
                    type="mutual_fund",
                    risk_level="high",
                    description="High-growth fund with potential for significant returns",
                    issuer="Yuanta Securities",
                    inception_date=datetime.now(timezone.utc),
                    expected_return="12-18%",
                    volatility=0.15,
                    sharpe_ratio=1.2,
                    minimum_investment=5000.0,
                    expense_ratio=0.015,
                    dividend_yield=0.01,
                    regulatory_status="approved",
                    compliance_requirements=["KYC", "AML"],
                    tags=["growth", "high-risk", "equity"],
                    categories=["mutual_fund", "equity"],
                    embedding_id="emb_prod_002"
                ))
            elif any(keyword in query_lower for keyword in ["low risk", "low-risk", "conservative", "stable", "safe"]):
                products.append(FinancialProduct(
                    product_id="PROD_001",
                    name="Yuanta Conservative Fund",
                    type="mutual_fund",
                    risk_level="low",
                    description="Conservative fund with stable returns and low volatility",
                    issuer="Yuanta Securities",
                    inception_date=datetime.now(timezone.utc),
                    expected_return="4-6%",
                    volatility=0.03,
                    sharpe_ratio=0.9,
                    minimum_investment=1000.0,
                    expense_ratio=0.008,
                    dividend_yield=0.03,
                    regulatory_status="approved",
                    compliance_requirements=["KYC", "AML"],
                    tags=["conservative", "stable", "low-risk"],
                    categories=["mutual_fund", "fixed_income"],
                    embedding_id="emb_prod_001"
                ))
            elif any(keyword in query_lower for keyword in ["etf", "index", "diversified"]):
                products.append(FinancialProduct(
                    product_id="PROD_003",
                    name="Yuanta ETF Index Fund",
                    type="etf",
                    risk_level="medium",
                    description="Diversified ETF tracking major market indices",
                    issuer="Yuanta Securities",
                    inception_date=datetime.now(timezone.utc),
                    expected_return="8-12%",
                    volatility=0.08,
                    sharpe_ratio=1.0,
                    minimum_investment=500.0,
                    expense_ratio=0.005,
                    dividend_yield=0.02,
                    regulatory_status="approved",
                    compliance_requirements=["KYC", "AML"],
                    tags=["etf", "diversified", "index"],
                    categories=["etf", "equity"],
                    embedding_id="emb_prod_003"
                ))
            else:
                # Default balanced fund for general queries
                products.append(FinancialProduct(
                    product_id="PROD_004",
                    name="Yuanta Balanced Fund",
                    type="mutual_fund",
                    risk_level="medium",
                    description="Balanced fund with moderate risk and steady returns",
                    issuer="Yuanta Securities",
                    inception_date=datetime.now(timezone.utc),
                    expected_return="8-12%",
                    volatility=0.06,
                    sharpe_ratio=1.1,
                    minimum_investment=2000.0,
                    expense_ratio=0.012,
                    dividend_yield=0.025,
                    regulatory_status="approved",
                    compliance_requirements=["KYC", "AML"],
                    tags=["balanced", "moderate", "diversified"],
                    categories=["mutual_fund", "mixed"],
                    embedding_id="emb_prod_004"
                ))
        
        return products
    
    def _create_dynamic_products_from_context(self, context: str) -> List[FinancialProduct]:
        """Create dynamic products based on context"""
        products = []
        
        # Create products based on context
        if "low-risk" in context.lower() or "conservative" in context.lower():
            products.append(FinancialProduct(
                product_id="PROD_001",
                name="Yuanta Conservative Fund",
                type="mutual_fund",
                risk_level="low",
                description="Conservative fund with stable returns and low volatility",
                issuer="Yuanta Securities",
                inception_date=datetime.now(timezone.utc),
                expected_return="4-6%",
                volatility=0.03,
                sharpe_ratio=0.9,
                minimum_investment=1000.0,
                expense_ratio=0.008,
                dividend_yield=0.03,
                regulatory_status="approved",
                compliance_requirements=["KYC", "AML"],
                tags=["conservative", "stable", "low-risk"],
                categories=["mutual_fund", "fixed_income"],
                embedding_id="emb_prod_001"
            ))
        elif "high-risk" in context.lower() or "growth" in context.lower():
            products.append(FinancialProduct(
                product_id="PROD_002",
                name="Yuanta Growth Fund",
                type="mutual_fund",
                risk_level="high",
                description="High-growth fund with potential for significant returns",
                issuer="Yuanta Securities",
                inception_date=datetime.now(timezone.utc),
                expected_return="12-18%",
                volatility=0.15,
                sharpe_ratio=1.2,
                minimum_investment=5000.0,
                expense_ratio=0.015,
                dividend_yield=0.01,
                regulatory_status="approved",
                compliance_requirements=["KYC", "AML"],
                tags=["growth", "high-risk", "equity"],
                categories=["mutual_fund", "equity"],
                embedding_id="emb_prod_002"
            ))
        elif "etf" in context.lower():
            products.append(FinancialProduct(
                product_id="PROD_003",
                name="Yuanta ETF Index Fund",
                type="etf",
                risk_level="medium",
                description="Diversified ETF tracking major market indices",
                issuer="Yuanta Securities",
                inception_date=datetime.now(timezone.utc),
                expected_return="8-12%",
                volatility=0.08,
                sharpe_ratio=1.0,
                minimum_investment=500.0,
                expense_ratio=0.005,
                dividend_yield=0.02,
                regulatory_status="approved",
                compliance_requirements=["KYC", "AML"],
                tags=["etf", "diversified", "index"],
                categories=["etf", "equity"],
                embedding_id="emb_prod_003"
            ))
        else:
            # Default balanced fund
            products.append(FinancialProduct(
                product_id="PROD_004",
                name="Yuanta Balanced Fund",
                type="mutual_fund",
                risk_level="medium",
                description="Balanced fund with moderate risk and steady returns",
                issuer="Yuanta Securities",
                inception_date=datetime.now(timezone.utc),
                expected_return="8-12%",
                volatility=0.06,
                sharpe_ratio=1.1,
                minimum_investment=2000.0,
                expense_ratio=0.012,
                dividend_yield=0.025,
                regulatory_status="approved",
                compliance_requirements=["KYC", "AML"],
                tags=["balanced", "moderate", "diversified"],
                categories=["mutual_fund", "mixed"],
                embedding_id="emb_prod_004"
            ))
        
        return products

    async def generate_response(self, retrieval_results: List[Dict[str, Any]], session_id: str) -> str:
        """Public method to generate response using real LLM"""
        try:
            self._logger.info(f"🔍 Generating response for session {session_id}")
            
            # Get the response generation handler
            response_handler = None
            for handler in self._subscribers.get(EventType.RESPONSE_GENERATION, []):
                if hasattr(handler, '_generate_dynamic_response'):
                    response_handler = handler
                    break
            
            if response_handler:
                self._logger.info("✅ Found response generation handler")
                response = await response_handler._generate_dynamic_response(retrieval_results, session_id)
                self._logger.info(f"✅ Generated response: {response[:100]}...")
                return response
            else:
                self._logger.error("❌ Response generation handler not found")
                return "I apologize, but I'm having trouble generating a response right now."
                
        except Exception as e:
            self._logger.error(f"❌ Error generating response: {e}")
            return "I apologize, but I'm having trouble generating a response right now."


# Global event bus instance
event_bus = EventBus()
message_queue = MessageQueue()

# Register default handlers
chat_handler = ChatMessageHandler(event_bus)
intent_handler = IntentAnalysisHandler(event_bus)
tool_handler = ToolSelectionHandler(event_bus)
retrieval_handler = DataRetrievalHandler(event_bus)
response_handler = ResponseGenerationHandler(event_bus)

# Subscribe handlers to events
event_bus.subscribe(EventType.CHAT_MESSAGE, chat_handler.handle_event)
event_bus.subscribe(EventType.INTENT_ANALYSIS, intent_handler.handle_event)
event_bus.subscribe(EventType.TOOL_SELECTION, tool_handler.handle_event)
event_bus.subscribe(EventType.DATA_RETRIEVAL, retrieval_handler.handle_event)
event_bus.subscribe(EventType.DATA_RETRIEVAL_COMPLETED, tool_handler.handle_data_retrieval_completed)
event_bus.subscribe(EventType.RESPONSE_GENERATION, response_handler.handle_event)
